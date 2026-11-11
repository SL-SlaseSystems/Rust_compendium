[← Spis treści](../README.md)
<!-- status: expanded -->

# Konfiguracja, sekrety, retry i idempotencja integracji

## Cele

Po tym rozdziale potrafisz:

- oddzielić konfigurację, sekret i stan operacji;
- ustalić deadline, politykę retry oraz bezpieczny klucz idempotencji;
- opisać awarię między wykonaniem skutku a dostarczeniem odpowiedzi.

## Model — Konfiguracja ma pochodzenie i cykl życia

Adres usługi, limit partii i timeout to konfiguracja; token dostępu jest sekretem; numer ostatnio obsłużonego zdarzenia jest stanem wykonania. Mają inne wymagania odtwarzania oraz dostępu. Nie przechowuj postępu integracji wyłącznie w pliku konfiguracji nadpisywanym przy wdrożeniu. Nie traktuj sekretu jak zwykłego pola z automatycznym `Debug`.

Scalaj warstwy w ustalonej kolejności: domyślne wartości, plik, środowisko, argumenty albo jawnie wybrana polityka produktu. Zapisz pochodzenie każdego końcowego ustawienia. Zmienne środowiska są wygodnym mechanizmem dostarczenia, ale nie uniwersalnym sejfem: mogą trafiać do diagnostyki procesu lub środowiska potomka. Sekret pobierany z zewnętrznego magazynu wymaga planu startu przy awarii i planu rotacji bez drukowania wartości.

Przy gorącym przeładowaniu wczytaj i zweryfikuj cały nowy zestaw, a następnie atomowo podmień uchwyt konfiguracji. Nie zmieniaj współdzielonej struktury pole po polu, bo żądanie może zobaczyć nowy adres ze starym tokenem. Długotrwałe operacje mogą zachować poprzedni snapshot; określ, kiedy wygasa i kiedy zamykasz stary klient. Rotacja wymaga ewentualnego okresu nakładania ważności po obu stronach.

~~~rust
use std::fmt;
struct Sekret(String);
impl fmt::Debug for Sekret {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str("Sekret([UKRYTO])")
    }
}
impl Sekret {
    fn ujawnij(&self) -> &str { &self.0 }
}
fn main() {
    let token = Sekret("wartosc-testowa".into());
    assert_eq!(format!("{token:?}"), "Sekret([UKRYTO])");
    assert_eq!(token.ujawnij(), "wartosc-testowa");
}
~~~

Typ ogranicza przypadkowy wyciek w `Debug`, ale nie szyfruje pamięci i nie chroni przed jawnym zalogowaniem `ujawnij()`. Nie obiecuje zerowania kopii po zwolnieniu. Udostępnij surową wartość tylko na granicy klienta; przejrzyj także serializację, telemetrię i komunikaty błędów. Częściowa redakcja, np. pozostawienie końcówki krótkiego tokenu, może ujawnić zbyt wiele.

## Timeout nie oznacza braku skutku

Wyobraź sobie wysłanie zlecenia, zatwierdzenie go przez partnera i utratę odpowiedzi w sieci. Lokalny timeout nie mówi, czy partner wykonał operację. Rozróżnij „na pewno nie wysłano”, „jawna odmowa” i „wynik nieznany”. Nawet błąd połączenia może wymagać analizy momentu, w którym wysłano część danych.

