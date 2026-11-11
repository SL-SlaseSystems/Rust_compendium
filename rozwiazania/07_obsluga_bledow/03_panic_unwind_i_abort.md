[← Spis treści](../../README.md)

# Rozwiązania: `panic!`, unwind i abort

[Rozdział źródłowy](../../07_obsluga_bledow/03_panic_unwind_i_abort.md).

## B03-1

~~~rust
fn main() {
    let wynik = std::panic::catch_unwind(|| panic!("kontrolowana awaria"));
    assert!(wynik.is_err());
}
~~~
Test dotyczy strategii unwind. Nie dowodzi zachowania przy abort.

## B03-2

~~~rust
fn zamien(v: &mut Vec<u8>, dane: &[&str]) -> Result<(), std::num::ParseIntError> {
    let nowy: Result<Vec<u8>, _> = dane.iter().map(|s| s.parse()).collect();
    *v = nowy?; Ok(())
}
fn main() {
    let mut v=vec![9];
    assert!(zamien(&mut v,&["1","999"]).is_err()); assert_eq!(v,[9]);
    zamien(&mut v,&["1","2"]).unwrap(); assert_eq!(v,[1,2]);
}
~~~

## B03-3

~~~rust
use std::sync::{Arc, atomic::{AtomicUsize,Ordering}};
struct Guard(Arc<AtomicUsize>);
impl Drop for Guard { fn drop(&mut self) { self.0.fetch_add(1,Ordering::Relaxed); } }
fn main() {
    let licznik=Arc::new(AtomicUsize::new(0));
    let kopia=Arc::clone(&licznik);
    let wynik=std::panic::catch_unwind(move || { let _g=Guard(kopia); panic!("test"); });
    assert!(wynik.is_err()); assert_eq!(licznik.load(Ordering::Relaxed),1);
}
~~~
Nie ma tutaj równoległego dostępu wymagającego publikacji dodatkowych danych.

