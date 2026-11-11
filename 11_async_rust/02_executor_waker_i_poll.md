[← Spis treści](../README.md)
<!-- status: expanded -->

# Executor, `Waker` i `poll`

## Cele

Po tym rozdziale potrafisz:

- zbudować future respektującą kontrakt ponownego wybudzenia;
- wyjaśnić utracone wake i ograniczenie czasu pojedynczego poll;


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


## Model — wake prosi o kolejną szansę, nie wykonuje operacji

`Waker` identyfikuje task wymagający ponownego sprawdzenia. Wywołanie `wake` nie musi uruchomić go natychmiast i nie oznacza, że zasób na pewno jest gotowy. Wiele wybudzeń może zostać scalonych w jeden poll. Future powinna ponownie sprawdzić stan zasobu i aktualizować zapisany waker do bieżącego kontekstu; nie może zakładać niezmienności taska między pollami.

Najtrudniejszy wyścig pojawia się między sprawdzeniem gotowości a rejestracją. Producent może ustawić wynik i obudzić stary lub nieistniejący waker, po czym konsument zapisze nowy waker i zwróci Pending na zawsze. Poprawny protokół łączy stan i rejestrację pod synchronizacją albo stosuje sprawdzenie–rejestrację–ponowne sprawdzenie z właściwymi atomikami. Samo „gdzieś wywołuję wake” nie zamyka tego dowodu.

~~~rust
use std::{future::Future, pin::{Pin, pin}, task::{Context, Poll, Waker}};
struct UstapRaz(bool);
impl Future for UstapRaz {
    type Output = ();
    fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        if self.0 { Poll::Ready(()) }
        else { self.0 = true; cx.waker().wake_by_ref(); Poll::Pending }
    }
}
fn main() {
    let mut f = pin!(UstapRaz(false));
    let mut cx = Context::from_waker(Waker::noop());
    assert_eq!(f.as_mut().poll(&mut cx), Poll::Pending);
    assert_eq!(f.as_mut().poll(&mut cx), Poll::Ready(()));
}
~~~

Future zapisuje stan przed wybudzeniem, dzięki czemu następny poll może zobaczyć postęp. Ręczne dwa polle sprawdzają automat, ale nie testują planisty. W produkcyjnym runtime waker zaplanowałby kolejny poll. Nie twórz bez końca `Pending` połączonego z natychmiastowym self-wake: to zajęta pętla przeniesiona do kolejki executora.

`Wake` ze standardowej biblioteki umożliwia budowę wakera z `Arc` bez ręcznej implementacji `RawWakerVTable`. To bezpieczniejszy punkt startu edukacyjnego. Nadal pozostaje problem kolejki, stanu taska i zamknięcia runtime’u. `RawWaker` wymaga osobnego dowodu własności w każdej funkcji vtable, w tym różnicy między zużywającym `wake` a pożyczającym `wake_by_ref`.

Po zakończeniu future nie musi obsługiwać kolejnego poll. Bezpieczna implementacja nie może z tego powodu powodować UB, ale może panikować. Warstwa agregująca futures powinna pamiętać, które już zakończyły pracę. Podobny problem występuje po anulowaniu: spóźniony sygnał zasobu może dotrzeć, gdy stan taska już znika. Własność wakera i zasobu musi wykluczać use-after-free bez zakładania braku takich sygnałów.

Czas pojedynczego poll jest częścią uczciwej współpracy. Samo użycie asynchronicznego typu nie zatrzyma długiej kompresji wykonywanej w środku. Ogranicz pracę, rozbij ją na kroki lub użyj odpowiedniej puli. Executor nie ma ogólnego bezpiecznego mechanizmu wywłaszczania dowolnego Rust w trakcie funkcji.

## Adapter `poll_fn`: closure staje się future

`std::future::poll_fn` tworzy future z `FnMut(&mut Context) -> Poll<T>`. Każde `poll` uruchamia closure ponownie, więc licznik postępu, częściowo odebrane dane i flaga zakończenia muszą znajdować się w jej stanie lub w pożyczanym obiekcie. Nie wykonuj za każdym wejściem ponownie skutku, który miał nastąpić raz. `Pending` oznacza obowiązek zorganizowania pobudki, a nie prośbę o aktywne odpytywanie bez końca. Nie polluj future ponownie po `Ready`.

