[← Spis treści](../README.md)
<!-- status: expanded -->

# HRTB, GAT, RPIT i `impl Trait`

> Przykłady: **stable**, Rust 1.90.0, Edition 2024. Źródła sprawdzono 11 listopada 2026 r.

## Cele

Po tym rozdziale potrafisz:

- odróżnić „dla każdego lifetime” od jednego parametru wybranego przez klienta;
- powiązać typ wyniku z pożyczką `self` przez GAT;
- kontrolować przechwytywanie parametrów w RPIT Edition 2024 przez `use<...>`;

## Model — kto wybiera typ i kiedy wiąże się pożyczka


Te mechanizmy opisują zależności typów i lifetimes, których nie da się
wyrazić prostym `T: Trait`.

## HRTB

Higher-ranked trait bound `for<'a>` znaczy „dla każdego lifetime `'a`”, a nie
„dla jednego lifetime wybranego wcześniej”.

~~~rust
fn pierwszy(s: &str) -> &str {
    s.split_whitespace().next().unwrap_or("")
}

fn zastosuj_do_dwoch<F>(f: F) -> (String, String)
where
    F: for<'a> Fn(&'a str) -> &'a str,
{
    let a = String::from("Ala ma");
    let b = String::from("Rust działa");
    (f(&a).to_owned(), f(&b).to_owned())
}

fn main() {
    assert_eq!(
        zastosuj_do_dwoch(pierwszy),
        ("Ala".to_owned(), "Rust".to_owned())
    );
}
~~~

Funkcja `f` musi działać dla dwóch niezależnych, lokalnych lifetimes. HRTB
pojawia się często w bounds `Fn`, deserializacji pożyczającej i visitorach.

## GAT

Generic associated type jest associated type z własnymi parametrami. Pozwala
powiązać wynik pożyczki z lifetime `self`:

~~~rust
trait Kolekcja {
    type Element;
    type Iter<'a>: Iterator<Item = &'a Self::Element>
    where
        Self: 'a;

    fn iter(&self) -> Self::Iter<'_>;
}

struct Liczby(Vec<i32>);

impl Kolekcja for Liczby {
    type Element = i32;
    type Iter<'a> = std::slice::Iter<'a, i32>;

    fn iter(&self) -> Self::Iter<'_> {
        self.0.iter()
    }
}

fn main() {
    let x = Liczby(vec![1, 2, 3]);
    assert_eq!(x.iter().copied().sum::<i32>(), 6);
}
~~~

Klauzula `where Self: 'a` mówi, że implementacja żyje wystarczająco długo.
GAT są stabilne, ale nie wszystkie oczekiwane wzorce lending iteratorów są
ergonomiczne; ograniczenia borrow checkera i dyn compatibility nadal mają
znaczenie.

## Argument-position `impl Trait`

~~~rust
fn pokaz(x: impl std::fmt::Display) -> String {
    x.to_string()
}

fn main() {
    assert_eq!(pokaz(42), "42");
}
~~~

To prawie anonimowy parametr generyczny wybierany przez wywołującego. Różnica
ma znaczenie m.in. dla możliwości jawnego podania parametru i kompatybilności
zmiany kolejności parametrów publicznego API.

## RPIT

Return-position `impl Trait` ukrywa jeden konkretny typ wybierany przez
implementację:

~~~rust
fn parzyste(dane: &[i32]) -> impl Iterator<Item = i32> + '_ {
    dane.iter().copied().filter(|x| x % 2 == 0)
}

fn main() {
    assert_eq!(parzyste(&[1, 2, 4]).collect::<Vec<_>>(), [2, 4]);
}
~~~

Wszystkie ścieżki return muszą mieć ten sam ukryty typ. Jeśli gałęzie mają
różne typy iteratorów, ujednolić je enumem, adapterem albo trait object.

Edition 2024 automatycznie przechwytuje wszystkie parametry generyczne
widoczne w zakresie RPIT. Bound `use<'a, T>` pozwala precyzyjnie określić
capture w obsługiwanych pozycjach.

## RPITIT i async traits

