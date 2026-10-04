[← Spis treści](../../README.md)

# Rozwiązania: funkcje, wyrażenia i instrukcje

## P03-1

`a` ma typ `i32` i wartość `21`, ponieważ `20 + 1` jest wyrażeniem końcowym.
Średnik w bloku `b` zmienia dodawanie w instrukcję wyrażeniową, która ignoruje
wynik, więc blok ma typ `()` i wartość `()`. Instrukcja `let` wewnątrz `c` sama
nie jest wynikiem bloku; wynikiem jest końcowe `x`, czyli `42` typu `i32`.

~~~rust
fn main() {
    let a = { 20 + 1 };
    let b = { 20 + 1; };
    let c = {
        let x = a * 2;
        x
    };

    let _: i32 = a;
    let _: () = b;
    let _: i32 = c;
    assert_eq!((a, b, c), (21, (), 42));
}
~~~

Adnotacje `_` są tu testem przewidywanych typów, nie koniecznością w zwykłym
programie.

## P03-2

Adnotacja `fn(i32) -> i32` tworzy oczekiwany kontekst koercji. Dzięki niej
unikatowy typ elementu każdej nazwanej funkcji zostaje zamieniony na wspólny typ
wskaźnika. Taki sam kontekst przyjmuje nieasynchroniczne closure bez przechwyceń.

~~~rust
fn dodaj_jeden(x: i32) -> i32 {
    x + 1
}

fn odejmij_jeden(x: i32) -> i32 {
    x - 1
}

fn main() {
    let mut operacja: fn(i32) -> i32 = dodaj_jeden;
    assert_eq!(operacja(10), 11);

    operacja = odejmij_jeden;
    assert_eq!(operacja(10), 9);

    let podwoj: fn(i32) -> i32 = |x| x * 2;
    assert_eq!(podwoj(10), 20);
}
~~~

Gdyby closure użyło wartości z otoczenia, zawierałoby stan i nie mogłoby zostać
skoercjonowane do zwykłego wskaźnika funkcji.

## P03-3

Pierwsza granica jest generyczna po `F: Fn(i32) -> i32`, bo polityka ma prawo
przechwycić konfigurację. Druga ma jawny typ `extern "C" fn(i32) -> i32`, bo ma
reprezentować bezstanowy callback wywoływany zgodnie z ABI C.

~~~rust
fn przetworz<F>(liczby: &[i32], polityka: F) -> Vec<i32>
where
    F: Fn(i32) -> i32,
{
    liczby.iter().copied().map(polityka).collect()
}

extern "C" fn podwoj_dla_c(x: i32) -> i32 {
    x * 2
}

fn wywolaj_callback(callback: extern "C" fn(i32) -> i32, x: i32) -> i32 {
    callback(x)
}

fn main() {
    let przesuniecie = 3;
    let wynik = przetworz(&[1, 2, 3], |x| x + przesuniecie);
    assert_eq!(wynik, [4, 5, 6]);

    let callback: extern "C" fn(i32) -> i32 = podwoj_dla_c;
    assert_eq!(wywolaj_callback(callback, 7), 14);
}
~~~

`Fn` opisuje zachowanie obiektu, który może nieść przechwycony stan, i pozwala
kompilatorowi wyspecjalizować `przetworz` dla konkretnego typu polityki.
`extern "C" fn` jest pojedynczym typem bezstanowego wskaźnika o konkretnej
konwencji wywołania. Sam wybór ABI C nie gwarantuje jeszcze poprawności całej
granicy FFI — typy danych, panika i kontrakty bezpieczeństwa wymagają osobnego
projektu.