Idempotencja oznacza, że powtórzenie tej samej logicznej operacji nie powoduje dodatkowego zamierzonego skutku. HTTP nadaje taką semantykę wybranym metodom, lecz nie obiecuje identycznych odpowiedzi każdej próby. `POST` może uzyskać idempotencję dzięki kontraktowi aplikacji. Sprawdzono 2026-11-11 w [RFC 9110, idempotent methods](https://www.rfc-editor.org/rfc/rfc9110.html#name-idempotent-methods).

Klucz generuj raz na operację biznesową i utrzymuj przez wszystkie próby. Odbiorca zapisuje klucz, fingerprint parametrów i wynik razem ze skutkiem albo w innym protokole gwarantującym spójność. Ten sam klucz z inną treścią musi dać konflikt. Okno deduplikacji musi obejmować realne późne ponowienia; usunięcie rejestru po minucie nie zabezpieczy zadania wznowionego jutro.

## Ograniczone ponawianie

Retry powinno mieć klasyfikację błędów, maksymalną liczbę prób, wspólny deadline i backoff z rozproszeniem (jitter). Błąd walidacji oraz brak uprawnień zwykle wymagają naprawy, nie ponowienia. Chwilowe przeciążenie może zasługiwać na retry zgodne z kontraktem partnera. Nie twórz dwóch niezależnych pętli, jednej w kliencie i drugiej w workerze: ich liczby prób mogą się mnożyć.

~~~rust
use std::time::Duration;
fn opoznienie(numer: u32) -> Duration {
    let mnoznik = 1_u64 << numer.min(5);
    Duration::from_millis((100 * mnoznik).min(2_000))
}
fn main() {
    assert_eq!(opoznienie(0), Duration::from_millis(100));
    assert_eq!(opoznienie(10), Duration::from_secs(2));
}
~~~

To deterministyczny rdzeń wyznaczania górnej granicy opóźnienia, bez losowania i bez wykonywania sieci. Produkcyjnie wylosuj jitter, obetnij czekanie do pozostałego czasu i nie rozpoczynaj próby, której budżet już nie mieści. Źródło czasu i losowania wstrzyknij do testu. Sam limit pojedynczego requestu nie ogranicza całego zadania wraz z oczekiwaniem i serializacją.

## Diagnostyka kompilatora

Próba przeniesienia posiadanego body do pierwszej próby pętli i ponownego użycia w drugiej może dać błąd moved value. Wydziel niezmienne bajty żądania albo konstruktor odtwarzający body dla kolejnej próby. Nie każdy stream da się odtworzyć: odczyt z rury lub pliku zmienianego w tle wymaga innego kontraktu. `clone()` uchwytu nie dowodzi, że ponawiasz identyczny payload.

Referencja do sekretu z lokalnie utworzonej konfiguracji nie może przeżyć tej konfiguracji. Przekaż własność snapshotu do taska przez odpowiedni uchwyt, zamiast wymuszać `'static`. Przy błędach `Send` sprawdź guardy i klientów utrzymywanych przez `.await` oraz wymagania runtime’u.

## Praktyka produkcyjna

Dla kolejki często przyjmujesz dostarczenie co najmniej raz. Potwierdzaj odbiór po trwałym zapisaniu skutku; awaria przed ACK daje duplikat, który powinien być nieszkodliwy. Outbox łączy transakcję domenową z zapisem zamiaru publikacji, ale worker nadal może opublikować ponownie. Odbiorca potrzebuje deduplikacji albo naturalnie idempotentnej operacji.

Circuit breaker ogranicza uderzanie w niesprawną zależność; nie naprawia niepoprawnego klucza ani nie zastępuje limitów współbieżności. Oddziel budżety partnerów, aby awaria jednego nie wyczerpała wszystkich workerów. Mierz liczbę logicznych operacji i prób oddzielnie, czas oczekiwania, odsetek wyników nieznanych oraz wiek najstarszej wiadomości. Do logów trafia identyfikator operacji i kategoria błędu, nie token oraz pełne body. Plan ręcznego wznowienia musi zachować pierwotny klucz, inaczej operator może nieświadomie zdublować skutek.

## Sprawdź, czy rozumiesz

- Dlaczego timeout po wysłaniu danych nie uprawnia do nadania nowego klucza?
- Kiedy sekwencyjne odświeżenie adresu i tokenu stworzy błędną konfigurację?
- Dlaczego outbox potrzebuje również obsługi duplikatów u odbiorcy?

## Ćwiczenia

- `C08-1` — podstawowe: Dla backoffu z przykładu podaj opóźnienia prób 0, 1, 4 i 5 oraz wskaż, czego brakuje do pełnej polityki retry. [Rozwiązanie](../rozwiazania/18_serializacja_konfiguracja_i_integracje/02_konfiguracja_sekrety_i_odpornosc_integracji.md#c08-1).
- `C08-2` — praktyczne: Zaprojektuj test redakcji sekretu obejmujący Debug konfiguracji i zagnieżdżony błąd klienta. Podaj dane testowe i asercje. [Rozwiązanie](../rozwiazania/18_serializacja_konfiguracja_i_integracje/02_konfiguracja_sekrety_i_odpornosc_integracji.md#c08-2).
- `C08-3` — pogłębione: Rozpisz stany operacji wysłania płatności, gdy odpowiedź ginie po zatwierdzeniu. Uwzględnij fingerprint, odpytywanie i późne ręczne wznowienie. [Rozwiązanie](../rozwiazania/18_serializacja_konfiguracja_i_integracje/02_konfiguracja_sekrety_i_odpornosc_integracji.md#c08-3).

## Powiązane tematy

- [Formaty i walidacja](01_formaty_serializacja_i_walidacja.md)
- [CLI i konfiguracja](../15_aplikacje_cli/01_komendy_argumenty_i_konfiguracja.md)
- [Transakcje i outbox](../17_bazy_danych_i_persystencja/01_repozytoria_pule_i_transakcje.md)
