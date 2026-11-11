[← Spis treści](../../README.md)

# Rozwiązania: Closures i rodzina `Fn`

## A27-1

Closure czyta próg przez pożyczkę. Konkretne wejścia mieszczą się w typie i nie wymagają przeniesienia stanu.

~~~rust
fn main() {
    let prog = 10;
    let wieksza = |n: i32| n > prog;
    assert!(!wieksza(9));
    assert!(!wieksza(10));
    assert!(wieksza(11));
    assert_eq!(prog, 10);
}
~~~

## A27-2

`FnMut` pozwala zmieniać pożyczony licznik, a `mut f` daje funkcji prawo wielokrotnego wywołania. Po powrocie pożyczka się kończy.

~~~rust
fn powtorz<F: FnMut()>(ile: usize, mut f: F) {
    for _ in 0..ile { f(); }
}
fn main() {
    let mut licznik = 0;
    powtorz(3, || licznik += 1);
    assert_eq!(licznik, 3);
    powtorz(0, || licznik += 1);
    assert_eq!(licznik, 3);
}
~~~

## A27-3

Jedno wyrażenie closure przechwytuje wybór oraz argument. Typ wyniku jest ten sam dla obu decyzji, bo gałąź znajduje się wewnątrz ciała.

~~~rust
fn operacja(dodaj: bool, n: i32) -> impl Fn(i32) -> i32 {
    move |x| if dodaj { x + n } else { x - n }
}
fn main() {
    let plus = operacja(true, 2);
    let minus = operacja(false, 3);
    assert_eq!(plus(5), 7);
    assert_eq!(plus(10), 12);
    assert_eq!(minus(5), 2);
}
~~~

Dwa oddzielne wyrażenia `move |x| ...` są różnymi anonimowymi typami. RPIT nie wybiera typu na podstawie wartości `bool` w runtime. Przy nieograniczonych liczbach należałoby ponadto zdefiniować zachowanie przepełnienia, na przykład przez wynik `Option<i32>` i `checked_add`/`checked_sub`.

