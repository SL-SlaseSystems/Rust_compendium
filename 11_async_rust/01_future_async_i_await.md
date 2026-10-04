[← Spis treści](../README.md)

# `Future`, `async` i `await`

Async Rust opisuje pracę, która może się zawiesić bez blokowania wątku.
`async fn` zwraca anonimowy typ implementujący `Future`. Samo utworzenie
future nie uruchamia jego ciała; future musi być polled przez executor.

## Składnia

~~~rust
use std::future::Future;

async fn pobierz_id() -> u64 {
    42
}

fn przyjmuje_future<F>(_: F)
where
    F: Future<Output = u64>,
{}

fn main() {
    przyjmuje_future(pobierz_id());
}
~~~

`.await` jest dozwolone w kontekście async i próbuje doprowadzić future do
`Ready`. Jeśli wynik to `Pending`, task oddaje sterowanie executorowi:

~~~rust
async fn dwa_kroki() -> u64 {
    let a = async { 20_u64 }.await;
    let b = async { 22_u64 }.await;
    a + b
}

fn main() {
    let _future = dwa_kroki();
}
~~~

Standard library definiuje `Future` i mechanikę `Poll`/`Waker`, ale nie
dostarcza ogólnego executora sieciowego ani timera. Runtime’y Tokio i
async-std są **third-party**.

## Async block i capture

`async { ... }` zwykle pożycza otoczenie, a `async move { ... }` przejmuje
bindingi. Podobnie jak closure, blok generuje anonimową state machine.

~~~rust
fn main() {
    let tekst = String::from("dane");
    let future = async move {
        tekst.len()
    };
    let _ = future;
}
~~~

## Współbieżność a równoległość

Wiele futures może współbieżnie postępować na jednym wątku, jeśli często
oddają sterowanie przy oczekiwaniu. Obliczenie CPU bez `await` blokuje cały
wątek executora. Równoległość wymaga wielu wątków lub osobnej puli pracy.

## Błędy

Async funkcja może zwracać `Result` i używać `?` normalnie:

~~~rust
use std::num::ParseIntError;

async fn parsuj(s: &str) -> Result<i32, ParseIntError> {
    let n = s.parse::<i32>()?;
    Ok(n * 2)
}

fn main() {
    let _ = parsuj("21");
}
~~~

Błąd powstaje dopiero przy poll. Upuszczenie nieukończonej future anuluje ją
przez destrukcję stanu, co ma konsekwencje dla cancellation safety.

## Powiązane tematy

- [Executor, `Waker` i `poll`](02_executor_waker_i_poll.md)
- [Taski, join, select i stream](03_taski_join_select_i_stream.md)
- [Pinning](../zaawansowane/07_pin_unpin_i_self_referential.md)
