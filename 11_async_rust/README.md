[← Spis treści](../README.md)

# 11. Async Rust

## Dla kogo i po co

Dla osób tworzących serwisy sieciowe i systemy wykonujące wiele operacji I/O bez blokowania wątków.

## Wymagania wstępne

Closures, traits, lifetimes, `Result` i podstawy współbieżności.

## Kolejność materiałów

1. [`Future`, `async` i `await`](01_future_async_i_await.md)
2. [Executor, `Waker` i `poll`](02_executor_waker_i_poll.md)
3. [Taski, `join`, `select` i strumienie](03_taski_join_select_i_stream.md)
4. [Anulowanie, timeouty i kod blokujący](04_anulowanie_timeouty_i_blocking.md)
5. [`Pin`, `Unpin` i typy self-referential](05_pin_unpin_i_self_referential.md)

## Po tym dziale

Rozumiesz cykl życia future, współpracę z executorem oraz zasady anulowania i izolowania pracy blokującej.

## Co dalej

Przejdź do sieci, protokołów i aplikacji webowych. `Pin` czytaj głębiej dopiero przy tworzeniu własnych future, runtime'ów lub abstrakcji self-referential.
