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

## Co dalej

Kontynuuj przez async Rust. Memory ordering i lock-free traktuj jako specjalizację wymagającą benchmarków, Miri, sanitizerów i przeglądu invariants.
