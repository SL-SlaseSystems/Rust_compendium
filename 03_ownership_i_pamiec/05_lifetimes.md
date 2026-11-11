[← Spis treści](../README.md)
<!-- status: expanded -->

# Lifetimes

> Przykłady: **stable**, Rust 1.90.0, Edition 2024. Źródła sprawdzono 11 listopada 2026 r.

## Cele

Po tym rozdziale potrafisz:

- powiązać czas życia wyniku z właściwym wejściem zamiast z wszystkimi argumentami;
- rozróżnić `T: 'static` od `&'static T`;
- ustalić, kiedy pożyczający model danych warto zastąpić posiadanym;

## Model — relacja ważności, nie licznik czasu


Lifetime opisuje relację ważności referencji. Adnotacja nie wydłuża życia
wartości i nie zmienia kodu wykonawczego; pomaga kompilatorowi powiązać
referencje wejściowe z wyjściową.

## Po co adnotacja

Gdy funkcja zwraca jedną z dwóch referencji, kompilator potrzebuje wspólnego
parametru:

~~~rust
fn dluzszy<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() >= y.len() { x } else { y }
}

fn main() {
    let a = String::from("dłuższy");
    let b = "krótki";
    assert_eq!(dluzszy(&a, b), "dłuższy");
}
~~~

`'a` znaczy: wynik nie może być używany dłużej niż część wspólna okresów
ważności `x` i `y`. Nie znaczy, że oba argumenty żyją identycznie długo.

~~~compile_fail
fn dluzszy<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() >= y.len() { x } else { y }
}

fn main() {
    let zewnetrzny = String::from("zewnętrzny");
    let wynik;
    {
        let lokalny = String::from("lokalny");
        wynik = dluzszy(&zewnetrzny, &lokalny);
    }
    println!("{wynik}");
}
~~~

## Elision

W typowych sygnaturach lifetimes są pomijane według reguł elision. Każdy
parametr referencyjny dostaje własny lifetime; jeśli jest dokładnie jeden,
przypisywany jest wynikowi. W metodzie preferowany jest lifetime `self`.

~~~rust
fn pierwszy(tekst: &str) -> &str {
    tekst.split_whitespace().next().unwrap_or("")
}

fn main() {
    assert_eq!(pierwszy("Rust jest szybki"), "Rust");
}
~~~

Jawne adnotacje stosuj, gdy relacja nie wynika z reguł, a nie wszędzie.

## Referencje w strukturach

~~~rust
#[derive(Debug)]
struct Fragment<'a> {
    tekst: &'a str,
}

impl<'a> Fragment<'a> {
    fn tekst(&self) -> &str {
        self.tekst
    }
}

fn main() {
    let dokument = String::from("sekcja");
    let fragment = Fragment { tekst: &dokument };
    assert_eq!(fragment.tekst(), "sekcja");
}
~~~

Struktura nie może przeżyć danych, które pożycza. Gdy model własności staje
się zbyt splątany, rozważ posiadanie `String`, `Cow<'a, str>` lub
przeprojektowanie granicy zamiast dodawania kolejnych parametrów.

## `'static`

`&'static T` jest referencją ważną do końca programu, np. literałem.
Bound `T: 'static` nie mówi, że wartość będzie żyła wiecznie; mówi, że typ
nie zawiera referencji krótszych niż `'static`. Posiadany `String` spełnia
`'static`, chociaż można go zniszczyć natychmiast.

## Bounds

`T: 'a` oznacza, że wszystkie referencje wewnątrz `T` są ważne co najmniej
przez `'a`. `'b: 'a` znaczy „`'b` przeżywa `'a`”. Zaawansowane relacje łączą
się z variance i drop checking.

## Reguły — sygnatura jest dowodem dla klienta

Lifetime nie jest datą wygaśnięcia ani czasem mierzonym zegarem. Reprezentuje obszar programu, w którym referencja może być używana. Kompilator analizuje ciało funkcji zgodnie z zadeklarowanymi relacjami, a klient ufa sygnaturze bez zaglądania do implementacji. Dlatego zbyt mocne powiązanie argumentów ogranicza poprawne użycia nawet wtedy, gdy funkcja zawsze zwraca tylko jeden z nich.

~~~rust
fn pierwszy<'a>(tekst: &'a str, separator: &str) -> &'a str {
    tekst.split(separator).next().unwrap_or(tekst)
}
fn main() {
    let dokument = String::from("Rust::język");
    let wynik;
    {
        let separator = String::from("::");
        wynik = pierwszy(&dokument, &separator);
    }
    assert_eq!(wynik, "Rust");
}
~~~

Wyjście zależy od `tekst`, lecz nie od długości życia `separator`. Parser używa separatora tylko podczas wywołania. Nadanie obu argumentom tego samego `'a` bez potrzeby mogłoby uniemożliwić późniejsze użycie `wynik`. Dobieraj relacje według pochodzenia zwracanych danych. Gdy zwracasz jedną z dwóch referencji, wspólne ograniczenie jest potrzebne; gdy zwracasz zawsze pierwszą, osobne lifetimes są dokładniejsze.

