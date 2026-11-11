[← Spis treści](../README.md)
<!-- status: expanded -->

# Dyn compatibility, vtables i dispatch

> Przykłady: **stable**, Rust 1.90.0, Edition 2024. Źródła sprawdzono 11 listopada 2026 r.

## Cele

Po tym rozdziale potrafisz:

- sprawdzić, które metody można wywołać przez trait object;
- oddzielić część generyczną z `where Self: Sized` od interfejsu dynamicznego;
- zadeklarować lifetime i auto traits obiektu zgodnie z jego użyciem;

## Model — wymazany typ, zachowany interfejs


Trait object `dyn Trait` umożliwia wywołanie zachowania typu wybranego w
runtime. Jest DST, więc używa się go przez `&dyn Trait`, `Box<dyn Trait>`,
`Arc<dyn Trait>` lub inny pointer.

## Dynamic dispatch

~~~rust
trait Render {
    fn render(&self) -> String;
}

struct Tekst(&'static str);
struct Liczba(i32);

impl Render for Tekst {
    fn render(&self) -> String { self.0.into() }
}
impl Render for Liczba {
    fn render(&self) -> String { self.0.to_string() }
}

fn polacz(elementy: &[Box<dyn Render>]) -> String {
    elementy
        .iter()
        .map(|e| e.render())
        .collect::<Vec<_>>()
        .join(",")
}

fn main() {
    let x: Vec<Box<dyn Render>> =
        vec![Box::new(Tekst("a")), Box::new(Liczba(2))];
    assert_eq!(polacz(&x), "a,2");
}
~~~

Konceptualnie fat pointer zawiera data pointer i vtable pointer. Vtable ma
informacje potrzebne do dispatch i zarządzania wartością, lecz jej dokładny
layout nie jest stabilnym ABI. Nie serializuj ani nie przekazuj vtable przez
FFI.

## Warunki dyn compatibility

W uproszczeniu trait:

- nie może wymagać `Self: Sized`;
- nie ma associated constants;
- nie ma GAT wymagających określenia w obiekcie;
- dispatchowalna metoda nie ma parametrów typów;
- metoda nie używa `Self` poza receiverem;
- receiver ma wspieraną formę, np. `&self`, `&mut self`, `Box<Self>`,
  `Arc<Self>` lub odpowiednie `Pin`;
- metoda nie zwraca opaque `impl Trait` ani `async fn`, jeśli ma być
  dispatchowalna.

Metodę niedostępną przez obiekt można oznaczyć `where Self: Sized`:

~~~rust
trait Nazwany {
    fn nazwa(&self) -> &str;

    fn opakuj(self) -> Box<Self>
    where
        Self: Sized,
    {
        Box::new(self)
    }
}

impl Nazwany for String {
    fn nazwa(&self) -> &str { self }
}

fn main() {
    let x: Box<dyn Nazwany> = String::from("Rust").opakuj();
    assert_eq!(x.nazwa(), "Rust");
}
~~~

## Associated types

Trait object musi określić niegeneryczne associated types potrzebne do pełnego
typu:

~~~rust
fn pierwszy(iter: &mut dyn Iterator<Item = i32>) -> Option<i32> {
    iter.next()
}

fn main() {
    let mut i = vec![3, 4].into_iter();
    assert_eq!(pierwszy(&mut i), Some(3));
}
~~~

## Lifetimes

`Box<dyn Trait>` w wielu miejscach domyślnie oznacza `Box<dyn Trait + 'static>`.
Nie znaczy to, że box żyje wiecznie; jego konkretny typ nie może zawierać
krótszych pożyczek. Jawne `Box<dyn Trait + 'a>` pozwala przechować obiekt
pożyczający.

Auto traits i bounds są częścią obiektu: `dyn Trait + Send + Sync` różni się
od `dyn Trait`. W wielowątkowym API deklaruj je w granicy.

## Upcasting i downcasting

Trait upcasting z `dyn SubTrait` do `dyn SuperTrait` jest wspierany w
stabilnym Rust dla odpowiednich coercions, ale nie jest downcastingiem.
Downcasting zwykle opiera się na `Any`, wymaga `'static` i ujawnia potrzebę
znajomości konkretnego typu. Częste downcasty sugerują zły kontrakt traitu.

## Static czy dynamic

Static dispatch umożliwia inline i brak vtable, ale monomorfizuje kod.
Dynamic dispatch zmniejsza liczbę wariantów kodu, umożliwia heterogeniczne
kolekcje i plugin-like wybór, lecz ma indirection. Koszt mierz w kontekście;
alokacja `Box` nie jest wymagana dla `&dyn Trait`.

## Reguły — czego potrzebuje klient nieznający Self

Dynamiczny klient zna metody traitu i ich kontrakty, lecz nie zna rozmiaru ani nazwy konkretnego `Self`. Metoda `fn skopiuj(&self) -> Self` wymagałaby zwrócenia nieznanej wartości przez wartość. Generyczna metoda `fn zapisz<T>(&self, x: T)` potrzebowałaby otwartego zbioru specjalizacji. Zwykła tablica metod obiektu nie rozwiązuje tych potrzeb. Dlatego dyn compatibility ogranicza interfejs wywoływany dynamicznie.

Można zachować takie metody dla użytkowników znających typ konkretny przez `where Self: Sized`. Nie wystarczy jednak dodać `Self: Sized` do samego traitu: to wykluczyłoby utworzenie każdego jego obiektu. Projektuj mały rdzeń dynamiczny oraz opcjonalne funkcje pomocnicze wymagające rozmiaru. Typowym przykładem jest konstruktor skojarzony niedostępny przez `dyn`.

Parametry lifetime w dispatchowalnej metodzie są dopuszczalne, inaczej niż ogólne parametry typu. Zwracanie `&str` powiązanego z `&self` działa, bo rozmiar referencji i relacja lifetimes są znane. Associated type trzeba ustalić, na przykład `dyn Iterator<Item = u8>`, jeśli jest częścią dostępnego interfejsu. GAT dostępne przez dynamiczny obiekt podlegają dalej ograniczeniom; umieszczenie `where Self: Sized` może wyłączyć dany element z powierzchni obiektu.

## Pożyczający obiekt i jego granica życia

~~~rust
trait Nazwa { fn nazwa(&self) -> &str; }
struct Widok<'a>(&'a str);
impl Nazwa for Widok<'_> { fn nazwa(&self) -> &str { self.0 } }
fn opakuj<'a>(s: &'a str) -> Box<dyn Nazwa + 'a> {
    Box::new(Widok(s))
}
fn main() {
    let tekst = String::from("pożyczony");
    let obiekt = opakuj(&tekst);
    assert_eq!(obiekt.nazwa(), "pożyczony");
}
~~~

