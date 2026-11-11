[← Spis treści](../README.md)
<!-- status: expanded -->

# Traits i associated items

> Przykłady: **stable**, Rust 1.90.0, Edition 2024. Źródła sprawdzono 11 listopada 2026 r.

## Cele

Po tym rozdziale potrafisz:

- wybrać associated type lub parametr traitu według liczby potrzebnych implementacji;
- rozpoznać konflikt coherence i legalnie użyć newtype;
- oddzielić kontrakt zachowania od mechanizmu static albo dynamic dispatch;

## Model — implementacja jest świadectwem kontraktu


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

## Reguły — podpis metody nie opisuje całej semantyki

Trait określa dostępne elementy, lecz dokumentacja określa ich prawa. `Eq`, `Ord` i `Hash` mają wymagania spójności, których kompilator nie dowodzi. Własny trait serializacji również powinien powiedzieć, czy wynik jest deterministyczny, czy metoda może częściowo zapisać dane i jak zachowuje się przy błędzie. Dwie implementacje o identycznej sygnaturze mogą mieć niezgodną semantykę, jeśli kontrakt pozostaje przemilczany.

Associated type wiąże wynik z konkretną implementacją, na przykład `Iterator::Item`. Nie trzeba za każdym razem wybierać go w wywołaniu `next`. Parametr traitu, jak `From<T>`, pozwala implementować konwersję z wielu różnych typów dla tego samego odbiorcy. Kryterium nie brzmi „krótsza składnia”, ale „czy ten sam `Self` powinien móc mieć wiele wersji zachowania dla różnych argumentów typu”.

~~~rust
trait Zrodlo {
    type Element;
    fn pierwszy(&self) -> Option<&Self::Element>;
}
impl<T> Zrodlo for Vec<T> {
    type Element = T;
    fn pierwszy(&self) -> Option<&T> { self.first() }
}
fn odczytaj<S: Zrodlo<Element = u32>>(s: &S) -> Option<u32> {
    s.pierwszy().copied()
}
fn main() {
    assert_eq!(odczytaj(&vec![7, 8]), Some(7));
    assert_eq!(odczytaj(&Vec::<u32>::new()), None);
}
~~~

Bound `Element = u32` wiąże associated type z potrzebą klienta, więc `.copied()` ma określoną semantykę. Gdyby klient potrzebował tylko referencji, mógłby pozostać ogólny po `S::Element`. Projekcję tego typu można zapisać w pełni jako `<S as Zrodlo>::Element`.

## Coherence jest regułą całego ekosystemu

Hasło „lokalny trait albo lokalny typ” jest dobrym punktem wyjścia, lecz dla implementacji z parametrami obowiązują bardziej precyzyjne reguły pokrycia. Lokalny typ w `Vec<MojTyp>` nie czyni samego `Vec` lokalnym. Pewne typy fundamentalne, takie jak `Box<T>`, są traktowane szczególnie przy lokalności, lecz nie jest to ogólna własność każdego kontenera. Przy implementacji obcego traitu sprawdź pierwszy lokalny typ w kolejności parametrów i brak niepokrytych parametrów przed nim zgodnie z Reference.

Nawet legalne lokalnie implementacje nie mogą się nakładać. `impl<T> MojTrait for T` obejmuje także twój konkretny `Rekord`, więc drugi `impl MojTrait for Rekord` może kolidować. Stabilny Rust nie daje ogólnej specjalizacji, która pozwalałaby dowolnie nadpisywać blanket impl. Newtype tworzy odrębną tożsamość, lecz także wymaga własnych konwersji i świadomego doboru udostępnionych metod.

## Diagnostyka kompilatora

Dwie implementacje obejmujące ten sam typ powodują E0119. Kompilator nie wybiera automatycznie „bardziej konkretnej”.

~~~compile_fail
trait Opis {}
struct Rekord;
impl<T> Opis for T {}
impl Opis for Rekord {}
fn main() {}
~~~

E0117 dotyczy implementowania obcego traitu dla obcego typu, a E0207 — parametru, którego implementacja nie wiąże w wymagany sposób. Przy E0034 metody z różnych traitów mają tę samą nazwę: użyj `<Typ as Trait>::metoda(...)`. Zmiana kolejności `use` nie jest poprawnym mechanizmem wyboru implementacji.

## Praktyka produkcyjna

Publiczny blanket impl może zablokować przyszłe implementacje klientów. Dodanie obowiązkowej metody do otwartego traitu jest zwykle zmianą łamiącą zgodność. Metoda domyślna zmniejsza koszt migracji, ale może wprowadzać nowe konflikty nazw i powinna mieć sens dla wszystkich istniejących implementacji.

Sealed trait ogranicza implementacje do biblioteki: prywatny supertrait stanowi barierę implementowania z zewnątrz. To dobry wybór, gdy autor musi znać wszystkie przypadki albo zachować swobodę rozbudowy, lecz odbiera użytkownikom możliwość rozszerzania zachowania. Rozdziel mały otwarty trait integracyjny od wewnętrznego zamkniętego protokołu, jeśli obie potrzeby występują naraz. Nie używaj niebezpiecznego traitu tylko po to, aby wymusić czytanie dokumentacji; `unsafe trait` wymaga rzeczywistego kontraktu bezpieczeństwa.

## Sprawdź, czy rozumiesz

1. Dlaczego `Iterator::Item` jest associated type, a `From<T>` ma parametr?
2. Czy `Vec<Lokalny>` jest lokalnym typem dla orphan rule?
3. Co blokuje ogólny `impl<T> Trait for T` w późniejszym rozwoju API?

## Ćwiczenia

- `A19-1` — podstawowe: zdefiniuj trait `Nazwa` z domyślnym powitaniem i zaimplementuj go dla własnego typu [Rozwiązanie](../rozwiazania/05_generics_traits_i_system_typow/02_traits_i_associated_items.md#a19-1).
- `A19-2` — praktyczne: zdefiniuj trait z associated type i funkcję wymagającą `Element = u8` [Rozwiązanie](../rozwiazania/05_generics_traits_i_system_typow/02_traits_i_associated_items.md#a19-2).
- `A19-3` — pogłębione: utwórz newtype dla `Vec<i32>` i legalnie zaimplementuj `Display`, opisując koszt oraz format [Rozwiązanie](../rozwiazania/05_generics_traits_i_system_typow/02_traits_i_associated_items.md#a19-3).

## Źródła i zakres stabilności

Associated items i supertraits: [Reference: traits](https://doc.rust-lang.org/reference/items/traits.html). Dokładne reguły orphan, pokrycia i coherence: [Reference: implementations](https://doc.rust-lang.org/reference/items/implementations.html#trait-implementation-coherence).

## Powiązane tematy

- [Konwersje, DST i trait objects](03_konwersje_dst_i_trait_objects.md)
- [Idiomy i extension traits](../14_idiomy_wzorce_i_architektura/01_idiomy_newtype_i_extension_traits.md)
- [HRTB, GAT i `impl Trait`](../05_generics_traits_i_system_typow/05_hrtb_gat_rpit_i_impl_trait.md)
