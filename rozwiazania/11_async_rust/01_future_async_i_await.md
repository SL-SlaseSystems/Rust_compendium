[← Spis treści](../../README.md)

# Rozwiązania: `Future`, `async` i `await`

[Rozdział źródłowy](../../11_async_rust/01_future_async_i_await.md).

## B19-1

~~~rust
use std::{cell::Cell,future::Future,pin::pin,task::{Context,Poll,Waker}};
async fn krok(n:&Cell<u32>){n.set(n.get()+1);}
fn main(){let n=Cell::new(0);let mut f=pin!(krok(&n));assert_eq!(n.get(),0);let mut cx=Context::from_waker(Waker::noop());assert_eq!(f.as_mut().poll(&mut cx),Poll::Ready(()));assert_eq!(n.get(),1);}
~~~
Waker bez działania jest wystarczający wyłącznie dla tego natychmiastowo gotowego przykładu.

## B19-2

~~~rust
fn send<T:Send>(_:&T){}
fn main(){let tekst=String::from("Ada");let f=async move{std::future::ready(()).await;tekst.len()};send(&f);drop(f);}
~~~
Test sprawdza typ; Drop bez poll nie wykonuje ciała future.

## B19-3

Bufor 64 KiB na milion aktywnych żądań to około 61 GiB samego payloadu, bez narzutu future, kolejek i runtime’u. Ogranicz liczbę przyjętych żądań przed alokacją, zmniejsz czas życia bufora i ustaw maksymalną wielkość wiadomości. Ograniczenie kolejki po alokacji nie usuwa pamięci zajętej przez producentów czekających na wysłanie. Pamięć licz jako sumę buforowanych, wykonywanych i oczekujących operacji, a nie samą pojemność jednej kolejki.

