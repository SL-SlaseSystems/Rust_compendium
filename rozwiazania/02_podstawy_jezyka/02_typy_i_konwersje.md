[← Spis treści](../../README.md)

# Rozwiązania: Typy i konwersje

## P02-1

`checked_add` sygnalizuje brak wyniku, a `wrapping_add` świadomie stosuje modulo.

~~~rust
fn main() { assert_eq!(255_u8.checked_add(1), None); assert_eq!(255_u8.wrapping_add(1), 0); }
~~~

## P02-2

`TryFrom` zachowuje informację o błędzie zamiast cichego obcięcia przez `as`.

~~~rust
use std::convert::TryFrom;
fn main() { assert_eq!(u8::try_from(255_u16), Ok(255)); assert!(u8::try_from(256_u16).is_err()); }
~~~

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
