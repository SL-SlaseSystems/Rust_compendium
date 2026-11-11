[← Spis treści](../README.md)
<!-- status: expanded -->

# Repozytoria, mapowanie typów, pule i transakcje

## Cele

Po tym rozdziale potrafisz:

- zaprojektować granicę repozytorium w języku domeny;
- odróżnić atomowość transakcji od jej izolacji;
- zaplanować użycie puli, zwrot połączeń i propagację błędów zapisu.

## Model — Repozytorium opisuje operację

Repozytorium nie musi być uniwersalnym traitem z metodami CRUD. Interfejs `zarezerwuj_towar(id, liczba)` lepiej opisuje niezmiennik niż `pobierz` i `zapisz`, gdy rezerwacja wymaga atomowego sprawdzenia stanu. Warstwa aplikacji ustala granicę transakcji obejmującą cały przypadek użycia. Ukrycie osobnego `commit` wewnątrz każdej metody uniemożliwia atomowe połączenie dwóch zmian.

Typ wiersza bazy nie jest automatycznie typem domeny. Kolumna `BIGINT` może zawierać wartość ujemną, której `Ilosc` nie dopuszcza. `NULL` mapuj na `Option` zgodnie ze znaczeniem, a nie na `0` lub pusty tekst. Waluty przechowuj z jawną jednostką i skalą; bezmyślny `f64` komplikuje równość i rozliczenia. Daty wymagają ustalenia strefy lub znaczenia lokalnego czasu. Ograniczenia bazy i konstruktory Rust uzupełniają się: do danych mogą pisać starsze usługi oraz narzędzia administracyjne.

~~~rust
#[derive(Debug, PartialEq)]
struct Ilosc(u32);
impl TryFrom<i64> for Ilosc {
    type Error = &'static str;
    fn try_from(x: i64) -> Result<Self, Self::Error> {
        let x = u32::try_from(x).map_err(|_| "poza zakresem")?;
        if x == 0 { Err("ilość zerowa") } else { Ok(Self(x)) }
    }
}
fn main() {
    assert_eq!(Ilosc::try_from(3), Ok(Ilosc(3)));
    assert!(Ilosc::try_from(-1).is_err());
    assert!(Ilosc::try_from(i64::MAX).is_err());
}
~~~

Konwersja `as u32` mogłaby zawinąć liczbę ujemną albo obciąć starsze bity. `TryFrom` zachowuje informację o uszkodzonych lub niezgodnych danych. Taki błąd zwykle oznacza awarię mapowania albo migracji, nie „rekordu nie znaleziono”. Rozdziel brak rekordu, konflikt biznesowy, błąd dekodowania i niedostępność bazy; przyczyna techniczna może pozostać w źródle błędu.

## Połączenie i pula

