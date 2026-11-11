[← Spis treści](../README.md)
<!-- status: expanded -->

# Migracje schematu, testy integracyjne i odtwarzanie danych

## Cele

Po tym rozdziale potrafisz:

- rozłożyć niezgodną zmianę schematu na zgodne etapy wdrożenia;
- dobrać izolację testów bazy do badanego zachowania;
- zaplanować sprawdzalne odtworzenie i nazwać dopuszczalną utratę danych.

## Model — Schemat jest współdzielonym kontraktem

W czasie rolling deployment stara i nowa aplikacja mogą używać tej samej bazy. Migracja nie jest prywatnym szczegółem nowego binarium. Usunięcie kolumny odczytywanej przez poprzednią wersję przerwie działające repliki nawet wtedy, gdy nowe zapytania poprawnie się kompilują. Klientem schematu są także zadania okresowe, raporty i narzędzia administracyjne.

Stosuj rozszerzenie i późniejsze zawężenie (expand–contract). Najpierw dodaj nową reprezentację, którą stary kod może ignorować. Wersja przejściowa nadal czyta stare pole, ale zapisuje oba pola atomowo, według jednej ustalonej transformacji. Wdróż taki dual-write do **wszystkich writerów**: replik, workerów, importów i narzędzi administracyjnych. Dopiero bariera zgodności — brak starych writerów oraz zakończenie ich rozpoczętych transakcji — pozwala rozpocząć backfill i później przełączyć odczyty. Stara wersja zapisująca jedno pole nie może wrócić przez rollback wdrożenia. Samo dodanie kolumny nie synchronizuje danych.

Przykład: kolumna `pelna_nazwa` objęta `NOT NULL` ma zostać zastąpiona przez początkowo nullable `nazwa_wyswietlana`. Podczas wdrażania wersji przejściowej `pelna_nazwa` pozostaje źródłem prawdy dla odczytu. Po barierze backfill uzgadnia nową kolumnę z aktualną starą wartością, także gdy nowa kolumna jest już nie-NULL: stary writer mógł ją wcześniej pozostawić nieaktualną. Każda partia wykonuje przypisanie bezpośrednio w SQL, bez wcześniejszego pobierania starej wartości do aplikacji. Bieżący dual-write utrzymuje zgodność obu pól podczas backfillu. Po sprawdzeniu kompletności i zgodności przełącz odczyty; usunięcie starej kolumny następuje jeszcze później. Nie interpretuj pustego tekstu jako braku wartości bez kontraktu domeny.

