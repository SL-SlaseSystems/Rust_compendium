# Ściąga Rusta

[← Spis treści](README.md)

Ściąga przypomina składnię; uzasadnienia i pułapki są w rozdziałach.

## Projekt

~~~text
cargo new nazwa
cargo check
cargo run -- arg
cargo test
cargo fmt --all
cargo clippy --all-targets --all-features
cargo doc --open
cargo build --release
cargo tree -e features
~~~

Minimalny `Cargo.toml`:

~~~toml
[package]
name = "nazwa"
version = "0.1.0"
edition = "2024"
rust-version = "1.85"

[dependencies]
~~~

## Bindingi i typy

~~~rust
const LIMIT: usize = 100;

fn main() {
    let x = 1_i32;
    let mut y: usize = 2;
    y += 1;
    let x = x.to_string(); // shadowing i zmiana typu

    let tuple = (x, y);
    let (tekst, liczba) = tuple;
    let tablica: [u8; 3] = [1, 2, 3];
    let slice: &[u8] = &tablica[1..];
    assert_eq!(tekst, "1");
    assert_eq!(liczba, 3);
    assert_eq!(slice, &[2_u8, 3]);
    assert_eq!(LIMIT, 100);
}
~~~

Liczby: `i8..i128`, `u8..u128`, `isize`, `usize`, `f32`, `f64`.
Pozostałe skalary: `bool` i `char`. Unit: `()`. Never: `!`.

## Funkcje i przepływ

~~~rust
fn klasyfikuj(x: i32) -> &'static str {
    match x {
        n if n < 0 => "ujemna",
        0 => "zero",
        1..=9 => "mała",
        _ => "duża",
    }
}

fn main() {
    let wynik = if true { 1 } else { 2 };
    for i in 0..3 {
        if i == 1 { continue; }
    }
    let z_petli = loop { break 42 };
    assert_eq!((klasyfikuj(7), wynik, z_petli), ("mała", 1, 42));
}
~~~

## Ownership

| Sygnatura | Znaczenie |
|---|---|
| `fn f(x: T)` | przejęcie ownership |
| `fn f(x: &T)` | pożyczka do odczytu |
| `fn f(x: &mut T)` | wyłączna pożyczka do mutacji |
| `fn f() -> T` | przekazanie ownership wyniku |
| `fn f<'a>(x: &'a T) -> &'a U` | wynik związany z lifetime wejścia |

~~~rust
fn dopisz(s: &mut String) { s.push('!'); }
fn widok(s: &str) -> &str { s.trim() }

fn main() {
    let mut s = String::from(" Rust ");
    assert_eq!(widok(&s), "Rust");
    dopisz(&mut s);
    let kopia = s.clone();
    assert_eq!(kopia, " Rust !");
}
~~~

## Typy i traits

~~~rust
#[derive(Debug, Clone, PartialEq)]
struct Punkt<T> { x: T, y: T }

enum Stan<T, E> {
    Gotowe(T),
    Blad(E),
}

trait Pole {
    type Wynik;
    fn pole(&self) -> Self::Wynik;
}

impl Pole for Punkt<i32> {
    type Wynik = i32;
    fn pole(&self) -> i32 { self.x * self.y }
}

fn pokaz(x: &impl std::fmt::Debug) -> String {
    format!("{x:?}")
}

fn main() {
    let p = Punkt { x: 2, y: 3 };
    assert_eq!(p.pole(), 6);
    assert!(pokaz(&p).contains('2'));
    let _ = Stan::<i32, &str>::Gotowe(1);
    let _ = Stan::<i32, &str>::Blad("x");
}
~~~

Dynamic dispatch: `&dyn Trait`, `Box<dyn Trait + Send + Sync>`.
Rozluźnienie rozmiaru: `T: ?Sized`. Associated type:
`Iterator<Item = T>`.

## Kolekcje i iteratory

~~~rust
use std::collections::{BTreeMap, HashSet, VecDeque};

