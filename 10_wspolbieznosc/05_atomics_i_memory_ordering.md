[← Spis treści](../README.md)

# Atomiki i memory ordering

Atomika gwarantuje niepodzielność konkretnej operacji. Memory ordering mówi,
jak ta operacja porządkuje inne odczyty i zapisy widziane przez różne wątki.
Rust używa modelu porządków zgodnego z C++20.

## Data race a race condition

Data race to niesynchronizowane współbieżne dostępy do tego samego miejsca,
z których co najmniej jeden jest zapisem nieatomowym — jest UB. Race condition
jest szerszym błędem zależnym od kolejności i może istnieć w całkowicie
bezpiecznym kodzie, np. check-then-act na dwóch blokadach.

Atomika usuwa data race dla własnej wartości, ale nie gwarantuje poprawności
całego protokołu.

## Porządki

- `Relaxed` — atomowość bez synchronizacji innych operacji;
- `Release` — wcześniejsze operacje nie przechodzą logicznie za publikację;
- `Acquire` — późniejsze operacje nie przechodzą przed przejęcie;
- `AcqRel` — oba kierunki dla read-modify-write;
- `SeqCst` — Acquire/Release plus jeden globalny porządek wszystkich operacji
  SeqCst.

Store przyjmuje Relaxed, Release lub SeqCst. Load — Relaxed, Acquire lub
SeqCst. Nie każda kombinacja jest logicznie dozwolona.

## Publikacja Release/Acquire

~~~rust
use std::sync::{
    Arc,
    atomic::{AtomicBool, AtomicUsize, Ordering},
};
use std::thread;

struct Stan {
    dane: AtomicUsize,
    gotowe: AtomicBool,
}

fn main() {
    let stan = Arc::new(Stan {
        dane: AtomicUsize::new(0),
        gotowe: AtomicBool::new(false),
    });
    let producent = Arc::clone(&stan);

    let h = thread::spawn(move || {
        producent.dane.store(42, Ordering::Relaxed);
        producent.gotowe.store(true, Ordering::Release);
    });

    while !stan.gotowe.load(Ordering::Acquire) {
        std::hint::spin_loop();
    }
    assert_eq!(stan.dane.load(Ordering::Relaxed), 42);
    h.join().unwrap();
}
~~~

Acquire odczytujący wartość z Release tworzy synchronizes-with. Wszystko
happens-before Release staje się widoczne po Acquire. Gdyby flaga była
Relaxed, ten związek nie istniałby, nawet jeśli test na x86 zawsze przechodzi.

## Read-modify-write

`fetch_add`, `swap` i `compare_exchange` jednocześnie czytają i zapisują.
CAS ma osobny ordering sukcesu oraz porażki:

~~~rust
use std::sync::atomic::{AtomicUsize, Ordering};

fn zwieksz_do_limit(licznik: &AtomicUsize, limit: usize) -> bool {
    let mut obecna = licznik.load(Ordering::Relaxed);
    loop {
        if obecna >= limit {
            return false;
        }
        match licznik.compare_exchange_weak(
            obecna,
            obecna + 1,
            Ordering::Relaxed,
            Ordering::Relaxed,
        ) {
            Ok(_) => return true,
            Err(nowsza) => obecna = nowsza,
        }
    }
}

fn main() {
    let x = AtomicUsize::new(0);
    assert!(zwieksz_do_limit(&x, 1));
    assert!(!zwieksz_do_limit(&x, 1));
}
~~~

`compare_exchange_weak` może zawieść pozornie i jest właściwe w pętli.
Failure ordering nie wykonuje store, więc nie może być Release ani AcqRel.

## Fences

`fence` porządkuje operacje między atomikami według formalnych reguł, ale nie
„flushuje całej pamięci” magicznie. `compiler_fence` ogranicza kompilator,
niekoniecznie CPU, i ma zastosowania m.in. przy sygnałach oraz DMA pod bardzo
konkretnym kontraktem.

## Metodyka dowodu

1. opisz stan i dozwolone przejścia;
2. wskaż jedną atomiczną zmienną synchronizującą;
3. narysuj relacje sequenced-before, reads-from i happens-before;
4. zacznij od mutexa albo SeqCst;
5. osłabiaj ordering pojedynczo z uzasadnieniem i testami Loom
   (**third-party**);
6. testuj na architekturze słabo uporządkowanej.

## Powiązane tematy

- [`Send`, `Sync` i atomiki](../10_wspolbieznosc/04_send_sync_i_atomiki.md)
- [Lock-free i ABA](06_lock_free_i_aba.md)
- [`unsafe` i soundness](../21_unsafe_soundness_i_model_pamieci/01_unsafe_i_soundness.md)