SQL jest szkicem dla PostgreSQL, zależnym od istniejącej tabeli i wersji silnika; nie jest wykonywany przez rustdoc. Zachowanie `ALTER TABLE`, wartości domyślnych i ograniczeń sprawdzono 2026-11-11 w [dokumentacji PostgreSQL](https://www.postgresql.org/docs/current/ddl-alter.html).

~~~text
ALTER TABLE osoby ADD COLUMN nazwa_wyswietlana text;
-- Wersja przejściowa: wszyscy writerzy zapisują oba pola atomowo,
-- czytelnicy nadal używają pelna_nazwa. Najpierw bariera zgodności.
UPDATE osoby SET nazwa_wyswietlana = pelna_nazwa
WHERE id >= $1 AND id < $2
  AND nazwa_wyswietlana IS DISTINCT FROM pelna_nazwa;
-- Po uzgodnieniu wszystkich partii i sprawdzeniu braku rozbieżności:
ALTER TABLE osoby ALTER COLUMN nazwa_wyswietlana SET NOT NULL;
-- Dopiero teraz można przełączyć odczyt na nazwa_wyswietlana.
~~~

Regresję ujawnia konkretny przeplot: `(Ala, NULL)` → przedwczesny backfill `(Ala, Ala)` → stary writer zmienia tylko `pelna_nazwa` na `Beata`, pozostawiając `(Beata, Ala)`. Odczyt nowego pola z fallbackiem zwróci `Ala`, ponieważ nowe pole nie jest NULL. Sam warunek `IS NULL` nigdy już tego wiersza nie naprawi. `IS DISTINCT FROM` wykrywa zarówno różnicę wartości, jak i obecność NULL tylko po jednej stronie; zobacz [predykaty porównań PostgreSQL](https://www.postgresql.org/docs/current/functions-comparison.html), sprawdzone 2026-11-11. Kolejność wdrożenia jest wnioskiem z protokołu migracji, nie szczególną gwarancją frameworka.

Test konceptualny powinien najpierw odtworzyć ten błędny harmonogram i wykazać nieaktualny odczyt. W poprawnym wariancie przed przełączeniem odczytu potwierdź barierę writerów, uzgodnij także początkowy stan `(Beata, Ala)` i sprawdź oba porządki operacji: backfill przed atomowym dual-write `Celina/Celina` oraz dual-write przed backfillem. W obu przypadkach wynik ma być `(Celina, Celina)`. Test integracyjny wymaga PostgreSQL i dwóch połączeń; nie został tutaj wykonany. Zachowanie konkurujących `UPDATE` i ponownej oceny warunku po oczekiwaniu opisuje [izolacja PostgreSQL](https://www.postgresql.org/docs/current/transaction-iso.html), sprawdzona 2026-11-11.

Duży `UPDATE` może trzymać blokady, produkować dziennik zmian i zwiększać opóźnienie replik. Partie ograniczają pracę jednego przebiegu i pozwalają wznowić proces, ale zwiększają liczbę commitów. Dobierz wielkość na podstawie pomiaru, nie stałej „bezpiecznej dla wszystkich baz”. Sprawdzenie `NOT NULL` oraz budowa indeksu też mają koszty i wymagania blokad. Nie przenoś gwarancji PostgreSQL na SQLite lub MySQL.

## Planowanie wznowienia

Backfill powinien być idempotentny i mieć trwały punkt wznowienia. Zakresy kluczy są zwykle łatwiejsze do odtworzenia niż rosnący `OFFSET`, lecz wymagają określenia zachowania wobec nowych wierszy i nieciągłych identyfikatorów. Numer ostatniego zakresu nie dowodzi kompletności, jeżeli część rekordów była pomijana po błędzie.

~~~rust
fn nastepny_zakres(start: u64, koniec: u64, partia: u64)
    -> Option<std::ops::Range<u64>>
{
    if partia == 0 || start >= koniec { return None; }
    Some(start..start.saturating_add(partia).min(koniec))
}
fn main() {
    assert_eq!(nastepny_zakres(8, 11, 2), Some(8..10));
    assert_eq!(nastepny_zakres(10, 11, 2), Some(10..11));
    assert_eq!(nastepny_zakres(11, 11, 2), None);
}
~~~

Zakres jest półotwarty. Po udanym zatwierdzeniu partii nowym startem jest `range.end`. Punkt wznowienia zapisuj atomowo z partią albo projektuj powtórzenie zakresu jako nieszkodliwe. Nasycone dodawanie zapobiega przepełnieniu granicy; kod nie ma reprezentować klucza większego niż `u64::MAX` jako końca półotwartego. Dla pełnej przestrzeni wartości potrzebny jest inny model, np. ostatni przetworzony klucz i osobny stan końca.

## Diagnostyka kompilatora

**Third-party:** makro SQLx `query!` weryfikuje zapytanie względem bazy dostępnej w czasie budowania albo przygotowanych metadanych offline. Błąd brakującej kolumny może oznaczać niezgodność migracji i środowiska CI, a `Option<T>` — nullable wynik. Nie usuwaj `Option` przez arbitralne wymuszenie non-null, jeżeli join może tworzyć puste wartości. Wymagania opisuje [SQLx query! 0.8.6](https://docs.rs/sqlx/0.8.6/sqlx/macro.query.html), zweryfikowane 2026-11-11.

Kompilacja nie dowodzi, że aktualna produkcyjna baza ma ten sam schemat ani że plan zapytania jest tani. Metadane offline też trzeba odnawiać i kontrolować w CI. Dynamiczne `query()` przenosi część błędów do wykonania; jest przydatne, ale wymaga testów dekodowania i odpowiednich przypadków nullability.

## Testy integracyjne i izolacja

Testuj na silniku oraz wersji zbliżonej do produkcyjnej. SQLite w pamięci nie sprawdzi blokad PostgreSQL. Rollback po teście jest szybki, lecz nie izoluje operacji wykonywanych przez inne połączenia ani efektów zewnętrznych. Osobna baza lub schemat na test kosztuje więcej, ale umożliwia test migracji, wielu połączeń i rzeczywistego commit.

**Third-party:** `#[sqlx::test]` może tworzyć izolowane bazy oraz stosować migracje przy odpowiednich features i uprawnieniach. Dokumentuje to [SQLx test 0.8.6](https://docs.rs/sqlx/0.8.6/sqlx/attr.test.html), sprawdzone 2026-11-11. Nie uruchamiaj takiego harnessu z adresem produkcyjnym. Test aktualizacji zaczyna od poprzedniego schematu i realistycznych danych, wykonuje migrację, sprawdza nowego klienta oraz klienta pozostającego jeszcze w oknie zgodności.

## Praktyka produkcyjna

Migracje przechowuj jako niezmienne, numerowane artefakty z historią wykonania. Ustal jednego koordynatora lub mechanizm blokady migracyjnej; wszystkie repliki nie powinny równocześnie uruchamiać ciężkiego backfillu. Ustaw deadline blokad i obserwuj postęp. Migracja odwrotna nie odtworzy usuniętych danych tylko dlatego, że istnieje plik `down.sql`.

Kopia zapasowa jest użyteczna dopiero po próbie odtworzenia. Ustal RPO — dopuszczalną utratę danych — i RTO — czas przywrócenia działania. Zmierz pobranie kopii, odtworzenie dziennika, uruchomienie zgodnego binarium i sprawdzenie niezmienników. Replikacja może powielić przypadkowe usunięcie, więc nie zastępuje historii kopii. Szyfrowanie bez dostępnego klucza oznacza kopię, której nie da się odzyskać. Próba odtworzenia powinna kończyć się raportem liczby rekordów i poprawności operacji, nie samym statusem narzędzia backupu.

## Sprawdź, czy rozumiesz

- Kiedy bezpieczne jest usunięcie starej kolumny podczas rolling deployment?
- Co może ominąć test oparty na rollbacku jednego połączenia?
- Dlaczego poprawny backup nie wyznacza jeszcze osiągniętego RTO?

## Ćwiczenia

- `C06-1` — podstawowe: Rozpisz trzy etapy zastąpienia pola email przez email_normalized bez przerywania starej aplikacji. Podaj warunek usunięcia starego pola. [Rozwiązanie](../rozwiazania/17_bazy_danych_i_persystencja/02_migracje_testy_i_odtwarzanie.md#c06-1).
- `C06-2` — praktyczne: Dla zakresu 0..11 i partii 4 podaj kolejne zakresy i punkt wznowienia po dwóch commitach. Opisz awarię przed zapisaniem checkpointu. [Rozwiązanie](../rozwiazania/17_bazy_danych_i_persystencja/02_migracje_testy_i_odtwarzanie.md#c06-2).
- `C06-3` — pogłębione: Zaprojektuj próbę odtworzenia dla RPO 15 minut i RTO 60 minut. Podaj mierzone czasy, kontrolę spójności i kryterium porażki. [Rozwiązanie](../rozwiazania/17_bazy_danych_i_persystencja/02_migracje_testy_i_odtwarzanie.md#c06-3).

## Powiązane tematy

- [Transakcje i pule](01_repozytoria_pule_i_transakcje.md)
- [Ewolucja formatu](../18_serializacja_konfiguracja_i_integracje/01_formaty_serializacja_i_walidacja.md)
- [Cargo i features](../08_moduly_cargo_i_workspaces/03_zaleznosci_features_i_cfg.md)