fn main() {
    let v: Vec<_> = (0..10)
        .filter(|x| x % 2 == 0)
        .map(|x| x * x)
        .collect();
    let suma: i32 = v.iter().copied().sum();

    let mut mapa = BTreeMap::new();
    *mapa.entry("rust").or_insert(0) += 1;
    let zbior = HashSet::from([1, 2, 3]);
    let kolejka = VecDeque::from(["a", "b"]);
    assert_eq!((suma, mapa["rust"], zbior.len(), kolejka.len()), (120, 1, 3, 2));
}
~~~

Tekst: `String` posiada, `&str` pożycza; `len` liczy bajty, `chars` scalar
values. Bezpieczny indeks: `get`.

## Błędy

~~~rust
use std::num::ParseIntError;

fn podwoj(s: Option<&str>) -> Result<i32, ParseIntError> {
    let tekst = s.unwrap_or("0");
    let n = tekst.parse::<i32>()?;
    Ok(n * 2)
}

fn main() {
    assert_eq!(podwoj(Some("21")), Ok(42));
    assert_eq!(Some(2).map(|x| x + 1), Some(3));
    assert_eq!(Ok::<_, ()>(2).and_then(|x| Ok(x + 1)), Ok(3));
}
~~~

`unwrap`/`expect`: test albo udowodniony invariant. Dane użytkownika:
`Result` i kontekst. `panic!`: błąd programu/naruszony invariant.

## Moduły

~~~text
mod prywatny;
pub mod api;
pub(crate) mod wewnetrzny;

pub use api::Klient;
use std::collections::HashMap as Mapa;

crate::modul::Typ
self::dziecko::funkcja
super::funkcja
~~~

## Testy i dokumentacja

~~~rust
fn plus(a: i32, b: i32) -> i32 { a + b }

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn dodaje() { assert_eq!(plus(2, 3), 5); }
}

fn main() {
    assert_eq!(plus(1, 1), 2);
}
~~~

Integracja: `tests/*.rs`. Doctest: blok `rust` w `///`.
`#[should_panic(expected = "...")]`, `#[ignore]`.

## Współbieżność

~~~rust
use std::sync::{Arc, Mutex, mpsc};
use std::thread;

fn main() {
    let stan = Arc::new(Mutex::new(0));
    let kopia = Arc::clone(&stan);
    let h = thread::spawn(move || *kopia.lock().unwrap() += 1);
    h.join().unwrap();

    let (tx, rx) = mpsc::channel();
    tx.send(42).unwrap();
    assert_eq!((*stan.lock().unwrap(), rx.recv().unwrap()), (1, 42));
}
~~~

`Send` — przenoszenie między wątkami. `Sync` — współdzielenie `&T`.
Atomiki: ordering jest częścią dowodu, nie tuningiem.

## Async

~~~rust
use std::future::Future;

async fn wynik() -> Result<u32, &'static str> { Ok(42) }

fn przyjmij<F: Future<Output = Result<u32, &'static str>>>(_: F) {}

fn main() {
    przyjmij(wynik());
}
~~~

Standard library ma `Future`, ale ogólny executor/timer i `Stream` pochodzą
z ekosystemu. Nie trzymaj blocking guarda przez `await`.

## Makra

~~~rust
macro_rules! vec_powtorz {
    ($x:expr; $n:expr) => {{
        let wartosc = $x;
        vec![wartosc; $n]
    }};
}

fn main() {
    assert_eq!(vec_powtorz!(7; 3), [7, 7, 7]);
}
~~~

## Unsafe — lista kontrolna

- Czy pointer jest non-null, aligned i dereferenceable dla rozmiaru operacji?
- Czy wskazuje poprawnie zainicjalizowane `T`?
- Czy provenance obejmuje tę samą żywą alokację?
- Czy aliasing `&T`/`&mut T` jest zachowany?
- Czy ownership prowadzi do dokładnie jednego drop/free?
- Czy panic i częściowa inicjalizacja pozostawiają poprawny stan?
- Czy `Send`/`Sync` i atomiki mają dowód?
- Czy komentarz `SAFETY` odpowiada na wszystkie punkty?

## Powiązane tematy

- [Pełny spis treści](README.md)
- [Słownik](slownik.md)
- [`unsafe`, soundness i model pamięci](21_unsafe_soundness_i_model_pamieci/README.md)
