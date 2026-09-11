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

Adnotacja wyniku lub turbofish daje `parse` konkretny `FromStr`.

~~~rust
fn main() { let n = "42".parse::<u32>().expect("liczba"); assert_eq!(n, 42); }
~~~
