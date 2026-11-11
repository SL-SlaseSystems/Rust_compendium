[← Spis treści](../../README.md)

# Rozwiązania: Dyn compatibility, vtables i dispatch

## A23-1

Utworzenie pożyczonego obiektu nie wymaga alokacji. `to_string` alokuje dopiero wynik formatowania.

~~~rust
use std::fmt::Display;
fn main() {
    let n = 42;
    let obiekt: &dyn Display = &n;
    assert_eq!(obiekt.to_string(), "42");
}
~~~

## A23-2

Konstruktor jest wyłączony z dynamicznego interfejsu, lecz zwykła metoda może być wywołana przez obiekt.

~~~rust
trait Nazwa {
    fn nazwa(&self) -> &str;
    fn nowy() -> Self where Self: Sized;
}
struct X;
impl Nazwa for X {
    fn nazwa(&self) -> &str { "X" }
    fn nowy() -> Self { X }
}
fn main() {
    let x = X::nowy();
    let obiekt: &dyn Nazwa = &x;
    assert_eq!(obiekt.nazwa(), "X");
}
~~~

`<dyn Nazwa>::nowy()` nie jest dozwolone. Nie ma znanej konkretnej implementacji, którą taki konstruktor miałby zwrócić.

## A23-3

Upcasting zachowuje obiekt i udostępnia mniejszy kontrakt. `Any` sprawdza natomiast tożsamość konkretnego typu; błędne oczekiwanie daje `None`.

~~~rust
use std::any::Any;
trait Nazwa { fn nazwa(&self) -> &str; }
trait Podpis: Nazwa { fn podpis(&self) -> String; }
struct Dokument;
impl Nazwa for Dokument { fn nazwa(&self) -> &str { "dokument" } }
impl Podpis for Dokument { fn podpis(&self) -> String { self.nazwa().into() } }
fn main() {
    let d = Dokument;
    let szczegolny: &dyn Podpis = &d;
    let ogolny: &dyn Nazwa = szczegolny;
    assert_eq!(ogolny.nazwa(), "dokument");
    assert_eq!(szczegolny.podpis(), "dokument");
    let any: &dyn Any = &d;
    assert!(any.downcast_ref::<Dokument>().is_some());
    assert!(any.downcast_ref::<String>().is_none());
}
~~~

Ten upcasting jest sprawdzony na stable Rust 1.90. `Any` nie wynika automatycznie z `Nazwa`; tutaj tworzymy oddzielny obiekt `&dyn Any` z konkretnej wartości. Częste odzyskiwanie typów przez `Any` sugeruje potrzebę lepszego interfejsu albo enuma.

