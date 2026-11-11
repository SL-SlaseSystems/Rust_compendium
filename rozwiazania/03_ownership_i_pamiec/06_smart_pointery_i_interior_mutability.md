[← Spis treści](../../README.md)

# Rozwiązania: Smart pointery i interior mutability

## A15-1

`Rc::clone` tworzy uchwyt do tej samej wartości. Porównanie treści nie odróżniłoby tego od niezależnego tekstu; `ptr_eq` bada tożsamość alokacji.

~~~rust
use std::rc::Rc;
fn main() {
    let a = Rc::new(String::from("wspólny"));
    let b = Rc::clone(&a);
    assert!(Rc::ptr_eq(&a, &b));
    assert_eq!(Rc::strong_count(&a), 2);
}
~~~

## A15-2

Odczyt żyje do jawnego `drop`, dlatego pierwsza próba mutacji kończy się błędem. Druga jest poprawna po zwolnieniu guarda.

~~~rust
use std::cell::RefCell;
fn main() {
    let liczba = RefCell::new(1);
    let guard = liczba.borrow();
    assert!(liczba.try_borrow_mut().is_err());
    drop(guard);
    *liczba.try_borrow_mut().unwrap() = 2;
    assert_eq!(*liczba.borrow(), 2);
}
~~~

## A15-3

Silny kierunek prowadzi od rodzica do dziecka. Zewnętrzny uchwyt dziecka pozwala obserwować je po usunięciu rodzica, ale słaba krawędź nie odtwarza cyklu.

~~~rust
use std::{cell::RefCell, rc::{Rc, Weak}};
struct Wezel {
    rodzic: RefCell<Weak<Wezel>>,
    dzieci: RefCell<Vec<Rc<Wezel>>>,
}
fn nowy() -> Rc<Wezel> {
    Rc::new(Wezel { rodzic: RefCell::new(Weak::new()), dzieci: RefCell::new(vec![]) })
}
fn main() {
    let rodzic = nowy();
    let dziecko = nowy();
    *dziecko.rodzic.borrow_mut() = Rc::downgrade(&rodzic);
    rodzic.dzieci.borrow_mut().push(Rc::clone(&dziecko));
    assert!(dziecko.rodzic.borrow().upgrade().is_some());
    drop(rodzic);
    assert!(dziecko.rodzic.borrow().upgrade().is_none());
}
~~~

W pełnym API operacja przepinania węzła musi ponadto usuwać stare krawędzie i zapobiegać cyklom logicznym. Sam wybór `Weak` rozwiązuje pokazany cykl własności, a nie wszystkie niezmienniki drzewa.

