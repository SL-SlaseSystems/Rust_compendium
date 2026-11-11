[← Spis treści](../../README.md)

# Rozwiązania: Wzorce i `match`

## A17-1

Zero jest wzorcem wartości, a ostatni `Some(_)` pokrywa wszystkie pozostałe liczby. `None` wymaga osobnego ramienia.

~~~rust
fn opis(x: Option<u8>) -> &'static str {
    match x { None => "brak", Some(0) => "zero", Some(_) => "inne" }
}
fn main() {
    assert_eq!(opis(None), "brak");
    assert_eq!(opis(Some(0)), "zero");
    assert_eq!(opis(Some(7)), "inne");
}
~~~

## A17-2

Dopasowujemy pożyczkę, więc `s` ma typ `&String`. `as_str` tworzy widok bez konsumpcji.

~~~rust
fn widok(x: &Option<String>) -> Option<&str> {
    match x { Some(s) => Some(s.as_str()), None => None }
}
fn main() {
    let x = Some(String::from("tekst"));
    assert_eq!(widok(&x), Some("tekst"));
    assert_eq!(x.unwrap(), "tekst");
}
~~~

Skrótem tej operacji jest `x.as_deref()`, lecz rozwinięcie pokazuje tryb wiązania.

## A17-3

Wzorzec sprawdza minimalny kształt, a guard zgodność długości. Przy błędzie niczego nie konsumujemy ani nie indeksujemy poza zakresem.

~~~rust
fn ramka(dane: &[u8]) -> Option<&[u8]> {
    match dane {
        [1, n, reszta @ ..] if usize::from(*n) == reszta.len() => Some(reszta),
        _ => None,
    }
}
fn main() {
    assert_eq!(ramka(&[1, 2, 7, 8]), Some(&[7, 8][..]));
    assert_eq!(ramka(&[1, 0]), Some(&[][..]));
    assert_eq!(ramka(&[2, 0]), None);
    assert_eq!(ramka(&[1, 2, 7]), None);
    assert_eq!(ramka(&[1]), None);
}
~~~

Ten kontrakt wymaga dokładnie jednej ramki w buforze. Parser strumieniowy powinien zwracać także niewykorzystaną resztę i rozróżniać niepełne dane od trwale błędnej ramki. Zmiana tej semantyki wymaga zmiany wyniku, a nie tylko dodania następnego guarda.

