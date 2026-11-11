[← Spis treści](../../README.md)

# Rozwiązania: Tablice, wektory i sekwencje

## A24-1

Pojemność nie ustala liczby elementów. Nie sprawdzamy równości pojemności z cztery, bo kontrakt gwarantuje co najmniej tyle miejsc.

~~~rust
fn main() {
    let mut dane = Vec::with_capacity(4);
    assert!(dane.capacity() >= 4);
    assert!(dane.is_empty());
    dane.extend([10, 20]);
    assert_eq!(dane.len(), 2);
    assert!(dane.capacity() >= dane.len());
}
~~~

## A24-2

Dodawanie na końcu i odbieranie z początku wyraża FIFO. Puste `pop_front` jest normalnym brakiem elementu.

~~~rust
use std::collections::VecDeque;
fn main() {
    let mut q = VecDeque::new();
    for zadanie in ["A", "B", "C"] { q.push_back(zadanie); }
    assert_eq!(q.pop_front(), Some("A"));
    assert_eq!(q.pop_front(), Some("B"));
    assert_eq!(q.pop_front(), Some("C"));
    assert_eq!(q.pop_front(), None);
}
~~~

## A24-3

Odwrócony porządek sprawia, że maksimum kopca odpowiada najmniejszej liczbie. Nie polegamy na kolejności `iter`; wynik budujemy przez `pop`.

~~~rust
use std::{cmp::Reverse, collections::BinaryHeap};
fn main() {
    let mut q: BinaryHeap<Reverse<u32>> = [4, 1, 7, 1].map(Reverse).into();
    let mut wynik = Vec::new();
    while let Some(Reverse(n)) = q.pop() { wynik.push(n); }
    assert_eq!(wynik, [1, 1, 4, 7]);
}
~~~

Równe priorytety nie definiują kolejności dodatkowych danych zadania. Jeśli FIFO w ramach tego samego priorytetu jest wymagane, dodaj monotoniczny numer kolejności do klucza i ustal jego kierunek porównania.

