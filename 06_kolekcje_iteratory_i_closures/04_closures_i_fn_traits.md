[← Spis treści](../README.md)

# Closures i rodzina `Fn`

Closure to anonimowa funkcja, która może przechwycić otoczenie. Kompilator
tworzy dla niej anonimową strukturę przechowującą przechwycone wartości.

## Inferencja i capture

~~~rust
fn main() {
    let prog = 10;
    let wieksze = |x: &i32| *x > prog;
    let wynik: Vec<_> = [5, 12, 20].iter().filter(|x| wieksze(x)).collect();
    assert_eq!(wynik, [&12, &20]);
}
~~~

Closure przechwytuje minimalnym wymaganym sposobem: przez `&T`, `&mut T` albo
wartość. Słowo `move` wymusza przejęcie bindingów do środka, lecz typy `Copy`
mogą zostać skopiowane.

~~~rust
fn main() {
    let tekst = String::from("dane");
    let dlugosc = move || tekst.len();
    assert_eq!(dlugosc(), 4);
}
~~~

`move` jest często konieczne dla wątku lub tasku, który może przeżyć bieżący
stos.

## `Fn`, `FnMut` i `FnOnce`

- `FnOnce` — można wywołać co najmniej raz; może skonsumować capture;
- `FnMut` — można wywoływać wielokrotnie z mutacją capture;
- `Fn` — można wywoływać wielokrotnie bez mutacji capture.

Hierarchia zdolności jest odwrotna intuicyjnie: każde `Fn` spełnia też
`FnMut` i `FnOnce`, lecz nie odwrotnie.

~~~rust
fn powtorz<F>(ile: usize, mut akcja: F)
where
    F: FnMut(usize),
{
    for i in 0..ile {
        akcja(i);
    }
}

fn main() {
    let mut suma = 0;
    powtorz(4, |i| suma += i);
    assert_eq!(suma, 6);
}
~~~

~~~rust
fn wykonaj<F, T>(f: F) -> T
where
    F: FnOnce() -> T,
{
    f()
}

fn main() {
    let tekst = String::from("oddaj");
    let odzyskany = wykonaj(|| tekst);
    assert_eq!(odzyskany, "oddaj");
}
~~~

## Zwracanie i przechowywanie closures

`impl Fn(i32) -> i32` ukrywa jeden konkretny typ closure. `Box<dyn Fn(...)>`
pozwala przechowywać heterogeniczne closures kosztem alokacji i dynamic
dispatch.

~~~rust
fn dodaj(n: i32) -> impl Fn(i32) -> i32 {
    move |x| x + n
}

fn main() {
    let plus_dwa = dodaj(2);
    assert_eq!(plus_dwa(5), 7);
}
~~~

Async closure zwraca future i może mieć bardziej złożone relacje capture.
Przy API callbacków wybieraj najsłabszy wystarczający bound: `FnOnce` daje
wywołującemu największą swobodę.

## Powiązane tematy

- [Iteratory](05_iteratory.md)
- [Wątki i scoped threads](../10_wspolbieznosc/01_watki_i_scoped_threads.md)
- [HRTB i `impl Trait`](../zaawansowane/05_hrtb_gat_rpit_i_impl_trait.md)
