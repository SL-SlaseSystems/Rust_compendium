[← Spis treści](../../README.md)

# Rozwiązania: Testy jednostkowe i integracyjne

[Rozdział źródłowy](../../09_dokumentacja_testowanie_i_jakosc/01_testy_jednostkowe_i_integracyjne.md).

## B10-1

~~~rust
fn mediana(mut dane: Vec<i32>) -> Option<f64> {
    if dane.is_empty() { return None; }
    dane.sort_unstable();
    let n = dane.len();
    if n % 2 == 1 { Some(dane[n / 2] as f64) }
    else { Some((dane[n / 2 - 1] as f64 + dane[n / 2] as f64) / 2.0) }
}
fn main() {
    assert_eq!(mediana(vec![i32::MIN, i32::MAX]), Some(-0.5));
    assert_eq!(mediana(vec![i32::MAX, i32::MAX]), Some(i32::MAX as f64));
    assert_eq!(mediana(vec![i32::MIN]), Some(i32::MIN as f64));
    assert_eq!(mediana(vec![]), None);
}
~~~

Konwersja każdego składnika przed sumą unika przepełnienia `i32`. Test pary minimum–maksimum wykrywa implementację dodającą liczby jeszcze jako `i32`.

## B10-2

~~~rust
fn uporzadkuj(v:&[i32])->Vec<i32>{let mut r=v.to_vec();r.sort_unstable();r.dedup();r}
fn main(){for v in [vec![],vec![4,4],vec![3,1,2,1]]{
 let r=uporzadkuj(&v);
 assert!(r.windows(2).all(|w|w[0]<w[1]));
 assert!(v.iter().all(|n|r.contains(n)));
 assert_eq!(uporzadkuj(&r),r);
}}
~~~

## B10-3

~~~rust
use std::{sync::mpsc,thread,time::Duration};
fn main(){
 let (tx,rx)=mpsc::channel();
 let h=thread::spawn(move||{let wynik=6*7;tx.send(wynik).unwrap();});
 assert_eq!(rx.recv_timeout(Duration::from_secs(2)).unwrap(),42);
 h.join().unwrap();
}
~~~
Komunikat niesie wynik inicjalizacji. Timeout ogranicza oczekiwanie, a `join` ujawnia panic workera.

