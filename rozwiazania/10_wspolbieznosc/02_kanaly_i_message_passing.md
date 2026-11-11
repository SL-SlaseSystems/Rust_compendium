[← Spis treści](../../README.md)

# Rozwiązania: Kanały i message passing

[Rozdział źródłowy](../../10_wspolbieznosc/02_kanaly_i_message_passing.md).

## B14-1

~~~rust
fn main(){let(tx,rx)=std::sync::mpsc::channel();tx.send(1).unwrap();tx.send(2).unwrap();drop(tx);assert_eq!(rx.iter().collect::<Vec<_>>(),[1,2]);}
~~~

## B14-2

~~~rust
use std::sync::mpsc::{sync_channel,TrySendError};
fn main(){let(tx,rx)=sync_channel(1);tx.send(String::from("a")).unwrap();
 let odzyskane=match tx.try_send(String::from("b")){Err(TrySendError::Full(s))=>s,_=>panic!("oczekiwano pełnego bufora")};
 assert_eq!(odzyskane,"b");assert_eq!(rx.recv().unwrap(),"a");}
~~~

## B14-3

~~~rust
use std::{sync::mpsc,thread};
fn main(){let(tx,rx)=mpsc::channel::<(u32,mpsc::Sender<u32>)>();
 let h=thread::spawn(move||{for(n,odp)in rx{let _=odp.send(n*2);}});
 let(a,b)=mpsc::channel();tx.send((21,a)).unwrap();assert_eq!(b.recv().unwrap(),42);
 let(a,b)=mpsc::channel();drop(b);tx.send((1,a)).unwrap();drop(tx);h.join().unwrap();}
~~~
Błąd wysłania odpowiedzi oznacza rezygnację klienta. Worker kontynuuje i kończy się po zamknięciu wejścia.

