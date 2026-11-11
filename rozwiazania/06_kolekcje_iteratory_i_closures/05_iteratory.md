[← Spis treści](../../README.md)

# Rozwiązania: Iteratory

## A28-1

`copied` zamienia pożyczone liczby na małe wartości `i32`, a końcowy `collect` uruchamia potok. Tablica jest nadal dostępna.

~~~rust
fn main() {
    let dane = [1, 2, 3, 4, 5, 6];
    let kwadraty: Vec<_> = dane.iter().copied()
        .filter(|n| n % 2 == 0).map(|n| n * n).collect();
    assert_eq!(kwadraty, [4, 16, 36]);
    assert_eq!(dane[0], 1);
}
~~~

## A28-2

`by_ref` pożycza stan zamiast oddawać go adapterowi na własność. Po zniszczeniu adaptera `take` można kontynuować oryginalny iterator.

~~~rust
fn main() {
    let mut iter = [1, 2, 3, 4].into_iter();
    let poczatek: Vec<_> = iter.by_ref().take(2).collect();
    let reszta: Vec<_> = iter.collect();
    assert_eq!(poczatek, [1, 2]);
    assert_eq!(reszta, [3, 4]);
}
~~~

## A28-3

Licznik jest równocześnie liczbą pozostałych elementów, dlatego obie granice `size_hint` są równe. `next` przy zerze nie odejmuje, więc nie przepełnia typu i pozostaje zakończone.

~~~rust
struct Odliczanie(u8);
impl Iterator for Odliczanie {
    type Item = u8;
    fn next(&mut self) -> Option<u8> {
        if self.0 == 0 { return None; }
        let n = self.0; self.0 -= 1; Some(n)
    }
    fn size_hint(&self) -> (usize, Option<usize>) {
        let n = usize::from(self.0); (n, Some(n))
    }
}
impl ExactSizeIterator for Odliczanie {}
impl std::iter::FusedIterator for Odliczanie {}
fn main() {
    let mut i = Odliczanie(2);
    assert_eq!(i.len(), 2);
    assert_eq!(i.next(), Some(2)); assert_eq!(i.len(), 1);
    assert_eq!(i.next(), Some(1)); assert_eq!(i.len(), 0);
    assert_eq!(i.next(), None); assert_eq!(i.next(), None);
    assert_eq!(i.size_hint(), (0, Some(0)));
}
~~~

Testy sprawdzają reprezentatywny przebieg, a uzasadnienie kontraktu wynika z niezmiennika licznika. Własny `unsafe` nie powinien traktować samego bezpiecznego traitu `ExactSizeIterator` jako gwarancji zaufanej długości dla dowolnej obcej implementacji.