Box posiada `Widok`, ale nie posiada bajtów `tekst`. Jawne `+ 'a` pozwala wyrazić tę zależność, a nie przedłuża ważności danych. Pożyczka `&self` podczas wywołania metody może być krótsza niż `'a`. W `&'a dyn Trait` domyślne ograniczenie obiektu często wynika z zewnętrznej referencji; reguły domyślnych lifetime obiektów nie są identyczne ze zwykłym elision wyników funkcji.

`dyn Trait + Send` obiecuje, że konkretny obiekt można przenieść do innego wątku; `+ Sync` umożliwia właściwy współdzielony dostęp. Zwykły `Box<dyn Trait>` nie nabywa tych zdolności na podstawie tego, że jedna aktualna implementacja je ma. Po wymazaniu typu klient zachowuje wyłącznie zadeklarowany kontrakt.

Upcasting przechodzi od bogatszego traitu do jego supertraitu i może zmienić metadane obiektu. Nie jest rzutowaniem do konkretnej struktury. `Any` daje odrębne, sprawdzane downcasting dla typów spełniających `'static`; nie służy do automatycznego odzyskiwania dowolnej pożyczającej implementacji.

## Diagnostyka kompilatora

Generyczna metoda bez wyłączenia `Self: Sized` uniemożliwia utworzenie tego trait object. Kompilator zgłasza E0038 i wskazuje problematyczną metodę.

