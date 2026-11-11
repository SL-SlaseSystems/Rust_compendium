[← Spis treści](../README.md)
<!-- status: expanded -->

# Iteratory

> Przykłady: **stable**, Rust 1.90.0, Edition 2024. Źródła sprawdzono 11 listopada 2026 r.

## Cele

Po tym rozdziale potrafisz:

- prześledzić typ `Item` przez `iter`, `copied`, `filter` i `collect`;
- rozpoznać punkt wykonania pracy i skutki krótkiego obiegu konsumenta;
- zaimplementować poprawne `next` oraz odróżnić zwykłą wskazówkę długości od niebezpiecznej obietnicy;

## Model — leniwy stan produkujący kolejne elementy


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

Samo utworzenie adaptera `map` nie wywołuje transformacji elementów. Wartość zwracana przez `#[must_use]`
powinna zostać skonsumowana. Adapter może przechwycić referencję, przez co
pożyczka trwa tak długo jak iterator i jego użycie.

## Zaawansowane kontrakty

`size_hint` podaje dolną i opcjonalną górną granicę; błędna dolna granica może
łamać logikę konsumenta, a dla kodu `unsafe` błędne dodatkowe obietnice są
szczególnie groźne. Traits `ExactSizeIterator` i `DoubleEndedIterator`
dodają możliwości, nie gwarantują automatycznie lepszej wydajności.

## Reguły — Item i stan są częścią kontraktu

`Iterator::next(&mut self)` zmienia stan maszyny i oddaje `Option<Item>`. `Item` jest jednym associated type dla tej implementacji, a nie rodziną zależną od każdej krótkiej pożyczki `self`. Iterator slice zwraca referencje do zewnętrznego bufora z odpowiednio długim lifetime; to inna sytuacja niż wynik pożyczający wewnętrzny, nadpisywany bufor po każdym wywołaniu. Ten drugi model może wymagać lending API i GAT.

`IntoIterator` definiuje sposób uzyskania iteratora. Wywołanie `into_iter` na `Vec<T>` konsumuje wektor, ale na `&Vec<T>` pożycza go i produkuje `&T`. Nie wnioskuj o własności wyłącznie z nazwy metody: sprawdź typ receivera. Dla tablic w Edition 2024 wywołanie przez wartość przekazuje elementy tablicy zgodnie z ich typem.

`filter` przyjmuje callback z `&Item`, więc nad `iter()` po `T` widzi `&&T`. `map` dostaje `Item` przez wartość. `.copied()` zamienia `&T` na `T` dla `Copy`, a `.cloned()` wykonuje `Clone`. Użyj ich tam, gdzie naprawdę chcesz wartości, zamiast dopisywać przypadkową liczbę gwiazdek do coraz dłuższego łańcucha.

~~~rust
fn suma(teksty: &[&str]) -> Result<u32, &'static str> {
    teksty.iter().try_fold(0_u32, |suma, tekst| {
        let n: u32 = tekst.parse().map_err(|_| "niepoprawna liczba")?;
        suma.checked_add(n).ok_or("przepełnienie")
    })
}
fn main() {
    assert_eq!(suma(&["2", "3"]), Ok(5));
    assert_eq!(suma(&[]), Ok(0));
    assert_eq!(suma(&["2", "x", "3"]), Err("niepoprawna liczba"));
    assert_eq!(suma(&["4294967295", "1"]), Err("przepełnienie"));
}
~~~

`try_fold` łączy agregację z krótkim obiegiem. Nie buduje pośredniego `Vec`, a błąd parsowania oraz przepełnienie są odrębnymi wynikami. Przetwarzanie zatrzymuje się przy pierwszej odmowie; wcześniejsze obliczenia nie są cofane. Jeśli callback zapisuje rekordy do pliku, krótki obieg nie zapewnia transakcji.

## Krótki obieg i dalszy ciąg iteratora

`take_while` musi pobrać pierwszy niespełniający element, aby sprawdzić warunek; ten element jest już skonsumowany i nie wraca do wejściowego iteratora. `peekable` pozwala podejrzeć kolejny element, ale sam może pobrać go do wewnętrznego cache. Przy parserze trzeba zdecydować, kto posiada ten stan i czy klient może kontynuować.

