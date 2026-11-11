[← Spis treści](../README.md)
<!-- status: expanded -->

# Stos, sterta i RAII

> Przykłady: **stable**, Rust 1.90.0, Edition 2024. Źródła sprawdzono 11 listopada 2026 r.

## Cele

Po tym rozdziale potrafisz:

- odróżnić logiczne posiadanie zasobu od fizycznego miejsca przechowywania wartości;
- przewidzieć niszczenie lokalnych bindingów i pól struktury;
- wybrać jawne zakończenie operacji, gdy błąd sprzątania musi dotrzeć do klienta;

## Model — właściciel, zakres i destruktor


Rust zarządza zasobami deterministycznie. Wartość ma właściciela, a gdy
właściciel wychodzi z zakresu, uruchamiany jest destruktor `Drop`. Ten wzorzec
to RAII: pozyskanie zasobu jest inicjalizacją obiektu.

## Stos i sterta

Stos przechowuje ramki wywołań i dane o rozmiarze znanym podczas kompilacji.
Operacje na jego szczycie są bardzo tanie. Sterta przechowuje dane o
dynamicznym rozmiarze lub czasie życia; alokator zwraca adres bloku.

`String` ma stały rozmiar wartości: jego nagłówek zawiera wskaźnik, długość
i pojemność. Lokalny nagłówek jest zwykle przechowywany na stosie albo
w rejestrach; bajty tekstu są w posiadanym buforze na stercie. `Vec<T>` ma
podobną reprezentację.

~~~rust
use std::mem::{size_of, size_of_val};

fn main() {
    let tekst = String::from("Rust");
    assert_eq!(size_of_val(&tekst), size_of::<String>());
    assert_eq!(tekst.len(), 4);
}
~~~

Rozmiar `String` zależy od ABI platformy; nie zakładaj konkretnej liczby
bajtów w przenośnym kodzie.

## Deterministyczne sprzątanie

