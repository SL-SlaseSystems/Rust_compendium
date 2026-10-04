[← Spis treści](../README.md)

# `Option` i `Result`

Rust modeluje spodziewany brak oraz błąd jako wartości. `Option<T>` ma
`Some(T)` lub `None`. `Result<T, E>` ma `Ok(T)` lub `Err(E)`.

## Brak nie jest null

~~~rust
fn dzielenie(a: i32, b: i32) -> Option<i32> {
    (b != 0).then(|| a / b)
}

fn main() {
    assert_eq!(dzielenie(8, 2), Some(4));
    assert_eq!(dzielenie(8, 0), None);
}
~~~

Wywołujący musi rozpakować enum. Kompilator nie pozwala użyć `Option<i32>`
jak `i32`.

## Błąd z informacją

~~~rust
#[derive(Debug, PartialEq)]
enum BladDzielenia {
    Zero,
    Niepodzielne,
}

fn dziel_dokladnie(a: i32, b: i32) -> Result<i32, BladDzielenia> {
    if b == 0 {
        Err(BladDzielenia::Zero)
    } else if a % b != 0 {
        Err(BladDzielenia::Niepodzielne)
    } else {
        Ok(a / b)
    }
}

fn main() {
    assert_eq!(dziel_dokladnie(8, 2), Ok(4));
    assert_eq!(dziel_dokladnie(7, 2), Err(BladDzielenia::Niepodzielne));
}
~~~

`Result` jest lepszy, gdy przyczyna braku ma znaczenie dla użytkownika lub
diagnostyki.

## Combinators

~~~rust
fn port(tekst: Option<&str>) -> Result<u16, &'static str> {
    tekst
        .ok_or("brak portu")?
        .parse::<u16>()
        .map_err(|_| "port nie jest liczbą")
        .and_then(|p| (p != 0).then_some(p).ok_or("port zero"))
}

fn main() {
    assert_eq!(port(Some("8080")), Ok(8080));
    assert_eq!(port(None), Err("brak portu"));
}
~~~

Najczęstsze metody to `map`, `and_then`, `or_else`, `filter`,
`unwrap_or`, `unwrap_or_else`, `map_err`, `ok_or` i `transpose`.
`Option<Result<T,E>>::transpose` daje `Result<Option<T>,E>`.

## `unwrap` i `expect`

`unwrap` powoduje panic przy `None`/`Err`. Jest sensowne w krótkim przykładzie,
teście albo gdy invariant został wcześniej udowodniony. `expect` powinno
opisywać założenie, które zostało złamane:

~~~rust
fn main() {
    let pierwsza = [10, 20]
        .first()
        .expect("tablica w tym miejscu jest niepusta");
    assert_eq!(*pierwsza, 10);
}
~~~

W danych użytkownika zamiast `unwrap` propaguj lub obsłuż błąd. Nie zmieniaj
automatycznie każdego `unwrap` na rozbudowany enum; oceniaj granicę i invariant.

## Powiązane tematy

- [Propagacja i operator `?`](02_propagacja_i_operator_question_mark.md)
- [Własne błędy i API](04_wlasne_bledy_i_api.md)
- [Wzorce i `match`](../04_struktury_enumy_i_wzorce/02_wzorce_i_match.md)
