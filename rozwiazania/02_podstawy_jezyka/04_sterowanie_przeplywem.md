[← Spis treści](../../README.md)

# Rozwiązania: Sterowanie przepływem

## A08-1

Wszystkie gałęzie zwracają ten sam typ `&str`; zakres jest domknięty po obu stronach.

~~~rust
fn opis(n: u8) -> &'static str {
    match n { 0 => "zero", 1..=9 => "cyfra", _ => "pozostałe" }
}
fn main() {
    assert_eq!(opis(0), "zero");
    assert_eq!(opis(9), "cyfra");
    assert_eq!(opis(10), "pozostałe");
}
~~~

## A08-2

`&mut` daje wyłączny dostęp do każdego elementu. Druga iteracja pożycza całą tablicę już po zakończeniu pierwszej.

~~~rust
fn podwoj(dane: &mut [i32]) { for x in dane { *x *= 2; } }
fn main() {
    let mut dane = [1, 2, 3];
    podwoj(&mut dane);
    let suma: i32 = dane.iter().sum();
    assert_eq!((dane, suma), ([2, 4, 6], 12));
}
~~~

Dla dowolnych danych produkcyjnych trzeba dodatkowo ustalić politykę przepełnienia mnożenia; tutaj konkretne wartości mieszczą się w typie.

## A08-3

Sprawdzenie długości przed pętlą pozwala odrzucić wejście bez przetwarzania prefiksu. `checked_add` rozdziela poprawny wynik od przepełnienia, a nie zamienia go na zawiniętą sumę.

~~~rust
fn suma(dane: &[u32], limit: usize) -> Option<u32> {
    if dane.len() > limit { return None; }
    let mut wynik = 0_u32;
    for &x in dane { wynik = wynik.checked_add(x)?; }
    Some(wynik)
}
fn main() {
    assert_eq!(suma(&[], 0), Some(0));
    assert_eq!(suma(&[2, 3], 2), Some(5));
    assert_eq!(suma(&[2, 3], 1), None);
    assert_eq!(suma(&[u32::MAX, 1], 2), None);
}
~~~

Jeśli klient musi rozróżniać dwa powody odmowy, zastąp `Option` enumem błędów. Sam mechanizm pętli nie narzuca tej decyzji API.

