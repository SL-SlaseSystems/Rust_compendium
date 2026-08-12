[← Spis treści](../README.md)

# Funkcje, wyrażenia i instrukcje

Sygnatura funkcji zawsze podaje typy parametrów. Typ zwracany zapisuje się po
`->`. Ostatnie wyrażenie bloku bez średnika jest jego wynikiem.

~~~rust
fn pole_prostokata(szerokosc: u32, wysokosc: u32) -> u32 {
    szerokosc * wysokosc
}

fn main() {
    assert_eq!(pole_prostokata(4, 5), 20);
}
~~~

Dodanie średnika do `szerokosc * wysokosc` zmieniłoby wynik bloku na `()` i
spowodowałoby błąd typów.

## Wyrażenie kontra instrukcja

Literał, wywołanie, blok, `if` i `match` są wyrażeniami, bo wytwarzają
wartość. Deklaracja `let` jest instrukcją.

~~~rust
fn main() {
    let bazowa = 10;
    let wynik = {
        let podwojona = bazowa * 2;
        podwojona + 1
    };
    assert_eq!(wynik, 21);
}
~~~

## Wczesny powrót

`return` jest przydatne w guard clauses, ale na końcu funkcji idiomatyczne
jest wyrażenie:

~~~rust
fn bezpieczne_dzielenie(a: f64, b: f64) -> Option<f64> {
    if b == 0.0 {
        return None;
    }
    Some(a / b)
}

fn main() {
    assert_eq!(bezpieczne_dzielenie(8.0, 2.0), Some(4.0));
    assert_eq!(bezpieczne_dzielenie(8.0, 0.0), None);
}
~~~

## Funkcje jako wartości

Wskaźnik funkcji ma typ `fn(A) -> R`. Closure ma własny anonimowy typ, ale
może zostać przekazany przez bounds `Fn`, `FnMut` lub `FnOnce`.

~~~rust
fn zastosuj(f: fn(i32) -> i32, x: i32) -> i32 {
    f(x)
}

fn podwoj(x: i32) -> i32 {
    x * 2
}

fn main() {
    assert_eq!(zastosuj(podwoj, 6), 12);
    assert_eq!(zastosuj(|x| x + 1, 6), 7);
}
~~~

Closure bez capture może zostać zamienione na wskaźnik funkcji. Closure
przechwytujące otoczenie już nie.

## Funkcje rozbieżne

Funkcja zwracająca `!` nigdy nie kończy się normalnie:

~~~rust
fn zatrzymaj(komunikat: &str) -> ! {
    panic!("{komunikat}")
}

fn main() {
    let nie_uruchamiaj = zatrzymaj as fn(&str) -> !;
    let _ = nie_uruchamiaj;
}
~~~

`!` może koercjonować się do oczekiwanego typu, co pozwala użyć `panic!` lub
`continue` w jednym z ramion `match`.

## Powiązane tematy

- [Sterowanie przepływem](04_sterowanie_przeplywem.md)
- [Closures i rodzina `Fn`](../05_kolekcje_i_iteratory/04_closures_i_fn_traits.md)
- [Propagacja i operator `?`](../06_bledy/02_propagacja_i_operator_question_mark.md)
