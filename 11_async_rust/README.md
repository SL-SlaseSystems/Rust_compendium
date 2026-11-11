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

## Praca z rozdziałami

Każdy rozdział zawiera model działania, przykłady, diagnostykę, decyzje produkcyjne i trzy zadania o rosnącym poziomie trudności. Najpierw przewiduj wynik kodu, następnie go uruchom, a dopiero potem porównaj rozwiązanie.

- [`Future`, `async` i `await`: rozwiązania](../rozwiazania/11_async_rust/01_future_async_i_await.md)
- [Executor, `Waker` i `poll`: rozwiązania](../rozwiazania/11_async_rust/02_executor_waker_i_poll.md)
- [Taski, join, select i stream: rozwiązania](../rozwiazania/11_async_rust/03_taski_join_select_i_stream.md)
- [Anulowanie, timeouty i kod blokujący: rozwiązania](../rozwiazania/11_async_rust/04_anulowanie_timeouty_i_blocking.md)
- [`Pin`, `Unpin` i typy self-referential: rozwiązania](../rozwiazania/11_async_rust/05_pin_unpin_i_self_referential.md)

Przykłady samowystarczalne odnoszą się do Rust 1.90, Edition 2024. Bloki `text` z zależnościami zewnętrznymi lub wymaganiami środowiskowymi opisują oddzielny kontrakt; nie są testami wykonanymi przez rustdoc.

## Co dalej

Przejdź do sieci, protokołów i aplikacji webowych. `Pin` czytaj głębiej dopiero przy tworzeniu własnych future, runtime'ów lub abstrakcji self-referential.
