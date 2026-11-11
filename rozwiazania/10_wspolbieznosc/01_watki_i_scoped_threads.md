[← Spis treści](../../README.md)

# Rozwiązania: Wątki i scoped threads

[Rozdział źródłowy](../../10_wspolbieznosc/01_watki_i_scoped_threads.md).

## B13-1

~~~rust
fn main(){let v=vec![1,2,3];let h=std::thread::spawn(move||v.into_iter().sum::<i32>());assert_eq!(h.join().unwrap(),6);}
~~~

## B13-2

~~~rust
fn main(){let mut v=[0;4];let(a,b)=v.split_at_mut(2);std::thread::scope(|s|{
 s.spawn(||a.fill(1));s.spawn(||b.fill(2));});assert_eq!(v,[1,1,2,2]);}
~~~

## B13-3

~~~rust
use std::{sync::mpsc,thread};
fn main(){let(tx,rx)=mpsc::channel::<u32>();let h=thread::spawn(move||rx.iter().sum::<u32>());
 tx.send(3).unwrap();tx.send(4).unwrap();drop(tx);assert_eq!(h.join().unwrap(),7);}
~~~
Wszyscy nadawcy zostają upuszczeni, więc iterator kończy się po opróżnieniu bufora. Dodatkowy ukryty klon `Sender` złamałby ten protokół zakończenia.

