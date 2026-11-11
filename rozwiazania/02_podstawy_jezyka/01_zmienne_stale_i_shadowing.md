[← Spis treści](../../README.md)

# Rozwiązania: Zmienne, stałe i shadowing

## P01-1

Każda gałąź przypisuje `wynik`, więc odczyt spełnia definite assignment.

~~~rust
fn main() {
    let wynik: i32;
    if true { wynik = 42; } else { wynik = 0; }
    assert_eq!(wynik, 42);
}
~~~


Wersja z parametrem sprawdza obie realne ścieżki. Typowanie wymaga pełnej inicjalizacji niezależnie od wyniku konkretnego testu.

~~~rust
fn wybierz(warunek: bool) -> i32 {
    let wynik;
    if warunek { wynik = 42; } else { wynik = 0; }
    wynik
}
fn main() { assert_eq!(wybierz(true), 42); assert_eq!(wybierz(false), 0); }
~~~

## P01-2

Kolejne `let` opisują kolejne reprezentacje tego samego wejścia; `mut` nie jest potrzebne.

~~~rust
fn main() {
    let port = " 8080 ";
    let port = port.trim();
    let port: u16 = port.parse().expect("port");
    assert_eq!(port, 8080);
}
~~~


`trim` pożycza pierwotny literał, a `parse` tworzy nową wartość liczbową. Shadowing wyraża kolejne reprezentacje portu i pozwala porzucić niepotrzebne nazwy pośrednie. `expect` jest tutaj dopuszczone dla stałych danych ćwiczenia; wejście z konfiguracji powinno zwracać `Result` i określać, czy port zero jest legalny w danej domenie.

## P01-3

Shadowing nie niszczy starej wartości natychmiast. Oba bindingi opuszczają ten sam scope, więc nowszy jest niszczony przed starszym.

~~~rust
use std::cell::RefCell;
use std::rc::Rc;

struct Zapis(&'static str, Rc<RefCell<Vec<&'static str>>>);
impl Drop for Zapis { fn drop(&mut self) { self.1.borrow_mut().push(self.0); } }

fn main() {
    let log = Rc::new(RefCell::new(Vec::new()));
    {
        let x = Zapis("stary", log.clone());
        let x = Zapis("nowy", log.clone());
        let _ = (&x, &log);
    }
    assert_eq!(*log.borrow(), ["nowy", "stary"]);
}
~~~


Gdyby zamiast drugiego `let x` użyto przypisania do `let mut x`, stara wartość zostałaby zniszczona podczas przypisania, a nie dopiero przy wyjściu z zakresu. NLL może skrócić pożyczkę dziennika, ale nie przenosi destruktorów znaczników do miejsc ich ostatniego użycia. Przy zasobie takim jak blokada lepiej ujawnić granicę wewnętrznym blokiem lub `drop` niż polegać na przesłoniętej nazwie.
