[← Spis treści](../README.md)
<!-- status: expanded -->

# `Send`, `Sync` i atomiki

## Cele

Po tym rozdziale potrafisz:

- wyprowadzić bounds wrappera z własności jego danych;
- odróżnić atomowy licznik od publikowania całego stanu;


`Send` i `Sync` są unsafe auto traits opisującymi bezpieczeństwo między
wątkami.

- `T: Send` — wartość `T` można bezpiecznie przenieść do innego wątku;
- `T: Sync` — `&T` można bezpiecznie współdzielić między wątkami;
- `T: Sync` jest związane z tym, że `&T: Send`.

Większość typów składających się z typów `Send`/`Sync` dostaje te traits
automatycznie. `Rc` nie jest `Send` ani `Sync`, a `RefCell<T>` nie jest
`Sync`, lecz może być `Send` przy `T: Send`; `Arc` jest thread-safe, ale
`Arc<T>` nie uczyni niebezpiecznego `T` bezpiecznym.

## Bounds na granicy

~~~rust
use std::thread;

fn w_tle<T, F>(zadanie: F) -> thread::JoinHandle<T>
where
    T: Send + 'static,
    F: FnOnce() -> T + Send + 'static,
{
    thread::spawn(zadanie)
}

fn main() {
    assert_eq!(w_tle(|| 40 + 2).join().unwrap(), 42);
}
~~~

Bounds wynikają z faktu, że closure i wynik przechodzą między wątkami, a
odłączony wątek może przeżyć bieżące referencje.

## Podstawowa atomika

Atomika wykonuje niepodzielne operacje na wspieranym typie:

~~~rust
use std::sync::{
    Arc,
    atomic::{AtomicUsize, Ordering},
};
use std::thread;

fn main() {
    let licznik = Arc::new(AtomicUsize::new(0));
    let watki: Vec<_> = (0..4)
        .map(|_| {
            let licznik = Arc::clone(&licznik);
            thread::spawn(move || {
                licznik.fetch_add(1, Ordering::Relaxed);
            })
        })
        .collect();
    for h in watki { h.join().unwrap(); }
    assert_eq!(licznik.load(Ordering::Relaxed), 4);
}
~~~

Relaxed gwarantuje atomowość licznika, lecz nie porządkuje innych odczytów i
zapisów. Do publikacji danych potrzebna jest relacja synchronizacji, często
Release/Acquire albo mutex.

## Ręczne implementacje są niebezpieczne

`unsafe impl Send for T` i `unsafe impl Sync for T` są obietnicą dla całego
bezpiecznego kodu. Błąd może prowadzić do undefined behavior. Typy z raw
pointers nie dostają automatycznie tych traits między innymi po to, aby
autor jawnie przeanalizował ownership, aliasing i synchronizację.

## Atomika czy blokada

Atomiki pasują do liczników, flag i dobrze udowodnionych protokołów.
Wielopolowy invariant jest zwykle prostszy i bezpieczniejszy za mutexem.
Lock-free nie znaczy wait-free, szybsze ani prostsze. Najpierw wybierz
poprawność, potem mierz contention.


## Model — bezpieczeństwo przenoszenia i pożyczania

`Send` odpowiada za przeniesienie wartości między wątkami, a `Sync` za bezpieczne udostępnienie wspólnej referencji. Są to różne pytania. `RefCell<T>` może być `Send`, gdy `T: Send`, ale nie jest `Sync`, bo jego mechanizm dynamicznych pożyczek nie jest synchronizowany między wątkami. `Rc<T>` nie jest ani `Send`, ani `Sync`, ponieważ klonowanie i niszczenie współdzielonych uchwytów modyfikuje nieatomowy licznik. To doprecyzowanie jest ważniejsze niż skrót „typ nie jest thread-safe”.

`Arc<T>` potrzebuje odpowiednich właściwości `T`; samo atomowe zliczanie referencji nie zabezpiecza wnętrza. `Arc<RefCell<T>>` nie zastępuje `Arc<Mutex<T>>`. Z kolei `Mutex<T>` może być `Sync` przy `T: Send`, ponieważ guard serializuje dostęp do wnętrza. Nie trzeba wymagać, by samo `T` było bezpieczne do równoczesnego współdzielenia bez ochrony.

~~~rust
use std::{cell::RefCell, sync::{Arc, Mutex}};
fn wymaga_send<T: Send>() {}
fn wymaga_sync<T: Sync>() {}
fn main() {
    wymaga_send::<RefCell<u32>>();
    wymaga_sync::<Mutex<RefCell<u32>>>();
    wymaga_send::<Arc<Mutex<RefCell<u32>>>>();
    let dane = Mutex::new(RefCell::new(7));
    *dane.lock().unwrap().borrow_mut() += 1;
    assert_eq!(*dane.lock().unwrap().borrow(), 8);
}
~~~

