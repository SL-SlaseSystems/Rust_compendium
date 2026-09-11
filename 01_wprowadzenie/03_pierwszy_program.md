[← Spis treści](../README.md)
<!-- status: expanded -->

# Pierwszy program

> Stan opisu: Rust 1.98.1, Edition 2024, zweryfikowany 10 września 2026 r. Przykłady wykonano lokalnie przez Rust 1.90.0, więc nie są deklaracją testu na 1.98.1.

## Cele

Po tym rozdziale potrafisz:

- wskazać crate root i źródło nazw użytych przez program;
- odczytać różnicę między instrukcją a wyrażeniem oraz wpływ średnika na typ;
- zaprojektować `main` zwracające wynik i diagnozować podstawowe błędy kompilacji.

## Model programu i crate root

Crate root jest plikiem, od którego kompilator buduje pojedynczy crate. W pakiecie Cargo `src/main.rs` jest rootem binarnego crate'a, a `src/lib.rs` — rootem crate'a bibliotecznego; pakiet może mieć oba. Przy `rustc plik.rs` podany plik jest rootem crate'a bez konwencji Cargo. Prelude biblioteki standardowej wprowadza część najczęstszych nazw, jak `Option` i `Result`, lecz nie wszystkie ścieżki: `std::fs::read_to_string` pozostaje jawne albo wymaga `use`.

`fn main` jest punktem wejścia binarium. Najczęstsze wyniki to `()` i `Result<(), E>`; ich przekształcenie w status procesu opisuje `std::process::Termination`. `Result` wypisuje błąd i zwraca status niepowodzenia zgodnie z implementacją `Termination`, ale szczegóły runtime'u nie są uniwersalnym kontraktem każdego środowiska. Zobacz [Termination](https://doc.rust-lang.org/std/process/trait.Termination.html) i [The Book: Hello, world](https://doc.rust-lang.org/book/ch01-02-hello-world.html).

## Reguły: wyrażenia, makra i formatowanie

Instrukcja wykonuje działanie, a wyrażenie oblicza wartość. Średnik tworzy instrukcję wyrażeniową i odrzuca wartość wyrażenia; blok bez końcowego wyrażenia ma wartość `()`. `println!` jest makrem, nie funkcją: `!` uruchamia rozwinięcie makra. Literał formatu jest sprawdzany podczas kompilacji; `{nazwa}` przechwytuje nazwę z zakresu, `{}` używa `Display`, a `{:?}` — `Debug`.

~~~rust
fn podatek(cena: i32) -> i32 {
    let stawka = 23;
    cena * stawka / 100
}

fn main() {
    let produkt = "książka";
    let cena = 100;
    println!("{produkt}: podatek = {}", podatek(cena));
    assert_eq!(podatek(cena), 23);
}
~~~

`main -> Result` pozwala użyć `?` i przekazać błąd do granicy procesu.

~~~rust
use std::error::Error;

fn liczba(tekst: &str) -> Result<u32, Box<dyn Error>> {
    Ok(tekst.parse()?)
}

fn main() -> Result<(), Box<dyn Error>> {
    assert_eq!(liczba("42")?, 42);
    Ok(())
}
~~~

## Uproszczony model kompilacji

To model mentalny aktualnej implementacji, nie stabilny interfejs `rustc`: parsowanie buduje `AST`; rozwijanie makr, rozwiązywanie nazw i wczesne linty przygotowują program; `HIR` służy inferencji, type checking i doborowi `trait`; po nim `THIR` wspiera wzorce oraz wyczerpalność, a konstrukcja `MIR`; borrow checking działa na `MIR`. Potem następują codegen, zwykle przez LLVM, i linkowanie. [Rustc Dev Guide](https://rustc-dev-guide.rust-lang.org/overview.html) opisuje szczegóły.

## Diagnostyka kompilatora

Średnik odrzuca wartość `42`; blok bez końcowego wyrażenia ocenia się do `()`, nie `i32`. Usuń go, gdy wartość ma być zwrócona.

~~~compile_fail
fn odpowiedz() -> i32 {
    42;
}
~~~

Nierozpoznane makro zwykle oznacza literówkę, brak importu albo brak zależności, a nie błąd linkera. Kompilator wskazuje nazwę i zakres rozwiązywania nazw.

~~~compile_fail
fn main() {
    printlin!("literówka");
}
~~~

## Praktyka produkcyjna

W binarium traktuj `main` jako cienką granicę: zbuduj konfigurację, wywołaj logikę zwracającą konkretny `Result`, zdecyduj o komunikacie i statusie procesu. Biblioteka nie powinna kończyć procesu ani ukrywać błędów w `println!`. Używaj jawnych importów w granicach modułów i uruchamiaj `cargo check` wcześnie; jest szybszym sygnałem niż czekanie na linkowanie. [The Book: errors](https://doc.rust-lang.org/book/ch09-00-error-handling.html) rozróżnia błędy odzyskiwalne od `panic!`.

## Sprawdź, czy rozumiesz

1. Kiedy `src/main.rs` i `src/lib.rs` są różnymi crate rootami?
2. Dlaczego końcowy średnik może unieważnić sygnaturę funkcji?
3. Co zyskuje program przez `main -> Result`?

## Ćwiczenia

- `W03-1` — podstawowe: przewidź wynik `let x = { 2 + 3 }; println!("{x}");` i wyjaśnij rolę bloku. Porównaj z [rozwiązaniem](../rozwiazania/01_wprowadzenie/03_pierwszy_program.md#w03-1).
- `W03-2` — praktyczne: napraw funkcję `fn f() -> String { String::from("ok"); }` bez zmiany jej kontraktu. Porównaj z [rozwiązaniem](../rozwiazania/01_wprowadzenie/03_pierwszy_program.md#w03-2).
- `W03-3` — pogłębione: napisz `main -> Result`, która parsuje argument tekstowy i propaguje błąd bez `unwrap`. Porównaj z [rozwiązaniem](../rozwiazania/01_wprowadzenie/03_pierwszy_program.md#w03-3).

## Powiązane tematy

- [Instalacja i toolchain](02_instalacja_i_toolchain.md)
- [Funkcje, wyrażenia i instrukcje](../02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md)
- [`Option` i `Result`](../06_bledy/01_option_i_result.md)
- [Cargo w praktyce](04_cargo_w_praktyce.md)