~~~compile_fail
trait Eksport {
    fn zapisz<T>(&self, wartosc: T);
}
fn uzyj(_: &dyn Eksport) {}
fn main() {}
~~~

Naprawa zależy od potrzeb: zastąp parametr wspólnym typem wejściowym, wydziel metodę generyczną do innego traitu albo dodaj `where Self: Sized` i zaakceptuj brak wywołania przez `dyn`. Wymuszenie `Box` nie naprawia dyn compatibility: zmienia własność wskaźnika, nie dostępność metod.

## Praktyka produkcyjna

Dynamic dispatch bywa opłacalny na granicy dużych operacji, gdzie koszt jednego skoku pośredniego jest mały wobec I/O lub obliczeń. W bardzo krótkiej pętli po małych elementach utrata inliningu i rozrzucenie danych po osobnych alokacjach mogą mieć większe znaczenie. Pomiar powinien obejmować także konstrukcję kolekcji, pamięć oraz rozmiar binarium.

Nie projektuj wtyczek binarnych jako wymiany surowych `dyn Trait` między niezależnie budowanymi bibliotekami. Layout vtable i ABI Rusta nie stanowią ogólnego stabilnego kontraktu FFI. Wtyczka ładowana dynamicznie potrzebuje jawnej granicy ABI, właściciela alokacji i reguł zgodności wersji. Trait object pozostaje wygodnym interfejsem wewnątrz kontrolowanego procesu kompilacji.

## Sprawdź, czy rozumiesz

1. Dlaczego `Box` nie naprawia traitu z generyczną metodą?
2. Czy metoda z parametrem lifetime jest automatycznie niedostępna przez `dyn`?
3. Czego `Box<dyn Trait + 'a>` jest właścicielem, gdy implementacja pożycza tekst?

## Ćwiczenia

- `A23-1` — podstawowe: utwórz `&dyn Display` wskazujące lokalną liczbę i wywołaj formatowanie bez `Box` [Rozwiązanie](../rozwiazania/05_generics_traits_i_system_typow/06_dyn_compatibility_vtables_i_dispatch.md#a23-1).
- `A23-2` — praktyczne: zaprojektuj trait z metodą `nazwa(&self)` i konstruktorem `nowy() -> Self where Self: Sized`; wywołaj odczyt przez `dyn` [Rozwiązanie](../rozwiazania/05_generics_traits_i_system_typow/06_dyn_compatibility_vtables_i_dispatch.md#a23-2).
- `A23-3` — pogłębione: utwórz `Podpis: Nazwa`, wykonaj upcasting z `&dyn Podpis` do `&dyn Nazwa`, a następnie porównaj to z downcastingiem przez `Any` [Rozwiązanie](../rozwiazania/05_generics_traits_i_system_typow/06_dyn_compatibility_vtables_i_dispatch.md#a23-3).

## Źródła i zakres stabilności

Dokładna lista warunków: [Reference: dyn compatibility](https://doc.rust-lang.org/reference/items/traits.html#dyn-compatibility). Lifetime obiektów: [Reference: lifetime elision](https://doc.rust-lang.org/reference/lifetime-elision.html#default-trait-object-lifetimes). Sprawdzany downcasting: [Any](https://doc.rust-lang.org/std/any/trait.Any.html).

## Powiązane tematy

- [Konwersje, DST i trait objects](../05_generics_traits_i_system_typow/03_konwersje_dst_i_trait_objects.md)
- [HRTB, GAT i RPIT](05_hrtb_gat_rpit_i_impl_trait.md)
- [Monomorfizacja i optymalizacja](../20_wydajnosc_i_optymalizacja/03_monomorfizacja_mir_llvm_i_optymalizacja.md)