W metodzie `fn tekst(&self) -> &str` reguła elision wiąże wynik z pożyczką `self`. Jeżeli struktura przechowuje `&'a str` i chcesz udostępnić pełną ważność źródła niezależnie od chwilowej pożyczki struktury, możesz jawnie zwracać `&'a str`. To jest mocniejsza obietnica, poprawna tylko wtedy, gdy dane rzeczywiście pochodzą z pola z takim lifetime'em, a nie z posiadanego bufora niszczonego ze strukturą.

Bounds `T: 'a` ograniczają referencje występujące w `T`. Posiadany `String` spełnia `T: 'static`, choć może zostać zniszczony zaraz po wywołaniu. Natomiast `&'static String` żąda samej referencji ważnej przez cały program. Zmiana boundu na `'static` nie jest uniwersalną naprawą błędu: często wymusza przeprojektowanie właściciela albo niepotrzebny wyciek przez `Box::leak`.

Samoodwołujące się struktury są odrębnym problemem. Zwykłe `struct Dane<'a> { bufor: String, fragment: &'a str }` nie dowodzi, że `fragment` wskazuje na własny bufor ani że przeniesienie struktury jest poprawne. Prosty model przechowuje zakresy bajtów i tworzy widok dopiero w metodzie pożyczającej `self`.

## Diagnostyka kompilatora

Brak informacji, które wejście jest źródłem wyniku, daje E0106. Ten przykład odrzuca się niezależnie od tego, że ciało zwraca tylko `x`: elision nie wyprowadza takiej relacji z implementacji.

~~~compile_fail
fn wybierz(x: &str, y: &str) -> &str {
    let _ = y;
    x
}
fn main() {}
~~~

Poprawna sygnatura to `fn wybierz<'a>(x: &'a str, y: &str) -> &'a str`. W E0597 z wcześniejszego przykładu `dluzszy` problem jest inny: relacja jest znana, ale właściciel jednego wejścia znika za wcześnie. Rozwiązaniem może być ograniczenie użycia wyniku do bloku albo utworzenie posiadanego wyniku. Żadna etykieta lifetime nie wskrzesi zniszczonych danych.

## Praktyka produkcyjna

Pożyczające modele rekordów dobrze służą analizie jednego dokumentu, gdy bufor wejściowy żyje przez całą operację. W magazynie, kolejce i zadaniu asynchronicznym właściciel często zmienia się niezależnie; posiadane `String`, `Vec` lub `Arc` mogą wyrazić kontrakt prościej. `Cow<'a, str>` pozwala odroczyć kopiowanie do chwili wymagającej własności albo mutacji.

Unikaj przepisywania jednego `'a` na wszystkie pola i metody bez analizy zależności. Szczególnie `&'a mut self` w `impl<'a>` potrafi zablokować obiekt na cały długi lifetime danych. Zwykłe `&mut self` daje krótszą pożyczkę dla pojedynczego wywołania. Najpierw ustal właściciela, następnie wynikowy widok, na końcu niezbędne adnotacje.

## Sprawdź, czy rozumiesz

1. Czy lifetime może sprawić, że lokalny `String` nie zostanie zniszczony?
2. Dlaczego wynik funkcji dzielącej tekst nie musi zależeć od lifetime separatora?
3. Co zmienia `fn tekst(&self) -> &'a str` wobec wyniku z elision?

## Ćwiczenia

- `A14-1` — podstawowe: napisz `pierwszy(&str) -> &str` zwracające pierwsze słowo i sprawdź pusty tekst [Rozwiązanie](../rozwiazania/03_ownership_i_pamiec/05_lifetimes.md#a14-1).
- `A14-2` — praktyczne: napisz funkcję z dwoma referencjami, której wynik zależy wyłącznie od pierwszej; użyj wyniku po zniszczeniu drugiego argumentu [Rozwiązanie](../rozwiazania/03_ownership_i_pamiec/05_lifetimes.md#a14-2).
- `A14-3` — pogłębione: zbuduj strukturę posiadającą `String` i zakres bajtów; konstruktor ma walidować UTF-8, a metoda zwracać widok związany z `&self` [Rozwiązanie](../rozwiazania/03_ownership_i_pamiec/05_lifetimes.md#a14-3).

## Źródła i zakres stabilności

Elision i domyślne bounds obiektów: [Reference: lifetime elision](https://doc.rust-lang.org/reference/lifetime-elision.html). Relacje outlives: [Reference: trait and lifetime bounds](https://doc.rust-lang.org/reference/trait-bounds.html#lifetime-bounds).

## Powiązane tematy

- [Referencje i borrowing](03_referencje_i_borrowing.md)
- [HRTB, GAT i `impl Trait`](../05_generics_traits_i_system_typow/05_hrtb_gat_rpit_i_impl_trait.md)
- [Variance i drop check](../05_generics_traits_i_system_typow/04_variance_subtyping_i_dropck.md)
