[← Spis treści](../../README.md)

# Rozwiązania: `Option` i `Result`

[Rozdział źródłowy](../../07_obsluga_bledow/01_option_i_result.md).

## B01-1

~~~rust
fn dziel(a: i32, b: i32) -> Option<i32> { a.checked_div(b) }
fn main() {
    assert_eq!(dziel(8, 2), Some(4));
    assert_eq!(dziel(8, 0), None);
    assert_eq!(dziel(i32::MIN, -1), None);
}
~~~
`checked_div` przenosi pełny kontrakt arytmetyczny do standardowego API.

## B01-2

~~~rust
fn port(s: Option<&str>) -> Result<Option<u16>, std::num::ParseIntError> {
    s.map(str::parse).transpose()
}
fn main() {
    assert_eq!(port(None).unwrap(), None);
    assert_eq!(port(Some("80")).unwrap(), Some(80));
    assert!(port(Some("x")).is_err());
}
~~~
Dodatnia wartość jest osobną regułą domenową; to zadanie bada format liczby.

## B01-3

~~~rust
fn main() {
    let mut wywolania = 0;
    let wynik = Some(7).unwrap_or_else(|| { wywolania += 1; 9 });
    assert_eq!((wynik, wywolania), (7, 0));
    let wynik = None::<u32>.unwrap_or_else(|| { wywolania += 1; 9 });
    assert_eq!((wynik, wywolania), (9, 1));
}
~~~
Closure pożycza licznik mutowalnie tylko na czas wywołania.

