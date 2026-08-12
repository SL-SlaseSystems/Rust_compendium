[← Spis treści](../README.md)

# Ownership, move i `Copy`

Każda wartość ma w danej chwili właściciela. Przypisanie lub przekazanie przez
wartość domyślnie przenosi (move) własność. Gdy właściciel wychodzi z zakresu,
wartość zostaje zniszczona.

## Przeniesienie

~~~rust
fn dlugosc(tekst: String) -> (String, usize) {
    let n = tekst.len();
    (tekst, n)
}

fn main() {
    let a = String::from("krab");
    let (a, n) = dlugosc(a);
    assert_eq!(n, 4);
    assert_eq!(a, "krab");
}
~~~

Przekazanie `a` do funkcji przeniosło wartość. Funkcja zwraca ją, aby
wywołujący ponownie przejął własność. W praktyce sam odczyt długości powinien
użyć referencji; przykład pokazuje mechanikę.

Po move stary binding nie może być użyty:

~~~compile_fail
fn main() {
    let pierwszy = String::from("dane");
    let drugi = pierwszy;
    println!("{pierwszy} i {drugi}");
}
~~~

Dzięki unieważnieniu `pierwszy` tylko jeden `String` zwolni wspólny bufor.

## `Clone` i `Copy`

`Clone::clone` wykonuje jawną logiczną kopię, która może alokować. `Copy` jest
markerem dla typów kopiowanych bitowo i bez destruktora, np. większości typów
skalarnych.

~~~rust
#[derive(Clone, Copy, Debug, PartialEq)]
struct Punkt {
    x: i32,
    y: i32,
}

fn main() {
    let p1 = Punkt { x: 2, y: 3 };
    let p2 = p1;
    assert_eq!(p1, p2);

    let s1 = String::from("x");
    let s2 = s1.clone();
    assert_eq!(s1, s2);
}
~~~

Typ implementujący `Drop` nie może implementować `Copy`. Nie dodawaj `Copy`
do typu tylko po to, aby uciszyć błąd move — decyzja jest częścią semantyki
API.

## Częściowe przeniesienie

Można przenieść jedno pole, a kopiować lub pożyczać inne:

~~~rust
struct Osoba {
    imie: String,
    wiek: u8,
}

fn main() {
    let osoba = Osoba { imie: "Ada".into(), wiek: 37 };
    let imie = osoba.imie;
    assert_eq!(osoba.wiek, 37);
    assert_eq!(imie, "Ada");
}
~~~

Nie można już użyć `osoba` jako całości. Dla typu implementującego `Drop`
przenoszenie pojedynczych pól jest ograniczone, bo destruktor oczekuje pełnej
wartości.

## Sposoby przekazywania

- `T` — funkcja przejmuje własność;
- `&T` — tylko czyta przez pożyczkę;
- `&mut T` — może zmieniać przez wyłączną pożyczkę;
- zwrot `T` — przekazuje własność wywołującemu.

To sygnatura, a nie komentarz, opisuje kontrakt zasobu.

## Powiązane tematy

- [Referencje i borrowing](03_referencje_i_borrowing.md)
- [Closures i rodzina `Fn`](../05_kolekcje_i_iteratory/04_closures_i_fn_traits.md)
- [`Send` i `Sync`](../09_wspolbieznosc/04_send_sync_i_atomiki.md)
