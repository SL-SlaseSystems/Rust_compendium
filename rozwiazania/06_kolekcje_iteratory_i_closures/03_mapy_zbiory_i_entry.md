[← Spis treści](../../README.md)

# Rozwiązania: Mapy, zbiory i `Entry`

## A26-1

Klucze pożyczają literał wejściowy; typ licznika określamy jawnie. Dla nieograniczonych danych trzeba określić politykę przepełnienia.

~~~rust
use std::collections::HashMap;
fn main() {
    let mut licznik = HashMap::new();
    for slowo in "rust kod rust".split_whitespace() {
        *licznik.entry(slowo).or_insert(0_u32) += 1;
    }
    assert_eq!(licznik.get("rust"), Some(&2));
    assert_eq!(licznik.get("brak"), None);
}
~~~

## A26-2

Szukamy pożyczonym tekstem, a `get_mut` pozwala zmienić tylko znalezioną wartość. Nie tworzymy nowego klucza.

~~~rust
use std::collections::HashMap;
fn main() {
    let mut mapa = HashMap::from([(String::from("rust"), 1_u32)]);
    let klucz: &str = "rust";
    assert_eq!(mapa.get(klucz), Some(&1));
    if let Some(n) = mapa.get_mut(klucz) { *n += 1; }
    assert_eq!(mapa.get(klucz), Some(&2));
}
~~~

Ten kontrakt aktualizuje wyłącznie istniejący klucz. Gdy brak ma powodować wstawienie, `entry` żąda posiadanego klucza; to może wymagać utworzenia `String`.

## A26-3

Drzewo narzuca kolejność grup, a wektory zachowują kolejność danych wejściowych. Są to dwie osobne gwarancje.

~~~rust
use std::collections::BTreeMap;
fn raport(dane: &[(&str, u32)]) -> Vec<(String, Vec<u32>)> {
    let mut grupy: BTreeMap<&str, Vec<u32>> = BTreeMap::new();
    for &(nazwa, id) in dane { grupy.entry(nazwa).or_default().push(id); }
    grupy.into_iter().map(|(k, v)| (k.to_owned(), v)).collect()
}
fn main() {
    assert_eq!(raport(&[("B", 2), ("A", 1), ("B", 3)]),
        vec![("A".into(), vec![1]), ("B".into(), vec![2, 3])]);
    assert!(raport(&[]).is_empty());
}
~~~

Wynik posiada nazwy, aby mógł przeżyć wejście. Jeśli raport jest przetwarzany natychmiast, można pozostać przy pożyczonych kluczach; jeśli ma być zapisany lub przekazany dalej, ta kopia jest świadomą granicą własności.

