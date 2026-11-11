[← Spis treści](../../README.md)

# Rozwiązania: `Pin`, `Unpin` i typy self-referential

[Rozdział źródłowy](../../11_async_rust/05_pin_unpin_i_self_referential.md).

## B23-1

~~~rust
fn main(){let p=Box::pin(7_u32);let adres=p.as_ref().get_ref() as *const u32;let q=p;assert_eq!(adres,q.as_ref().get_ref() as *const u32);}
~~~

## B23-2

~~~rust
use std::{future::Future,pin::pin,task::{Context,Poll,Waker}};
fn main(){let mut f=pin!(async{42});let mut cx=Context::from_waker(Waker::noop());assert_eq!(f.as_mut().poll(&mut cx),Poll::Ready(42));}
~~~
Nie jest to executor dla future zwracających Pending.

## B23-3

Jeżeli metoda udostępnia `Pin<&mut Pole>`, odtąd pole nie może zostać wyniesione przed końcem swojego życia. Obowiązek dotyczy również Drop struktury i wszystkich alternatywnych metod dostępu. `Pin::set` najpierw niszczy starą wartość na miejscu, z zachowaniem wymagań Drop, a potem instaluje nową pod tym adresem. `mem::replace` zwróciłoby starą żywą wartość i pozwoliło ją przenieść, dlatego nie jest równoważne. Projekcja unsafe musi ponadto zachować poprawne aliasowanie i alignment.

