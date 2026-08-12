[← Spis treści](../README.md)

# `Arc`, `Mutex`, `RwLock` i `Condvar`

Współdzielony stan między wątkami zwykle łączy współdzielone ownership
`Arc<T>` z synchronizacją dostępu.

## `Arc<Mutex<T>>`

~~~rust
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let licznik = Arc::new(Mutex::new(0_u32));
    let mut watki = Vec::new();

    for _ in 0..4 {
        let licznik = Arc::clone(&licznik);
        watki.push(thread::spawn(move || {
            let mut guard = licznik.lock().unwrap();
            *guard += 1;
        }));
    }
    for h in watki { h.join().unwrap(); }
    assert_eq!(*licznik.lock().unwrap(), 4);
}
~~~

Guard odblokowuje mutex przez RAII. Skracaj jego zakres i nie wykonuj pod
blokadą wolnego I/O ani obcego callbacku.

## Poisoning

Jeżeli wątek panikuje z guardem mutexa, standardowy mutex staje się poisoned.
`lock` zwraca wtedy `PoisonError`, ale dane nadal można odzyskać przez
`into_inner` po świadomej ocenie invariants. `unwrap` nie jest jedyną
strategią — może propagować panic do kolejnych wątków.

## `RwLock<T>`

RwLock pozwala wielu czytelnikom albo jednemu piszącemu. Nie gwarantuje
konkretnej polityki fairness; zależy od systemu. Przy krótkim stanie i częstym
zapisie mutex może być szybszy. Zawsze mierz.

~~~rust
use std::sync::RwLock;

fn main() {
    let dane = RwLock::new(vec![1, 2]);
    {
        let odczyt = dane.read().unwrap();
        assert_eq!(odczyt.len(), 2);
    }
    dane.write().unwrap().push(3);
    assert_eq!(&*dane.read().unwrap(), &[1, 2, 3]);
}
~~~

## `Condvar`

Condition variable czeka na zmianę predykatu chronionego tym samym mutexem.
Zawsze sprawdzaj warunek w pętli, bo występują spurious wakeups:

~~~rust
use std::sync::{Arc, Condvar, Mutex};
use std::thread;

fn main() {
    let para = Arc::new((Mutex::new(false), Condvar::new()));
    let worker = Arc::clone(&para);
    let h = thread::spawn(move || {
        let (lock, cv) = &*worker;
        *lock.lock().unwrap() = true;
        cv.notify_one();
    });

    let (lock, cv) = &*para;
    let mut gotowe = lock.lock().unwrap();
    while !*gotowe {
        gotowe = cv.wait(gotowe).unwrap();
    }
    h.join().unwrap();
}
~~~

## Deadlock

Rust zapobiega data races, ale nie deadlockom. Ustal globalną kolejność
blokad, unikaj trzymania kilku naraz i rozważ message passing. `try_lock`
może pomóc, lecz retry bez backoff potrafi stworzyć livelock.

## Powiązane tematy

- [Kanały](02_kanaly_i_message_passing.md)
- [`Send` i `Sync`](04_send_sync_i_atomiki.md)
- [Panic safety](../06_bledy/03_panic_unwind_i_abort.md)
