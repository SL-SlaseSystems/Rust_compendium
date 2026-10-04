[← Spis treści](../README.md)

# Testy jednostkowe i integracyjne

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

## Powiązane tematy

- [Testy dokumentacyjne i rustdoc](02_testy_dokumentacyjne_i_rustdoc.md)
- [Własne błędy](../07_obsluga_bledow/04_wlasne_bledy_i_api.md)
- [Wątki](../10_wspolbieznosc/01_watki_i_scoped_threads.md)