~~~rust
use std::{future::{poll_fn, Future}, pin::pin, task::{Context, Poll, Waker}};
fn main() {
    let mut krok = 0;
    let future = poll_fn(move |cx| {
        krok += 1;
        if krok == 1 {
            cx.waker().wake_by_ref();
            Poll::Pending
        } else {
            Poll::Ready(42)
        }
    });
    let mut future = pin!(future);
    let mut cx = Context::from_waker(Waker::noop());
    assert_eq!(future.as_mut().poll(&mut cx), Poll::Pending);
    assert_eq!(future.as_mut().poll(&mut cx), Poll::Ready(42));
}
~~~

Test celowo wykonuje dwa kroki ręcznie. `Waker::noop` nie jest tu executorem i nie obsłuży prawdziwego oczekiwania na I/O. Pierwsza gałąź modeluje przekazanie pobudki; w integracji zdarzeniowej zarejestruj aktualny waker przy zasobie i zabezpiecz wyścig między rejestracją a zmianą stanu. Przy budowaniu `select` przez `poll_fn` podaj kolejność odpytywania, politykę remisu i skutki upuszczenia przegranego future. Adapter nie zapewnia sam fairness ani cancellation safety. Kontrakt: [poll_fn](https://doc.rust-lang.org/std/future/fn.poll_fn.html).

## Diagnostyka kompilatora

Błąd próby mutacji przez `Pin<&mut T>` oznacza zwykle brak `Unpin` albo brak bezpiecznej projekcji. W przykładzie boolowski typ jest `Unpin`, więc dereferencja mutowalna jest dozwolona. „Future stoi” bez błędu kompilacji często oznacza utracone wake, brak uruchomionego sterownika I/O albo niepollujący executor. Dodawanie `sleep` do `poll` pogarsza sytuację: blokuje wątek zamiast rejestrować gotowość.

## Praktyka produkcyjna

Własne futures testuj dla gotowości natychmiastowej, Pending, zmiany wakera, anulowania i wybudzenia po anulowaniu. Rejestruj liczbę poll i długość wykonania podczas diagnozy przeciążenia. Korzystaj z gotowych prymitywów runtime’u, jeśli ich kontrakt pokrywa wymagania. Minimalny executor edukacyjny powinien jawnie wymieniać brakujące gwarancje: reentrancy, fairness, usypianie bez utraty sygnału i shutdown. Nie przedstawiaj pętli ręcznego poll z noop wakerem jako uniwersalnego uruchamiania I/O.

## Sprawdź, czy rozumiesz

- Czy dwa wake muszą dać dwa polle?
- Gdzie powstaje wyścig sprawdzenia i rejestracji wakera?
- Dlaczego self-wake w każdej iteracji może przeciążyć executor?

## Ćwiczenia

- `B20-1` — podstawowe: Napisz natychmiastowo gotową future z pojedynczym wynikiem. [Rozwiązanie](../rozwiazania/11_async_rust/02_executor_waker_i_poll.md#b20-1).
- `B20-2` — praktyczne: Sprawdź automat future ustępującej dokładnie raz. [Rozwiązanie](../rozwiazania/11_async_rust/02_executor_waker_i_poll.md#b20-2).
- `B20-3` — pogłębione: Rozpisz przeplot prowadzący do utraconego wake i poprawny wariant z mutexem. [Rozwiązanie](../rozwiazania/11_async_rust/02_executor_waker_i_poll.md#b20-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [Wake: bezpieczna budowa wakera](https://doc.rust-lang.org/std/task/trait.Wake.html)
- [Waker::wake i scalanie wybudzeń](https://doc.rust-lang.org/std/task/struct.Waker.html#method.wake)

## Powiązane tematy

- [`Future`, `async` i `await`](01_future_async_i_await.md)
- [Pinning](../11_async_rust/05_pin_unpin_i_self_referential.md)
- [`unsafe` i soundness](../21_unsafe_soundness_i_model_pamieci/01_unsafe_i_soundness.md)
