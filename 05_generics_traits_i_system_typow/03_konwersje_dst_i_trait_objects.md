[← Spis treści](../README.md)
<!-- status: expanded -->

# Konwersje, DST i trait objects

> Przykłady: **stable**, Rust 1.90.0, Edition 2024. Źródła sprawdzono 11 listopada 2026 r.

## Cele

Po tym rozdziale potrafisz:

- wybrać `From`, `TryFrom`, `AsRef` lub `Borrow` według semantyki operacji;
- usunąć domyślne `Sized` tam, gdzie funkcja działa przez referencję;
- wyjaśnić, które koszty wynikają z `Box`, a które z `dyn Trait`;

## Model — zmiana wartości, widok i wymazanie typu


## Traits konwersji

- `From<T>` / `Into<U>` — konwersja nieomylna i bez utraty znaczenia;
- `TryFrom<T>` / `TryInto<U>` — konwersja mogąca zwrócić błąd;
- `AsRef<T>` / `AsMut<T>` — tani widok referencyjny;
- `Borrow<T>` — widok zachowujący równoważność używaną np. przez mapy;
- `FromStr` — parsowanie tekstu.

Implementuj `From`; `Into` powstanie automatycznie. Nie używaj `From` dla
konwersji mogącej zawieść lub zaskakująco tracącej dane.

~~~rust
#[derive(Debug, PartialEq)]
struct Milimetry(u32);

impl From<u32> for Milimetry {
    fn from(value: u32) -> Self {
        Self(value)
    }
}

fn zmierz<T: Into<Milimetry>>(x: T) -> Milimetry {
    x.into()
}

fn main() {
    assert_eq!(zmierz(25_u32), Milimetry(25));
}
~~~

## Coercions

W określonych miejscach Rust wykonuje bezpieczne koercje, np. `&mut T` do
`&T`, `&String` do `&str` przez `Deref`, tablicę do slice oraz typ konkretny
do trait object. Nie są to dowolne konwersje jak w językach dynamicznych.

## Typy o dynamicznym rozmiarze

`str`, `[T]` i `dyn Trait` są dynamically sized types (DST). Ich rozmiaru nie
zna kompilator w miejscu ogólnym, dlatego używa się ich za wskaźnikiem:
`&str`, `Box<[T]>`, `Arc<dyn Trait>`.

Domyślny bound generyka to `T: Sized`. Zapis `T: ?Sized` rozluźnia go:

~~~rust
fn rozmiar_wskazywanej<T: ?Sized>(wartosc: &T) -> usize {
    std::mem::size_of_val(wartosc)
}

fn main() {
    assert_eq!(rozmiar_wskazywanej("abc"), 3);
    assert_eq!(rozmiar_wskazywanej(&[1_u16, 2][..]), 4);
}
~~~

Referencja do DST jest zwykle fat pointerem: niesie adres oraz metadane,
np. długość slice lub wskaźnik do vtable. Nie polegaj na szczegółach layoutu,
jeśli Reference nie daje gwarancji dla danego zastosowania.

## Trait objects

~~~rust
trait Pole {
    fn pole(&self) -> f64;
}

struct Kwadrat(f64);
struct Kolo(f64);

impl Pole for Kwadrat { fn pole(&self) -> f64 { self.0 * self.0 } }
impl Pole for Kolo { fn pole(&self) -> f64 { std::f64::consts::PI * self.0 * self.0 } }

fn suma(figury: &[Box<dyn Pole>]) -> f64 {
    figury.iter().map(|f| f.pole()).sum()
}

fn main() {
    let figury: Vec<Box<dyn Pole>> = vec![Box::new(Kwadrat(2.0)), Box::new(Kolo(1.0))];
    assert!(suma(&figury) > 7.0);
}
~~~

`dyn Pole` umożliwia heterogeniczną kolekcję i dynamic dispatch. Koszt to
indirection, wywołanie przez vtable i zwykle utrudniony inline. Zaletą jest
mniejszy kod oraz wybór implementacji w runtime.

Trait musi być dyn-compatible: między innymi metody wywoływane przez obiekt
nie mogą wymagać `Self: Sized` ani mieć własnych parametrów generycznych.
Termin „object safety” bywa używany historycznie; Reference mówi o dyn
compatibility.

## Reguły — podobny wynik nie oznacza tego samego kontraktu

