[← Spis treści](../README.md)

# Generics i const generics

Generics parametryzują kod typem, lifetime’em lub wartością stałą. Pozwalają
zapisać algorytm raz bez rezygnacji ze statycznego typowania.

## Parametry typów

~~~rust
fn wiekszy<T: PartialOrd>(a: T, b: T) -> T {
    if a >= b { a } else { b }
}

fn main() {
    assert_eq!(wiekszy(3, 7), 7);
    assert_eq!(wiekszy('z', 'a'), 'z');
}
~~~

Bound `T: PartialOrd` mówi, jakiej operacji potrzebuje implementacja.
Alternatywna klauzula `where T: PartialOrd` jest czytelniejsza przy wielu
parametrach.

## Typ generyczny

~~~rust
#[derive(Debug, PartialEq)]
struct Para<T, U> {
    pierwsza: T,
    druga: U,
}

impl<T, U> Para<T, U> {
    fn zamien(self) -> Para<U, T> {
        Para { pierwsza: self.druga, druga: self.pierwsza }
    }
}

impl<T> Para<T, T>
where
    T: std::ops::Add<Output = T>,
{
    fn suma(self) -> T {
        self.pierwsza + self.druga
    }
}

fn main() {
    let p = Para { pierwsza: 1, druga: "a" }.zamien();
    assert_eq!(p, Para { pierwsza: "a", druga: 1 });
    assert_eq!(Para { pierwsza: 2, druga: 3 }.suma(), 5);
}
~~~

Metoda może istnieć tylko dla wybranych parametrów. Parametr metody może być
inny niż parametr typu.

## Monomorfizacja

Dla statycznego dispatch kompilator generuje wyspecjalizowany kod dla
używanych podstawień. Zwykle daje to wydajność i możliwość inliningu, ale
może zwiększyć czas kompilacji oraz rozmiar binarium. Nie jest prawdą, że
każda funkcja generyczna musi powodować duży bloat — optymalizator może
scalać identyczny kod.

## Const generics

Stabilny Rust pozwala parametryzować wiele typów wartościami stałymi,
najczęściej długością tablicy:

~~~rust
fn suma<const N: usize>(dane: [i32; N]) -> i32 {
    dane.into_iter().sum()
}

#[derive(Debug, PartialEq)]
struct Bufor<T, const N: usize> {
    dane: [T; N],
}

fn main() {
    assert_eq!(suma([1, 2, 3]), 6);
    let b = Bufor { dane: [true; 4] };
    assert_eq!(b.dane.len(), 4);
}
~~~

Nie wszystkie wyrażenia na parametrach const są dozwolone w stabilnym
języku. Zaawansowane generic const expressions pozostają obszarem rozwoju;
sprawdzaj Unstable Book zamiast zakładać dostępność na stable.

## Turbofish i inferencja

Zapis `collect::<Vec<_>>()` podaje parametr, którego nie da się wywnioskować
z wyniku. Podkreślenie prosi kompilator o wywnioskowanie konkretnego miejsca.
Nadmierne adnotacje zwiększają szum, ale w publicznych sygnaturach typy są
zawsze częścią kontraktu.

## Powiązane tematy

- [Traits i associated items](02_traits_i_associated_items.md)
- [Iteratory](../06_kolekcje_iteratory_i_closures/05_iteratory.md)
- [Monomorfizacja i optymalizacja](../zaawansowane/13_monomorfizacja_mir_llvm_i_optymalizacja.md)