`impl Trait` w wyniku metody traitu (RPITIT) jest anonimowym associated type.
`async fn` w traitach jest stabilne i desugaruje się do takiego ukrytego
future. Publiczny trait powinien przemyśleć bounds wyniku, np. `Send`; odbiorca
nie może dodać brakującego boundu do anonimowego typu.

~~~rust
trait Licz {
    fn wartosci(&self) -> impl Iterator<Item = i32> + '_;
}

impl Licz for Vec<i32> {
    fn wartosci(&self) -> impl Iterator<Item = i32> + '_ {
        self.iter().copied()
    }
}

fn main() {
    assert_eq!(vec![1, 2].wartosci().sum::<i32>(), 3);
}
~~~

Trait z RPITIT/`async fn` nie jest automatycznie dyn-compatible.

## TAIT i inne granice

Type alias `type Ukryty = impl Trait` (TAIT) pozostaje **nightly** pod bramką
`type_alias_impl_trait` według Unstable Book (weryfikacja 2026-11-11).
`impl Trait` nie może być zwykłym typem pola ani bindingu `let`.

## Reguły — trzy różne kwantyfikacje

W `fn f<T: Trait>(x: T)` konkretny typ wybiera klient. W `fn f() -> impl Trait` konkretny typ wybiera implementacja i klient poznaje tylko zadeklarowane zdolności. `for<'a>` dodaje jeszcze inne zobowiązanie: implementacja musi działać dla dowolnej ważności pożyczki wybranej w miejscu zastosowania. Nie zastępuje to `'static`; callback przyjmujący wyłącznie `&'static str` nie obsłuży dowolnego lokalnego `&str`.

GAT jest rodziną typów. `type Widok<'a>` pozwala implementacji dostarczać różny typ widoku dla kolejnych `'a`, zwykle powiązany z pożyczką obiektu. To umożliwia tzw. lending API, w którym następny wynik pożycza mutowalnie wnętrze iteratoropodobnego obiektu. Zwykły `Iterator::Item` nie ma osobnego parametru lifetime dla każdego wywołania `next`; nie wyraża bezpośrednio takiej rodziny wyników.

Nie każde API potrzebuje jednak własnego GAT. Jeśli wynik jest po prostu `&[T]`, zwykła metoda z elision może wystarczyć. GAT nabiera wartości, kiedy implementacje mają różne rodzaje widoku albo klient ma operować generycznie nad tą rodziną. Dodatkowa ogólność zwiększa trudność diagnostyki i może ograniczyć użycie `dyn`.

## Precyzyjne capture w Edition 2024

RPIT domyślnie przechwytuje widoczne parametry generyczne, także lifetimes. To może utrzymać zależność wyniku od pożyczki, nawet jeśli ukryty typ przechowuje tylko liczbę. `use<>` pozwala w odpowiedniej pozycji powiedzieć, że wynik nie przechwytuje żadnego parametru.

~~~rust
fn indeksy(tekst: &str) -> impl Iterator<Item = usize> + use<> {
    0..tekst.len()
}
fn main() {
    let iter;
    {
        let tekst = String::from("Rust");
        iter = indeksy(&tekst);
    }
    assert_eq!(iter.collect::<Vec<_>>(), [0, 1, 2, 3]);
}
~~~

Ukrytym typem jest `Range<usize>`, który nie przechowuje referencji do tekstu. Po wyjściu z bloku nadal można go konsumować. Liczby są indeksami bajtowymi i nie gwarantują granic UTF-8; przykład pokazuje capture, a nie sposób cięcia Unicode. Jeśli funkcja faktycznie zwraca `tekst.chars()`, nie wolno usunąć zależności od wejścia.

`use<'a, T>` nie jest zamiennikiem dowolnego outlives boundu. Lista określa parametry przechwycone przez ukryty typ; nadal obowiązują ograniczenia składni i konieczność uwzględnienia wymaganych parametrów typów oraz const. Z kolei `+ 'a` wymaga, by wynik przeżywał `'a`. To różne obietnice i powinny być wybierane według danych przechowywanych przez wynik.