`From<T>` konsumuje wejście i tworzy nową reprezentację. Dla `String::from(&str)` oznacza to alokację posiadanego bufora, mimo że konwersja nie zwraca błędu. „Nieomylna” nie znaczy „darmowa”. `TryFrom` oddziela walidację od wyniku i pozwala klientowi podjąć decyzję przy odmowie. Implementując `From<T> for U`, otrzymujesz odpowiedni `Into<U>` przez blanket impl; ręczne dodawanie obu zwykle koliduje.

`AsRef<T>` służy taniemu uzyskaniu widoku. `Borrow<T>` obiecuje ponadto zgodną semantykę porównania, porządku i haszowania dla typu posiadanego oraz pożyczonego, gdy te operacje są zdefiniowane. Dlatego klucz porównywany bez uwzględnienia wielkości liter nie powinien implementować `Borrow<str>` z normalnym, czułym na wielkość liter `str`. Sam dostęp do bajtów nie wystarcza do tego kontraktu.

~~~rust
#[derive(Debug, PartialEq)]
struct Procent(u8);
impl TryFrom<u16> for Procent {
    type Error = &'static str;
    fn try_from(n: u16) -> Result<Self, Self::Error> {
        if n <= 100 { Ok(Self(n as u8)) } else { Err("poza 0..=100") }
    }
}
fn main() {
    assert_eq!(Procent::try_from(100), Ok(Procent(100)));
    assert_eq!(Procent::try_from(101), Err("poza 0..=100"));
}
~~~

Rzutowanie w gałęzi sukcesu jest bezstratne dzięki wcześniejszemu dowodowi zakresu. Nie wolno przenieść go przed walidację: `356_u16 as u8` dałoby `100` i błędnie przeszło kontrolę domenową. Najpierw waliduj pełną reprezentację wejścia, potem buduj węższy typ.

## Sized i granice koercji

`?Sized` znaczy „może nie mieć rozmiaru znanego statycznie”, a nie „musi być niesized”. Funkcja `fn f<T: ?Sized>(x: &T)` działa z `u32`, `str` i slice, jeśli jej ciało korzysta tylko z operacji dostępnych dla tych typów. Parametr przez wartość zwykle wymaga `Sized`, bo jego przechowanie i przekazanie wymaga ustalenia rozmiaru.

Koercja zachodzi w wybranym miejscu, na przykład przy przypisaniu do `&dyn Trait` albo przekazaniu argumentu o znanym oczekiwanym typie. Nie przenika dowolnie przez kontenery: `Vec<Box<Kwadrat>>` nie zamienia się automatycznie w `Vec<Box<dyn Pole>>`. Możesz ustalić oczekiwany typ już przy konstrukcji albo przemapować elementy. W tym drugim przypadku trzeba zbudować nową reprezentację kolekcji, nawet jeśli poszczególne boxy zachowują swoje alokacje.

`dyn Trait` wymazuje konkretny typ, zachowując określony interfejs i dodatkowe bounds. `&dyn Trait` nie wymaga osobnej alokacji; `Box<dyn Trait>` posiada obiekt na stercie z wyjątkami dotyczącymi zerowego rozmiaru. Nie traktuj „dwóch słów” ani układu vtable jako uniwersalnego formatu ABI.

## `Cow`: widok albo posiadana reprezentacja

`Cow<'a, str>` jest enumem z wariantami `Borrowed(&'a str)` i `Owned(String)`. Odczyt przez `as_ref` lub dereferencję nie wymaga zamiany widoku na właściciela. Dzięki temu funkcja normalizująca tekst może oddać wejściową pożyczkę, gdy zmiany nie są potrzebne, i własny bufor tylko dla zmienionego wyniku. Zależność od `'a` nadal obowiązuje dla wariantu pożyczonego.

`to_mut()` zapewnia mutowalny dostęp do posiadanej reprezentacji: przy `Borrowed` najpierw tworzy własną kopię, a przy `Owned` korzysta z istniejącej wartości. Samo wywołanie `to_mut` może więc skopiować dane, nawet jeżeli późniejsza operacja niczego nie zmieni. Nie mutuje źródłowego tekstu.

