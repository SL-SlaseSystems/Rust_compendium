[← Spis treści](../README.md)
<!-- status: expanded -->

# Atomiki i memory ordering

## Cele

Po tym rozdziale potrafisz:

- wskazać krawędzie happens-before w publikacji danych;
- dobrać poprawne porządki sukcesu i porażki CAS;


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
niekoniecznie CPU. Nie tworzy ogólnej synchronizacji między wątkami i nie
zastępuje platformowych reguł dostępu do MMIO lub DMA. Może służyć
specyficznym protokołom z handlerem sygnału w tym samym wątku.

## Metodyka dowodu

1. opisz stan i dozwolone przejścia;
2. wskaż jedną atomiczną zmienną synchronizującą;
3. narysuj relacje sequenced-before, reads-from i happens-before;
4. zacznij od mutexa albo SeqCst;
5. osłabiaj ordering pojedynczo z uzasadnieniem i testami Loom
   (**third-party**);
6. testuj na architekturze słabo uporządkowanej.


## Model formalny: co łączy dwa wątki

Rozumowanie o „przesuwaniu instrukcji” jest pomocną intuicją, ale nie dowodem. W jednym wątku mamy relację sequenced-before. Odczyt, który pobiera wartość z odpowiedniego zapisu Release, tworzy przy Acquire relację synchronizes-with. Połączenie tych relacji daje happens-before. Kluczowe jest wskazanie, który zapis odczytano; samo użycie słów Release i Acquire w dwóch dowolnych miejscach nie łączy wątków.

W przykładzie publikacji zapis `dane = 42` jest przed zapisem flagi Release. Odczyt Acquire, który zobaczył `true` z tego zapisu, następuje przed odczytem danych. Przechodniość daje: zapis danych happens-before odczyt danych. Pole `dane` jest atomowe, aby przykład pozostał bezpieczny także przy błędnym osłabieniu flagi, ale bez synchronizacji nie mamy uzasadnienia oczekiwanego wyniku. Zamiana tego pola na zwykłą niesynchronizowaną komórkę wymagałaby dodatkowego `unsafe` i przy złym protokole groziłaby UB.

To protokół jednorazowy. Jeżeli producent zacznie nadpisywać payload po pierwszym `true`, ta sama flaga nie zapewni automatycznie bezpiecznej kolejnej rundy. Potrzebny jest nowy stan, numer generacji, potwierdzenie odbioru albo blokada. „Flaga była kiedyś ustawiona” nie oznacza własności całej przyszłej historii danych.

RMW ma część odczytu i zapisu. `Acquire` na udanym RMW nie daje Release dla jego zapisu; `Release` nie daje Acquire dla odczytu. `AcqRel` łączy obie role, a `SeqCst` dodaje globalny porządek odpowiednich operacji. Nie zastępuje to analizy, czy wieloetapowy algorytm ma właściwy punkt linearyzacji.

~~~rust
use std::sync::atomic::{AtomicUsize, Ordering};
fn przejmij(stan: &AtomicUsize) -> bool {
    stan.compare_exchange(0, 1, Ordering::Acquire, Ordering::Relaxed).is_ok()
}
fn oddaj(stan: &AtomicUsize) { stan.store(0, Ordering::Release); }
fn main() {
    let stan = AtomicUsize::new(0);
    assert!(przejmij(&stan));
    assert!(!przejmij(&stan));
    oddaj(&stan);
    assert!(przejmij(&stan));
}
~~~

Przykład demonstruje wyłącznie przejścia flagi, nie kompletną blokadę chroniącą nieatomowe dane. Release podczas oddania może synchronizować udane Acquire następnego właściciela, jeśli odczyta ten zapis. Porażka CAS nie uzyskuje własności zasobu i nie potrzebuje tu publikowanych danych, więc Relaxed wystarcza. Brakuje guardu, obsługi panic, usypiania i dowodu dostępu do wnętrza; nie traktuj szkicu protokołu jak gotowego mutexa.

`spin_loop` jest wskazówką dla procesora, a nie synchronizacją ani gwarancją oddania czasu innym wątkom. Nie dowodzi postępu planisty. Test na jednej maszynie nie sprawdza wszystkich zachowań dopuszczonych przez model pamięci. Osłabianie porządków wymaga uzasadnienia niezależnego od wyników benchmarku.

## Diagnostyka kompilatora

Niepoprawny porządek dla load/store lub porażki CAS może zostać wykryty przez lint albo panic API. Porażka CAS nie zapisuje, więc `Release` i `AcqRel` nie są dozwolone w tym argumencie. Brak diagnostyki nie oznacza poprawności synchronizacji: `Relaxed` jest legalny w wielu miejscach, w których daje błędny protokół. Opisz odczytywany zapis, nie tylko nazwy użytych wariantów `Ordering`.

## Praktyka produkcyjna

Zapisz automat stanów, punkt linearyzacji i relacje happens-before obok implementacji. Dla niezależnych statystyk wybierz Relaxed; dla publikacji wskaż konkretne pary odczytu i zapisu. Zacznij od prostszej blokady, jeśli nie masz pełnego dowodu atomowego protokołu. Modelowanie Loom **third-party** pomaga eksplorować ograniczony model, lecz nie dowodzi własności kodu korzystającego z innych atomików lub pominiętych zachowań. Mierz opóźnienia przy konkurencji i zachowaj testy shutdown oraz ponownego użycia.

## Sprawdź, czy rozumiesz

- Czy dowolny load Acquire synchronizuje z dowolnym store Release?
- Dlaczego ponowne użycie flagi zmienia dowód protokołu?
- Która część udanego RMW jest osłabiona przy samym Acquire?

## Ćwiczenia

- `B17-1` — podstawowe: Wybierz Relaxed dla niezależnego licznika i odczytaj wynik po join. [Rozwiązanie](../rozwiazania/10_wspolbieznosc/05_atomics_i_memory_ordering.md#b17-1).
- `B17-2` — praktyczne: Rozpisz pełny łańcuch happens-before jednorazowej publikacji. [Rozwiązanie](../rozwiazania/10_wspolbieznosc/05_atomics_i_memory_ordering.md#b17-2).
- `B17-3` — pogłębione: Wyjaśnij dobór porządku porażki CAS przy przejmowaniu flagi oraz brak dowodu mutexa. [Rozwiązanie](../rozwiazania/10_wspolbieznosc/05_atomics_i_memory_ordering.md#b17-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [Ordering i model C++20](https://doc.rust-lang.org/std/sync/atomic/enum.Ordering.html)
- [AtomicUsize::compare_exchange](https://doc.rust-lang.org/std/sync/atomic/struct.AtomicUsize.html#method.compare_exchange)
- [Atomics: memory model](https://doc.rust-lang.org/std/sync/atomic/index.html)

## Powiązane tematy

- [`Send`, `Sync` i atomiki](../10_wspolbieznosc/04_send_sync_i_atomiki.md)
- [Lock-free i ABA](06_lock_free_i_aba.md)
- [`unsafe` i soundness](../21_unsafe_soundness_i_model_pamieci/01_unsafe_i_soundness.md)