Pula ogranicza liczbę jednoczesnych połączeń i amortyzuje ich tworzenie. To współdzielony zasób procesu. **Third-party:** SQLx 0.8.6 pozwala klonować uchwyt puli, nabywać połączenie i zamykać pulę przez `close().await`. Kontrakty opisuje [Pool](https://docs.rs/sqlx/0.8.6/sqlx/struct.Pool.html), zweryfikowany 2026-11-11. Nie opakowuj całej puli w jeden zewnętrzny mutex.

Limit licz dla wszystkich replik i workerów. Dziesięć replik z pulą 30 może potrzebować 300 połączeń, niezależnie od pozornie małej wartości lokalnej. Oddziel czas oczekiwania na połączenie od czasu zapytania. Połączenie utrzymywane podczas powolnego HTTP blokuje zasób bez pracy bazy. Pobierz dane, zakończ transakcję i dopiero wywołaj zewnętrzną usługę, chyba że projekt wymaga innego protokołu spójności.

## Transakcja i izolacja

Atomowość oznacza zatwierdzenie całego zestawu zmian albo jego wycofanie w bazie. Nie określa, co dwie równoległe transakcje mogą odczytać. W PostgreSQL `Read Committed` wykonuje zwykłe odczyty względem snapshotu polecenia; dwa `SELECT` w tej samej transakcji mogą widzieć różne zatwierdzone dane. `Serializable` może odrzucić transakcję, wymagając ponowienia całej operacji. Zweryfikowano 2026-11-11 w [dokumentacji izolacji PostgreSQL](https://www.postgresql.org/docs/current/transaction-iso.html).

Dla prostej rezerwacji użyj warunkowego `UPDATE ... WHERE stan >= $1` i sprawdź liczbę zmienionych wierszy. Osobne pobranie stanu, sprawdzenie w Rust i bezwarunkowy zapis łatwo gubi aktualizacje. Dla niezmienników wielu wierszy rozważ blokady w ustalonej kolejności lub odpowiednią izolację i retry. Nie ma jednego poziomu właściwego dla wszystkich modeli.

**Third-party:** szkic SQLx 0.8.6 wymaga `postgres`, runtime Tokio, konfiguracji TLS, istniejącej tabeli `magazyn(id BIGINT PRIMARY KEY, stan BIGINT CHECK (stan >= 0))` i serwera. Nie jest wykonywany przez rustdoc. API transakcji sprawdzono w [Transaction](https://docs.rs/sqlx/0.8.6/sqlx/struct.Transaction.html), 2026-11-11.

~~~text
async fn rezerwuj(pool: &sqlx::PgPool, id: i64, ile: Ilosc)
    -> Result<bool, sqlx::Error>
{
    let mut tx = pool.begin().await?;
    let wynik = sqlx::query(
        "UPDATE magazyn SET stan = stan - $1 WHERE id = $2 AND stan >= $1"
    )
    .bind(i64::from(ile.0)).bind(id)
    .execute(&mut *tx).await?;
    let przyjeto = wynik.rows_affected() == 1;
    tx.commit().await?;
    Ok(przyjeto)
}
~~~

Parametry nie są wklejane do SQL przez `format!`. `false` oznacza tutaj brak pasującego wiersza, czyli wspólny wynik braku zasobu i niewystarczającego stanu; jeżeli API ma je rozróżniać, potrzeba dodatkowego, spójnego kontraktu. Dla jednego polecenia jawna transakcja może być zbędna, lecz staje się potrzebna po dodaniu wpisu rezerwacji lub outboxu. Błąd `commit` może pozostawić klientowi nieznany wynik, gdy połączenie zerwie się po zatwierdzeniu.

## Diagnostyka kompilatora

Transakcja SQLx ma wyłączne operacje przez `&mut`; dwa równoczesne zapytania na tej samej pożyczce nie przejdą borrow checkera. Wykonuj je sekwencyjnie albo użyj niezależnych połączeń, świadomie tracąc wspólną transakcję. W szkicu `&mut *tx` przekazuje pożyczkę połączenia, a `commit(self)` konsumuje transakcję. Użycie jej później jest błędem przeniesienia. Nie zastępuj tego klonowaniem nowej puli.

## Praktyka produkcyjna

Rejestruj czas nabycia połączenia, czas zapytania, timeouty i liczbę retry. Nie loguj pełnych parametrów zawierających dane prywatne. Ustaw limity statementów i blokad zgodnie z budżetem żądania. Wycofanie transakcji po drop traktuj jako mechanizm awaryjny; jawne `rollback().await` daje możliwość obserwacji błędu porządkowania. Po zakończeniu pracy kontrolowanie zamknij pulę.

Retry wykonuj tylko dla rozpoznanych, przejściowych sytuacji, z limitem prób i wspólnym deadline. Ponawiaj całą transakcję, a efekty poza bazą przenieś do protokołu outbox lub innego jawnego mechanizmu. Rollback SQL nie cofnie już wysłanego maila.

## Sprawdź, czy rozumiesz

- Dlaczego poprawnie typowane zapytanie może naruszyć niezmiennik biznesowy?
- Co oznacza nieznany wynik commit dla ponawiania rezerwacji?
- Które operacje powinny należeć do jednej transakcji z wpisem outbox?

## Ćwiczenia

- `C05-1` — podstawowe: Pokaż dlaczego rzutowanie -1_i64 as u32 nie nadaje się do mapowania dodatniej ilości. Zapisz trzy przypadki graniczne TryFrom. [Rozwiązanie](../rozwiazania/17_bazy_danych_i_persystencja/01_repozytoria_pule_i_transakcje.md#c05-1).
- `C05-2` — praktyczne: Wyjaśnij przeplot dwóch rezerwacji po 7 sztuk przy stanie 10: najpierw dla SELECT+UPDATE, potem dla warunkowego UPDATE. Podaj wynik oczekiwany. [Rozwiązanie](../rozwiazania/17_bazy_danych_i_persystencja/01_repozytoria_pule_i_transakcje.md#c05-2).
- `C05-3` — pogłębione: Zaprojektuj idempotentną rezerwację z kluczem operacji i outboxem. Uwzględnij dwa równoległe wywołania i zerwanie połączenia podczas commit. [Rozwiązanie](../rozwiazania/17_bazy_danych_i_persystencja/01_repozytoria_pule_i_transakcje.md#c05-3).

## Powiązane tematy

- [Migracje i odtwarzanie](02_migracje_testy_i_odtwarzanie.md)
- [Model błędów HTTP](../16_web_i_api/01_http_routing_stan_i_bledy.md)
- [Retry i idempotencja](../18_serializacja_konfiguracja_i_integracje/02_konfiguracja_sekrety_i_odpornosc_integracji.md)
