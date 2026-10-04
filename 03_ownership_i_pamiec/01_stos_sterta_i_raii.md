[← Spis treści](../README.md)

# Stos, sterta i RAII

Rust zarządza zasobami deterministycznie. Wartość ma właściciela, a gdy
właściciel wychodzi z zakresu, uruchamiany jest destruktor `Drop`. Ten wzorzec
to RAII: pozyskanie zasobu jest inicjalizacją obiektu.

## Stos i sterta

Stos przechowuje ramki wywołań i dane o rozmiarze znanym podczas kompilacji.
Operacje na jego szczycie są bardzo tanie. Sterta przechowuje dane o
dynamicznym rozmiarze lub czasie życia; alokator zwraca adres bloku.

`String` jest wartością o stałym rozmiarze na stosie: zawiera wskaźnik,
długość i pojemność. Bajty tekstu są zwykle na stercie. `Vec<T>` ma podobną
reprezentację.

~~~rust
use std::mem::{size_of, size_of_val};

fn main() {
    let tekst = String::from("Rust");
    assert_eq!(size_of_val(&tekst), size_of::<String>());
    assert_eq!(tekst.len(), 4);
}
~~~

Rozmiar `String` zależy od ABI platformy; nie zakładaj konkretnej liczby
bajtów w przenośnym kodzie.

## Deterministyczne sprzątanie

~~~rust
struct Znacznik(&'static str);

impl Drop for Znacznik {
    fn drop(&mut self) {
        println!("drop {}", self.0);
    }
}

fn main() {
    let _a = Znacznik("A");
    {
        let _b = Znacznik("B");
    } // B jest niszczone tutaj
} // A jest niszczone tutaj
~~~

Zmienne lokalne są zwykle niszczone w odwrotnej kolejności deklaracji.
Pola struktury są niszczone w kolejności deklaracji pól po wykonaniu
`Drop::drop` struktury. Nie wywołuje się `value.drop()` bezpośrednio; do
wcześniejszego zniszczenia służy `std::mem::drop(value)`.

## RAII obejmuje więcej niż pamięć

Destruktor może zamknąć plik, zwolnić blokadę, socket lub inny uchwyt.
Guard zwrócony przez `Mutex::lock` zwalnia blokadę przy wyjściu z zakresu,
także podczas propagacji błędu lub panic z unwinding.

Rust nie gwarantuje uruchomienia destruktorów przy `process::abort`, nagłym
zakończeniu procesu ani wycieku przez `mem::forget`. Destruktor nie jest więc
miejscem dla jedynej kopii krytycznej operacji biznesowej.

## Stos nie jest nieskończony

Głęboka rekursja może przepełnić stos. Duże dane można przenieść na stertę
przez `Box<T>`, ale samo opakowanie nie zmienia algorytmu rekursywnego.
W strukturach rekurencyjnych indirection jest też potrzebne, aby typ miał
skończony rozmiar.

~~~rust
enum Lista {
    Element(i32, Box<Lista>),
    Koniec,
}

fn main() {
    let lista = Lista::Element(1, Box::new(Lista::Koniec));
    match lista {
        Lista::Element(n, reszta) => {
            assert_eq!(n, 1);
            assert!(matches!(*reszta, Lista::Koniec));
        }
        Lista::Koniec => unreachable!(),
    }
}
~~~

## Powiązane tematy

- [Ownership, move i Copy](02_ownership_move_i_copy.md)
- [Smart pointery](06_smart_pointery_i_interior_mutability.md)
- [Layout i alignment](../21_unsafe_soundness_i_model_pamieci/03_layout_alignment_i_uninitialized_memory.md)
