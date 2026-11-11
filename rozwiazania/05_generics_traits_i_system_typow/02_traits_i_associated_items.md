[← Spis treści](../../README.md)

# Rozwiązania: Traits i associated items

## A19-1

Metoda domyślna korzysta tylko z wymaganego `nazwa`; implementacja dostarcza tę minimalną część kontraktu.

~~~rust
trait Nazwa {
    fn nazwa(&self) -> &str;
    fn powitanie(&self) -> String { format!("Cześć, {}", self.nazwa()) }
}
struct Osoba(String);
impl Nazwa for Osoba { fn nazwa(&self) -> &str { &self.0 } }
fn main() { assert_eq!(Osoba("Ada".into()).powitanie(), "Cześć, Ada"); }
~~~

## A19-2

Associated type jest wybierany przez implementację, a klient ogranicza go do bajtu. W przykładzie źródłem jest stała wartość.

~~~rust
trait Zrodlo { type Element; fn pobierz(&self) -> Self::Element; }
struct Bajt;
impl Zrodlo for Bajt { type Element = u8; fn pobierz(&self) -> u8 { 7 } }
fn czytaj<S: Zrodlo<Element = u8>>(s: &S) -> u16 { u16::from(s.pobierz()) }
fn main() { assert_eq!(czytaj(&Bajt), 7); }
~~~

## A19-3

Lokalny `Lista` pozwala implementować obcy `Display`. Format jest jawny: przecinki bez spacji, bez nawiasów i bez końcowego separatora.

~~~rust
use std::fmt;
struct Lista(Vec<i32>);
impl fmt::Display for Lista {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        for (i, n) in self.0.iter().enumerate() {
            if i != 0 { write!(f, ",")?; }
            write!(f, "{n}")?;
        }
        Ok(())
    }
}
fn main() {
    assert_eq!(Lista(vec![1, 2, 3]).to_string(), "1,2,3");
    assert_eq!(Lista(vec![]).to_string(), "");
}
~~~

Samo opakowanie przenosi nagłówek wektora i nie kopiuje elementów. `fmt` zapisuje do dostarczonego formattera; alokację wyniku wykonuje dopiero `to_string`. Typ nie dostaje automatycznie całego API wektora ani konwersji do niego.

