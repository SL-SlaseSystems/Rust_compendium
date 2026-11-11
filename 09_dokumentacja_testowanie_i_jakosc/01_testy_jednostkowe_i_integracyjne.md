[← Spis treści](../README.md)
<!-- status: expanded -->

# Testy jednostkowe i integracyjne

## Cele

Po tym rozdziale potrafisz:

- wybrać test według granicy kontraktu;
- zaprojektować przypadki brzegowe i izolację zasobów;


`cargo test` kompiluje kod w profilu testowym, znajduje funkcje `#[test]` i
uruchamia je domyślnie równolegle.

## Test jednostkowy

~~~rust
pub fn mediana(mut dane: Vec<i32>) -> Option<f64> {
    if dane.is_empty() {
        return None;
    }
    dane.sort_unstable();
    let s = dane.len();
    if s % 2 == 1 {
        Some(dane[s / 2] as f64)
    } else {
        Some((dane[s / 2 - 1] as f64 + dane[s / 2] as f64) / 2.0)
    }
}

fn main() {
    assert_eq!(mediana(vec![3, 1, 2]), Some(2.0));
    assert_eq!(mediana(vec![1, 3]), Some(2.0));
    assert_eq!(mediana(vec![]), None);
}
~~~

W crate źródłowym testy zwykle są w prywatnym module:

~~~rust
fn podwoj(x: i32) -> i32 { x * 2 }

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn podwaja_liczbe_dodatnia() {
        assert_eq!(podwoj(21), 42);
    }
}

fn main() {}
~~~

Test może zwracać `Result<(), E>` i używać `?`. Makra `assert_eq!` i
`assert_ne!` pokazują obie strony przez `Debug`.

## Integracja

Każdy plik w `tests/*.rs` jest osobnym crate’em i widzi tylko publiczne API:

~~~text
// tests/api.rs
use moja_biblioteka::Funkcja;

#[test]
fn publiczny_kontrakt() {
    assert_eq!(Funkcja::nowa().wynik(), 42);
}
~~~

Wspólne helpery umieszczaj np. w `tests/common/mod.rs`, a nie
`tests/common.rs`, jeśli nie mają być osobnym targetem testowym.

## Panic, ignorowanie i filtrowanie

~~~rust
fn wymaga_dodatniej(x: i32) {
    assert!(x > 0, "x musi być dodatnie");
}

#[test]
#[should_panic(expected = "x musi być dodatnie")]
fn odrzuca_zero() {
    wymaga_dodatniej(0);
}

fn main() {}
~~~

`#[ignore]` oznacza kosztowny lub środowiskowy test. Uruchom
`cargo test -- --ignored`. Filtrowanie nazw: `cargo test fragment_nazwy`.
`-- --nocapture` pokazuje stdout.

## Izolacja

Testy nie powinny współdzielić stałej ścieżki, portu czy globalnego mutable
state. Twórz unikalne katalogi tymczasowe i sprzątaj przez RAII. Jeśli test
wymaga serializacji, powód powinien być jawny; nie ukrywaj race condition
flagą jednego wątku.

## Co testować

- publiczne zachowanie i invariants;
- przypadki brzegowe: pusto, minimum, maksimum, Unicode, błąd;
- klasy błędów i zachowanie retry;
- własności algorytmu przez property testing (**third-party**, np. proptest);
- nie szczegóły prywatnej implementacji.


## Model — test ma odróżniać poprawną implementację od błędnej

Test jednostkowy ma szybki dostęp do małej reguły i może sprawdzać prywatny niezmiennik. Test integracyjny odtwarza sposób użycia biblioteki przez konsumenta. Test procesu sprawdza kody wyjścia, argumenty i strumienie CLI. Wybór wynika z rodzaju błędu, który chcesz wykryć, a nie z potrzeby jednakowej liczby testów w katalogach. Ten sam scenariusz na wszystkich poziomach może podnieść koszty bez zwiększenia ochrony.

Dla mediany sprawdź pusty zbiór, parzystą i nieparzystą długość, duplikaty oraz granice liczb. Przekształcenie każdej liczby do `f64` przed dodaniem unika przepełnienia `i32`, ale wyznacza osobny kontrakt reprezentacji wyniku. Nie testuj tylko przypadku `1,2,3`; wiele błędnych algorytmów też zwróci dla niego poprawny wynik.

