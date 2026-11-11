[← Spis treści](../../README.md)

# Rozwiązania: HRTB, GAT, RPIT i `impl Trait`

## A22-1

Nazwana funkcja z elision ma odpowiednią ogólność dla obu pożyczek. Wyniki zamieniamy na posiadane długości.

~~~rust
fn dlugosc(s: &str) -> usize { s.len() }
fn dwa<F: for<'a> Fn(&'a str) -> usize>(f: F) -> (usize, usize) {
    let a = String::from("A");
    let b = String::from("Rust");
    (f(&a), f(&b))
}
fn main() { assert_eq!(dwa(dlugosc), (1, 4)); }
~~~

## A22-2

Wynik przechowuje jedynie skopiowaną długość. `use<>` jawnie odcina domyślne capture lifetime wejścia.

~~~rust
fn indeksy(s: &str) -> impl Iterator<Item = usize> + use<> { 0..s.len() }
fn main() {
    let iter = { let s = String::from("abc"); indeksy(&s) };
    assert_eq!(iter.collect::<Vec<_>>(), [0, 1, 2]);
}
~~~

Przy wyniku `s.bytes()` taki kontrakt byłby niepoprawny, bo iterator pożycza dane.

## A22-3

Associated type jest tu parametryzowany czasem każdej pożyczki. Wynik z wyłącznym dostępem blokuje kolejną mutowalną pożyczkę obiektu do końca swojego użycia.

~~~rust
trait Bufor {
    type Widok<'a> where Self: 'a;
    fn widok(&mut self) -> Self::Widok<'_>;
}
struct Bajty(Vec<u8>);
impl Bufor for Bajty {
    type Widok<'a> = &'a mut [u8];
    fn widok(&mut self) -> Self::Widok<'_> { &mut self.0 }
}
fn main() {
    let mut b = Bajty(vec![1, 2]);
    {
        let fragment = b.widok();
        fragment[0] = 9;
    }
    assert_eq!(b.widok(), [9, 2]);
}
~~~

Dla tego jednego typu prosta metoda `fn widok(&mut self) -> &mut [u8]` byłaby wystarczająca. GAT staje się uzasadnione, gdy kolejne implementacje potrzebują odmiennych typów widoku. Ćwiczenie demonstruje relację, a nie potrzebę stosowania jej w każdym buforze.

