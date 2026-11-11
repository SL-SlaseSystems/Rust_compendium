[← Spis treści](../../README.md)

# Rozwiązania: Executor, `Waker` i `poll`

[Rozdział źródłowy](../../11_async_rust/02_executor_waker_i_poll.md).

## B20-1

~~~rust
use std::{future::Future,pin::pin,task::{Context,Poll,Waker}};
fn main(){let mut f=pin!(std::future::ready(42));let mut cx=Context::from_waker(Waker::noop());assert_eq!(f.as_mut().poll(&mut cx),Poll::Ready(42));}
~~~

## B20-2

~~~rust
use std::{future::Future,pin::{Pin,pin},task::{Context,Poll,Waker}};
struct Raz(bool);
impl Future for Raz{type Output=();fn poll(mut self:Pin<&mut Self>,cx:&mut Context<'_>)->Poll<()>{if self.0{Poll::Ready(())}else{self.0=true;cx.waker().wake_by_ref();Poll::Pending}}}
fn main(){let mut f=pin!(Raz(false));let mut cx=Context::from_waker(Waker::noop());assert!(f.as_mut().poll(&mut cx).is_pending());assert!(f.as_mut().poll(&mut cx).is_ready());}
~~~

## B20-3

Błędny przeplot: konsument czyta „brak wyniku”; producent zapisuje wynik i nie znajduje wakera; konsument zapisuje waker, zwraca Pending; nic już go nie budzi. Poprawny wariant przechowuje `Option<Wynik>` i `Option<Waker>` pod jednym mutexem. Konsument w sekcji krytycznej odbiera wynik albo zapisuje bieżący waker. Producent pod tą samą blokadą zapisuje wynik i zabiera waker, następnie zwalnia blokadę i wywołuje wake. Wybudzanie poza blokadą ogranicza reentrancy i czas sekcji krytycznej.

