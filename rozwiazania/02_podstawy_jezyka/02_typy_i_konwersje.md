[← Spis treści](../../README.md)

# Rozwiązania: Typy i konwersje

## P02-1

`checked_add` sygnalizuje brak wyniku, a `wrapping_add` świadomie stosuje modulo.

~~~rust
fn main() { assert_eq!(255_u8.checked_add(1), None); assert_eq!(255_u8.wrapping_add(1), 0); }
~~~


`checked_add` jest właściwe dla walidowanej liczby rekordów, której przekroczenie ma być błędem. `wrapping_add` pasuje do arytmetyki modulo określonej protokołem lub algorytmem. Obie metody zachowują tę samą semantykę niezależnie od domyślnego `overflow-checks`; nie wymagamy, by odbiorca znał profil kompilacji. Dla limitu nasycanego inną poprawną decyzją może być `saturating_add`, lecz nie zastępuje ona sygnalizowania błędu.

## P02-2

`TryFrom` zachowuje informację o błędzie zamiast cichego obcięcia przez `as`.

~~~rust
use std::convert::TryFrom;
fn main() { assert_eq!(u8::try_from(255_u16), Ok(255)); assert!(u8::try_from(256_u16).is_err()); }
~~~


Granice testu są celowe: 255 jest największą poprawną wartością, a 256 pierwszą niepoprawną. Rzut `256_u16 as u8` dałby zero i nie poinformowałby klienta o utracie danych. Jeżeli domena dopuszcza tylko 0–100, samo poprawne `TryFrom<u16> for u8` nie wystarcza: po konwersji potrzebny jest jeszcze warunek domenowy albo osobny walidowany typ.

## P02-3

Turbofish wybiera typ bezpośrednio, adnotacja wyniku przekazuje go wstecz, a typ parametru odbiorcy także może sterować inferencją.

~~~rust
fn przyjmij(_: u16) {}
fn main() {
    let a = "42".parse::<u32>().expect("liczba");
    let b: u16 = "42".parse().expect("liczba");
    przyjmij("42".parse().expect("liczba"));
    assert_eq!((a, b), (42, 42));
}
~~~


Każdy zapis wybiera implementację `FromStr`, a nie zmienia algorytmu parsowania w runtime. Przy `parse::<u16>()` typ błędu wynika z wybranego typu docelowego. Brak kontekstu nie oznacza, że program musi używać rzutowania: trzeba przekazać informację o typie na jednej z granic, najlepiej tam, gdzie odpowiada ona wymaganiu domeny.
