[← Spis treści](../README.md)

# Propagacja i operator `?`

Operator `?` kończy bieżącą funkcję wcześniej przy `Err` lub `None`, a przy
sukcesie rozpakowuje wartość. Zachowuje czytelny „happy path”.

## Propagacja `Result`

~~~rust
use std::num::ParseIntError;

fn podwoj(tekst: &str) -> Result<i32, ParseIntError> {
    let liczba = tekst.trim().parse::<i32>()?;
    Ok(liczba * 2)
}

fn main() {
    assert_eq!(podwoj("21"), Ok(42));
    assert!(podwoj("x").is_err());
}
~~~

Rozwinięcie mentalne to `match`: dla `Ok` kontynuuj, dla `Err` wykonaj
wczesny return. Dokładna semantyka używa traits `Try` i `FromResidual`;
na stabilnym Rust własne implementacje tego mechanizmu są ograniczone.

## Automatyczna konwersja błędu

`?` wywołuje `From::from`, jeżeli błąd funkcji docelowej ma zostać zmieniony
na błąd funkcji bieżącej:

~~~rust
use std::fmt;
use std::num::ParseIntError;

#[derive(Debug)]
struct Blad(ParseIntError);

impl From<ParseIntError> for Blad {
    fn from(e: ParseIntError) -> Self { Self(e) }
}

impl fmt::Display for Blad {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "niepoprawna liczba: {}", self.0)
    }
}

fn wczytaj(s: &str) -> Result<i32, Blad> {
    Ok(s.parse::<i32>()?)
}

fn main() {
    assert_eq!(wczytaj("42").unwrap(), 42);
}
~~~

Nie twórz zbyt szerokiej implementacji `From`, która usuwa ważną informację.

## `?` z `Option`

~~~rust
fn drugie_slowo(tekst: &str) -> Option<&str> {
    let mut slowa = tekst.split_whitespace();
    slowa.next()?;
    slowa.next()
}

fn main() {
    assert_eq!(drugie_slowo("a b c"), Some("b"));
    assert_eq!(drugie_slowo("a"), None);
}
~~~

Zwykła funkcja zwracająca `Result` nie może bezpośrednio użyć `?` na
`Option`; najpierw nadaj brakowi znaczenie przez `ok_or`.

## Granice

`?` działa w funkcji, closure lub bloku, którego typ powrotu jest zgodny z
residual. `main` może zwracać `Result<(), E>`, a blok `try` pozostaje
funkcjonalnością niestabilną — sprawdzaj aktualny Unstable Book.

## Kontekst błędu

Propagacja bez kontekstu może zostawić użytkownika z „No such file” bez nazwy
operacji. Biblioteka może wzbogacić własny enum, a aplikacja użyć crate’a
**third-party** `anyhow` i `Context`. Kontekst dodawaj przy przejściu między
warstwami abstrakcji, nie w każdym wierszu.

## Powiązane tematy

- [`Option` i `Result`](01_option_i_result.md)
- [Własne błędy i API](04_wlasne_bledy_i_api.md)
- [Funkcje i wyrażenia](../02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md)
