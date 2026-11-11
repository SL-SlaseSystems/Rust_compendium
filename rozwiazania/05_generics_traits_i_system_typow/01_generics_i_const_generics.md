[← Spis treści](../../README.md)

# Rozwiązania: Generics i const generics

## A18-1

Krotka jest konsumowana, a jej pola przenoszone w odwrotnej kolejności. Żaden bound nie jest potrzebny.

~~~rust
fn zamien<T, U>((a, b): (T, U)) -> (U, T) { (b, a) }
fn main() {
    assert_eq!(zamien((String::from("A"), 7)), (7, String::from("A")));
}
~~~

## A18-2

Delegujemy obsługę pustki do slice. Długość należy do typu, ale wynik nadal wymaga `Option`, bo dozwolone jest zero.

~~~rust
fn ostatni<T, const N: usize>(xs: &[T; N]) -> Option<&T> { xs.last() }
fn main() {
    assert_eq!(ostatni(&[1, 2, 3]), Some(&3));
    assert_eq!(ostatni(&[0_u8; 0]), None);
}
~~~

## A18-3

Bound podaje także typ wyniku operatora. Nie zakładamy, że samo istnienie `Add` gwarantuje `Output = Self`.

~~~rust
use std::ops::Add;
fn suma<T: Add<Output = T>>(a: T, b: T) -> T { a + b }
#[derive(Debug, PartialEq)]
struct Punkty(u32);
impl Add for Punkty {
    type Output = Self;
    fn add(self, rhs: Self) -> Self { Self(self.0 + rhs.0) }
}
fn main() {
    assert_eq!(suma(2_u32, 3), 5);
    assert_eq!(suma(Punkty(4), Punkty(5)), Punkty(9));
}
~~~

Dla newtype domenowego trzeba osobno określić zachowanie przepełnienia. Jeśli ma ono być omylne, lepiej udostępnić nazwaną metodę zwracającą `Result` niż ukryć błąd wewnątrz zwykłego `Add` bez uzgodnionej semantyki.

