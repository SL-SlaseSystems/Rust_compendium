[← Spis treści](../../README.md)

# Rozwiązania: Ownership, move i `Copy`

## A11-1

Parametr przejmuje tekst, a krotka oddaje go wywołującemu. Długość obliczamy przed przeniesieniem do wyniku.

~~~rust
fn policz(s: String) -> (String, usize) { let n = s.len(); (s, n) }
fn main() {
    let tekst = String::from("Rust");
    let (tekst, n) = policz(tekst);
    assert_eq!((tekst.as_str(), n), ("Rust", 4));
}
~~~

To ćwiczenie mechaniki. API potrzebujące wyłącznie długości powinno zwykle przyjmować `&str`.

## A11-2

`Option::take` zostawia `None`, dlatego kolejne pobranie ma jednoznaczne zachowanie.

~~~rust
struct Slot { tekst: Option<String> }
impl Slot { fn pobierz(&mut self) -> Option<String> { self.tekst.take() } }
fn main() {
    let mut slot = Slot { tekst: Some(String::from("zadanie")) };
    assert_eq!(slot.pobierz().as_deref(), Some("zadanie"));
    assert_eq!(slot.pobierz(), None);
}
~~~

## A11-3

Próba parsowania tylko pożycza tekst. Po zakończeniu pożyczki gałąź błędu może przenieść oryginalny bufor do wyniku.

~~~rust
fn parsuj(s: String) -> Result<u32, (String, std::num::ParseIntError)> {
    match s.parse::<u32>() {
        Ok(n) => Ok(n),
        Err(e) => Err((s, e)),
    }
}
fn main() {
    assert_eq!(parsuj("42".into()).unwrap(), 42);
    let (wejscie, blad) = parsuj("-1".into()).unwrap_err();
    assert_eq!(wejscie, "-1");
    assert!(!blad.to_string().is_empty());
}
~~~

Klient może teraz poprawić bufor, zapisać go do kolejki błędów albo podjąć ponowną próbę. Sukces konsumuje wejście i zwalnia je przy wyjściu z funkcji. To jest decyzja o własności danych po obu stronach wyniku, nie tylko sposób zadowolenia borrow checkera.