~~~rust
use std::borrow::Cow;
fn main() {
    let zrodlo = String::from("rust");
    let mut tekst: Cow<'_, str> = Cow::Borrowed(&zrodlo);
    assert!(matches!(&tekst, Cow::Borrowed(_)));
    tekst.to_mut().make_ascii_uppercase();
    assert!(matches!(&tekst, Cow::Owned(_)));
    tekst.to_mut().push('!');
    assert_eq!(zrodlo, "rust");
    assert_eq!(tekst.into_owned(), "RUST!");
}
~~~

`into_owned` konsumuje enum: przenosi istniejący `String` albo kopiuje wariant pożyczony. `Cow` nie oznacza współwłasności z licznikiem referencji jak `Rc`; jest wyborem reprezentacji według potrzeby kopiowania. Źródło: [Cow](https://doc.rust-lang.org/std/borrow/enum.Cow.html), sprawdzone 11 listopada 2026 r.

## Diagnostyka kompilatora

`?Sized` trzeba dodać świadomie. Domyślne `T: Sized` wyklucza `str`, mimo że parametr funkcji jest referencją.

~~~compile_fail
fn dlugosc_typu<T>(x: &T) -> usize { std::mem::size_of_val(x) }
fn main() { let _ = dlugosc_typu("abc"); }
~~~

Naprawa to `T: ?Sized`, ponieważ `size_of_val` potrafi skorzystać z metadanych. Jeśli ciało używa `size_of::<T>()`, samo rozluźnienie boundu nie wystarczy. Przy błędzie konwersji kontenera sprawdź miejsce koercji, zamiast używać `transmute`: legalna konwersja wskaźnika nie dowodzi zgodności layoutu dwóch typów kolekcji.

## Praktyka produkcyjna

W publicznym API unikaj zbyt wielu konkurencyjnych konwersji generycznych. Parametr `impl Into<String>` jest wygodny przy przechowywaniu nazwy, lecz dla samego odczytu `&str` jest prostszy i nie sugeruje alokacji. `impl AsRef<Path>` ma sens na granicy ścieżek, a wewnętrzna funkcja może pracować już na `&Path`.

Wybierając trait object, nazwij powód: heterogeniczna kolekcja, wybór implementacji w runtime albo ograniczenie monomorfizacji. Jeśli zbiór wariantów jest mały i zamknięty, enum może dać pełne sprawdzenie przypadków oraz brak indywidualnych alokacji. Koszt mierz dla całej operacji, łącznie z układem pamięci i częstotliwością wywołań.

## Sprawdź, czy rozumiesz

1. Dlaczego nie każda implementacja `AsRef<str>` powinna być także `Borrow<str>`?
2. Czy `T: ?Sized` wyklucza typy o znanym rozmiarze?
3. Dlaczego `Vec<Box<T>>` nie przechodzi automatycznie do `Vec<Box<dyn Trait>>`?

## Ćwiczenia

- `A20-1` — podstawowe: zdefiniuj `Procent` z `TryFrom<u16>` i przetestuj 0, 100, 101 oraz 356 [Rozwiązanie](../rozwiazania/05_generics_traits_i_system_typow/03_konwersje_dst_i_trait_objects.md#a20-1).
- `A20-2` — praktyczne: napisz `bajty<T: AsRef<[u8]>>(T) -> usize` i pokaż tablicę, slice oraz wektor [Rozwiązanie](../rozwiazania/05_generics_traits_i_system_typow/03_konwersje_dst_i_trait_objects.md#a20-2).
- `A20-3` — pogłębione: użyj `&dyn Display` do wyświetlenia dwóch różnych lokalnych typów bez `Box`; porównaj kontrakt z wersją generyczną [Rozwiązanie](../rozwiazania/05_generics_traits_i_system_typow/03_konwersje_dst_i_trait_objects.md#a20-3).

## Źródła i zakres stabilności

Koercje: [Reference: type coercions](https://doc.rust-lang.org/reference/type-coercions.html). Równoważność pożyczonego klucza: [Borrow](https://doc.rust-lang.org/std/borrow/trait.Borrow.html). Rozluźnienie `Sized`: [DST](https://doc.rust-lang.org/reference/dynamically-sized-types.html).

## Powiązane tematy

- [Traits i associated items](02_traits_i_associated_items.md)
- [Dyn compatibility, vtables i dispatch](../05_generics_traits_i_system_typow/06_dyn_compatibility_vtables_i_dispatch.md)
- [Projektowanie publicznego API](../14_idiomy_wzorce_i_architektura/03_projektowanie_api_i_semver.md)
