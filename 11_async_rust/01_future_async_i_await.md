[← Spis treści](../README.md)
<!-- status: expanded -->

# `Future`, `async` i `await`

## Cele

Po tym rozdziale potrafisz:

- wyjaśnić leniwe ciało `async fn` i punkty zawieszenia;
- wyprowadzić własność oraz `Send` ze stanu future;


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


## Model — future przechowuje to, czego potrzebuje po zawieszeniu

Wywołanie `async fn` tworzy wartość z argumentami; ciało zaczyna wykonywać się przy poll. Wyrażenia użyte do obliczenia argumentów są jednak wykonywane podczas zwykłego wywołania. „Async jest leniwe” nie oznacza więc, że każdy efekt w całym otoczeniu zostaje odroczony. Funkcja zwracająca `impl Future`, która sama nie jest `async fn`, może wykonać przygotowanie jeszcze przed zwróceniem future.

`.await` nie obiecuje oddania czasu executorowi. Jeśli oczekiwana future jest gotowa, wykonanie idzie dalej w tym samym poll. Pętla zawierająca wiele natychmiastowo gotowych `await` może nadal długo zajmować wątek. Yield i budżety kooperacyjne są kontraktami konkretnego runtime’u, a nie automatycznym efektem każdego słowa `await`.

~~~rust
use std::{cell::Cell, future::Future, pin::pin, task::{Context, Poll, Waker}};
async fn policz(licznik: &Cell<u32>) -> u32 {
    licznik.set(licznik.get() + 1);
    async { 42 }.await
}
fn main() {
    let licznik = Cell::new(0);
    let mut f = pin!(policz(&licznik));
    assert_eq!(licznik.get(), 0);
    let mut cx = Context::from_waker(Waker::noop());
    assert_eq!(f.as_mut().poll(&mut cx), Poll::Ready(42));
    assert_eq!(licznik.get(), 1);
}
~~~

To kontrolowany pojedynczy poll future, która kończy się natychmiast. Waker bez działania nie obsłuży prawdziwego oczekiwania na I/O, dlatego kod nie jest ogólnym executorem. Pokazuje moment wykonania efektu bez zależności zewnętrznych. Po `Ready` nie pollujemy ponownie.

Po każdym potencjalnym zawieszeniu stan musi zawierać wartości używane później. Jeśli przechowywany `Rc` albo standardowy guard mutexa nie jest `Send`, cała future może nie być `Send`. To istotne dla wielowątkowego `spawn`, którego kontrakt jest osobny od samej definicji `Future`. Lokalna future może być całkiem poprawna bez `Send`; problem pojawia się dopiero przy przekroczeniu określonej granicy.

`async move` przejmuje przechwycone bindingi, lecz przechwycona referencja nadal jest referencją. Do niezależnego taska przekaż posiadane dane albo kontrolowane `Arc`, jeśli zadanie ma przeżyć bieżący zakres. Nie klonuj całej konfiguracji bez powodu; wybierz mały snapshot danych potrzebnych do pracy. Własność taska powinna być powiązana z właścicielem uchwytu i planem shutdown.

Przerwanie future przez Drop niszczy jej zachowany stan. Nie cofa efektów wykonanych przed zawieszeniem. Backpressure nie wynika też z samego `await`: nieograniczona kolejka może zwracać gotowość natychmiast i pozwolić producentowi zająć pamięć. Limit kolejki, liczby tasków i rozmiaru payloadu trzeba zaprojektować jawnie.

## Diagnostyka kompilatora

`E0728` sygnalizuje `await` poza kontekstem async. Błąd `future cannot be sent between threads safely` wymaga odczytania listy wartości zachowanych przez punkt `await`. Skróć zakres guardu przed oczekiwaniem albo wybierz świadomie lokalny model wykonania. Ostrzeżenie o nieużytej future może oznaczać, że operacja nigdy nie została wykonana. Samo przypisanie do `_` nie uruchamia jej ciała.

## Praktyka produkcyjna

Ustal, kto polluje pracę, kto posiada taski oraz kto odbiera ich błędy. Nie wprowadzaj async do czysto obliczeniowej funkcji tylko dla zgodności nazwy z resztą systemu. Kontroluj pamięć zachowaną w stanie future: duży bufor żyjący przez wiele `await` mnoży koszt przez liczbę żądań. Testuj anulowanie w istotnych punktach i unikaj blokującego I/O na wątku executora. Rozróżniaj gwarancje standardowego traitu od zachowania wybranego runtime’u **third-party**.

## Sprawdź, czy rozumiesz

- Czy każdy `await` oddaje sterowanie?
- Jakie efekty zachodzą przed utworzeniem future z argumentów `async fn`?
- Dlaczego `async move` nie naprawia krótkiej referencji?

## Ćwiczenia

- `B19-1` — podstawowe: Sprawdź licznikiem, że ciało `async fn` wykonuje się dopiero przy poll. [Rozwiązanie](../rozwiazania/11_async_rust/01_future_async_i_await.md#b19-1).
- `B19-2` — praktyczne: Utwórz future posiadającą `String` i sprawdź statycznie jej `Send`. [Rozwiązanie](../rozwiazania/11_async_rust/01_future_async_i_await.md#b19-2).
- `B19-3` — pogłębione: Wyjaśnij ograniczenie pamięci dla miliona żądań przechowujących bufor przez `await`. [Rozwiązanie](../rozwiazania/11_async_rust/01_future_async_i_await.md#b19-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [Future::poll](https://doc.rust-lang.org/std/future/trait.Future.html)
- [Await expressions](https://doc.rust-lang.org/reference/expressions/await-expr.html)

## Powiązane tematy

- [Executor, `Waker` i `poll`](02_executor_waker_i_poll.md)
- [Taski, join, select i stream](03_taski_join_select_i_stream.md)
- [Pinning](../11_async_rust/05_pin_unpin_i_self_referential.md)
