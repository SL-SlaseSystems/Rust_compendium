[← Spis treści](../README.md)
<!-- status: expanded -->

# Generics i const generics

> Przykłady: **stable**, Rust 1.90.0, Edition 2024. Źródła sprawdzono 11 listopada 2026 r.

## Cele

Po tym rozdziale potrafisz:

- uzasadnić bound konkretną operacją używaną w ciele funkcji;
- odróżnić parametr wybierany przez klienta od typu wybieranego przez implementację;
- zastosować długość tablicy jako parametr const bez założenia dostępności dowolnej arytmetyki typów;

## Model — algorytm sprawdzany dla wszystkich dopuszczonych typów


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

## Reguły — implementacja korzysta tylko z obietnic

Ciało funkcji generycznej musi być poprawne dla każdego podstawienia spełniającego bounds, a nie tylko dla typu z pierwszego przykładu. `T: PartialOrd` pozwala porównywać, lecz nie dodaje prawa do wyświetlenia, klonowania ani dodawania. Gdy wynik jest pożyczony, funkcja nie musi konsumować `T` ani żądać `Copy`. Wybór parametrów opisuje również liczbę niezależnych typów: dwa argumenty `T` muszą mieć ten sam typ, a dwa osobne `impl Trait` mogą mieć różne.

Przykład `wiekszy` z `PartialOrd` ma określone zachowanie przy nieporównywalności: porównanie z `NaN` jest fałszywe i wybierana jest druga gałąź. Jeżeli algorytm potrzebuje pełnego porządku, zażądaj `Ord` albo jawnie obsłuż `partial_cmp` zwracające `None`. Poszerzenie zbioru typów nie zawsze oznacza poprawniejszą abstrakcję.

~~~rust
fn minimum<T: Ord>(dane: &[T]) -> Option<&T> {
    dane.iter().min()
}
fn main() {
    let slowa = [String::from("beta"), String::from("alfa")];
    assert_eq!(minimum(&slowa).map(String::as_str), Some("alfa"));
    assert!(minimum::<u8>(&[]).is_none());
    assert_eq!(slowa[0], "beta");
}
~~~

Wynik pożycza wybrany element. Nie ma `Clone`, `Copy` ani alokacji wyniku, a puste wejście jest reprezentowane przez `None`. Taki bound mówi o faktycznej potrzebie algorytmu. Dołożenie `Display` tylko dlatego, że diagnostyka miałaby drukować elementy, ograniczyłoby wszystkich klientów; logowanie można oddzielić od samego wyboru minimum.

## Const generics i granica stable

Parametr `const N: usize` staje się częścią tożsamości typu: `Bufor<u8, 4>` i `Bufor<u8, 8>` są różnymi typami. W stabilnym zakresie pokazanym w Rust 1.90 można bezpośrednio użyć `N` jako długości tablicy. Typy parametrów const są ograniczone; nie można dowolnie wybrać `String` ani typu zmiennoprzecinkowego. Dowolne wyrażenie typu `[u8; N + 1]` nie jest ogólnie dostępne na stable.

Nie myl tego z obliczeniem liczby w zwykłym ciele funkcji albo z konkretnym `[u8; 3 + 1]`. Ograniczenie dotyczy zależności rozmiaru typu od parametru generycznego. **nightly** `generic_const_exprs` wymaga `#![feature(generic_const_exprs)]` i pozostaje niekompletnym obszarem języka według Unstable Book sprawdzonego 11 listopada 2026 r. Projekt stable może zamiast tego przyjąć osobny parametr rozmiaru i sprawdzić relację w konstruktorze.

## Diagnostyka kompilatora

Brak boundu to brak uprawnienia do użycia operacji. E0369 nie znika od tego, że wywołanie w `main` używa tylko `i32`.

~~~compile_fail
fn suma<T>(a: T, b: T) -> T { a + b }
fn main() { let _ = suma(1, 2); }
~~~

Potrzebny bound to `T: std::ops::Add<Output = T>`. Gdy `collect` lub `parse` nie mają wystarczającego kontekstu, dopisz typ wyniku albo turbofish; nie zmieniaj wszystkich pośrednich typów na `String`. Przy const generic odróżnij niezgodną długość tablicy od błędu niedozwolonego wyrażenia na parametrze.

## Praktyka produkcyjna

Każdy dodatkowy parametr publicznego typu zwiększa liczbę relacji, które musi rozumieć klient. Generyki stosuj dla rzeczywistej zmienności, na przykład źródła danych lub strategii, a stały format pakietu można opisać konkretnym typem. W dużych bibliotekach wydziel ciężką część implementacji do funkcji niegenerycznej po zamianie wejścia na prosty wspólny widok.

Monomorfizacja umożliwia specjalizację i inline, ale nie daje uniwersalnej gwarancji rozmiaru ani czasu kompilacji. Mierz program dla typowego zestawu podstawień. Długość tablicy w typie eliminuje część błędów granic API, lecz wiele różnych `N` może zwiększyć liczbę instancji kodu. Dla rozmiarów pochodzących z sieci zwykły slice jest często właściwszy.

## Sprawdź, czy rozumiesz

1. Dlaczego poprawne wywołanie z `i32` nie zastąpi boundu w definicji generycznej?
2. Kiedy `PartialOrd` jest za słabym kontraktem dla wyboru minimum?
3. Czym różnią się `[u8; N]` i `[u8; N + 1]` na Rust 1.90 stable?

## Ćwiczenia

- `A18-1` — podstawowe: napisz generyczne `zamien((T, U)) -> (U, T)` bez `Clone` [Rozwiązanie](../rozwiazania/05_generics_traits_i_system_typow/01_generics_i_const_generics.md#a18-1).
- `A18-2` — praktyczne: napisz `ostatni<T, const N: usize>(&[T; N]) -> Option<&T>` i sprawdź `N = 0` [Rozwiązanie](../rozwiazania/05_generics_traits_i_system_typow/01_generics_i_const_generics.md#a18-2).
- `A18-3` — pogłębione: napisz generyczną sumę dwóch wartości z minimalnym boundem `Add`; pokaż `u32` oraz własny newtype [Rozwiązanie](../rozwiazania/05_generics_traits_i_system_typow/01_generics_i_const_generics.md#a18-3).

## Źródła i zakres stabilności

Dozwolone parametry i ograniczenia const: [Reference: generic parameters](https://doc.rust-lang.org/reference/items/generics.html). Status niestabilny: [Unstable Book: generic_const_exprs](https://doc.rust-lang.org/unstable-book/language-features/generic-const-exprs.html).

## Powiązane tematy

- [Traits i associated items](02_traits_i_associated_items.md)
- [Iteratory](../06_kolekcje_iteratory_i_closures/05_iteratory.md)
- [Monomorfizacja i optymalizacja](../20_wydajnosc_i_optymalizacja/03_monomorfizacja_mir_llvm_i_optymalizacja.md)
