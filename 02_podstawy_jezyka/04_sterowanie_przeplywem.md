[← Spis treści](../README.md)
<!-- status: expanded -->

# Sterowanie przepływem

> Przykłady: **stable**, Rust 1.90.0, Edition 2024. Źródła sprawdzono 11 listopada 2026 r.

## Cele

Po tym rozdziale potrafisz:

- wybrać `if`, `match`, `for` i `loop` według rodzaju warunku zakończenia;
- wyjaśnić własność elementów w trzech wariantach pętli `for`;
- obsłużyć brak danych przez `let else` bez pozostawiania częściowo poprawnego stanu;

## Model — wartość gałęzi i warunek zakończenia


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

## Reguły — zakończenie jest częścią algorytmu

Wynik `if` jest wartością jednej wykonanej gałęzi. Gdy pomijasz `else`, nieobsłużona ścieżka daje `()`, więc użyteczna wartość gałęzi także musi być zgodna z `()`. Warunek nie konwertuje liczb na `bool`: pisz `n != 0`, aby wyrazić dokładne znaczenie. `match` również jest wyrażeniem, a zgodność wyników dotyczy wszystkich osiągalnych ramion. Ramię z `return` lub `panic!` nie musi produkować zwykłej wartości, bo nie wraca do miejsca dopasowania.

`loop` może zwracać wartość przez `break wynik`; `for` i `while` służą wykonaniu iteracji i nie przyjmują takiego wyniku `break`. W pętli licznikowej sprawdź, czy aktualizacja następuje także po `continue`. Łatwo stworzyć nieskończoną pętlę, gdy inkrementacja jest pod pomijaną gałęzią. `for` usuwa ten obowiązek: kolejne elementy dostarcza iterator, a nie ręczna modyfikacja indeksu.

~~~rust
fn suma_do_limitu(dane: &[u32], limit: u32) -> Option<u32> {
    let mut suma = 0_u32;
    for &liczba in dane {
        let nowa = suma.checked_add(liczba)?;
        if nowa > limit {
            return None;
        }
        suma = nowa;
    }
    Some(suma)
}

fn main() {
    assert_eq!(suma_do_limitu(&[2, 3, 5], 10), Some(10));
    assert_eq!(suma_do_limitu(&[2, 3, 6], 10), None);
    assert_eq!(suma_do_limitu(&[], 0), Some(0));
}
~~~

`for &liczba in dane` dopasowuje `&u32` i kopiuje skalarną wartość. `checked_add` wykrywa przepełnienie przed porównaniem z limitem. Stan aktualizujemy dopiero po pełnej walidacji kroku. Puste wejście ma określony wynik, więc funkcja nie potrzebuje specjalnego warunku „pierwszy element istnieje”.

`let else` pozostawia poprawnie związane nazwy w dalszej części tego samego zakresu. Gałąź `else` musi zakończyć bieżący przepływ przez `return`, `break`, `continue` albo inną konstrukcję rozbieżną. Samo wydrukowanie błędu i przejście dalej nie wystarczy: wówczas nazwa z nieudanego wzorca nie miałaby wartości. Dobieraj formę pod to, czy interesuje cię jedna ścieżka sukcesu, czy pełne rozróżnienie wariantów.

## Diagnostyka kompilatora

Niezgodne wyniki gałęzi to zwykle E0308. Poniżej jedna gałąź daje liczbę, a druga tekst; naprawą może być wspólny enum albo identyczny typ wyniku, zależnie od intencji.

~~~compile_fail
fn main() {
    let wynik = if true { 42 } else { "brak" };
    println!("{wynik}");
}
~~~

Drugi częsty komunikat to „`else` clause of `let...else` does not diverge”. Dodaj rzeczywiste wyjście ze ścieżki. Nie zmieniaj go na `panic!`, jeśli brak danych jest oczekiwanym wynikiem; zwróć `None` albo własny błąd. Ostrzeżenia o nieosiągalnym ramieniu `match` sprawdzaj od góry: wcześniejsze `_` mogło przechwycić wszystkie warianty.

## Praktyka produkcyjna

Każda pętla zależna od wejścia powinna mieć policzalny postęp i ograniczony koszt. Parser przesuwa pozycję, kolejka zdejmuje element, a próba sieciowa zużywa budżet ponowień i czasu. Brak postępu oznacza ryzyko zajęcia procesora przez jeden wadliwy rekord. Przy usłudze rozważ limit liczby elementów, nie tylko warunek poprawności pojedynczego elementu.

Przerwanie pętli nie cofa wcześniejszych efektów. Jeżeli trzy rekordy zapisano do bazy przed błędem czwartego, `break` nie tworzy transakcji. Zdecyduj, czy algorytm ma być atomowy, częściowy czy wznawialny, i zwracaj informację o postępie. Testuj puste wejście, trafienie limitu dokładnie oraz jego przekroczenie o jeden.

## Sprawdź, czy rozumiesz

1. Dlaczego `if` bez `else` nie może zwrócić `u32` na jednej ścieżce?
2. Co dzieje się z elementami `Vec<String>` po `for x in wektor`?
3. Jaki niezmiennik postępu chroni parser przed pustą iteracją?

## Ćwiczenia

- `A08-1` — podstawowe: napisz klasyfikator `u8`: zero, 1–9 i pozostałe; sprawdź granice 0, 9, 10 [Rozwiązanie](../rozwiazania/02_podstawy_jezyka/04_sterowanie_przeplywem.md#a08-1).
- `A08-2` — praktyczne: podwój liczby przez `for` po `&mut [i32]`, a potem wylicz sumę bez konsumowania tablicy [Rozwiązanie](../rozwiazania/02_podstawy_jezyka/04_sterowanie_przeplywem.md#a08-2).
- `A08-3` — pogłębione: napisz funkcję przyjmującą `&[u32]` i limit liczby elementów; zwróć sumę tylko gdy mieści się cały zbiór i nie ma przepełnienia [Rozwiązanie](../rozwiazania/02_podstawy_jezyka/04_sterowanie_przeplywem.md#a08-3).

## Źródła i zakres stabilności

Gałęzie i wyniki pętli opisuje [Rust Reference: loop expressions](https://doc.rust-lang.org/reference/expressions/loop-expr.html); wzorce oraz wymóg rozbieżności `let else` — [let statements](https://doc.rust-lang.org/reference/statements.html#let-statements).

## Powiązane tematy

- [Wzorce i `match`](../04_struktury_enumy_i_wzorce/02_wzorce_i_match.md)
- [Iteratory](../06_kolekcje_iteratory_i_closures/05_iteratory.md)
- [`Option` i `Result`](../07_obsluga_bledow/01_option_i_result.md)
