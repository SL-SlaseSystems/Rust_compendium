[← Spis treści](../../README.md)

# Rozwiązania: Stos, sterta i RAII

## A10-1

Rozmiar nagłówka jest ten sam; długość danych jest inną wielkością.

~~~rust
fn main() {
    let a = String::from("a");
    let b = "b".repeat(1024);
    assert_eq!(std::mem::size_of_val(&a), std::mem::size_of_val(&b));
    assert_eq!((a.len(), b.len()), (1, 1024));
}
~~~

Nie porównujemy adresów ani nie zakładamy 24 bajtów, ponieważ to nie jest przenośny sposób mierzenia całej pamięci programu.

## A10-2

Kolejność lokalnych bindingów w tym samym zakresie jest odwrotna do ich deklaracji. Dziennik ma osobnego właściciela, więc można go obejrzeć po zniszczeniu znaczników.

~~~rust
use std::{cell::RefCell, rc::Rc};
struct Znak(&'static str, Rc<RefCell<Vec<&'static str>>>);
impl Drop for Znak { fn drop(&mut self) { self.1.borrow_mut().push(self.0); } }
fn main() {
    let log = Rc::new(RefCell::new(Vec::new()));
    {
        let _a = Znak("A", Rc::clone(&log));
        let _b = Znak("B", Rc::clone(&log));
    }
    assert_eq!(*log.borrow(), ["B", "A"]);
}
~~~

## A10-3

Przykład modeluje zatwierdzenie bez wykonywania I/O. Błąd pojawia się jako wynik metody, więc klient ma szansę podjąć decyzję; pole `zatwierdzony` pozwala destruktorowi wykonać co najwyżej sprzątanie pomocnicze.

~~~rust
struct Zapis { zatwierdzony: bool }
impl Zapis {
    fn finish(mut self, dostepny: bool) -> Result<(), &'static str> {
        if !dostepny { return Err("zapis niedostępny"); }
        self.zatwierdzony = true;
        Ok(())
    }
}
impl Drop for Zapis {
    fn drop(&mut self) {
        if !self.zatwierdzony { /* best-effort sprzątanie, bez paniki */ }
    }
}
fn main() {
    assert_eq!(Zapis { zatwierdzony: false }.finish(false), Err("zapis niedostępny"));
    assert_eq!(Zapis { zatwierdzony: false }.finish(true), Ok(()));
}
~~~

W prawdziwym pliku `finish` powinno wywołać konkretne operacje zapisu i synchronizacji. Ten model nie dowodzi trwałości danych po awarii zasilania.

