[← Spis treści](../README.md)

# `String`, `str` i Unicode

Tekst w Rust jest poprawnym UTF-8. `String` posiada bufor, `&str` jest
pożyczonym widokiem. Oddzielaj operacje na bajtach, scalar values i grafemach.

## Budowanie tekstu

~~~rust
use std::fmt::Write;

fn main() {
    let mut tekst = String::with_capacity(32);
    tekst.push_str("wynik");
    tekst.push(':');
    write!(&mut tekst, " {}", 42).unwrap();
    assert_eq!(tekst, "wynik: 42");
}
~~~

`format!` zwraca nowy `String`. `push_str` nie przejmuje ownership argumentu.
Trait `fmt::Write` umożliwia formatowanie bez tworzenia tymczasowego tekstu.

## Trzy poziomy

~~~rust
fn main() {
    let s = "a\u{301}🦀"; // a + combining acute accent + crab
    assert_eq!(s.len(), 7);             // bajty: 1 + 2 + 4
    assert_eq!(s.chars().count(), 3);   // scalar values
    assert_eq!(s.as_bytes()[0], b'a');
}
~~~

Użytkownik może widzieć tu dwa grafemy, ale standard library nie zapewnia
pełnej segmentacji grafemów. Wymaga ona np. crate’a **third-party**
`unicode-segmentation` i zależy od wersji standardu Unicode.

## Bezpieczne cięcie

`get(range)` zwraca `None`, jeżeli granica nie wypada między kodami UTF-8:

~~~rust
fn main() {
    let s = "żaba";
    assert_eq!(s.get(0..2), Some("ż"));
    assert_eq!(s.get(0..1), None);
    assert_eq!(s.char_indices().next(), Some((0, 'ż')));
}
~~~

Nie iteruj po `chars().nth(i)` w pętli indeksowej — każde `nth` przechodzi
od bieżącej pozycji iteratora, a odtwarzanie iteratora może dać koszt
kwadratowy. Iteruj raz lub zbuduj indeks właściwy dla domeny.

## Parsowanie i normalizacja

~~~rust
fn main() {
    let liczba: i32 = " 42 ".trim().parse().expect("poprawna liczba");
    assert_eq!(liczba, 42);
    assert!("Rust".eq_ignore_ascii_case("rUsT"));
}
~~~

Różne sekwencje Unicode mogą wyglądać identycznie. Standard library nie
normalizuje tekstu automatycznie. Przed porównaniem identyfikatorów
użytkowych zdefiniuj politykę normalizacji, wielkości liter i locale; do
pełnego Unicode użyj sprawdzonej biblioteki.

## Konwersje i własność

- `String::from(s)` / `s.to_owned()` — tworzą posiadany tekst;
- `String::from_utf8(Vec<u8>)` — waliduje UTF-8 i może oddać oryginalne bajty;
- `String::from_utf8_lossy` — zwraca `Cow<str>` i zastępuje błędy znakiem
  U+FFFD;
- `as_str` — pożycza `&str`;
- `into_bytes` — konsumuje `String` bez kopiowania bufora.

## Powiązane tematy

- [Slices i `str`](../03_pamiec_i_wlasnosc/04_slices_i_str.md)
- [Pliki i I/O](../12_systemy_i_interoperacyjnosc/01_pliki_io_i_procesy.md)
- [FFI, ABI i C strings](../12_systemy_i_interoperacyjnosc/03_ffi_abi_i_repr.md)
