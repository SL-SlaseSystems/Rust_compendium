[← Spis treści](../README.md)

# Executor, `Waker` i `poll`

Centralny kontrakt wygląda tak:

~~~rust
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll};

struct Gotowe(Option<u32>);

impl Future for Gotowe {
    type Output = u32;

    fn poll(mut self: Pin<&mut Self>, _cx: &mut Context<'_>) -> Poll<u32> {
        Poll::Ready(self.0.take().expect("future nie może być polled po Ready"))
    }
}

fn main() {
    let _ = Gotowe(Some(42));
}
~~~

`Pin<&mut Self>` chroni future, których stan może zawierać odniesienia zależne
od adresu. `Context` daje `Waker`. Wynik to `Poll::Ready(value)` lub
`Poll::Pending`.

## Zasada waker

Jeżeli `poll` zwraca `Pending`, future musi zapewnić, że bieżący lub nowszy
waker zostanie obudzony, gdy możliwy będzie postęp. Executor nie powinien
kręcić pętli poll bez sygnału. Typowy przebieg:

1. executor polluje task;
2. future pyta zasób i rejestruje waker;
3. zasób nie jest gotowy, więc wraca `Pending`;
4. sterownik I/O lub timer wywołuje `wake`;
5. executor umieszcza task ponownie w kolejce;
6. następny poll daje postęp lub `Ready`.

Waker może zostać zastąpiony między pollami. Rejestracja musi unikać utraconego
wybudzenia, szczególnie gdy gotowość zmienia się równolegle.

## Zakaz poll po zakończeniu

Po `Ready` kontrakt nie gwarantuje, że kolejny `poll` jest dozwolony; może
spowodować panic, lecz nie może sam z siebie prowadzić do UB w bezpiecznym
kodzie. Adapter `Fuse` z ekosystemu może utrwalić zakończenie.

## Executor

Minimalny executor ma kolejkę gotowych tasków, przechowuje przypięte futures i
tworzy wakery dodające task z powrotem. Prawdziwy runtime potrzebuje również
reaktora I/O, timerów, strategii fairness i shutdown.

Szkic przepływu, nie kompletna implementacja:

~~~text
while let Some(task) = ready_queue.pop() {
    if task.future.poll(task.context()).is_ready() {
        task.complete();
    }
}
~~~

Pisanie własnego `RawWaker` jest `unsafe`: vtable musi poprawnie zarządzać
ownership i zliczaniem referencji dla `clone`, `wake`, `wake_by_ref` i `drop`.
W aplikacji użyj dojrzałego runtime’u.

## Fairness

Future, której `poll` wykonuje dużo pracy i nie oddaje sterowania, głodzi inne
taski. Runtime może mieć budżety kooperacyjne, lecz biblioteka nie powinna
zakładać konkretnej polityki. Dziel pracę i przenoś CPU-bound obliczenia do
dedykowanej puli.

## Powiązane tematy

- [`Future`, `async` i `await`](01_future_async_i_await.md)
- [Pinning](../11_async_rust/05_pin_unpin_i_self_referential.md)
- [`unsafe` i soundness](../21_unsafe_soundness_i_model_pamieci/01_unsafe_i_soundness.md)
