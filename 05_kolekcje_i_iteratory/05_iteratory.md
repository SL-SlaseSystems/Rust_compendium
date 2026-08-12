[← Spis treści](../README.md)

# Iteratory

Iterator jest leniwą maszyną produkującą kolejne `Item` przez `next`.
Adaptery budują nowy iterator, a konsumenci uruchamiają przetwarzanie.

## Trzy sposoby wejścia

- `kolekcja.iter()` — elementy `&T`;
- `kolekcja.iter_mut()` — elementy `&mut T`;
- `kolekcja.into_iter()` — zwykle elementy `T` i konsumpcja kolekcji.

~~~rust
fn main() {
    let dane = vec![1, 2, 3, 4, 5];
    let wynik: Vec<_> = dane
        .iter()
        .copied()
        .filter(|x| x % 2 == 1)
        .map(|x| x * x)
        .collect();
    assert_eq!(wynik, [1, 9, 25]);
    assert_eq!(dane.len(), 5);
}
~~~

`filter` dostaje referencję do elementu iteratora, stąd czasem pojawia się
podwójna referencja. `copied` lub `cloned` może uprościć dalszy kod.

## Własny iterator

~~~rust
struct Odliczanie {
    nastepna: u8,
}

impl Iterator for Odliczanie {
    type Item = u8;

    fn next(&mut self) -> Option<Self::Item> {
        if self.nastepna == 0 {
            None
        } else {
            let wynik = self.nastepna;
            self.nastepna -= 1;
            Some(wynik)
        }
    }
}

fn main() {
    let wartosci: Vec<_> = Odliczanie { nastepna: 3 }.collect();
    assert_eq!(wartosci, [3, 2, 1]);
}
~~~

Wystarczy zaimplementować `next`; trait dostarcza wiele metod domyślnych.
Po pierwszym `None` zwykły Iterator może teoretycznie znów zwrócić `Some`.
`FusedIterator` lub adapter `fuse` wyraża trwałe zakończenie.

## Adaptery i konsumenci

Adaptery: `map`, `filter`, `filter_map`, `flat_map`, `flatten`, `zip`,
`chain`, `enumerate`, `take`, `skip`, `peekable`, `scan`.

Konsumenci: `collect`, `sum`, `fold`, `try_fold`, `find`, `position`,
`any`, `all`, `count`, `for_each`.

~~~rust
fn main() {
    let teksty = ["1", "2", "x", "4"];
    let wynik: Result<Vec<i32>, _> =
        teksty.into_iter().map(str::parse::<i32>).collect();
    assert!(wynik.is_err());

    let suma = (1..)
        .map(|x| x * x)
        .take_while(|x| *x < 30)
        .sum::<i32>();
    assert_eq!(suma, 55);
}
~~~

`collect` potrafi odwrócić `Iterator<Item = Result<T, E>>` w
`Result<Collection<T>, E>` i zatrzymuje się na pierwszym błędzie.

## Leniwość i ownership

Samo wywołanie `map` nic nie oblicza. Wartość zwracana przez `#[must_use]`
powinna zostać skonsumowana. Adapter może przechwycić referencję, przez co
pożyczka trwa tak długo jak iterator i jego użycie.

## Zaawansowane kontrakty

`size_hint` podaje dolną i opcjonalną górną granicę; błędna dolna granica może
łamać logikę konsumenta, a dla kodu `unsafe` błędne dodatkowe obietnice są
szczególnie groźne. Traits `ExactSizeIterator` i `DoubleEndedIterator`
dodają możliwości, nie gwarantują automatycznie lepszej wydajności.

## Powiązane tematy

- [Closures](04_closures_i_fn_traits.md)
- [`Option` i `Result`](../06_bledy/01_option_i_result.md)
- [Zero-cost abstractions](../13_wzorce_i_architektura/05_wydajnosc_i_zero_cost.md)