`by_ref` pożycza iterator, dzięki czemu konsument może zużyć tylko prefiks i oddać dostęp do reszty. `fuse` gwarantuje trwałe zakończenie po `None`. Sama implementacja bez tego kontraktu może teoretycznie wznowić produkcję; nie opieraj protokołu na silniejszej obietnicy bez odpowiedniego boundu.

`size_hint` i `ExactSizeIterator` są bezpiecznymi kontraktami: błędna implementacja może zepsuć wynik lub wydajność, lecz nie wolno na jej podstawie powodować UB w bezpiecznym konsumencie. Kod `unsafe` potrzebujący silniejszej gwarancji musi mieć dodatkowy prawidłowy dowód. Niestabilne mechanizmy takie jak `TrustedLen` mają odrębny kontrakt i nie wynikają ze zwykłego `Iterator`.

## Diagnostyka kompilatora

Iterator jest posiadaną wartością; niektóre konsumujące metody odbierają możliwość późniejszego użycia tej samej nazwy.

~~~compile_fail
fn main() {
    let iter = vec![1, 2, 3].into_iter();
    let pierwszy = iter.take(1).collect::<Vec<_>>();
    let reszta = iter.collect::<Vec<_>>();
    println!("{pierwszy:?} {reszta:?}");
}
~~~

Naprawą jest `let mut iter` oraz `iter.by_ref().take(1)`, gdy zamierzasz zachować pozostały stan. Przy E0283 na `collect` podaj typ wyniku, ponieważ ten sam iterator może zasilić różne kolekcje. Ostrzeżenie o nieużytym `map` zwykle oznacza, że leniwy potok nigdy nie został skonsumowany.

## Praktyka produkcyjna

Krótszy zapis nie zawsze jest czytelniejszym algorytmem. Łańcuch iteratorów pasuje do lokalnych transformacji; złożona maszyna stanów z wieloma wyjściami często lepiej wygląda jako `for`. Nie zbieraj pośrednich kolekcji tylko po to, aby rozpocząć kolejny etap, jeżeli można połączyć adaptery.

W nieograniczonym strumieniu zawsze wskaż warunek końca, limit wyniku albo konsumenta o krótkim obiegu. `collect` nad nieskończonym iteratorem nie kończy pracy i może wyczerpać pamięć. Uważaj także na `flatten` nad `Result`: może pominąć błędy jako puste iteratory; `collect::<Result<Vec<_>, _>>()` jawnie propaguje pierwszy błąd.

## Sprawdź, czy rozumiesz

1. Dlaczego `filter` nad `iter()` często widzi `&&T`?
2. Jaki element zużywa `take_while`, kiedy warunek staje się fałszywy?
3. Czy bezpieczny konsument może ufać błędnemu `size_hint` dla operacji `unsafe` bez dodatkowego dowodu?

## Ćwiczenia

- `A28-1` — podstawowe: z tablicy 1–6 wybierz kwadraty parzystych liczb bez konsumowania tablicy [Rozwiązanie](../rozwiazania/06_kolekcje_iteratory_i_closures/05_iteratory.md#a28-1).
- `A28-2` — praktyczne: zużyj dwa pierwsze elementy iteratora przez `by_ref`, a potem zbierz pozostałe [Rozwiązanie](../rozwiazania/06_kolekcje_iteratory_i_closures/05_iteratory.md#a28-2).
- `A28-3` — pogłębione: zaimplementuj odliczanie wraz z poprawnym `size_hint` i `ExactSizeIterator`; sprawdź długość po każdym `next` oraz trwałe zakończenie [Rozwiązanie](../rozwiazania/06_kolekcje_iteratory_i_closures/05_iteratory.md#a28-3).

## Źródła i zakres stabilności

Kontrakty adapterów, krótkiego obiegu i `size_hint`: [Iterator](https://doc.rust-lang.org/std/iter/trait.Iterator.html). Ograniczenia gwarancji rozmiaru: [ExactSizeIterator](https://doc.rust-lang.org/std/iter/trait.ExactSizeIterator.html). Trwałe zakończenie: [FusedIterator](https://doc.rust-lang.org/std/iter/trait.FusedIterator.html).

## Powiązane tematy

- [Closures](04_closures_i_fn_traits.md)
- [`Option` i `Result`](../07_obsluga_bledow/01_option_i_result.md)
- [Zero-cost abstractions](../20_wydajnosc_i_optymalizacja/01_wydajnosc_i_zero_cost.md)
