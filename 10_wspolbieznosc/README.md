[← Spis treści](../README.md)

# 10. Współbieżność

## Dla kogo i po co

Dla osób budujących programy wielowątkowe: od bezpiecznych wątków i kanałów po atomiki i struktury lock-free.

## Wymagania wstępne

Ownership, smart pointery, traits oraz obsługa błędów. Dwa ostatnie materiały wymagają także swobody w czytaniu `unsafe`.

## Kolejność materiałów

1. [Wątki i scoped threads](01_watki_i_scoped_threads.md)
2. [Kanały i message passing](02_kanaly_i_message_passing.md)
3. [`Arc`, `Mutex`, `RwLock` i `Condvar`](03_arc_mutex_rwlock_i_condvar.md)
4. [`Send`, `Sync` i atomiki](04_send_sync_i_atomiki.md)
5. [Atomiki i memory ordering](05_atomics_i_memory_ordering.md)
6. [Lock-free i problem ABA](06_lock_free_i_aba.md)

## Po tym dziale

Umiesz wybrać model komunikacji, uzasadnić synchronizację i rozpoznać, kiedy atomiki lub lock-free są niepotrzebnym ryzykiem.

## Praca z rozdziałami

Każdy rozdział zawiera model działania, przykłady, diagnostykę, decyzje produkcyjne i trzy zadania o rosnącym poziomie trudności. Najpierw przewiduj wynik kodu, następnie go uruchom, a dopiero potem porównaj rozwiązanie.

- [Wątki i scoped threads: rozwiązania](../rozwiazania/10_wspolbieznosc/01_watki_i_scoped_threads.md)
- [Kanały i message passing: rozwiązania](../rozwiazania/10_wspolbieznosc/02_kanaly_i_message_passing.md)
- [`Arc`, `Mutex`, `RwLock` i `Condvar`: rozwiązania](../rozwiazania/10_wspolbieznosc/03_arc_mutex_rwlock_i_condvar.md)
- [`Send`, `Sync` i atomiki: rozwiązania](../rozwiazania/10_wspolbieznosc/04_send_sync_i_atomiki.md)
- [Atomiki i memory ordering: rozwiązania](../rozwiazania/10_wspolbieznosc/05_atomics_i_memory_ordering.md)
- [Lock-free i problem ABA: rozwiązania](../rozwiazania/10_wspolbieznosc/06_lock_free_i_aba.md)

Przykłady samowystarczalne odnoszą się do Rust 1.90, Edition 2024. Bloki `text` z zależnościami zewnętrznymi lub wymaganiami środowiskowymi opisują oddzielny kontrakt; nie są testami wykonanymi przez rustdoc.

## Co dalej

Kontynuuj przez async Rust. Memory ordering i lock-free traktuj jako specjalizację wymagającą benchmarków, Miri, sanitizerów i przeglądu invariants.
