[← Spis treści](../README.md)
<!-- status: expanded -->

# `Option` i `Result`

## Cele

Po tym rozdziale potrafisz:

- dobrać `Option` lub `Result` do znaczenia braku;
- zachować pożyczanie i rozróżnić leniwe kombinatory;


Rust modeluje spodziewany brak oraz błąd jako wartości. `Option<T>` ma
`Some(T)` lub `None`. `Result<T, E>` ma `Ok(T)` lub `Err(E)`.

## Brak nie jest null

~~~rust
fn dzielenie(a: i32, b: i32) -> Option<i32> {
    a.checked_div(b)
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
    Przepelnienie,
}

fn dziel_dokladnie(a: i32, b: i32) -> Result<i32, BladDzielenia> {
    if b == 0 {
        Err(BladDzielenia::Zero)
    } else if a == i32::MIN && b == -1 {
        Err(BladDzielenia::Przepelnienie)
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


## Model — informacja, własność i koszt

`Option<T>` odpowiada na pytanie, czy wynik istnieje. `Result<T, E>` niesie decyzję, czy operacja spełniła kontrakt. Brak użytkownika w wyszukiwarce może być normalnym `None`, a brak obowiązkowego identyfikatora w konfiguracji błędem. Sam typ nie wybiera polityki: to dokumentacja określa, czy brak jest oczekiwany, czy wymaga interwencji. Nie zamieniaj błędów parsera na `None`, jeżeli odbiorca potrzebuje odróżnić brak danych od danych uszkodzonych.

Metody konsumujące `self`, takie jak `map`, zwykle przenoszą zawartość. Gdy chcesz jedynie odczytać tekst, użyj `as_ref` lub `as_deref`; nie klonuj całego obiektu tylko po to, aby sprawdzić pole. `Option<String>::as_deref()` daje `Option<&str>`, więc walidator może pożyczyć tekst bez alokacji. Odpowiedniki dla `Result` pozwalają obejrzeć zarówno sukces, jak i błąd. Pożyczka nadal podlega zwykłym regułom czasu życia.

~~~rust
fn main() {
    let nazwa = Some(String::from("Ada"));
    let dlugosc = nazwa.as_deref().map(str::len);
    assert_eq!(dlugosc, Some(3));
    assert_eq!(nazwa.as_deref(), Some("Ada"));
    let ustawienie: Option<Result<u16, _>> = Some("8080".parse());
    assert_eq!(ustawienie.transpose().unwrap(), Some(8080));
}
~~~

`transpose` rozdziela dwie osie informacji: opcjonalność pola oraz poprawność podanej wartości. Dla `None` otrzymujesz `Ok(None)`, a dla niepoprawnego tekstu `Err`. `flatten` usuwa tylko jedną warstwę zagnieżdżonego `Option`; nie jest zamiennikiem walidacji.

`unwrap_or(kosztowny_fallback())` oblicza argument także dla `Some`. Wersja `unwrap_or_else(|| kosztowny_fallback())` wykonuje closure tylko przy braku. Analogiczna różnica zachodzi między `ok_or` i `ok_or_else`. Wybór jest istotny, gdy kontekst błędu formatuje tekst, pobiera blokadę lub wykonuje efekt uboczny. `then_some` również oblicza argument od razu, natomiast `then` dostaje closure. Nie chowaj operacji mogącej panikować w gorliwie obliczanym fallbacku.

Arytmetyka ma dodatkowy kontrakt. Dla podpisanych liczb całkowitych para `MIN / -1` przepełnia wynik, choć dzielnik nie jest zerem. `checked_div` koduje oba przypadki jako `None`; przy `Result` można nadać przepełnieniu osobny wariant. Stwierdzenie „sprawdziłem zero, więc każde dzielenie jest bezpieczne” byłoby za mocne.

## Diagnostyka kompilatora

Próba `let liczba: u16 = Some(80);` daje niezgodność typów: wariant enumu nie konwertuje się sam na zawartość. Wybierz `match`, `if let` lub kombinator i jawnie obsłuż `None`. Ostrzeżenie `unused_must_use` przy pominiętym `Result` wskazuje nieobsłużony kontrakt, nie kosmetykę. `let _ = operacja()` ucisza lint, lecz nadal wymaga uzasadnienia odrzucenia błędu. Po przeniesieniu przez `map` odwołanie do starego `Option<String>` daje błąd użycia przeniesionej wartości; rozwiązaniem jest pożyczanie, gdy własność ma pozostać w wywołującym.

## Praktyka produkcyjna

Na granicy API opisz, co dokładnie oznacza brak. Dla odczytu konfiguracji zwykle rozróżnij brak, zły format i wartość spoza zakresu. Nie traktuj `Result<T, String>` jako automatycznej poprawy: tekst utrudnia maszynową reakcję. Z kolei wewnętrzna funkcja wyszukująca indeks nie potrzebuje rozbudowanego błędu, jeśli brak jest jedyną informacją. Testuj wszystkie warianty oraz skrajne wartości. Koszt dodatkowego enumu jest zazwyczaj mały, ale nie zakładaj konkretnego layoutu każdego `Option<T>` bez udokumentowanej gwarancji dla danego typu.

## Sprawdź, czy rozumiesz

- Dlaczego `Some("x".parse::<u16>()).transpose()` różni się od odrzucenia błędu przez `ok()`?
- Który fallback wykona się mimo sukcesu i dlaczego?
- Jaki drugi przypadek poza zerowym dzielnikiem obsługuje `checked_div`?

## Ćwiczenia

- `B01-1` — podstawowe: Napisz bezpieczne dzielenie `i32`, sprawdzając zero i `i32::MIN / -1`. [Rozwiązanie](../rozwiazania/07_obsluga_bledow/01_option_i_result.md#b01-1).
- `B01-2` — praktyczne: Zamień opcjonalny tekst portu na `Result<Option<u16>, ParseIntError>` bez gubienia błędu. [Rozwiązanie](../rozwiazania/07_obsluga_bledow/01_option_i_result.md#b01-2).
- `B01-3` — pogłębione: Sprawdź licznikiem wywołań, że leniwy fallback nie uruchamia się przy `Some`. [Rozwiązanie](../rozwiazania/07_obsluga_bledow/01_option_i_result.md#b01-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [Option: własność i kombinatory](https://doc.rust-lang.org/std/option/enum.Option.html)
- [Result i transpose](https://doc.rust-lang.org/std/result/enum.Result.html)

## Powiązane tematy

- [Propagacja i operator `?`](02_propagacja_i_operator_question_mark.md)
- [Własne błędy i API](04_wlasne_bledy_i_api.md)
- [Wzorce i `match`](../04_struktury_enumy_i_wzorce/02_wzorce_i_match.md)
