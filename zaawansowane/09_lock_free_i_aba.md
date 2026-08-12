[← Spis treści](../README.md)

# Lock-free i problem ABA

Algorytm **lock-free** gwarantuje postęp systemu jako całości: jakiś wątek
zakończy operację. **Wait-free** daje skończoną liczbę kroków każdemu
uczestnikowi. **Obstruction-free** gwarantuje postęp tylko bez konkurencji.
Żadne z nich nie znaczy automatycznie „szybsze”.

## CAS loop

Najprostszy wzorzec aktualizuje jedną wartość:

~~~rust
use std::sync::atomic::{AtomicUsize, Ordering};

fn maksimum(atom: &AtomicUsize, kandydat: usize) {
    let mut obecne = atom.load(Ordering::Relaxed);
    while kandydat > obecne {
        match atom.compare_exchange_weak(
            obecne,
            kandydat,
            Ordering::Relaxed,
            Ordering::Relaxed,
        ) {
            Ok(_) => return,
            Err(nowsze) => obecne = nowsze,
        }
    }
}

fn main() {
    let x = AtomicUsize::new(4);
    maksimum(&x, 9);
    maksimum(&x, 2);
    assert_eq!(x.load(Ordering::Relaxed), 9);
}
~~~

Operacja jest idempotentna względem retry. Closure CAS nie może wykonywać
efektu zewnętrznego zakładając, że zostanie wywołane raz.

## ABA

Wątek A odczytuje pointer o wartości A i zostaje zatrzymany. Wątek B:

1. zmienia head A → B;
2. zwalnia A;
3. allocator ponownie używa tego samego adresu;
4. ustawia head na liczbowo „A”.

CAS wątku A widzi ten sam adres i uznaje, że stan się nie zmienił, choć węzeł
ma inną tożsamość. Sam ordering nie rozwiązuje ABA.

Techniki:

- licznik wersji w tagged pointerze, jeśli zakres i alignment wystarczą;
- hazard pointers;
- epoch-based reclamation;
- reference counting zaprojektowane dla atomików;
- brak natychmiastowego ponownego użycia pamięci.

Każda ma subtelne warunki postępu, overflow, pinning wątku i cleanup.

## Reclamation jest trudniejsza niż CAS

Usunięcie pointera z listy nie znaczy, że żaden wątek go już nie odczyta.
Natychmiastowy `Box::from_raw` może dać use-after-free. Trzeba udowodnić:

- kiedy wszyscy czytelnicy przestali mieć pointer;
- jak wątek ogłasza chroniony węzeł;
- co dzieje się po panic lub zawieszeniu wątku;
- czy destructor elementu może re-enterować strukturę;
- czy shutdown odzyskuje retired nodes.

Dlatego ręczna lock-free lista jest zwykle złym pierwszym wyborem.

## Pointer tagging i provenance

Przechowuj pointer w `AtomicPtr<T>` zamiast `AtomicUsize`, jeśli to pointer.
Strict Provenance `map_addr` pozwala zmieniać bity adresu przy zachowaniu
provenance. Przed dereferencją usuń tag i udowodnij alignment oraz granice
alokacji. Liczba wolnych bitów wynika z alignment, nie intuicji.

## False sharing i contention

Dwie niezależne atomiki na jednej cache line mogą wzajemnie unieważniać cache.
Padding może pomóc, ale layout i rozmiar cache line zależą od platformy.
CAS pod wysoką konkurencją może wielokrotnie ponawiać, zużywać energię i być
wolniejszy od mutexa usypiającego wątek.

## Narzędzia

- Loom (**third-party**) eksploruje przeploty dla własnych odpowiedników
  atomików;
- Miri wykrywa część UB, ale nie jest modelem wydajności;
- sanitizery wykrywają wykonane data races;
- model checker lub formalny dowód jest właściwy dla krytycznego algorytmu.

Najpierw użyj `Mutex`, kanału albo sprawdzonej kolekcji. Lock-free wybieraj po
profilu i z planem audytu.

## Powiązane tematy

- [Atomiki i memory ordering](08_atomics_i_memory_ordering.md)
- [Raw pointers i provenance](02_raw_pointers_aliasing_i_provenance.md)
- [`Arc` i blokady](../09_wspolbieznosc/03_arc_mutex_rwlock_i_condvar.md)
