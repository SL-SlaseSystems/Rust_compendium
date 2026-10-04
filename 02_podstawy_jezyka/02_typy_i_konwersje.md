[← Spis treści](../README.md)
<!-- status: expanded -->

# Typy i konwersje

> Rust 1.98.1, Edition 2024, zweryfikowany 10 września 2026 r.; przykłady wykonano lokalnie przez Rust 1.90.0.

## Cele

Po tym rozdziale potrafisz:

- dobierać reprezentację liczby, tekstu i kolekcji do kontraktu;
- rozróżniać konwersję niejawną, rzutowanie i walidowaną zmianę typu;
- diagnozować typowe błędy inferencji i konwersji.

## Model — reprezentacja i typ

Liczby całkowite (integers) to `i8`…`i128`, `u8`…`u128`, `isize` i `usize`; `usize` zależy od targetu i służy rozmiarom/indeksom, a `isize` jest jego znakowym odpowiednikiem, użytecznym np. dla offsetów. Bez kontekstu integer domyślnie jest `i32`, liczba zmiennoprzecinkowa (floating-point) `f64`; przyrostki (`10_u8`, `2.0_f32`) ustalają typ. `bool` ma dwa stany. `char` jest czterobajtową wartością skalarną Unicode, nie grafemem ani stringiem. Krotka miesza typy, `()` jest typem jednostkowym (unit), a `[T; N]` ma długość w typie. `!` opisuje wyrażenie, które nie wraca normalnie; nie polegaj na szczegółach mechanizmu wyboru zastępczego (fallback) `!` zależnych od Edition 2024.

~~~rust
fn main() {
    let dane: [u8; 3] = [1, 2, 3];
    let para = ('🦀', true);
    assert_eq!(dane[1_usize], 2);
    assert_eq!(para.0, '🦀');
}
~~~

## Arytmetyka i konwersje

Przepełnienie arytmetyki w czasie wykonania (runtime) kontroluje `[profile.*] overflow-checks`: domyślnie `dev` je włącza, a `release` wyłącza, lecz oba profile można skonfigurować. Nie zakładaj zawsze zawijania. Dzielenie lub reszta dla podpisanego `MIN / -1` są zawsze sprawdzane i panikują; zwykłe `+`, `-`, `*` zależą od flagi. Wyraź intencję przez `checked_*`, `wrapping_*`, `saturating_*` lub `overflowing_*`.

~~~rust
fn main() {
    assert_eq!(255_u8.checked_add(1), None);
    assert_eq!(255_u8.wrapping_add(1), 0);
    assert_eq!(250_u8.saturating_add(20), 255);
    assert_eq!(255_u8.overflowing_add(1), (0, true));
}
~~~

Niejawne wymuszenia typu (coercions) zachodzą tylko w określonych kontekstach, np. `&mut T` do `&T`; nie są ogólną konwersją liczbową. `as` ma zdefiniowane reguły, ale może utracić dane. `From`/`Into` są nieomylne, `TryFrom`/`TryInto` są omylnymi konwersjami zwracającymi `Result`, a `str::parse` używa `FromStr`; turbofish (`parse::<u16>()`) pomaga inferencji.

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
- `P02-3` — pogłębione: porównaj turbofish, adnotację wyniku i kontekst odbiorcy dla `"42".parse()`. [Rozwiązanie](../rozwiazania/02_podstawy_jezyka/02_typy_i_konwersje.md#p02-3).

## Powiązane tematy

- [`Option` i `Result`](../07_obsluga_bledow/01_option_i_result.md)
- [Newtype](../14_idiomy_wzorce_i_architektura/01_idiomy_newtype_i_extension_traits.md)