W publicznym `async fn` traitu ukryty future jest częścią kontraktu. Jeśli odbiorca wymaga `Send`, rozważ jawną metodę zwracającą `impl Future<Output = ...> + Send`, gdy implementacja może spełnić tę obietnicę. Nie dodawaj `Send` bez potrzeby do jednowątkowego wykonawcy.

## Diagnostyka kompilatora

RPIT ukrywa jeden konkretny typ dla danej funkcji, a nie dowolny typ spełniający trait w każdej gałęzi.

~~~compile_fail
fn liczby(odwroc: bool) -> impl Iterator<Item = i32> {
    if odwroc { (0..3).rev() } else { 0..3 }
}
fn main() {}
~~~

`Rev<Range<i32>>` i `Range<i32>` różnią się. Rozwiązaniem może być wspólny adapter, enum albo `Box<dyn Iterator<Item = i32>>`. Ostatnia opcja zmienia koszty i kontrakt lifetime. Przy błędzie HRTB „implementation is not general enough” sprawdź, czy callback działa dla dowolnego wejściowego lifetime, a nie tylko dla jednej konkretnej pożyczki.

## Praktyka produkcyjna

Dobieraj najsłabszy mechanizm opisujący potrzebę. Zwykła referencja jest prostsza od rodziny GAT, a konkretny typ wyniku bywa bardziej użyteczny dla klientów niż celowe ukrycie wszystkich jego zdolności. `impl Iterator` może ograniczać zależność od implementacji, lecz zadeklarowanie `DoubleEndedIterator` czy `ExactSizeIterator` jest osobnym zobowiązaniem publicznego API.

Sprawdzaj przykłady po zmianie edition. Automatyczne capture może spowodować dłuższą pożyczkę bez zmiany ciała funkcji. Nie rozwiązuj takiej regresji automatycznie klonowaniem danych; porównaj rzeczywiście przechowywane parametry i ewentualnie użyj precyzyjnej listy `use<...>`. Status TAIT nie wynika ze stabilności zwykłego RPIT: są to odrębne mechanizmy.

## Sprawdź, czy rozumiesz

1. Dlaczego callback tylko dla `&'static str` nie spełnia dowolnego HRTB?
2. Czym różni się associated type od rodziny GAT?
3. Dlaczego `use<>` w przykładzie pozwala zniszczyć wejściowy `String`?

## Ćwiczenia

- `A22-1` — podstawowe: napisz HRTB wywołujące przekazaną funkcję z dwoma niezależnymi lokalnymi tekstami [Rozwiązanie](../rozwiazania/05_generics_traits_i_system_typow/05_hrtb_gat_rpit_i_impl_trait.md#a22-1).
- `A22-2` — praktyczne: napisz RPIT zwracające zakres indeksów i użyj `use<>`, aby wynik przeżył tekst wejściowy [Rozwiązanie](../rozwiazania/05_generics_traits_i_system_typow/05_hrtb_gat_rpit_i_impl_trait.md#a22-2).
- `A22-3` — pogłębione: zdefiniuj GAT `Widok<'a>` i metodę pożyczającą `&mut self`; implementacja ma zwracać mutowalny slice wewnętrznego bufora [Rozwiązanie](../rozwiazania/05_generics_traits_i_system_typow/05_hrtb_gat_rpit_i_impl_trait.md#a22-3).

## Źródła i zakres stabilności

Capture i `use`: [Reference: impl Trait](https://doc.rust-lang.org/reference/types/impl-trait.html) oraz [Edition Guide: RPIT lifetime capture](https://doc.rust-lang.org/edition-guide/rust-2024/rpit-lifetime-capture.html). TAIT: [Unstable Book](https://doc.rust-lang.org/unstable-book/language-features/type-alias-impl-trait.html), nadal **nightly**, `#![feature(type_alias_impl_trait)]`, weryfikacja 11 listopada 2026 r.

## Powiązane tematy

- [Traits i associated items](../05_generics_traits_i_system_typow/02_traits_i_associated_items.md)
- [Dyn compatibility](06_dyn_compatibility_vtables_i_dispatch.md)
- [`Future` i async](../11_async_rust/01_future_async_i_await.md)
