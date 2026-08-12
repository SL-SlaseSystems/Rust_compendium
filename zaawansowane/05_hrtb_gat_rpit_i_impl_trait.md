[← Spis treści](../README.md)

# HRTB, GAT, RPIT i `impl Trait`

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
`type_alias_impl_trait` według Unstable Book (weryfikacja 2026-08-12).
`impl Trait` nie może być zwykłym typem pola ani bindingu `let`.

## Powiązane tematy

- [Traits i associated items](../04_typy_i_modelowanie/04_traits_i_associated_items.md)
- [Dyn compatibility](06_dyn_compatibility_vtables_i_dispatch.md)
- [`Future` i async](../10_async/01_future_async_i_await.md)