Asercje typów są sprawdzane podczas kompilacji i pokazują dokładny kontrakt. Przykład nie potrzebuje `RefCell` wewnątrz mutexa do zwykłej mutacji; służy rozdzieleniu dwóch mechanizmów. W realnym kodzie usuń zbędną warstwę, jeśli guard już daje wystarczającą mutowalność.

Własne raw pointers celowo nie uzyskują automatycznie `Send` i `Sync`. Ręczna implementacja musi objąć alokację, aliasing, destrukcję, dostęp współbieżny i ewentualne ograniczenie zasobu do konkretnego wątku. Uchwyt do systemowego API może być pamięciowo prosty, lecz mieć thread affinity. Nie dopisuj `unsafe impl` tylko dlatego, że kompilator odrzucił przekazanie go do `spawn`.

`'static` i `Send` są niezależne. Wartość może nie zawierać krótkich pożyczek, a mimo to nie nadawać się do przesłania, jak `Rc<String>`. Scoped thread może przyjąć pożyczkę o krótszym czasie życia, ale nadal wymaga bezpiecznego przeniesienia closure. Podobnie future przechowująca `Rc` przez `await` może być lokalna, a nieprzenośna między wątkami.

Atomowy licznik zapewnia niepodzielność `fetch_add`, nie całego „sprawdź i zarezerwuj”. Odczyt limitu i późniejszy inkrement mogą przejść jednocześnie w dwóch wątkach. Dla limitu trzeba jednej operacji CAS lub blokady obejmującej warunek i zmianę. Relaxed może być wystarczający dla niezależnej statystyki, ale nie publikuje obok leżącej kolekcji.

## Diagnostyka kompilatora

Komunikat „cannot be sent/shared between threads safely” zawiera łańcuch pól i przechwyceń prowadzący do problematycznego typu. Czytaj go do środka zamiast dodawać bounds na zewnętrznym wrapperze. Dla obiektu traitowego `dyn Trait` jawnie wymagaj `Send + Sync` tylko wtedy, gdy architektura tego wymaga. `unsafe impl` potrafi uciszyć błąd, ale nie stanowi naprawy bez dowodu wszystkich niezmienników.

## Praktyka produkcyjna

Sprawdzaj oczekiwane auto traits publicznych typów w kodzie testowym kompilacji. Dodanie `Rc`, guardu lub wskaźnika do prywatnego pola może usunąć `Send`, co dla konsumenta jest zmianą API. Nie narzucaj wielowątkowości komponentom celowo lokalnym. Wybierz blokadę dla wielopolowego stanu i atomikę dla jasno wyodrębnionej wartości. Profiluj rzeczywistą konkurencję: nawet atomowa operacja może być kosztowna przy wielu zapisach tej samej linii cache.

## Sprawdź, czy rozumiesz

- Czy `RefCell<u32>` jest `Send`, `Sync`, czy oba?
- Dlaczego `Arc` nie naprawia `RefCell`?
- Jak `Send` różni się od `'static`?

## Ćwiczenia

- `B16-1` — podstawowe: Sprawdź przy kompilacji `Send` dla `RefCell<u32>` oraz `Sync` dla `Mutex<RefCell<u32>>`. [Rozwiązanie](../rozwiazania/10_wspolbieznosc/04_send_sync_i_atomiki.md#b16-1).
- `B16-2` — praktyczne: Pokaż odrzucone wysłanie `Rc` do wątku i poprawkę przez `Arc`. [Rozwiązanie](../rozwiazania/10_wspolbieznosc/04_send_sync_i_atomiki.md#b16-2).
- `B16-3` — pogłębione: Wyjaśnij race condition limitu realizowanego przez oddzielne load i fetch_add. [Rozwiązanie](../rozwiazania/10_wspolbieznosc/04_send_sync_i_atomiki.md#b16-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [Send](https://doc.rust-lang.org/std/marker/trait.Send.html)
- [Sync i przykład RefCell](https://doc.rust-lang.org/std/marker/trait.Sync.html)
- [Arc: thread safety](https://doc.rust-lang.org/std/sync/struct.Arc.html#thread-safety)

## Powiązane tematy

- [`Arc` i blokady](03_arc_mutex_rwlock_i_condvar.md)
- [Atomiki i memory ordering](../10_wspolbieznosc/05_atomics_i_memory_ordering.md)
- [Lock-free i ABA](../10_wspolbieznosc/06_lock_free_i_aba.md)
