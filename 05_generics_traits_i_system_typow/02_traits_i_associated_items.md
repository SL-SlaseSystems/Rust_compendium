[← Spis treści](../README.md)

# Traits i associated items

Trait opisuje współdzielone zachowanie. Jest podobny do interfejsu, ale
obsługuje implementacje domyślne, associated types i constants, bounds,
statyczny oraz dynamiczny dispatch.

## Definicja i implementacja

~~~rust
trait Opis {
    const KATEGORIA: &'static str;

    fn nazwa(&self) -> &str;

    fn opis(&self) -> String {
        format!("{}: {}", Self::KATEGORIA, self.nazwa())
    }
}

struct Narzedzie(String);

impl Opis for Narzedzie {
    const KATEGORIA: &'static str = "narzędzie";

    fn nazwa(&self) -> &str {
        &self.0
    }
}

fn pokaz<T: Opis>(x: &T) -> String {
    x.opis()
}

fn main() {
    assert_eq!(pokaz(&Narzedzie("cargo".into())), "narzędzie: cargo");
}
~~~

`T: Opis` daje static dispatch. `impl Opis` w parametrze jest skrótem dla
anonimowego parametru generycznego; w wyniku oznacza jeden konkretny, lecz
ukryty typ.

## Associated type kontra parametr

~~~rust
trait Pobierz {
    type Element;
    fn pobierz(&self) -> Option<&Self::Element>;
}

struct Magazyn<T>(Vec<T>);

impl<T> Pobierz for Magazyn<T> {
    type Element = T;
    fn pobierz(&self) -> Option<&T> {
        self.0.first()
    }
}

fn main() {
    let m = Magazyn(vec![10, 20]);
    assert_eq!(m.pobierz(), Some(&10));
}
~~~

Associated type wybiera jeden typ na implementację. Parametr traitu pozwala
temu samemu typowi implementować trait wielokrotnie dla różnych parametrów.

## Coherence i orphan rule

Implementacja musi być jednoznaczna. Możesz implementować swój trait dla
obcego typu albo obcy trait dla swojego typu, ale nie obcy trait dla obcego
typu. Zapobiega to konfliktom między niezależnymi crate’ami. Wzorzec newtype
tworzy lokalny typ, gdy potrzebujesz legalnej implementacji.

Blanket implementation obejmuje całą rodzinę:

~~~rust
trait Pusty {
    fn pusty(&self) -> bool;
}

impl<T> Pusty for Vec<T> {
    fn pusty(&self) -> bool {
        self.is_empty()
    }
}

fn main() {
    assert!(Vec::<u8>::new().pusty());
}
~~~

W publicznej bibliotece blanket impl może ograniczyć przyszłe implementacje,
więc jest decyzją kompatybilności.

## Supertraits i pełna składnia

`trait Raport: std::fmt::Display` wymaga `Display`. Gdy metody mają tę samą
nazwę, użyj fully qualified syntax:

~~~rust
trait A { fn nazwa() -> &'static str; }
trait B { fn nazwa() -> &'static str; }
struct X;
impl A for X { fn nazwa() -> &'static str { "A" } }
impl B for X { fn nazwa() -> &'static str { "B" } }

fn main() {
    assert_eq!(<X as A>::nazwa(), "A");
    assert_eq!(<X as B>::nazwa(), "B");
}
~~~

## Sealed traits i negatywne granice

Publiczny trait można „zapieczętować” prywatnym supertraitem, aby użytkownicy
mogli go wywoływać, lecz nie implementować. Stabilny Rust nie udostępnia
ogólnych negatywnych bounds; nie projektuj API zakładając `T: !Trait`.

## Powiązane tematy

- [Konwersje, DST i trait objects](03_konwersje_dst_i_trait_objects.md)
- [Idiomy i extension traits](../14_idiomy_wzorce_i_architektura/01_idiomy_newtype_i_extension_traits.md)
- [HRTB, GAT i `impl Trait`](../05_generics_traits_i_system_typow/05_hrtb_gat_rpit_i_impl_trait.md)
