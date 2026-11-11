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


Dodanie średnika po `2 + 3` zmieniłoby wynik bloku na `()`, choć samo dodawanie nadal jest poprawnym wyrażeniem. Średnik po całym `let x = ...;` zamyka natomiast instrukcję wiązania i jest prawidłowy. To dwie różne pozycje składniowe, dlatego nie należy usuwać wszystkich średników w programie.

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


Równoważna postać `return String::from("ok");` jest legalna, ale przy jedynym końcowym wyniku niepotrzebnie rozbudowuje zapis. Zmiana sygnatury na `fn f()` usunęłaby komunikat kompilatora kosztem zerwania kontraktu zadania: klient nie otrzymałby tekstu. W rozwiązaniu naprawiamy źródło niezgodności, a nie wymaganie odbiorcy.

## W03-3

`?` przekazuje błąd parsowania do `main`, a brak argumentu zamieniamy w błąd. Pomocnik jest testowalny deterministycznie; `main` rzeczywiście czyta `std::env::args().nth(1)`.

~~~rust
fn parse_arg(tekst: Option<String>) -> Result<u32, String> {
    let tekst = tekst.ok_or_else(|| "brak argumentu".to_owned())?;
    tekst.parse::<u32>().map_err(|e| e.to_string())
}

fn main() {
    assert_eq!(parse_arg(Some("42".into())), Ok(42));
    assert!(parse_arg(None).is_err());
}
~~~

Poniższy wariant jest oznaczony `no_run`, ponieważ doctest nie ma stabilnego argumentu procesu, lecz stanowi kompletny wariant programu:

~~~rust,no_run
use std::error::Error;

fn main() -> Result<(), Box<dyn Error>> {
    let tekst = std::env::args().nth(1).ok_or("brak argumentu")?;
    let liczba: u32 = tekst.parse()?;
    println!("{liczba}");
    Ok(())
}
~~~


`std::env::args()` wymaga reprezentacji argumentów jako Unicode i może panikować przy niepoprawnym Unicode. Narzędzie operujące na dowolnych nazwach plików powinno używać `args_os()` oraz `PathBuf`. Dla liczby użytkowej kontrakt tekstowy bywa wystarczający, ale należy go nazwać. Brak argumentu, pusty argument i niepoprawna liczba są różnymi przypadkami wejścia; rozszerzenie testu powinno objąć wszystkie trzy.
