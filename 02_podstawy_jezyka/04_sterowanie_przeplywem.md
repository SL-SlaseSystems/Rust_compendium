[← Spis treści](../README.md)

# Sterowanie przepływem

Warunki w Rust muszą mieć typ `bool`. Nie ma niejawnej zamiany liczby lub
wskaźnika na prawdę/fałsz.

## `if` jako wyrażenie

Wszystkie ramiona muszą mieć zgodny typ:

~~~rust
fn kategoria(wiek: u8) -> &'static str {
    if wiek < 13 {
        "dziecko"
    } else if wiek < 18 {
        "nastolatek"
    } else {
        "dorosły"
    }
}

fn main() {
    assert_eq!(kategoria(20), "dorosły");
}
~~~

## `loop`

`loop` tworzy pętlę bezwarunkową. `break wartość` nadaje całej pętli wynik:

~~~rust
fn main() {
    let mut n = 0;
    let kwadrat = loop {
        n += 1;
        if n == 5 {
            break n * n;
        }
    };
    assert_eq!(kwadrat, 25);
}
~~~

Etykiety rozróżniają zagnieżdżone pętle:

~~~rust
fn main() {
    let mut pary = 0;
    'zewnetrzna: for x in 0..5 {
        for y in 0..5 {
            if x + y > 3 {
                break 'zewnetrzna;
            }
            pary += 1;
        }
    }
    assert_eq!(pary, 4);
}
~~~

## `while` i `for`

`while` jest właściwe, gdy liczba iteracji zależy od warunku. `for` korzysta
z `IntoIterator` i jest bezpieczniejszy od ręcznego indeksowania:

~~~rust
fn main() {
    let mut liczby = vec![1, 2, 3];
    for n in &mut liczby {
        *n *= 2;
    }
    assert_eq!(liczby, [2, 4, 6]);

    let suma: i32 = (1..=4).sum();
    assert_eq!(suma, 10);
}
~~~

`&kolekcja` iteruje po `&T`, `&mut kolekcja` po `&mut T`, a kolekcja
przekazana przez wartość zwykle oddaje własność elementów.

## `match` i `let else`

`match` sprawdza wyczerpująco warianty. `let else` obsługuje niepasujący
wzorzec przez przepływ rozbieżny:

~~~rust
fn pierwszy_dodatni(dane: &[i32]) -> Option<i32> {
    let Some(wartosc) = dane.iter().copied().find(|x| *x > 0) else {
        return None;
    };
    Some(wartosc)
}

fn main() {
    assert_eq!(pierwszy_dodatni(&[-2, 0, 7]), Some(7));
}
~~~

## Pułapki

- zakres `a..b` nie zawiera `b`, a `a..=b` zawiera;
- modyfikacja indeksu ręcznej pętli łatwo prowadzi do błędu granic;
- `break` i `continue` bez etykiety dotyczą najbliższej pętli;
- pusta pętla `loop {}` może zużywać rdzeń procesora.

## Powiązane tematy

- [Wzorce i `match`](../04_typy_i_modelowanie/02_wzorce_i_match.md)
- [Iteratory](../05_kolekcje_i_iteratory/05_iteratory.md)
- [`Option` i `Result`](../06_bledy/01_option_i_result.md)
