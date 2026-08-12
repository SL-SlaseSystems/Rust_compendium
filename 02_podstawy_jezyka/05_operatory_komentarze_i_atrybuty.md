[← Spis treści](../README.md)

# Operatory, komentarze i atrybuty

## Operatory

Rust ma operatory arytmetyczne `+ - * / %`, porównania `== != < <= > >=`,
logiczne `&& || !`, bitowe `& | ^ << >>` oraz przypisania złożone, np.
`+=`. Operatory logiczne są leniwe.

~~~rust
fn main() {
    let x = 0b1010_u8;
    let y = 0b1100_u8;
    assert_eq!(x & y, 0b1000);
    assert_eq!(x | y, 0b1110);

    let mut n = 2;
    n <<= 3;
    assert_eq!(n, 16);
}
~~~

Własne typy mogą implementować wiele operatorów przez traits z `std::ops`,
np. `Add`. Nie można zmienić precedencji ani tworzyć nowych symboli.

Ważne operatory i formy języka:

- `&x` i `&mut x` — pożyczanie;
- `*p` — dereferencja;
- `a..b`, `a..=b` — zakresy;
- `?` — propagacja braku lub błędu;
- `as` — jawne rzutowanie;
- `.await` — zawieszenie future w kontekście async.

## Komentarze

`//` komentuje do końca wiersza, a komentarz blokowy obejmuje wiele wierszy.
Komentarze dokumentacyjne są przetwarzane przez rustdoc:

~~~rust
/// Zwraca kwadrat liczby.
///
/// # Examples
///
/// ```
/// assert_eq!(kwadrat(4), 16);
/// ```
pub fn kwadrat(x: i32) -> i32 {
    x * x
}

fn main() {
    assert_eq!(kwadrat(3), 9);
}
~~~

`//!` dokumentuje element nadrzędny, zwykle moduł lub crate. Dokumentacja
publicznego API powinna wyjaśniać błędy (`# Errors`), panic (`# Panics`) i
wymagania safety (`# Safety`).

## Atrybuty

Atrybut zewnętrzny `#[...]` dotyczy następnego elementu, a wewnętrzny
`#![...]` — elementu, w którym się znajduje.

~~~rust
#[derive(Debug, Clone, PartialEq, Eq)]
struct Uzytkownik {
    id: u64,
}

#[must_use = "wynik walidacji trzeba obsłużyć"]
fn poprawny_id(id: u64) -> bool {
    id > 0
}

fn main() {
    let a = Uzytkownik { id: 1 };
    assert_eq!(a.clone(), a);
    assert!(poprawny_id(a.id));
}
~~~

Popularne atrybuty to `derive`, `test`, `cfg`, `allow`/`warn`/`deny`,
`inline`, `repr` i `must_use`. Nie dodawaj `#[allow(...)]` bez komentarza,
dlaczego ostrzeżenie jest świadomie akceptowane.

## Precedencja i czytelność

Precedencja jest opisana w Reference, ale kod nie powinien zmuszać czytelnika
do jej pamiętania. Nawiasy są tanie. `rustfmt` ujednolica układ, lecz nie
naprawia niejasnego znaczenia wyrażenia.

## Powiązane tematy

- [Propagacja i operator `?`](../06_bledy/02_propagacja_i_operator_question_mark.md)
- [Zależności, features i `cfg`](../07_moduly_i_cargo/03_zaleznosci_features_i_cfg.md)
- [Testy dokumentacyjne i rustdoc](../08_testowanie_i_jakosc/02_testy_dokumentacyjne_i_rustdoc.md)