~~~rust
struct Znacznik(&'static str);

impl Drop for Znacznik {
    fn drop(&mut self) {
        println!("drop {}", self.0);
    }
}

fn main() {
    let _a = Znacznik("A");
    {
        let _b = Znacznik("B");
    } // B jest niszczone tutaj
} // A jest niszczone tutaj
~~~

Zmienne lokalne są zwykle niszczone w odwrotnej kolejności deklaracji.
Pola struktury są niszczone w kolejności deklaracji pól po wykonaniu
`Drop::drop` struktury. Nie wywołuje się `value.drop()` bezpośrednio; do
wcześniejszego zniszczenia służy `std::mem::drop(value)`.

## RAII obejmuje więcej niż pamięć

Destruktor może zamknąć plik, zwolnić blokadę, socket lub inny uchwyt.
Guard zwrócony przez `Mutex::lock` zwalnia blokadę przy wyjściu z zakresu,
także podczas propagacji błędu lub panic z unwinding.

Rust nie gwarantuje uruchomienia destruktorów przy `process::abort`, nagłym
zakończeniu procesu ani wycieku przez `mem::forget`. Destruktor nie jest więc
miejscem dla jedynej kopii krytycznej operacji biznesowej.

## Stos nie jest nieskończony

Głęboka rekursja może przepełnić stos. Duże dane można przenieść na stertę
przez `Box<T>`, ale samo opakowanie nie zmienia algorytmu rekursywnego.
W strukturach rekurencyjnych indirection jest też potrzebne, aby typ miał
skończony rozmiar.

~~~rust
enum Lista {
    Element(i32, Box<Lista>),
    Koniec,
}

fn main() {
    let lista = Lista::Element(1, Box::new(Lista::Koniec));
    match lista {
        Lista::Element(n, reszta) => {
            assert_eq!(n, 1);
            assert!(matches!(*reszta, Lista::Koniec));
        }
        Lista::Koniec => unreachable!(),
    }
}
~~~

## Reguły — pamięć i semantyka to osobne warstwy

„Na stosie” jest użytecznym uproszczeniem dla lokalnych wartości, lecz optymalizator może całkowicie usunąć wartość albo przechowywać ją w rejestrze. `String` umieszczony jako pole `Box<Rekord>` ma swój nagłówek wewnątrz alokacji tego rekordu, a nie obowiązkowo na stosie. Istotny kontrakt brzmi: `String` posiada swój bufor, niezależnie od położenia nagłówka. Nie wyprowadzaj reguł bezpieczeństwa z obserwowanego adresu lokalnej zmiennej.

`size_of::<T>()` mierzy rozmiar samej wartości, bez rekurencyjnego sumowania posiadanych alokacji. Dwa `Vec<u8>` o identycznym typie mogą posiadać bufory o zupełnie różnych pojemnościach. Dla typu zero-sized rozmiar wartości może wynosić zero; ani `Box`, ani `Vec` nie gwarantują osobnej alokacji dla takiego elementu. Ma to znaczenie przy szacowaniu pamięci i projektowaniu własnych alokatorów.

Pożyczka może skończyć się przy ostatnim użyciu, ale właściciel zwykle pozostaje do końca swojego drop scope. Jeżeli blokada ma zostać zwolniona przed kosztowną pracą, zaznacz granicę blokiem. To czytelniejszy kontrakt niż nadzieja, że optymalizator wcześniej zniszczy nieużywaną zmienną.

~~~rust
use std::sync::Mutex;
fn main() {
    let dane = Mutex::new(vec![1, 2]);
    let kopia = {
        let mut guard = dane.lock().unwrap();
        guard.push(3);
        guard.clone()
    }; // guard zwalnia blokadę przed pracą na kopii
    assert_eq!(kopia.into_iter().sum::<i32>(), 6);
    assert!(dane.try_lock().is_ok());
}
~~~

Kopia bufora jest tutaj celowym kosztem skrócenia sekcji krytycznej. Alternatywą może być przeniesienie danych przez `mem::take`, ale zmienia ono stan pozostawiany pod blokadą. W obu projektach trzeba ustalić, czy pozostali użytkownicy mogą w tym momencie zobaczyć pusty bufor. RAII rozwiązuje zwolnienie blokady, a nie protokół wymiany danych.

## Diagnostyka kompilatora

Rekurencyjny typ bez pośrednika nie ma skończonego rozmiaru. Kompilator zgłasza E0072 i zwykle sugeruje `Box`, referencję albo inny wskaźnik.

~~~compile_fail
enum Lista {
    Element(i32, Lista),
    Koniec,
}
fn main() {}
~~~

`Box<Lista>` nadaje polu stały rozmiar, ale nie gwarantuje stałego zużycia stosu przy rekursywnym przetwarzaniu ani niszczeniu bardzo długiej listy. Innym błędem jest jawne `wartosc.drop()`: język zabrania bezpośredniego wywoływania destruktora; `drop(wartosc)` konsumuje właściciela w kontrolowany sposób. `drop(&wartosc)` niszczy tylko referencję.

## Praktyka produkcyjna

Operacje mogące zawieść powinny mieć jawną metodę kończenia, na przykład `finish(self) -> Result<...>`. Destruktor ma sygnaturę bez wyniku, więc nie potrafi przekazać błędu zamknięcia pliku jako zwykłego `Result`. W zapisie trwałych danych rozróżniaj opróżnienie bufora użytkownika od synchronizacji z nośnikiem i gwarancji konkretnego systemu plików.

Unikaj paniki w destruktorze. Druga panika podczas odwijania stosu może zakończyć proces, a profil `panic = "abort"` w ogóle nie odwija stosu. Krytyczną operację biznesową wykonuj i potwierdzaj jawnie. Dla dużych struktur testuj koszt ich niszczenia; brak wycieku nie dowodzi, że zamknięcie usługi zmieści się w budżecie czasu.

## Sprawdź, czy rozumiesz

1. Czy `size_of::<Vec<u8>>()` obejmuje jego elementy?
2. Dlaczego koniec pożyczki nie dowodzi zwolnienia blokady?
3. Jak zwrócić błąd operacji końcowej, skoro `Drop::drop` zwraca `()`?

## Ćwiczenia

- `A10-1` — podstawowe: porównaj rozmiar dwóch `String` z tekstem o różnej długości bez zakładania liczby bajtów nagłówka [Rozwiązanie](../rozwiazania/03_ownership_i_pamiec/01_stos_sterta_i_raii.md#a10-1).
- `A10-2` — praktyczne: utwórz typ z `Drop`, zapisz kolejność niszczenia dwóch lokalnych wartości do współdzielonego dziennika [Rozwiązanie](../rozwiazania/03_ownership_i_pamiec/01_stos_sterta_i_raii.md#a10-2).
- `A10-3` — pogłębione: zaprojektuj obiekt zapisu z `finish(self) -> Result`; pokaż, że nieudane zatwierdzenie jest obserwowalne przed destruktorem [Rozwiązanie](../rozwiazania/03_ownership_i_pamiec/01_stos_sterta_i_raii.md#a10-3).

## Źródła i zakres stabilności

Kolejność niszczenia i przypisanie: [Rust Reference: destructors](https://doc.rust-lang.org/reference/destructors.html). Rozmiary wartości: [std::mem::size_of](https://doc.rust-lang.org/std/mem/fn.size_of.html). `Box` dla ZST: [std::boxed](https://doc.rust-lang.org/std/boxed/index.html).

## Powiązane tematy

- [Ownership, move i Copy](02_ownership_move_i_copy.md)
- [Smart pointery](06_smart_pointery_i_interior_mutability.md)
- [Layout i alignment](../21_unsafe_soundness_i_model_pamieci/03_layout_alignment_i_uninitialized_memory.md)