~~~rust
fn normalizuj(dane: &[i32]) -> Vec<i32> {
    let mut wynik = dane.to_vec();
    wynik.sort_unstable();
    wynik.dedup();
    wynik
}
fn main() {
    for przypadek in [vec![], vec![2], vec![3, 1, 3, -1]] {
        let raz = normalizuj(&przypadek);
        assert_eq!(normalizuj(&raz), raz); // idempotencja
        assert!(raz.windows(2).all(|p| p[0] < p[1]));
        assert!(przypadek.iter().all(|n| raz.contains(n)));
    }
}
~~~

Przykład sprawdza własności zamiast konkretnego sposobu sortowania. Idempotencja sama nie wystarcza: funkcja zawsze zwracająca pustą kolekcję też jest idempotentna. Druga i trzecia asercja ograniczają inne klasy błędów. Przy większych danych generatory **third-party** mogą dostarczać więcej przypadków, ale nadal trzeba poprawnie wybrać własności.

`#[test]` jest uruchamiany przez harness, a nie przez zwykłe `main`. Blok dokumentacyjny zawierający testy wymaga świadomej interpretacji: sam doctest nie jest pełnym zastępstwem `cargo test` danego pakietu. Testy nie powinny polegać na kolejności wykonania. Globalna zmiana katalogu bieżącego lub środowiska wpływa na cały proces; w Edition 2024 mutacja środowiska ma dodatkowy kontrakt bezpieczeństwa.

Czas rzeczywisty i `sleep` są słabą metodą synchronizacji. Jeśli test ma poczekać na gotowość workera, użyj kanału albo bariery. Dla algorytmu deadline przekaż zegar jako zależność i przetestuj upływ czasu deterministycznie. Test sieciowy powinien używać portu wybranego przez system, obsługiwać błędy oraz ograniczać oczekiwanie. Sam timeout zmniejsza ryzyko zawieszenia CI, ale nie wyjaśnia przyczyny błędu.

## Diagnostyka kompilatora

Jeżeli test nie jest znajdowany, sprawdź `#[test]`, lokalizację targetu i użyte filtry. `assert_eq!` wymaga `PartialEq` i `Debug`; brak implementacji to problem porównywanego typu, nie makra testowego. Test wywołujący prywatną metodę z `tests/` poprawnie dostaje błąd prywatności. Zdecyduj, czy sprawdzać publiczny kontrakt, czy przenieść sprawdzanie niezmiennika do modułu jednostkowego; nie otwieraj API tylko dla testu.

## Praktyka produkcyjna

Dobieraj testy do realnego ryzyka. Szybkie reguły domenowe powinny wykonywać się bez sieci i wspólnego globalnego stanu. Osobno utrzymuj mały zestaw testów adapterów i procesów. Niestabilny test jest kosztem operacyjnym: zapisz przyczynę, a nie tylko automatycznie ponawiaj go do sukcesu. Test regresyjny powinien zawodzić dla znanego błędnego zachowania. Zachowuj dane wejściowe i komunikat błędu pozwalające odtworzyć awarię, zwłaszcza gdy generator wybrał przypadek losowo.

## Sprawdź, czy rozumiesz

- Dlaczego sama idempotencja nie dowodzi poprawnego usuwania duplikatów?
- Którego kontraktu nie sprawdzi test wywołujący prywatne metody?
- Czemu `sleep` nie dowodzi gotowości workera?

## Ćwiczenia

- `B10-1` — podstawowe: Dodaj przypadki graniczne mediany dla minimum i maksimum `i32`. [Rozwiązanie](../rozwiazania/09_dokumentacja_testowanie_i_jakosc/01_testy_jednostkowe_i_integracyjne.md#b10-1).
- `B10-2` — praktyczne: Sprawdź trzy własności sortowania i deduplikacji dla kilku różnych wejść. [Rozwiązanie](../rozwiazania/09_dokumentacja_testowanie_i_jakosc/01_testy_jednostkowe_i_integracyjne.md#b10-2).
- `B10-3` — pogłębione: Zastąp oczekiwanie czasowe w teście workera komunikatem gotowości. [Rozwiązanie](../rozwiazania/09_dokumentacja_testowanie_i_jakosc/01_testy_jednostkowe_i_integracyjne.md#b10-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [The Rust Book: organizacja testów](https://doc.rust-lang.org/book/ch11-03-test-organization.html)
- [libtest i atrybuty](https://doc.rust-lang.org/reference/attributes/testing.html)

## Powiązane tematy

- [Testy dokumentacyjne i rustdoc](02_testy_dokumentacyjne_i_rustdoc.md)
- [Własne błędy](../07_obsluga_bledow/04_wlasne_bledy_i_api.md)
- [Wątki](../10_wspolbieznosc/01_watki_i_scoped_threads.md)
