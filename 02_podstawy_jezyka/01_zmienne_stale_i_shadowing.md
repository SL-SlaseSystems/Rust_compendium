[← Spis treści](../README.md)
<!-- status: expanded -->

# Zmienne, stałe i shadowing

> Przykłady: **stable**, Rust 1.90.0, Edition 2024. Źródła uzupełniono 11 listopada 2026 r.; nie deklarujemy testu na Rust 1.98.1.

## Cele

Po tym rozdziale potrafisz:

- dobrać binding, wzorzec `let`, `const` albo `static` do czasu życia danych;
- wyjaśnić inicjalizację, shadowing i zakres niszczenia wartości;
- naprawić E0381/E0384 bez wprowadzania globalnej mutacji `unsafe`.

## Model — binding, wartość i place

Wzorzec w `let` wiąże nazwę lub nazwy z dopasowaną wartością; późniejsze użycie identyfikatora może utworzyć place expression, czyli miejsce odczytu albo zapisu. Zwykłe `let` wymaga wzorca nieobalalnego (irrefutable): musi zawsze pasować. Wiązanie domyślnie przenosi wartość albo kopiuje ją dla `Copy`; `ref`/`ref mut` oraz dziedziczony tryb wiązania z match ergonomics tworzą wiązania referencyjne. Wzorce `&`/`&mut` zamiast tego dopasowują, destrukturyzują i dereferencjują już istniejącą referencję. Destrukturyzacja jest więc bezpośrednia i użyteczna.

~~~rust
fn main() {
    let (nazwa, port) = ("api", 8080_u16);
    let mut licznik = 0;
    licznik += 1;
    assert_eq!((nazwa, port, licznik), ("api", 8080, 1));
}
~~~

`mut` dotyczy bindingu, nie koniecznie wnętrza obiektu: `Cell` i `Mutex` oferują mutowalność wnętrza (interior mutability) przez własne API. Inicjalizacja może być odroczona, lecz analiza pewnej inicjalizacji (definite assignment) wymaga przypisania na każdej ścieżce przed odczytem.

Shadowing tworzy nowy binding; może zmienić typ. Stary binding pozostaje w swoim drop scope, a jego wartość zwykle jest niszczona na końcu tego zakresu, nie w chwili ostatniego użycia ani automatycznie przy shadowingu. Nieleksykalne czasy życia (non-lexical lifetimes, NLL) mogą zakończyć *pożyczkę* po ostatnim użyciu, ale nie przesuwają `Drop` wartości.

~~~rust
fn main() {
    let wejscie = String::from(" 41 ");
    let wejscie = wejscie.trim();
    let wejscie: i32 = wejscie.parse().expect("liczba");
    assert_eq!(wejscie + 1, 42);
}
~~~

`const` wymaga typu i wyrażenia obliczalnego w czasie kompilacji; nie ma jednej adresowalnej globalnej lokacji, a każde użycie oznacza osobną wartość. `static` oznacza jedną globalną lokację przez cały program. Odczyt i zapis `static mut` są operacjami `unsafe`; w Edition 2024 tworzenie referencji do niego jest domyślnie odrzucane przez `static_mut_refs`, ponieważ aliasowanie globalnej mutacji łatwo łamie reguły pamięci. Preferuj atomiki albo blokady, nie „bezpieczny accessor” ukrywający `static mut`.

~~~rust
use std::sync::atomic::{AtomicUsize, Ordering};

static LICZNIK: AtomicUsize = AtomicUsize::new(0);

fn main() {
    assert_eq!(LICZNIK.fetch_add(1, Ordering::Relaxed), 0);
    assert_eq!(LICZNIK.load(Ordering::Relaxed), 1);
}
~~~

## Nazwa pomijana i zasób nadal posiadany

`let _ = wyrazenie;` nie tworzy nazwanego właściciela wyniku. Tymczasowy guard uzyskany w takim wyrażeniu może zostać od razu zniszczony. `let _guard = wyrazenie;` tworzy natomiast zwykły binding, którego nazwa jedynie wyłącza ostrzeżenie o nieużyciu. Jeżeli wyrażenie zwraca blokadę, ta różnica zmienia czas jej utrzymywania. Nie używaj pojedynczego `_` do przechowywania zasobu przez resztę bloku.

