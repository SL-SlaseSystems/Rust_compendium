[← Spis treści](../README.md)
<!-- status: expanded -->

# Wzorce i `match`

> Przykłady: **stable**, Rust 1.90.0, Edition 2024. Źródła sprawdzono 11 listopada 2026 r.

## Cele

Po tym rozdziale potrafisz:

- rozróżnić wzorzec obalalny od nieobalalnego i wybrać odpowiednią konstrukcję;
- przewidzieć przeniesienie albo pożyczenie pól podczas dopasowania;
- napisać wyczerpujący `match` bez ukrycia ważnego przypadku pod `_`;

## Model — kształt, wiązanie i kolejność ramion


Wzorzec jednocześnie sprawdza kształt wartości i wiąże jej części. Występuje
w `match`, `let`, parametrach funkcji, `if let`, `while let` i `let else`.

## Wyczerpujący `match`

~~~rust
#[derive(Debug)]
enum Zdarzenie {
    Klik { x: i32, y: i32 },
    Klawisz(char),
    Zamkniecie,
}

fn opis(z: Zdarzenie) -> String {
    match z {
        Zdarzenie::Klik { x: 0, y } => format!("lewa krawędź, y={y}"),
        Zdarzenie::Klik { x, y } => format!("klik {x},{y}"),
        Zdarzenie::Klawisz('q' | 'Q') => "wyjście".into(),
        Zdarzenie::Klawisz(c) if c.is_ascii_digit() => "cyfra".into(),
        Zdarzenie::Klawisz(_) => "inny klawisz".into(),
        Zdarzenie::Zamkniecie => "zamknięcie".into(),
    }
}

fn main() {
    assert_eq!(opis(Zdarzenie::Klawisz('7')), "cyfra");
    assert_eq!(opis(Zdarzenie::Klik { x: 0, y: 8 }), "lewa krawędź, y=8");
    assert_eq!(opis(Zdarzenie::Zamkniecie), "zamknięcie");
}
~~~

Ramiona są sprawdzane od góry. Guard `if` nie uczestniczy w sprawdzaniu
wyczerpującości tak precyzyjnie jak sam wzorzec.

## Refutable i irrefutable

Wzorzec `let (x, y) = para` pasuje zawsze i jest irrefutable. `Some(x)` może
nie pasować, więc wymaga `if let`, `let else` albo `match`.

~~~rust
fn dodaj(opcja: Option<i32>, suma: &mut i32) {
    if let Some(x) = opcja {
        *suma += x;
    }
}

fn main() {
    let mut suma = 0;
    for x in [Some(2), None, Some(5)] {
        dodaj(x, &mut suma);
    }
    assert_eq!(suma, 7);
}
~~~

## Destrukturyzacja i ownership

Wzorzec na wartości może przenieść pola. `ref` i `ref mut` jawnie wiążą
referencję, choć match ergonomics często robi to automatycznie, gdy dopasowana
wartość jest referencją.

~~~rust
struct Rekord {
    nazwa: String,
    wynik: u32,
}

fn main() {
    let r = Rekord { nazwa: "Ada".into(), wynik: 10 };
    let Rekord { ref nazwa, wynik } = r;
    assert_eq!(nazwa, "Ada");
    assert_eq!(wynik, 10);
    assert_eq!(r.nazwa, "Ada");
}
~~~

Operator `@` wiąże całą wartość i jednocześnie ją sprawdza:

~~~rust
fn kategoria(n: u8) -> &'static str {
    match n {
        zero @ 0 => {
            assert_eq!(zero, 0);
            "zero"
        }
        mala @ 1..=9 => {
            assert!(mala < 10);
            "mała"
        }
        _ => "duża",
    }
}

fn main() {
    assert_eq!(kategoria(7), "mała");
}
~~~

`..` ignoruje pozostałe pola lub elementy. Podkreślenie `_` niczego nie
wiąże; nazwa zaczynająca się od podkreślenia nadal może przenieść wartość.

## Reguły — dopasowanie nie jest warunkiem tekstowym

Wzorzec opisuje strukturę: wariant enuma, liczbę elementów slice, literał albo zakres. Guard jest dopiero dodatkowym obliczeniem logicznym po dopasowaniu. Dwa guardy `if n > 0` i `if n <= 0` nie zastępują dla kompilatora pełnego dowodu pokrycia wszystkich wartości. Pozostaw jawne ramię rezerwowe, jeśli podział zależy od dowolnego kodu warunku.

Binding o nazwie `oczekiwany` we wzorcu nie porównuje z lokalną zmienną o tej nazwie: tworzy nową nazwę i ją przesłania. Do porównania z wartością ustalaną w runtime użyj guarda, na przykład `Some(x) if x == oczekiwany`. Stałe i warianty z jednoznacznymi ścieżkami mogą natomiast stanowić wzorce wartości.

~~~rust
fn odczytaj(dane: &[u8]) -> Option<(u8, &[u8])> {
    match dane {
        [typ @ 1..=3, reszta @ ..] => Some((*typ, reszta)),
        _ => None,
    }
}
fn main() {
    assert_eq!(odczytaj(&[2, 9, 8]), Some((2, &[9, 8][..])));
    assert_eq!(odczytaj(&[1]), Some((1, &[][..])));
    assert_eq!(odczytaj(&[]), None);
    assert_eq!(odczytaj(&[4]), None);
}
~~~

