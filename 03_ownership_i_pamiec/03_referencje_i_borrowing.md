[← Spis treści](../README.md)

# Referencje i borrowing

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

## Powiązane tematy

- [Slices i `str`](04_slices_i_str.md)
- [Lifetimes](05_lifetimes.md)
- [Raw pointers i aliasing](../zaawansowane/02_raw_pointers_aliasing_i_provenance.md)