Podobnie shadowing nie jest tym samym co przypisanie. `x = nowa_wartosc` zastępuje zawartość tego samego miejsca i niszczy poprzednią zainicjalizowaną wartość. `let x = nowa_wartosc` wprowadza kolejne miejsce, nawet jeśli nazwa jest taka sama. Przy zwykłych liczbach trudno to zauważyć, lecz przy blokadzie lub pliku ma to znaczenie dla kolejności zdarzeń.

~~~rust
fn main() {
    let mut napis = String::from("stary");
    napis = String::from("nowy");
    assert_eq!(napis, "nowy");
    let napis = napis.len();
    assert_eq!(napis, 4);
}
~~~

Pierwsza zmiana utrzymuje typ `String`; druga tworzy binding typu `usize` i konsumuje wynik odczytu długości. Stary bufor nie jest dostępny przez nazwę, ale nie należy na tej podstawie wnioskować o jego dokładnym momencie zwolnienia. Gdy czas zwolnienia jest częścią protokołu, użyj bloku albo `drop` przed zmianą etapu.

Stała nie jest także zamiennikiem konfigurowalnego ustawienia: `const LIMIT` wbudowuje decyzję w program, a argument funkcji pozwala różnym instancjom usługi mieć różne limity. Globalną mutację ogranicz do sytuacji, w których współdzielona tożsamość jest wymagana, i dokumentuj synchronizację.

## Diagnostyka kompilatora

E0381 oznacza odczyt bindingu przed pewną inicjalizacją; przypisz go w każdej gałęzi albo użyj `Option`. E0384 oznacza próbę przypisania do niemutowalnego bindingu; dodaj `mut` tylko gdy zmienia się stan tej samej tożsamości, a nie gdy etap transformacji zasługuje na shadowing.

~~~compile_fail
fn main() {
    let wynik: i32;
    if false { wynik = 1; }
    println!("{wynik}"); // E0381
}
~~~

~~~compile_fail
fn main() {
    let port = 8080;
    port = 8081; // E0384
}
~~~

## Zakres i kolejność `Drop`

Lokalne bindingi w tym samym leksykalnym drop scope są niszczone w odwrotnej kolejności deklaracji; shadowed bindingi nadal mają własne scope'y. Pola agregatu są natomiast niszczone w kolejności deklaracji. To odrębne od NLL.

## Praktyka produkcyjna

Używaj wzorców `let` do wydobycia struktury, jawnego typu przy granicach parsowania i shadowingu dla kolejnych reprezentacji jednego pojęcia. Dla globalnego stanu wybierz `Atomic*`, `Mutex` lub przekaż zależność jawnie. Szczegóły opisują [Reference: variables](https://doc.rust-lang.org/reference/variables.html), [destructors](https://doc.rust-lang.org/reference/destructors.html) i [static items](https://doc.rust-lang.org/reference/items/static-items.html).

## Sprawdź, czy rozumiesz

1. Dlaczego NLL nie oznacza wcześniejszego `Drop`?
2. Czym różni się mutowalność bindingu od interior mutability?
3. Dlaczego `static mut` nie jest zamiennikiem atomika?

## Ćwiczenia

- `P01-1` — podstawowe: zainicjalizuj `wynik` na wszystkich gałęziach bez wartości domyślnej. Porównaj z [rozwiązaniem](../rozwiazania/02_podstawy_jezyka/01_zmienne_stale_i_shadowing.md#p01-1).
- `P01-2` — praktyczne: przekształć tekst do `u16` przez shadowing, bez `mut`. Porównaj z [rozwiązaniem](../rozwiazania/02_podstawy_jezyka/01_zmienne_stale_i_shadowing.md#p01-2).
- `P01-3` — pogłębione: pokaż kolejność drop dla shadowed bindingów. Porównaj z [rozwiązaniem](../rozwiazania/02_podstawy_jezyka/01_zmienne_stale_i_shadowing.md#p01-3).

## Źródła i zakres stabilności

Stałe i tożsamość: [Reference: constant items](https://doc.rust-lang.org/reference/items/constant-items.html) i [static items](https://doc.rust-lang.org/reference/items/static-items.html). Scope i zniszczenie są odrębne od ostatniego użycia pożyczki.

## Powiązane tematy

- [Typy i konwersje](02_typy_i_konwersje.md)
- [Stos, sterta i RAII](../03_ownership_i_pamiec/01_stos_sterta_i_raii.md)
- [Smart pointery i interior mutability](../03_ownership_i_pamiec/06_smart_pointery_i_interior_mutability.md)