Wzorzec wymaga co najmniej jednego bajtu. `typ` jest pożyczonym elementem i kopiujemy go przez `*typ`, a `reszta` pozostaje pożyczonym slice. Operator `@` zachowuje nazwę dla wartości, której kształt dodatkowo ograniczono. Cała funkcja nie alokuje, lecz jej wynik nie może przeżyć wejścia. Pusta reszta jest legalna dla nagłówka bez danych.

Dopasowanie `match &wartosc` zwykle wiąże pola przez referencję dzięki match ergonomics; `match wartosc` może je przenieść. Znak `ref` tworzy binding referencyjny, a wzorzec `&` dopasowuje już istniejącą referencję. W Edition 2024 nie można dowolnie dodawać `ref`, `ref mut` i `mut` przy odziedziczonym trybie referencyjnym: albo korzystaj z ergonomii konsekwentnie, albo wypisz pełny wzorzec referencji. Stare przykłady z wcześniejszych editions mogą więc wymagać migracji.

Wzorce alternatywne `A(x) | B(x)` muszą wiązać zgodne nazwy w zgodnych trybach. `..` skraca pomijanie pól, ale może również ukryć nowo dodane pole w lokalnym kodzie. Jeżeli nowe dane powinny wymusić przegląd przetwarzania, jawne wymienienie pól daje lepszy sygnał podczas refaktoryzacji.

## Diagnostyka kompilatora

Obalalny wzorzec w zwykłym `let` daje E0005: `None` nie tworzy wiązania `x`. Wybierz `let else`, `if let` albo pełny `match`.

~~~compile_fail
fn main() {
    let opcja: Option<u32> = None;
    let Some(x) = opcja;
    println!("{x}");
}
~~~

E0004 oznacza brak wariantu w `match`, a ostrzeżenie `unreachable_patterns` sygnalizuje ramię przechwycone wcześniej. Wzorzec `_nazwa` nadal wiąże i może przenieść wartość, podczas gdy `_` jej nie wiąże. Jeżeli dalszy kod zgłasza E0382, sprawdź właśnie tryb wiązania pól, zamiast dodawać `clone` do całego dopasowywanego obiektu.

## Praktyka produkcyjna

W maszynie stanów używaj pełnego `match`, gdy dodanie nowego wariantu powinno wymusić decyzję w każdym miejscu. `_` jest odpowiednie dla świadomie nieobsługiwanych kategorii, ale komentarz powinien wyjaśniać ich wspólne znaczenie. Długie guardy przenieś do nazwanych funkcji domenowych, zachowując kolejność priorytetów.

Dopasowanie nie waliduje automatycznie semantyki pól. Wariant `Przelew { kwota }` może zawierać zero, jeżeli konstruktor tego nie zabrania. Połącz wzorce z walidowanymi typami, aby nie powtarzać tych samych warunków. Przy pożyczającym parserze trzymaj pełny bufor przy życiu, a zapis do długiej kolejki wykonuj przez jawne przejęcie lub kopię potrzebnego fragmentu.

## Sprawdź, czy rozumiesz

1. Dlaczego `Some(oczekiwany)` zwykle nie porównuje z lokalną zmienną?
2. Kiedy `match &rekord` zapobiega przeniesieniu `String`?
3. Dlaczego dwa przeciwne guardy nie zawsze tworzą wyczerpujący `match`?

## Ćwiczenia

- `A17-1` — podstawowe: napisz `match` dla `Option<u8>` rozróżniający brak, zero i inne wartości [Rozwiązanie](../rozwiazania/04_struktury_enumy_i_wzorce/02_wzorce_i_match.md#a17-1).
- `A17-2` — praktyczne: dopasuj `&Option<String>` tak, aby otrzymać `Option<&str>` i zachować właściciela [Rozwiązanie](../rozwiazania/04_struktury_enumy_i_wzorce/02_wzorce_i_match.md#a17-2).
- `A17-3` — pogłębione: napisz parser nagłówka `[wersja, dlugosc, dane @ ..]`, który przyjmuje tylko wersję 1 i dokładnie deklarowaną liczbę bajtów [Rozwiązanie](../rozwiazania/04_struktury_enumy_i_wzorce/02_wzorce_i_match.md#a17-3).

## Źródła i zakres stabilności

Wzorce, binding modes i ograniczenia Edition 2024: [Rust Reference: patterns](https://doc.rust-lang.org/reference/patterns.html). Zmiany migracyjne: [Edition Guide: match ergonomics](https://doc.rust-lang.org/edition-guide/rust-2024/match-ergonomics.html).

## Powiązane tematy

- [Struktury i enumy](01_struktury_enumy_i_metody.md)
- [Sterowanie przepływem](../02_podstawy_jezyka/04_sterowanie_przeplywem.md)
- [`Option` i `Result`](../07_obsluga_bledow/01_option_i_result.md)
