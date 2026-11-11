[← Spis treści](../../README.md)

# Rozwiązania: Variance, subtyping i drop check

## A21-1

Referencja statyczna może być traktowana jako ważna przez krótszy okres. Argument `kotwica` nazywa ten okres w sygnaturze.

~~~rust
fn skroc<'a>(tekst: &'static str, _kotwica: &'a ()) -> &'a str { tekst }
fn main() {
    let lokalny = ();
    assert_eq!(skroc("stały", &lokalny), "stały");
}
~~~

## A21-2

Delegowanie do `Box` usuwa potrzebę ręcznego odzyskiwania alokacji. Destruktor wnętrza wykonuje się po zniszczeniu boxa.

~~~rust
use std::cell::Cell;
struct Zasob<'a>(&'a Cell<bool>);
impl Drop for Zasob<'_> { fn drop(&mut self) { self.0.set(true); } }
fn main() {
    let zniszczony = Cell::new(false);
    let wlasciciel = Box::new(Zasob(&zniszczony));
    assert!(!zniszczony.get());
    drop(wlasciciel);
    assert!(zniszczony.get());
}
~~~

`Box<T>` ma własny protokół alokacji i niszczenia. Ten przykład nie wymaga `NonNull`, `PhantomData`, ręcznego `Drop` kontenera ani `unsafe`.

## A21-3

Strażnik znajduje się w wewnętrznym bloku, więc jego destruktor odczytuje nadal istniejący tekst. Dziennik potwierdza, że odczyt nastąpił przy zniszczeniu strażnika.

~~~rust
use std::cell::Cell;
struct Straznik<'a> { tekst: &'a str, odczytana: &'a Cell<usize> }
impl Drop for Straznik<'_> {
    fn drop(&mut self) { self.odczytana.set(self.tekst.len()); }
}
fn main() {
    let tekst = String::from("Rust");
    let odczytana = Cell::new(0);
    {
        let _straznik = Straznik { tekst: &tekst, odczytana: &odczytana };
        assert_eq!(odczytana.get(), 0);
    }
    assert_eq!(odczytana.get(), 4);
    assert_eq!(tekst, "Rust");
}
~~~

Gdyby właściciel tekstu powstał w krótszym bloku niż strażnik, adnotacja lifetime nie naprawiłaby kolejności destrukcji. Należałoby zmienić zakresy albo sprawić, by strażnik posiadał swój tekst.

