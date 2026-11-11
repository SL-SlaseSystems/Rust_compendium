[← Spis treści](../../README.md)

# Rozwiązania: Makra proceduralne

[Rozdział źródłowy](../../12_makra/03_makra_proceduralne.md).

## B26-1

`#[derive(Koduj)]` dodaje implementację i pozostawia strukturę. `#[sledz] fn f()` jest makrem atrybutowym, które ma zwrócić zachowaną lub zmienioną funkcję. `sql!(...)` to makro function-like zastępujące wywołanie tokenami. Wybór określa kontrakt zachowania oryginalnego itemu, a nie tylko wygląd składni.

## B26-2

Rozwiązanie ma dwa pakiety. Bloki są plikami projektu Cargo, więc oznaczono je `text`. Ten wariant sprawdzono osobno przez `cargo run --offline` i negatywne `cargo check --offline`, na Rust 1.90, Edition 2024, 11 listopada 2026. Nie wymaga zewnętrznych crate’ów.

Plik `Cargo.toml` w korzeniu:

~~~text
[workspace]
members = ["macro", "app"]
resolver = "3"
~~~

Plik `macro/Cargo.toml`:

~~~text
[package]
name = "odpowiedz_macro"
version = "0.1.0"
edition = "2024"

[lib]
proc-macro = true
~~~

Plik `macro/src/lib.rs`:

~~~text
use proc_macro::TokenStream;

#[proc_macro]
pub fn odpowiedz(input: TokenStream) -> TokenStream {
    if !input.is_empty() {
        return "compile_error!(\"odpowiedz! nie przyjmuje argumentów\")"
            .parse().unwrap();
    }
    "42_u32".parse().unwrap()
}
~~~

Plik `app/Cargo.toml`; alias od razu sprawdza zmianę nazwy zależności:

~~~text
[package]
name = "konsument"
version = "0.1.0"
edition = "2024"

[dependencies]
makro = { package = "odpowiedz_macro", path = "../macro" }
~~~

Plik `app/src/main.rs`:

~~~text
fn main() {
    let wynik: u32 = makro::odpowiedz!();
    assert_eq!(wynik, 42);
}
~~~

`cargo run --offline -p konsument` kończy się sukcesem. Po zamianie wywołania na `makro::odpowiedz!(1)` polecenie `cargo check --offline -p konsument` ma zostać odrzucone komunikatem „odpowiedz! nie przyjmuje argumentów”. Sam błąd nie jest tu doctestem `compile_fail`, ponieważ dotyczy złożonego, osobno budowanego projektu. `unwrap` parsuje wyłącznie kontrolowane stałe autora; wejście użytkownika jest walidowane.

## B26-3

Zestaw pozytywny: wywołanie w wyrażeniu, przypisanie wyniku do `u32`, konsument z aliasem zależności. Zestaw negatywny: pojedynczy argument, dowolna grupa tokenów, wywołanie w kontekście wymagającym itemu, jeśli kontrakt dopuszcza tylko wyrażenie. Test runtime sprawdza wynik 42. Dla makra korzystającego z runtime crate’a dodatkowo sprawdź brak importów, alias runtime’u i wywołanie wewnątrz biblioteki. Porównanie diagnostyki należy przypiąć do toolchainu lub aktualizować świadomie po zmianach rustc.

