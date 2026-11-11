[← Spis treści](../../README.md)

# Rozwiązania: `String`, `str` i Unicode

## A25-1

Dwie reprezentacje mogą być wizualnie podobne i mieć różne długości. Porównanie standardowe rozróżnia ich zawartość.

~~~rust
fn main() {
    let zlozony = "ą";
    let rozlozony = "a\u{328}";
    assert_eq!((zlozony.len(), zlozony.chars().count()), (2, 1));
    assert_eq!((rozlozony.len(), rozlozony.chars().count()), (3, 2));
    assert_ne!(zlozony, rozlozony);
}
~~~

## A25-2

Błąd posiada wejściowe bajty. Nie wykonujemy stratnej konwersji, więc pozostają dostępne do zapisania lub analizy.

~~~rust
fn main() {
    let bajty = vec![b'A', 0xff, b'B'];
    let blad = String::from_utf8(bajty).unwrap_err();
    assert_eq!(blad.utf8_error().valid_up_to(), 1);
    assert_eq!(blad.into_bytes(), [b'A', 0xff, b'B']);
}
~~~

## A25-3

Zmniejszamy limit co najwyżej o kilka bajtów do poprawnej granicy. Nie przetwarzamy całego tekstu w celu policzenia grafemów; to jest kontrakt bajtowy.

~~~rust
fn prefiks(s: &str, limit: usize) -> &str {
    let mut koniec = limit.min(s.len());
    while !s.is_char_boundary(koniec) { koniec -= 1; }
    &s[..koniec]
}
fn main() {
    assert_eq!(prefiks("żółw", 1), "");
    assert_eq!(prefiks("żółw", 3), "ż");
    assert_eq!(prefiks("żółw", 4), "żó");
    assert_eq!(prefiks("żółw", 99), "żółw");
    assert_eq!(prefiks("", 0), "");
}
~~~

Zero jest zawsze granicą UTF-8, więc odejmowanie nie przechodzi poniżej zera. Wynik może przerwać grafem złożony; jeśli aplikacja obiecuje zachowanie grafemów, potrzebuje dodatkowej segmentacji, a następnie limitu bajtów.

