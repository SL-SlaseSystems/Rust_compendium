[← Spis treści](../README.md)

# Lifetimes

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

## Powiązane tematy

- [Referencje i borrowing](03_referencje_i_borrowing.md)
- [HRTB, GAT i `impl Trait`](../zaawansowane/05_hrtb_gat_rpit_i_impl_trait.md)
- [Variance i drop check](../zaawansowane/04_variance_subtyping_i_dropck.md)
