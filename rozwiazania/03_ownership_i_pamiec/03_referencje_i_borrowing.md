[← Spis treści](../../README.md)

# Rozwiązania: Referencje i borrowing

## A12-1

Funkcja pożycza tekst, więc po powrocie właściciel może go nadal odczytać i modyfikować.

~~~rust
fn dlugosc(s: &str) -> usize { s.len() }
fn main() {
    let mut s = String::from("Rust");
    assert_eq!(dlugosc(&s), 4);
    s.push('!');
    assert_eq!(s, "Rust!");
}
~~~

## A12-2

Dla jednego elementu przyjmujemy jeden przyrost. `split_first_mut` oddziela pierwszy element od reszty, więc pożyczki nie zachodzą na siebie.

~~~rust
fn zwieksz_konce(xs: &mut [i32]) {
    let Some((pierwszy, reszta)) = xs.split_first_mut() else { return; };
    *pierwszy += 1;
    if let Some(ostatni) = reszta.last_mut() { *ostatni += 1; }
}
fn main() {
    let mut puste: [i32; 0] = [];
    zwieksz_konce(&mut puste);
    let mut jeden = [5]; zwieksz_konce(&mut jeden);
    let mut trzy = [1, 2, 3]; zwieksz_konce(&mut trzy);
    assert_eq!(jeden, [6]); assert_eq!(trzy, [2, 2, 4]);
}
~~~

Dla liczb zewnętrznych dodaj świadomą politykę przepełnienia; ćwiczenie skupia się na rozłączności pożyczek.

## A12-3

Oba indeksy walidujemy przed modyfikacją. Zwracamy brak dla niepoprawnego wejścia i sukces także wtedy, gdy indeksy są równe.

~~~rust
fn zamien<T>(xs: &mut [T], a: usize, b: usize) -> Option<()> {
    if a >= xs.len() || b >= xs.len() { return None; }
    xs.swap(a, b);
    Some(())
}
fn main() {
    let mut xs = [1, 2, 3];
    assert_eq!(zamien(&mut xs, 0, 2), Some(()));
    assert_eq!(xs, [3, 2, 1]);
    assert_eq!(zamien(&mut xs, 1, 1), Some(()));
    assert_eq!(zamien(&mut xs, 9, 0), None);
    assert_eq!(xs, [3, 2, 1]);
}
~~~

Nie trzeba ręcznie konstruować dwóch referencji do elementów. Bezpieczne API slice ma już potrzebny kontrakt, także dla równości indeksów.

