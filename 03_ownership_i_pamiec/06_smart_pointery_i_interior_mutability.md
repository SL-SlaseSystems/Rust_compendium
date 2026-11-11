[← Spis treści](../README.md)
<!-- status: expanded -->

# Smart pointery i interior mutability

> Przykłady: **stable**, Rust 1.90.0, Edition 2024. Źródła sprawdzono 11 listopada 2026 r.

## Cele

Po tym rozdziale potrafisz:

- dobrać pojedynczą lub współdzieloną własność osobno od mutowalności;
- wykryć konflikt `RefCell` i skrócić życie guarda;
- przerwać cykl własności przez `Weak` i obsłużyć nieudane `upgrade`;

## Model — własność oraz dostęp to dwie decyzje


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

## Reguły — nie składaj typów bez potrzeby

`Rc<RefCell<T>>` łączy dwa niezależne mechanizmy: `Rc` ustala liczbę właścicieli, a `RefCell` sprawdza dostęp do jednego `T`. Zewnętrzne `Rc` nie usuwa kontroli pożyczek. `Arc<T>` zmienia sposób współdzielenia między wątkami, ale nie czyni automatycznie wnętrza `T` bezpiecznym do współbieżnej mutacji. Na przykład `Arc<RefCell<T>>` nie jest zamiennikiem `Arc<Mutex<T>>`.

`RefCell::borrow()` zwraca `Ref`, a `borrow_mut()` — `RefMut`. To obiekty posiadające wpis w dynamicznej kontroli pożyczek; ich zniszczenie zwalnia uprawnienie. Koniec ostatniego odczytu guarda nie musi zniszczyć go wcześniej. Użyj bloku albo jawnego `drop`, zwłaszcza przed callbackiem, który może ponownie wejść do tej samej struktury.

~~~rust
use std::cell::RefCell;
fn main() {
    let stan = RefCell::new(vec![1, 2]);
    let odczyt = stan.borrow();
    assert!(stan.try_borrow_mut().is_err());
    drop(odczyt);
    {
        let mut zapis = stan.try_borrow_mut().expect("brak aktywnej pożyczki");
        zapis.push(3);
    }
    assert_eq!(*stan.borrow(), [1, 2, 3]);
}
~~~

Pierwszy konflikt jest oczekiwanym `Err`, więc przykład nie wymaga wywołania paniki. W projekcie z callbackami zdecyduj, czy taki konflikt jest błędem API, czy zdarzeniem, które można odroczyć. `try_borrow_mut` daje możliwość obsługi, ale samo ignorowanie błędu może utracić aktualizację.

`Cell<T>` nie wydaje zwykłej referencji do zmienialnego wnętrza. `get` wymaga `Copy`, natomiast `set`, `replace` i `take` pozwalają operować także na innych typach przy odpowiednich bounds. Jest dobry dla małego licznika lub stanu wymienianego w całości. `RefCell` jest potrzebny wtedy, gdy trzeba pożyczyć wnętrze i wykonać na nim dłuższą operację.

`Weak` nie utrzymuje wartości przy życiu. `upgrade` zwraca `Option<Rc<T>>`, ponieważ ostatni właściciel mógł już zniknąć. W drzewie rodzic może posiadać dzieci przez silne `Rc`, a dziecko wskazywać rodzica przez `Weak`. Zmienienie tylko jednego dowolnego odnośnika nie dowodzi braku wszystkich cykli w bardziej złożonym grafie; opisz kierunek własności całej struktury.

## Diagnostyka kompilatora

Nie można uzyskać dowolnej mutacji przez współdzielone `Rc`. Próba zwykłego przypisania wymagałaby `DerefMut`, którego `Rc` nie udostępnia.

~~~compile_fail
use std::rc::Rc;
fn main() {
    let mut dane = Rc::new(String::from("A"));
    dane.push('B');
}
~~~

Jeżeli właściciel jest rzeczywiście jeden, `Rc::get_mut(&mut dane)` zwraca opcjonalny wyłączny dostęp; wymaga braku innych silnych i słabych uchwytów. `Rc::make_mut` może sklonować dane, zapewniając copy-on-write, a przy samych `Weak` je odłączyć. `RefCell` wybierz dla współdzielonego stanu o jednej tożsamości. Konflikt dynamiczny nie jest `compile_fail`: sprawdzaj go przez `try_borrow`.

## Praktyka produkcyjna

Rysuj silne krawędzie grafu własności i osobno relacje obserwacji. `strong_count` jest narzędziem diagnostycznym, nie protokołem synchronizacji ani dowodem, że właściciel zaraz nie zniknie. Przy `Weak` obsłuż normalny brak zasobu: cache może wrócić do źródła, a usunięty rodzic oznaczać odłączony węzeł.

Trzymaj guardy krótko i nie wywołuj nieznanego kodu z aktywnym `RefMut`. Nawet jednowątkowa reentrancja potrafi doprowadzić do paniki. Zanim dodasz interior mutability, sprawdź, czy da się przekazać `&mut T` z warstwy koordynującej. Taki projekt eliminuje klasę konfliktów dynamicznych i zwykle prostszy jest w testowaniu.

## Sprawdź, czy rozumiesz

1. Który składnik `Rc<RefCell<T>>` kontroluje właścicieli, a który pożyczki?
2. Dlaczego `Arc<RefCell<T>>` nie rozwiązuje współbieżnej mutacji?
3. Czemu odczyt `strong_count` nie zastępuje `upgrade`?

## Ćwiczenia

- `A15-1` — podstawowe: utwórz dwa `Rc<String>` do tego samego tekstu i sprawdź tożsamość przez `Rc::ptr_eq` [Rozwiązanie](../rozwiazania/03_ownership_i_pamiec/06_smart_pointery_i_interior_mutability.md#a15-1).
- `A15-2` — praktyczne: obsłuż konflikt `RefCell` przez `try_borrow_mut`, a po zwolnieniu czytelnika skutecznie zmień wartość [Rozwiązanie](../rozwiazania/03_ownership_i_pamiec/06_smart_pointery_i_interior_mutability.md#a15-2).
- `A15-3` — pogłębione: zbuduj rodzica silnie posiadającego dziecko i dziecko ze słabą referencją do rodzica; po usunięciu rodzica sprawdź `upgrade` [Rozwiązanie](../rozwiazania/03_ownership_i_pamiec/06_smart_pointery_i_interior_mutability.md#a15-3).

## Źródła i zakres stabilności

Kontrakty pożyczek dynamicznych: [std::cell](https://doc.rust-lang.org/std/cell/index.html). Warunki unikalności: [Rc::get_mut](https://doc.rust-lang.org/std/rc/struct.Rc.html#method.get_mut) i [Rc::make_mut](https://doc.rust-lang.org/std/rc/struct.Rc.html#method.make_mut).

## Powiązane tematy

- [`Arc`, `Mutex` i `RwLock`](../10_wspolbieznosc/03_arc_mutex_rwlock_i_condvar.md)
- [Pinning](../11_async_rust/05_pin_unpin_i_self_referential.md)
- [`unsafe` i soundness](../21_unsafe_soundness_i_model_pamieci/01_unsafe_i_soundness.md)
