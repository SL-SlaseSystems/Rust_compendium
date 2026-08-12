[← Spis treści](../README.md)

# Konwersje, DST i trait objects

## Traits konwersji

- `From<T>` / `Into<U>` — konwersja nieomylna i bez utraty znaczenia;
- `TryFrom<T>` / `TryInto<U>` — konwersja mogąca zwrócić błąd;
- `AsRef<T>` / `AsMut<T>` — tani widok referencyjny;
- `Borrow<T>` — widok zachowujący równoważność używaną np. przez mapy;
- `FromStr` — parsowanie tekstu.

Implementuj `From`; `Into` powstanie automatycznie. Nie używaj `From` dla
konwersji mogącej zawieść lub zaskakująco tracącej dane.

~~~rust
#[derive(Debug, PartialEq)]
struct Milimetry(u32);

impl From<u32> for Milimetry {
    fn from(value: u32) -> Self {
        Self(value)
    }
}

fn zmierz<T: Into<Milimetry>>(x: T) -> Milimetry {
    x.into()
}

fn main() {
    assert_eq!(zmierz(25_u32), Milimetry(25));
}
~~~

## Coercions

W określonych miejscach Rust wykonuje bezpieczne koercje, np. `&mut T` do
`&T`, `&String` do `&str` przez `Deref`, tablicę do slice oraz typ konkretny
do trait object. Nie są to dowolne konwersje jak w językach dynamicznych.

## Typy o dynamicznym rozmiarze

`str`, `[T]` i `dyn Trait` są dynamically sized types (DST). Ich rozmiaru nie
zna kompilator w miejscu ogólnym, dlatego używa się ich za wskaźnikiem:
`&str`, `Box<[T]>`, `Arc<dyn Trait>`.

Domyślny bound generyka to `T: Sized`. Zapis `T: ?Sized` rozluźnia go:

~~~rust
fn rozmiar_wskazywanej<T: ?Sized>(wartosc: &T) -> usize {
    std::mem::size_of_val(wartosc)
}

fn main() {
    assert_eq!(rozmiar_wskazywanej("abc"), 3);
    assert_eq!(rozmiar_wskazywanej(&[1_u16, 2][..]), 4);
}
~~~

Referencja do DST jest zwykle fat pointerem: niesie adres oraz metadane,
np. długość slice lub wskaźnik do vtable. Nie polegaj na szczegółach layoutu,
jeśli Reference nie daje gwarancji dla danego zastosowania.

## Trait objects

~~~rust
trait Pole {
    fn pole(&self) -> f64;
}

struct Kwadrat(f64);
struct Kolo(f64);

impl Pole for Kwadrat { fn pole(&self) -> f64 { self.0 * self.0 } }
impl Pole for Kolo { fn pole(&self) -> f64 { std::f64::consts::PI * self.0 * self.0 } }

fn suma(figury: &[Box<dyn Pole>]) -> f64 {
    figury.iter().map(|f| f.pole()).sum()
}

fn main() {
    let figury: Vec<Box<dyn Pole>> = vec![Box::new(Kwadrat(2.0)), Box::new(Kolo(1.0))];
    assert!(suma(&figury) > 7.0);
}
~~~

`dyn Pole` umożliwia heterogeniczną kolekcję i dynamic dispatch. Koszt to
indirection, wywołanie przez vtable i zwykle utrudniony inline. Zaletą jest
mniejszy kod oraz wybór implementacji w runtime.

Trait musi być dyn-compatible: między innymi metody wywoływane przez obiekt
nie mogą wymagać `Self: Sized` ani mieć własnych parametrów generycznych.
Termin „object safety” bywa używany historycznie; Reference mówi o dyn
compatibility.

## Powiązane tematy

- [Traits i associated items](04_traits_i_associated_items.md)
- [Dyn compatibility, vtables i dispatch](../zaawansowane/06_dyn_compatibility_vtables_i_dispatch.md)
- [Projektowanie publicznego API](../13_wzorce_i_architektura/03_projektowanie_api_i_semver.md)
