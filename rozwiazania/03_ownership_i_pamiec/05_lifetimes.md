[← Spis treści](../../README.md)

# Rozwiązania: Lifetimes

## A14-1

Jeden parametr referencyjny wystarcza dla elision. Literał pusty może być skrócony do lifetime wejścia.

~~~rust
fn pierwszy(s: &str) -> &str { s.split_whitespace().next().unwrap_or("") }
fn main() {
    assert_eq!(pierwszy("Rust działa"), "Rust");
    assert_eq!(pierwszy(""), "");
}
~~~

## A14-2

Drugi argument jest używany chwilowo; nie uczestniczy w typie wyniku. To pozwala użyć wyniku po końcu jego właściciela.

~~~rust
fn zachowaj<'a>(pierwszy: &'a str, drugi: &str) -> &'a str {
    assert!(!drugi.is_empty()); pierwszy
}
fn main() {
    let glowny = String::from("dokument");
    let wynik;
    { let opis = String::from("etykieta"); wynik = zachowaj(&glowny, &opis); }
    assert_eq!(wynik, "dokument");
}
~~~

## A14-3

Zakres jest sprawdzany przed utworzeniem obiektu. Prywatne pola chronią niezmiennik: późniejsze przeniesienie struktury nie unieważnia liczbowych offsetów.

~~~rust
use std::ops::Range;
struct Fragment { tekst: String, zakres: Range<usize> }
impl Fragment {
    fn nowy(tekst: String, zakres: Range<usize>) -> Option<Self> {
        tekst.get(zakres.clone())?;
        Some(Self { tekst, zakres })
    }
    fn widok(&self) -> &str { &self.tekst[self.zakres.clone()] }
}
fn main() {
    let f = Fragment::nowy("żaba".into(), 0..2).unwrap();
    let przeniesiony = f;
    assert_eq!(przeniesiony.widok(), "ż");
    assert!(Fragment::nowy("żaba".into(), 0..1).is_none());
}
~~~

Nie udostępniamy mutacji tekstu, która mogłaby zmienić granice. Jeśli taka operacja zostanie dodana, musi przeliczyć albo ponownie zwalidować zakres. Model nie wymaga self-reference ani `unsafe`.

