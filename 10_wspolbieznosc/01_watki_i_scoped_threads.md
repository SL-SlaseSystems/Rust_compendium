[← Spis treści](../README.md)

# Wątki i scoped threads

`std::thread` udostępnia wątki systemowe. Closure przekazane do
`thread::spawn` musi być `'static` i `Send`, ponieważ wątek może przeżyć
wywołujący zakres.

## Spawn i join

~~~rust
use std::thread;

fn main() {
    let dane = vec![1, 2, 3, 4];
    let uchwyt = thread::spawn(move || dane.into_iter().sum::<i32>());
    let suma = uchwyt.join().expect("wątek nie powinien panikować");
    assert_eq!(suma, 10);
}
~~~

`move` przenosi wektor do closure. `JoinHandle::join` zwraca `Result`, bo
wątek może zakończyć się panic. Upuszczenie handle’a odłącza wątek; nie
zatrzymuje go automatycznie.

## Scoped threads

`thread::scope` gwarantuje join przed końcem zakresu, dlatego wątki mogą
pożyczać dane lokalne:

~~~rust
use std::thread;

fn main() {
    let dane = [1, 2, 3, 4, 5, 6];
    let (lewa, prawa) = dane.split_at(3);

    let (a, b) = thread::scope(|s| {
        let a = s.spawn(|| lewa.iter().sum::<i32>());
        let b = s.spawn(|| prawa.iter().sum::<i32>());
        (a.join().unwrap(), b.join().unwrap())
    });

    assert_eq!(a + b, 21);
}
~~~

Scoped threads nie eliminują kosztu tworzenia wątku. Dla wielu małych zadań
używa się puli wątków, np. crate’a **third-party** Rayon dla data parallelism.

## Builder i rozmiar stosu

`thread::Builder` nadaje nazwę oraz rozmiar stosu i zwraca błąd przy tworzeniu.
Nazwa pomaga w diagnostyce. Zbyt mały stos prowadzi do overflow, zbyt duży
rezerwuje przestrzeń adresową; nie dobieraj go bez pomiaru.

## Kooperacyjne zatrzymanie

Rust nie ma bezpiecznego „kill thread”. Przekaż token anulowania, kanał albo
`AtomicBool` i zaprojektuj punkty sprawdzania:

~~~rust
use std::sync::{
    Arc,
    atomic::{AtomicBool, Ordering},
};
use std::thread;

fn main() {
    let stop = Arc::new(AtomicBool::new(false));
    let worker_stop = Arc::clone(&stop);
    let h = thread::spawn(move || {
        while !worker_stop.load(Ordering::Relaxed) {
            thread::yield_now();
        }
        "zatrzymano"
    });
    stop.store(true, Ordering::Relaxed);
    assert_eq!(h.join().unwrap(), "zatrzymano");
}
~~~

Relaxed wystarcza tutaj tylko dla samej flagi; nie publikuje dodatkowych
danych. Zaawansowane porządki pamięci opisuje osobny rozdział.

## Powiązane tematy

- [Kanały](02_kanaly_i_message_passing.md)
- [`Send`, `Sync` i atomiki](04_send_sync_i_atomiki.md)
- [Atomiki i memory ordering](../zaawansowane/08_atomics_i_memory_ordering.md)
