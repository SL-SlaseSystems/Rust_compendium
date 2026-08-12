[← Spis treści](../README.md)

# Slices i `str`

Slice jest pożyczonym, ciągłym widokiem na sekwencję. `&[T]` zawiera wskaźnik
do pierwszego elementu oraz długość; nie posiada danych. Dzięki temu jedna
funkcja może przyjąć tablicę, `Vec<T>` lub część obu.

~~~rust
fn srednia(dane: &[f64]) -> Option<f64> {
    if dane.is_empty() {
        None
    } else {
        Some(dane.iter().sum::<f64>() / dane.len() as f64)
    }
}

fn main() {
    let tablica = [2.0, 4.0, 8.0];
    assert_eq!(srednia(&tablica[..2]), Some(3.0));
    assert_eq!(srednia(&Vec::<f64>::new()), None);
}
~~~

Mutowalny slice `&mut [T]` pozwala zmieniać elementy, lecz nie długość
sekwencji:

~~~rust
fn wyzeruj(dane: &mut [i32]) {
    dane.fill(0);
}

fn main() {
    let mut dane = [1, 2, 3, 4];
    wyzeruj(&mut dane[1..3]);
    assert_eq!(dane, [1, 0, 0, 4]);
}
~~~

Indeksowanie poza zakresem powoduje panic. Metoda `get` zwraca `Option` i
pozwala obsłużyć brak elementu.

## `String` i `str`

`String` posiada rozszerzalny bufor UTF-8. `str` jest typem niesized
reprezentującym poprawne bajty UTF-8; spotyka się go prawie zawsze przez
`&str`. Literał tekstowy ma typ `&'static str`.

~~~rust
fn powitanie(imie: &str) -> String {
    format!("Cześć, {imie}!")
}

fn main() {
    let posiadany = String::from("Ada");
    assert_eq!(powitanie(&posiadany), "Cześć, Ada!");
    assert_eq!(powitanie("Ferris"), "Cześć, Ferris!");
}
~~~

## Granice UTF-8

Zakres na `str` jest zakresem bajtów i musi wypaść na granicach kodowania
znaków. Dlatego `tekst[0]` nie jest dostępne: „znak” może oznaczać bajt,
Unicode scalar value albo grafem widoczny dla człowieka.

~~~rust
fn main() {
    let tekst = "żółw";
    assert_eq!(tekst.len(), 7); // bajty UTF-8: 2 + 2 + 2 + 1
    let znaki: Vec<char> = tekst.chars().collect();
    assert_eq!(znaki, ['ż', 'ó', 'ł', 'w']);
    assert_eq!(&tekst[0..2], "ż");
}
~~~

Rozcinaj tekst przez `char_indices`, `split` lub parser domenowy. Segmentacja
grafemów wymaga biblioteki **third-party**, np. `unicode-segmentation`.

## Wzorce na slices

~~~rust
fn opis(dane: &[i32]) -> &'static str {
    match dane {
        [] => "pusto",
        [_] => "jeden",
        [pierwszy, .., ostatni] if pierwszy == ostatni => "symetryczne końce",
        _ => "wiele",
    }
}

fn main() {
    assert_eq!(opis(&[1, 2, 1]), "symetryczne końce");
}
~~~

## Powiązane tematy

- [Referencje i borrowing](03_referencje_i_borrowing.md)
- [`String`, `str` i Unicode](../05_kolekcje_i_iteratory/02_string_str_i_unicode.md)
- [DST i trait objects](../04_typy_i_modelowanie/05_konwersje_dst_i_trait_objects.md)
