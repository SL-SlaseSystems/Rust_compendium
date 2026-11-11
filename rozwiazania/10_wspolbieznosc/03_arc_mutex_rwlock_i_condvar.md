[← Spis treści](../../README.md)

# Rozwiązania: `Arc`, `Mutex`, `RwLock` i `Condvar`

[Rozdział źródłowy](../../10_wspolbieznosc/03_arc_mutex_rwlock_i_condvar.md).

## B15-1

~~~rust
use std::sync::Mutex;
fn main(){let m=Mutex::new((5_u32,0_u32));{let mut s=m.lock().unwrap();s.0-=1;s.1+=1;}let s=m.lock().unwrap();assert_eq!(s.0+s.1,5);}
~~~

## B15-2

~~~rust
use std::sync::{Arc,Mutex,Condvar};
fn main(){let para=Arc::new((Mutex::new(Vec::<u32>::new()),Condvar::new()));let p=Arc::clone(&para);
 let h=std::thread::spawn(move||{let(m,cv)=&*p;m.lock().unwrap().push(7);cv.notify_one();});
 let(m,cv)=&*para;let mut g=cv.wait_while(m.lock().unwrap(),|v|v.is_empty()).unwrap();assert_eq!(g.pop(),Some(7));drop(g);h.join().unwrap();}
~~~

## B15-3

Dla cache, którą wolno odtworzyć, uzyskaj guard przez `match lock()`; przy `PoisonError` użyj `into_inner`, wyczyść cache do udokumentowanego pustego stanu, sprawdź licznik rozmiaru i dopiero wtedy wywołaj `clear_poison`. Dla księgi finansowej samo wyczyszczenie byłoby niedopuszczalne: przerwij obsługę i odtwórz stan z trwałego źródła. Polityka wynika z domeny, a nie z dostępności metody `into_inner`. Naprawa oraz odczyt muszą pozostać pod tą samą blokadą.

