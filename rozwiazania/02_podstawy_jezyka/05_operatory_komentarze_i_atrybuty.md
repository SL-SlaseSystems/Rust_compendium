[← Spis treści](../../README.md)

# Rozwiązania: Operatory, komentarze i atrybuty

## A09-1

Krótki obieg nie wywołuje drugiego bloku. Po zmianie `&&` na `&` licznik zostałby zwiększony.

~~~rust
fn main() {
    let mut licznik = 0;
    let wynik = false && { licznik += 1; true };
    assert!(!wynik);
    assert_eq!(licznik, 0);
}
~~~

## A09-2

Typ lewego operandu określa szerokość maski. Indeksy 0–7 są poprawne, osiem jest już poza szerokością `u8`.

~~~rust
/// Zwraca maskę pojedynczego bitu albo brak, gdy indeks przekracza 7.
fn bit(n: u32) -> Option<u8> { 1_u8.checked_shl(n) }
fn main() {
    assert_eq!(bit(0), Some(1));
    assert_eq!(bit(7), Some(128));
    assert_eq!(bit(8), None);
}
~~~

## A09-3

Oznaczamy wynik walidacji i odbieramy go w warunku. Lint chroni omyłkę programisty; typ `bool` nadal nie daje tak bogatego opisu błędu jak `Result`.

~~~rust
#[must_use = "odmowa musi przerwać wysyłanie"]
fn mozna_wyslac(rozmiar: usize, limit: usize) -> bool { rozmiar <= limit }
fn wyslij(rozmiar: usize, limit: usize) -> Result<(), &'static str> {
    if !mozna_wyslac(rozmiar, limit) { return Err("limit"); }
    Ok(())
}
fn main() {
    assert_eq!(wyslij(3, 3), Ok(()));
    assert_eq!(wyslij(4, 3), Err("limit"));
}
~~~

Jawne zignorowanie pasowałoby do pomiaru statystycznego, który nie ma wpływu na wysyłanie. Dla funkcji nazwanej jako obowiązkowa walidacja byłoby sprzeczne z opisanym kontraktem. Jeżeli wywołujący nie powinien mieć możliwości pominięcia sprawdzenia, konstruktor walidowanego typu i parametr tego typu są mocniejszą granicą niż sam lint.

