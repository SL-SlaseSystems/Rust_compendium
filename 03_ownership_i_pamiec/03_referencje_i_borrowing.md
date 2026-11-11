[← Spis treści](../README.md)
<!-- status: expanded -->

# Referencje i borrowing

> Przykłady: **stable**, Rust 1.90.0, Edition 2024. Źródła sprawdzono 11 listopada 2026 r.

## Cele

Po tym rozdziale potrafisz:

- wykryć konflikt pożyczek i wskazać ich ostatnie rzeczywiste użycie;
- rozróżnić przeniesienie `&mut T` od jego krótkiego ponownego pożyczenia;
- podzielić mutowalną sekwencję na rozłączne części przez bezpieczne API;

## Model — dostęp współdzielony albo wyłączny


Referencja pozwala korzystać z wartości bez przejmowania ownership. Jest
zawsze ważna dla swojego typu i nie może być null. Podstawowe formy to
współdzielona `&T` i mutowalna `&mut T`.

## Dwie centralne reguły

W danym okresie użycia wartości można mieć:

1. dowolnie wiele referencji współdzielonych; albo
2. jedną referencję mutowalną.

Dodatkowo referencja nie może żyć dłużej niż referent. Te reguły eliminują
wiszące wskaźniki i wyścigi danych.

~~~rust
fn dopisz_wykrzyknik(tekst: &mut String) {
    tekst.push('!');
}

fn main() {
    let mut tekst = String::from("Rust");
    let dlugosc = tekst.len(); // krótka pożyczka współdzielona
    dopisz_wykrzyknik(&mut tekst);
    assert_eq!((dlugosc, tekst.as_str()), (4, "Rust!"));
}
~~~

Non-lexical lifetimes (NLL) pozwalają zakończyć pożyczkę przy ostatnim użyciu,
a nie dopiero przy końcu całego bloku.

## Konflikt pożyczek

~~~compile_fail
fn main() {
    let mut tekst = String::from("abc");
    let pierwsza = &tekst;
    tekst.push('d');
    println!("{pierwsza}");
}
~~~

`push` może realokować bufor i unieważnić `pierwsza`. Kompilator odrzuca kod
niezależnie od tego, czy w tym konkretnym uruchomieniu pojemność by wystarczyła.

## Reborrowing

Przekazanie `&mut T` do funkcji tworzy zwykle krótszą reborrow, dzięki czemu
oryginalnej referencji można użyć po wywołaniu:

~~~rust
fn zwieksz(x: &mut i32) {
    *x += 1;
}

fn main() {
    let mut liczba = 1;
    let r = &mut liczba;
    zwieksz(r);
    zwieksz(r);
    assert_eq!(*r, 3);
}
~~~

Operator `*` dereferencjonuje. Rust stosuje też deref coercion w typowych
miejscach, np. przekazując `&String` tam, gdzie oczekiwane jest `&str`.

## Referencja a surowy wskaźnik

`&T` niesie silne gwarancje ważności, wyrównania i aliasowania. `*const T`
oraz `*mut T` mogą być null lub nieważne; utworzenie ich jest zwykle
bezpieczne, ale dereferencja wymaga `unsafe`. Nie konwertuj wskaźnika obcego
API na referencję, dopóki nie udowodnisz wszystkich jej invariants.

## Projektowanie sygnatur

- przyjmuj `&str` zamiast `&String`, gdy potrzebujesz tylko widoku tekstu;
- przyjmuj `&[T]` zamiast `&Vec<T>`;
- przyjmuj `T`, gdy funkcja ma zachować lub zniszczyć wartość;
- skracaj zakres `&mut`, aby zmniejszyć konflikty;
- nie zwracaj referencji do lokalnej wartości.

~~~compile_fail
fn bledna_referencja() -> &'static String {
    let lokalny = String::from("znika");
    &lokalny
}
~~~

## Reguły — wyłączność dotyczy dostępu

Reguła „jedno `&mut`” jest skrótem dotyczącym aktywnego dostępu do nakładającej się pamięci. Nie zakazuje dwóch wyłącznych referencji do różnych pól struktury ani do rozłącznych części slice. Wyłączna referencja nie musi być używana do mutacji: nawet sam odczyt przez nią jest objęty prawem wyłączności. `&T` zwykle zamraża dane obserwowane przez tę ścieżkę, z wyjątkiem legalnej mutowalności wnętrza zbudowanej na `UnsafeCell`.

NLL analizuje rzeczywiste użycia, ale nie odgaduje intencji biznesowej. Referencja przechowana w strukturze lub iteratorze pozostaje potrzebna, jeżeli później odczytasz ten obiekt. Skrócenie zakresu, skopiowanie małego wyniku albo zakończenie pracy iteratora często wyraża zamierzoną granicę lepiej niż próba dodawania adnotacji lifetime.

~~~rust
fn main() {
    let mut dane = [10, 20, 30, 40];
    let (lewa, prawa) = dane.split_at_mut(2);
    lewa[0] += prawa[0];
    prawa[1] += lewa[1];
    assert_eq!(dane, [40, 20, 30, 60]);
}
~~~

