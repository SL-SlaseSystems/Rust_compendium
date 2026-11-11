[← Spis treści](../../README.md)

# Rozwiązania: Konwersje, DST i trait objects

## A20-1

Sprawdzamy wejście przed rzutem. Wartość 356 chroni przed błędem obcięcia, który mógłby zamienić ją w legalne 100.

~~~rust
#[derive(Debug, PartialEq)]
struct Procent(u8);
impl TryFrom<u16> for Procent {
    type Error = ();
    fn try_from(n: u16) -> Result<Self, ()> {
        if n <= 100 { Ok(Self(n as u8)) } else { Err(()) }
    }
}
fn main() {
    assert_eq!(Procent::try_from(0), Ok(Procent(0)));
    assert_eq!(Procent::try_from(100), Ok(Procent(100)));
    assert!(Procent::try_from(101).is_err());
    assert!(Procent::try_from(356).is_err());
}
~~~

## A20-2

`AsRef` normalizuje wejście do jednego widoku. Przekazanie wektora przez wartość konsumuje go, mimo że sama metoda `as_ref` jedynie pożycza; przekazanie `&wektor` zachowuje właściciela.

~~~rust
fn bajty<T: AsRef<[u8]>>(dane: T) -> usize { dane.as_ref().len() }
fn main() {
    let tablica = [1_u8, 2, 3];
    let wektor = vec![4_u8, 5];
    assert_eq!(bajty(tablica), 3);
    assert_eq!(bajty(&tablica[..2]), 2);
    assert_eq!(bajty(&wektor), 2);
    assert_eq!(wektor.len(), 2);
}
~~~

## A20-3

Referencje do dwóch obiektów o różnych typach mają wspólny typ `&dyn Display`. Alokacja wynikowego `String` pochodzi z `format!`, nie z utworzenia referencji do trait object.

~~~rust
use std::fmt::Display;
fn dynamicznie(x: &dyn Display) -> String { format!("{x}") }
fn statycznie<T: Display>(x: &T) -> String { format!("{x}") }
fn main() {
    let liczba = 42;
    let tekst = String::from("Rust");
    let obiekty: [&dyn Display; 2] = [&liczba, &tekst];
    assert_eq!(dynamicznie(obiekty[0]), "42");
    assert_eq!(dynamicznie(obiekty[1]), "Rust");
    assert_eq!(statycznie(&liczba), "42");
}
~~~

Wersja generyczna może zostać wyspecjalizowana dla każdego typu. Dynamiczna przyjmuje wspólny interfejs; odbiorca nie zna konkretnego typu. Żadna z tych sygnatur nie gwarantuje lepszej wydajności bez pomiaru rzeczywistego zastosowania.

