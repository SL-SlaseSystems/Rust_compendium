[← Spis treści](../../README.md)

# Rozwiązania: `Send`, `Sync` i atomiki

[Rozdział źródłowy](../../10_wspolbieznosc/04_send_sync_i_atomiki.md).

## B16-1

~~~rust
fn send<T:Send>(){} fn sync<T:Sync>(){}
fn main(){send::<std::cell::RefCell<u32>>();sync::<std::sync::Mutex<std::cell::RefCell<u32>>>();}
~~~

## B16-2

~~~compile_fail
fn main(){let x=std::rc::Rc::new(7);std::thread::spawn(move||*x);}
~~~
Closure posiada `Rc`, którego nie można przesłać między wątkami.

~~~rust
fn main(){let x=std::sync::Arc::new(7);let h=std::thread::spawn(move||*x);assert_eq!(h.join().unwrap(),7);}
~~~

## B16-3

Dwa wątki odczytują `0` przy limicie `1`. Oba uznają `0 < 1`, a potem oba wykonują `fetch_add(1)`, kończąc z `2`. Każda operacja jest atomowa, więc nie ma data race, ale kontrakt limitu jest złamany. `SeqCst` samo nie łączy dwóch operacji w jedną. Naprawa to pętla CAS warunkująca zmianę na aktualnej wartości albo mutex chroniący cały warunek i inkrementację.