`split_at_mut` sprawdza punkt podziału i gwarantuje rozłączność wyników. Kompilator nie musi dowodzić, że dwa dowolne wyrażenia indeksowe mają różne wyniki. Przy API wymagającym dwóch mutowalnych fragmentów użyj właśnie operacji dokumentującej podział. Zwykłe `let a = &mut v[i]; let b = &mut v[j];` nie dostarcza takiego dowodu dla dynamicznych indeksów.

W `zwieksz(r)` oczekiwany typ parametru pozwala utworzyć krótsze `&mut *r`. Natomiast `let drugi = r;` może przenieść samo `&mut`, po czym stara nazwa nie jest dostępna. Gdy chcesz jawnie zaznaczyć reborrow, napisz `let drugi = &mut *r;` i zakończ jego używanie przed powrotem do `r`. Rozróżnienie wynika z kontekstu koercji, nie z dowolnej decyzji kompilatora.

Wybrane wywołania metod korzystają z pożyczania dwufazowego. Dzięki temu `v.push(v.len())` może być poprawne, chociaż jawne utworzenie `&mut v` przed odczytem długości może spowodować konflikt. To ograniczony mechanizm rezerwacji i aktywacji pożyczki; nie jest ogólną zgodą na równoczesny odczyt oraz mutację dowolnej struktury.

## Diagnostyka kompilatora

Konflikt E0499 oznacza dwie nakładające się pożyczki wyłączne. Ostatnie użycie `pierwszy` jest po utworzeniu `drugi`, więc pożyczki muszą być aktywne razem.

~~~compile_fail
fn main() {
    let mut dane = [1, 2];
    let pierwszy = &mut dane[0];
    let drugi = &mut dane[1];
    *pierwszy += *drugi;
}
~~~

Naprawą dla tych dwóch elementów jest `split_at_mut(1)`, a nie `unsafe` z założeniem, że „przecież indeksy są różne”. Przy E0502 znajdź późniejszy odczyt referencji współdzielonej. Przy E0515 zwrot wskazuje dane lokalne; zwróć właściciela albo fragment danych wejściowych. Typ `&'static` nie przedłuża życia lokalnego bufora.

## Praktyka produkcyjna

Przyjmuj najmniejsze potrzebne uprawnienie: widok tylko do odczytu dla parsowania, `&mut` dla transformacji, własność dla przechowania. Duże struktury dziel na niezależne pola, jeśli operacje naturalnie używają ich rozłącznie. Metoda przyjmująca `&mut self` pożycza całe `self` według swojej sygnatury; klient nie zna jej wewnętrznego użycia pól.

Nie walcz z diagnostyką przez przypadkowe klonowanie całych kolekcji. Najpierw zapisz na kartce, kto posiada bufor, kto go czyta i czy operacja może realokować. Jeżeli dwie fazy wymagają sprzecznych uprawnień, rozdziel je na odczyt metadanych i mutację. Przykładowo skopiowanie indeksu `usize` zwykle kosztuje mniej niż sklonowanie całego tekstu.

## Sprawdź, czy rozumiesz

1. Dlaczego kompilator dopuszcza mutowanie dwóch pól, ale nie musi rozumieć dwóch indeksów?
2. Czym różnią się `let s = r` i `let s = &mut *r` dla `&mut T`?
3. Czy posiadanie dużej pojemności `Vec` uchyla konflikt z jego `push`?

## Ćwiczenia

- `A12-1` — podstawowe: napisz `dlugosc(&str) -> usize` i po wywołaniu nadal użyj właściciela `String` [Rozwiązanie](../rozwiazania/03_ownership_i_pamiec/03_referencje_i_borrowing.md#a12-1).
- `A12-2` — praktyczne: zwiększ pierwszy i ostatni element niepustej sekwencji, obsługując osobno długości 0 i 1 [Rozwiązanie](../rozwiazania/03_ownership_i_pamiec/03_referencje_i_borrowing.md#a12-2).
- `A12-3` — pogłębione: napisz funkcję zamieniającą dwa elementy slice przez bezpieczne `swap`; uzasadnij wybór kontraktu dla błędnych indeksów [Rozwiązanie](../rozwiazania/03_ownership_i_pamiec/03_referencje_i_borrowing.md#a12-3).

## Źródła i zakres stabilności

Referencje: [Reference: pointer types](https://doc.rust-lang.org/reference/types/pointer.html). Podział slice: [slice::split_at_mut](https://doc.rust-lang.org/std/primitive.slice.html#method.split_at_mut). Pożyczanie dwufazowe jest opisane jako mechanizm implementacji w [Rustc Dev Guide](https://rustc-dev-guide.rust-lang.org/borrow_check/two_phase_borrows.html).

## Powiązane tematy

- [Slices i `str`](04_slices_i_str.md)
- [Lifetimes](05_lifetimes.md)
- [Raw pointers i aliasing](../21_unsafe_soundness_i_model_pamieci/02_raw_pointers_aliasing_i_provenance.md)
