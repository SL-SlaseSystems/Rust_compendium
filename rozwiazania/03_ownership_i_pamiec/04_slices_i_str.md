[← Spis treści](../../README.md)

# Rozwiązania: Slices i `str`

## A13-1

`first` udostępnia dokładnie potrzebny kontrakt. Parametr generyczny nie wymaga `Copy` ani `Clone`, bo wynik jest pożyczką.

~~~rust
fn pierwszy<T>(xs: &[T]) -> Option<&T> { xs.first() }
fn main() {
    let xs = [String::from("A")];
    assert_eq!(pierwszy(&xs).map(String::as_str), Some("A"));
    assert_eq!(pierwszy::<u8>(&[]), None);
}
~~~

## A13-2

`split_once` rozdziela pierwsze wystąpienie separatora. Drugie `=` zostaje częścią wartości; pusty klucz jest tu dopuszczony i można go zakazać osobną walidacją.

~~~rust
fn para(s: &str) -> Option<(&str, &str)> { s.split_once('=') }
fn main() {
    assert_eq!(para("żółw=mały"), Some(("żółw", "mały")));
    assert_eq!(para("a=b=c"), Some(("a", "b=c")));
    assert_eq!(para("brak"), None);
}
~~~

## A13-3

Najpierw sprawdzamy resztę `chunks_exact`, a dopiero potem tworzymy wynik. Każdy chunk ma dwa bajty, więc indeksy 0 i 1 są poprawne.

~~~rust
fn dekoduj(dane: &[u8]) -> Option<Vec<u16>> {
    let chunks = dane.chunks_exact(2);
    if !chunks.remainder().is_empty() { return None; }
    Some(chunks.map(|c| u16::from_be_bytes([c[0], c[1]])).collect())
}
fn main() {
    assert_eq!(dekoduj(&[0, 1, 1, 0]), Some(vec![1, 256]));
    assert_eq!(dekoduj(&[]), Some(vec![]));
    assert_eq!(dekoduj(&[1]), None);
}
~~~

Wynik posiada liczby, lecz wejściowy bufor nie jest kopiowany do pośredniej kolekcji. Endianness jest jawną częścią formatu. W dużym strumieniu podobną logikę można udostępnić jako iterator i ograniczyć liczbę wyników zamiast alokować cały `Vec`.

