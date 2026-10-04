[← Spis treści](../README.md)

# `macro_rules!`

Makro deklaratywne dopasowuje tokeny wejściowe do wzorców i rozwija je do
nowego kodu. Działa przed pełną analizą typów, dlatego nie zna wyników
inferencji.

## Pierwsze makro

~~~rust
macro_rules! maksimum {
    ($jedna:expr) => { $jedna };
    ($pierwsza:expr, $($reszta:expr),+ $(,)?) => {{
        let mut wynik = $pierwsza;
        $(
            let kandydat = $reszta;
            if kandydat > wynik {
                wynik = kandydat;
            }
        )+
        wynik
    }};
}

fn main() {
    assert_eq!(maksimum!(3, 9, 2,), 9);
    assert_eq!(maksimum!(7), 7);
}
~~~

Każde ramię ma matcher i transcriber. `expr` dopasowuje wyrażenie.
`$(...),+` oznacza co najmniej jedno powtórzenie rozdzielone przecinkiem, a
`$(,)?` opcjonalny końcowy przecinek.

Podwójny blok `{{ ... }}` ogranicza zakres nazw pomocniczych i sam jest
wyrażeniem.

## Wielokrotna ewaluacja

Makro tekstowo generujące `$x + $x` może wykonać argument z efektem ubocznym
dwa razy. Zwiąż wyrażenie lokalnie:

~~~rust
macro_rules! podwoj_raz {
    ($x:expr) => {{
        let wartosc = $x;
        wartosc + wartosc
    }};
}

fn main() {
    let mut n = 1;
    let wynik = podwoj_raz!({
        n += 1;
        n
    });
    assert_eq!((wynik, n), (4, 2));
}
~~~

To nadal przenosi wartość do bindingu i wymaga, aby dodanie było poprawne.
Makro nie ma własnej ogólnej sygnatury typów jak funkcja.

## Formy delimitera

Wywołania `m!()`, `m![]` i `m!{}` przekazują token tree. Semicolon zależy od
kontekstu oraz rodzaju rozwinięcia. Makro może generować wyrażenia, items,
patterns, statements lub types, ale wynik musi pasować do miejsca wywołania.

## Eksport i zakres

`macro_rules!` ma reguły zakresu tekstowego oraz ścieżkowego. Atrybut
`#[macro_export]` umieszcza makro w korzeniu crate’a publicznego. W kodzie
2018+ zwykle importuje się makro przez `use crate_name::macro_name`.
`#[macro_use]` jest starszym mechanizmem i powinien mieć uzasadnienie.

## Kiedy makro

Użyj funkcji lub traitu, jeśli wystarczą. Makro ma sens, gdy potrzebujesz
zmiennej liczby elementów składni, generowania items, dopasowania tokenów lub
API typu DSL. Koszt to gorsze komunikaty, dłuższa kompilacja i trudniejsze
narzędzia.

## Powiązane tematy

- [Higiena, fragmenty i repetition](02_higiena_fragmenty_i_repetition.md)
- [Makra proceduralne](03_makra_proceduralne.md)
- [Zaawansowane makra proceduralne](../zaawansowane/10_zaawansowane_makra_proceduralne.md)
