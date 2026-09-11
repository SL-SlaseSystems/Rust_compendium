[← Spis treści](../../README.md)

# Rozwiązania: Pierwszy program

## W03-1

Wynik to `5`. Blok jest wyrażeniem, a `2 + 3` bez średnika jest jego wartością.

~~~rust
fn main() {
    let x = { 2 + 3 };
    assert_eq!(x, 5);
}
~~~

## W03-2

Usuń średnik, aby ostatnim wyrażeniem bloku był `String`, zgodny z wynikiem funkcji.

~~~rust
fn f() -> String {
    String::from("ok")
}

fn main() {
    assert_eq!(f(), "ok");
}
~~~

## W03-3

`?` przekazuje błąd parsowania do `main`, a `Result` pozostawia decyzję o statusie procesu implementacji `Termination`.

~~~rust
use std::error::Error;

fn main() -> Result<(), Box<dyn Error>> {
    let tekst = "42";
    let liczba: u32 = tekst.parse()?;
    assert_eq!(liczba, 42);
    Ok(())
}
~~~
