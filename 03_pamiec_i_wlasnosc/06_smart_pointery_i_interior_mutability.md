[← Spis treści](../README.md)

# Smart pointery i interior mutability

Smart pointer jest strukturą zachowującą się jak wskaźnik, ale niosącą
dodatkową semantykę ownership, zliczania referencji lub kontroli dostępu.

## `Box<T>`

`Box<T>` posiada jedną wartość na stercie. Używa się go dla rekurencyjnych
typów, dużych wartości, trait objects i jawnego indirection.

~~~rust
fn main() {
    let liczba = Box::new(41);
    assert_eq!(*liczba + 1, 42);
}
~~~

Samo opakowanie w `Box` nie udostępnia współdzielonego ownership.

## `Rc<T>` i `Weak<T>`

`Rc<T>` zlicza silne referencje w jednym wątku. Klonowanie `Rc` zwiększa
licznik, nie kopiuje danych.

~~~rust
use std::rc::{Rc, Weak};

fn main() {
    let wartosc = Rc::new(String::from("wspólna"));
    let druga = Rc::clone(&wartosc);
    let slaba: Weak<String> = Rc::downgrade(&wartosc);
    assert_eq!(Rc::strong_count(&wartosc), 2);
    assert_eq!(druga.as_str(), "wspólna");
    drop(wartosc);
    drop(druga);
    assert!(slaba.upgrade().is_none());
}
~~~

Cykl z samych `Rc` wycieka logicznie, bo liczniki nie spadają do zera.
Relacje „rodzic” lub cache zwykle powinny używać `Weak`.

## Interior mutability

`Cell<T>` pozwala kopiować lub zastępować wartość bez wydawania `&mut`.
`RefCell<T>` przenosi reguły borrowing do runtime: `borrow` i `borrow_mut`
zwracają guardy, a konflikt powoduje panic.

~~~rust
use std::cell::{Cell, RefCell};

fn main() {
    let licznik = Cell::new(0);
    licznik.set(licznik.get() + 1);
    assert_eq!(licznik.get(), 1);

    let log = RefCell::new(Vec::new());
    log.borrow_mut().push("zdarzenie");
    assert_eq!(log.borrow().len(), 1);
}
~~~

`Cell` i `RefCell` nie są `Sync`. Do współdzielenia między wątkami służą
zwykle `Arc<Mutex<T>>` lub atomiki.

## `Deref` i `Drop`

`Deref` umożliwia `*pointer` i deref coercions. Nie implementuj go tylko po
to, aby „dziedziczyć” metody innego typu — powinien istnieć oczywisty target.
`DerefMut` wymaga wyłącznego dostępu.

Smart pointer często implementuje `Drop`, aby zwolnić zasób. Kod `unsafe`
wewnątrz takiej abstrakcji musi zachować ważność, aliasing i poprawne
zniszczenie dla wszystkich bezpiecznych wywołań.

## Dobór typu

| Potrzeba | Typ |
|---|---|
| jeden właściciel na stercie | `Box<T>` |
| wielu właścicieli, jeden wątek | `Rc<T>` |
| wielu właścicieli, wiele wątków | `Arc<T>` |
| mutacja prostego `Copy` przez `&T` | `Cell<T>` |
| dynamiczne borrowing w jednym wątku | `RefCell<T>` |
| mutacja między wątkami | `Mutex<T>` / `RwLock<T>` |

Nie zaczynaj od `Rc<RefCell<T>>` jako uniwersalnego rozwiązania. Może ukryć
niejasne ownership i przenieść błędy do runtime.

## Powiązane tematy

- [`Arc`, `Mutex` i `RwLock`](../09_wspolbieznosc/03_arc_mutex_rwlock_i_condvar.md)
- [Pinning](../zaawansowane/07_pin_unpin_i_self_referential.md)
- [`unsafe` i soundness](../zaawansowane/01_unsafe_i_soundness.md)
