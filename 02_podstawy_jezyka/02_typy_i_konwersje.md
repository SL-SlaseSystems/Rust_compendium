[← Spis treści](../README.md)
<!-- status: expanded -->

# Typy i konwersje

> Rust 1.98.1, Edition 2024, zweryfikowany 10 września 2026 r.; przykłady wykonano lokalnie przez Rust 1.90.0.

## Cele

- dobierać reprezentację liczby, tekstu i kolekcji do kontraktu;
- rozróżniać konwersję niejawną, rzutowanie i walidowaną zmianę typu;
- diagnozować typowe błędy inferencji i konwersji.

## Model — reprezentacja i typ

Liczby całkowite to `i8`…`i128`, `u8`…`u128`, `isize` i `usize`; dwa ostatnie zależą od targetu i służą rozmiarom/indeksom. Bez kontekstu integer domyślnie jest `i32`, float `f64`; przyrostki (`10_u8`, `2.0_f32`) ustalają typ. `bool` ma dwa stany. `char` jest czterobajtową wartością skalarną Unicode, nie grafemem ani stringiem. Krotka miesza typy, `()` jest unit, a `[T; N]` ma długość w typie. `!` opisuje wyrażenie, które nie wraca normalnie; nie polegaj na szczegółach fallbacku `!` zależnych od Edition 2024.

~~~rust
fn main() {
    let dane: [u8; 3] = [1, 2, 3];
    let para = ('🦀', true);
    assert_eq!(dane[1_usize], 2);
    assert_eq!(para.0, '🦀');
}
~~~

## Arytmetyka i konwersje

Przepełnienie w profilu `dev` zwykle wywołuje panic, a `release` zwykle ma wyłączone kontrole; ustawienia profilu mogą to zmienić, więc nie zakładaj zawsze zawijania. Wyraź intencję przez `checked_*`, `wrapping_*`, `saturating_*` lub `overflowing_*`.

~~~rust
fn main() {
    assert_eq!(255_u8.checked_add(1), None);
    assert_eq!(255_u8.wrapping_add(1), 0);
    assert_eq!(250_u8.saturating_add(20), 255);
    assert_eq!(255_u8.overflowing_add(1), (0, true));
}
~~~

Coercions zachodzą tylko w określonych kontekstach, np. `&mut T` do `&T`; nie są ogólną konwersją liczbową. `as` ma zdefiniowane reguły, ale może utracić dane. `From`/`Into` są nieomylne, `TryFrom`/`TryInto` walidują, a `str::parse` używa `FromStr`; turbofish (`parse::<u16>()`) pomaga inferencji.

~~~rust
use std::convert::TryFrom;
fn main() {
    let port: u16 = "8080".parse().expect("liczba");
    assert!(u8::try_from(300_u16).is_err());
    assert_eq!(port as u32, 8080);
}
~~~

## Diagnostyka kompilatora

Brak kontekstu dla metody liczbowej wymaga adnotacji lub przyrostka; E0308 oznacza niedopasowane typy. Rzut `300_u16 as u8` jest legalny, lecz stratny. Indeks tablicy musi mieć `usize`.

~~~compile_fail
fn main() { let xs = [1, 2]; let i: i32 = 1; println!("{}", xs[i]); }
~~~

## Praktyka produkcyjna

Waliduj dane na granicy przez `TryFrom`/`parse`, nie przez `as`. Dla domeny twórz newtype, np. `struct Port(u16);`, aby nie pomylić identyfikatora z rozmiarem. Źródła: [Book](https://doc.rust-lang.org/book/ch03-02-data-types.html), [casts](https://doc.rust-lang.org/reference/expressions/operator-expr.html#type-cast-expressions), [convert](https://doc.rust-lang.org/std/convert/).

## Sprawdź, czy rozumiesz

1. Dlaczego `usize` nie jest formatem danych sieciowych?
2. Kiedy `as` jest gorsze od `TryFrom`?
3. Co daje turbofish?

## Ćwiczenia

- `P02-1` — podstawowe: porównaj `checked_add` i `wrapping_add`. [Rozwiązanie](../rozwiazania/02_podstawy_jezyka/02_typy_i_konwersje.md#p02-1).
- `P02-2` — praktyczne: przekonwertuj `u16` do `u8` bez utraty danych. [Rozwiązanie](../rozwiazania/02_podstawy_jezyka/02_typy_i_konwersje.md#p02-2).
- `P02-3` — pogłębione: napraw inferencję `"42".parse()`. [Rozwiązanie](../rozwiazania/02_podstawy_jezyka/02_typy_i_konwersje.md#p02-3).

## Powiązane tematy

- [`Option` i `Result`](../06_bledy/01_option_i_result.md)
- [Newtype](../13_wzorce_i_architektura/01_idiomy_newtype_i_extension_traits.md)
