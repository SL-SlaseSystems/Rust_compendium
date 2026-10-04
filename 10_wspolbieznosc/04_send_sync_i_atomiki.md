[← Spis treści](../README.md)

# `Send`, `Sync` i atomiki

`Send` i `Sync` są unsafe auto traits opisującymi bezpieczeństwo między
wątkami.

- `T: Send` — wartość `T` można bezpiecznie przenieść do innego wątku;
- `T: Sync` — `&T` można bezpiecznie współdzielić między wątkami;
- `T: Sync` jest związane z tym, że `&T: Send`.

Większość typów składających się z typów `Send`/`Sync` dostaje te traits
automatycznie. `Rc` i `RefCell` ich nie mają; `Arc` jest thread-safe, ale
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

## Powiązane tematy

- [`Arc` i blokady](03_arc_mutex_rwlock_i_condvar.md)
- [Atomiki i memory ordering](../10_wspolbieznosc/05_atomics_i_memory_ordering.md)
- [Lock-free i ABA](../10_wspolbieznosc/06_lock_free_i_aba.md)
