[← Spis treści](../README.md)

# Tablice, wektory i sekwencje

Dobór kolekcji opisuje oczekiwane operacje, nie tylko „wiele elementów”.

## Tablica, slice i wektor

- `[T; N]` — długość stała w typie, dane zwykle inline;
- `&[T]` — pożyczony widok na ciągły fragment;
- `Vec<T>` — posiadany, ciągły bufor o zmiennej długości.

~~~rust
fn odwroc(dane: &mut [i32]) {
    dane.reverse();
}

fn main() {
    let tablica = [1, 2, 3];
    let mut wektor = Vec::with_capacity(4);
    wektor.extend_from_slice(&tablica);
    wektor.push(4);
    odwroc(&mut wektor);
    assert_eq!(wektor, [4, 3, 2, 1]);
    assert!(wektor.capacity() >= wektor.len());
}
~~~

`Vec` ma długość i pojemność. `push` może realokować, więc referencje do
elementów nie mogą pozostawać aktywne podczas mutacji wektora.

`get(index)` zwraca `Option<&T>`; indeksowanie `v[index]` powoduje panic poza
zakresem. `swap_remove` usuwa w O(1), ale zmienia kolejność. `remove` zachowuje
kolejność kosztem przesunięcia końcówki.

## `VecDeque<T>`

Dwukierunkowa kolejka wspiera tanie dodawanie i zdejmowanie na obu końcach:

~~~rust
use std::collections::VecDeque;

fn main() {
    let mut q = VecDeque::new();
    q.push_back("drugie");
    q.push_front("pierwsze");
    assert_eq!(q.pop_front(), Some("pierwsze"));
    assert_eq!(q.pop_back(), Some("drugie"));
}
~~~

Bufor może zawijać się w pamięci i składać z dwóch slices. Gdy potrzebujesz
jednego ciągłego obszaru, użyj `make_contiguous`.

## `LinkedList<T>`

Standardowa lista dwukierunkowa istnieje, ale rzadko przewyższa `Vec` lub
`VecDeque`. Dodatkowe alokacje i słaba lokalność cache często dominują nad
teoretycznym O(1) wstawiania. Wybieraj ją dopiero po pomiarze i gdy API
kursora/listy rzeczywiście pasuje.

## `BinaryHeap<T>`

Kopiec binarny jest kolejką priorytetową typu max-heap:

~~~rust
use std::collections::BinaryHeap;

fn main() {
    let mut zadania = BinaryHeap::from([2, 9, 4]);
    assert_eq!(zadania.pop(), Some(9));
    assert_eq!(zadania.peek(), Some(&4));
}
~~~

Do min-heap opakuj klucz w `std::cmp::Reverse`. Zmiana wartości wpływającej na
porządek, gdy jest w kopcu, jest błędem logicznym; bezpieczne API ogranicza
możliwość takiej mutacji.

## Złożoność i pamięć

Notacja O opisuje wzrost, lecz nie stałe koszty i cache. `Vec` zwykle jest
najlepszym domyślnym wyborem dla sekwencji. Rezerwuj pojemność, jeśli znasz
przybliżony rozmiar, ale nie trzymaj ogromnego bufora „na wszelki wypadek”.

## Powiązane tematy

- [Slices i `str`](../03_ownership_i_pamiec/04_slices_i_str.md)
- [Mapy i zbiory](03_mapy_zbiory_i_entry.md)
- [Iteratory](05_iteratory.md)
