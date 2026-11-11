[← Spis treści](../README.md)
<!-- status: expanded -->

# `String`, `str` i Unicode

> Przykłady: **stable**, Rust 1.90.0, Edition 2024. Źródła sprawdzono 11 listopada 2026 r.

## Cele

Po tym rozdziale potrafisz:

- policzyć osobno bajty i wartości skalarne Unicode bez utożsamiania ich z grafemami;
- przeprowadzić walidowaną lub stratną konwersję bajtów według celu aplikacji;
- wyciąć prefiks na granicy UTF-8 i rozpoznać ograniczenia takiej operacji;

## Model — poprawne kodowanie i znaczenie tekstu


Tekst w Rust jest poprawnym UTF-8. `String` posiada bufor, `&str` jest
pożyczonym widokiem. Oddzielaj operacje na bajtach, scalar values i grafemach.

## Budowanie tekstu

~~~rust
use std::fmt::Write;

fn main() {
    let mut tekst = String::with_capacity(32);
    tekst.push_str("wynik");
    tekst.push(':');
    write!(&mut tekst, " {}", 42).unwrap();
    assert_eq!(tekst, "wynik: 42");
}
~~~

`format!` zwraca nowy `String`. `push_str` nie przejmuje ownership argumentu.
Trait `fmt::Write` umożliwia formatowanie bez tworzenia tymczasowego tekstu.

## Trzy poziomy

~~~rust
fn main() {
    let s = "a\u{301}🦀"; // a + combining acute accent + crab
    assert_eq!(s.len(), 7);             // bajty: 1 + 2 + 4
    assert_eq!(s.chars().count(), 3);   // scalar values
    assert_eq!(s.as_bytes()[0], b'a');
}
~~~

Użytkownik może widzieć tu dwa grafemy, ale standard library nie zapewnia
pełnej segmentacji grafemów. Wymaga ona np. crate’a **third-party**
`unicode-segmentation` i zależy od wersji standardu Unicode.

## Bezpieczne cięcie

`get(range)` zwraca `None`, jeżeli granica nie wypada między kodami UTF-8:

~~~rust
fn main() {
    let s = "żaba";
    assert_eq!(s.get(0..2), Some("ż"));
    assert_eq!(s.get(0..1), None);
    assert_eq!(s.char_indices().next(), Some((0, 'ż')));
}
~~~

Nie iteruj po `chars().nth(i)` w pętli indeksowej — każde `nth` przechodzi
od bieżącej pozycji iteratora, a odtwarzanie iteratora może dać koszt
kwadratowy. Iteruj raz lub zbuduj indeks właściwy dla domeny.

## Parsowanie i normalizacja

~~~rust
fn main() {
    let liczba: i32 = " 42 ".trim().parse().expect("poprawna liczba");
    assert_eq!(liczba, 42);
    assert!("Rust".eq_ignore_ascii_case("rUsT"));
}
~~~

Różne sekwencje Unicode mogą wyglądać identycznie. Standard library nie
normalizuje tekstu automatycznie. Przed porównaniem identyfikatorów
użytkowych zdefiniuj politykę normalizacji, wielkości liter i locale; do
pełnego Unicode użyj sprawdzonej biblioteki.

## Konwersje i własność

- `String::from(s)` / `s.to_owned()` — tworzą posiadany tekst;
- `String::from_utf8(Vec<u8>)` — waliduje UTF-8 i może oddać oryginalne bajty;
- `String::from_utf8_lossy` — zwraca `Cow<str>` i zastępuje błędy znakiem
  U+FFFD;
- `as_str` — pożycza `&str`;
- `into_bytes` — konsumuje `String` bez kopiowania bufora.

## Reguły — UTF-8 nie rozstrzyga semantyki

Każdy `String` i `str` w bezpiecznym API zawiera poprawne UTF-8. Nie oznacza to, że tekst jest poprawnym adresem, identyfikatorem ani słowem w danym języku. `char` reprezentuje Unicode scalar value, czyli punkt kodowy poza zakresem surogatów, a nie jednostkę UTF-16 czy widoczny znak użytkownika. Emoji z łącznikami i modyfikatorami może zawierać wiele wartości `char`.

Długość jest liczbą bajtów i można ją odczytać bez przechodzenia całego tekstu. `chars().count()` musi przejść przez kodowanie. Wielokrotne budowanie `s.chars().nth(i)` od zera tworzy sumę przejść po kolejnych prefiksach i może mieć koszt kwadratowy. W edytorze tekstu potrzebny bywa indeks offsetów albo struktura dostosowana do operacji, a nie zwykły `String` z udawanym dostępem losowym do grafemów.

~~~rust
fn prefiks_skalarow(s: &str, ile: usize) -> &str {
    let koniec = s.char_indices().nth(ile).map_or(s.len(), |(i, _)| i);
    &s[..koniec]
}
fn main() {
    assert_eq!(prefiks_skalarow("żółw", 2), "żó");
    assert_eq!(prefiks_skalarow("żółw", 0), "");
    assert_eq!(prefiks_skalarow("żółw", 99), "żółw");
    assert_eq!(prefiks_skalarow("a\u{301}", 1), "a");
}
~~~

`char_indices` daje offsety bajtowe na granicach UTF-8. Wybrany offset pozwala bezpiecznie utworzyć slice. Ostatnie porównanie ujawnia ograniczenie: jeden scalar value nie zachowuje całego grafemu `a` z akcentem łączącym. Przy obcinaniu nazwy w interfejsie należy ustalić regułę grafemów, a czasem również szerokości wyświetlania, która jest jeszcze innym pojęciem.

## Błędy kodowania i normalizacja

`str::from_utf8(&bajty)` waliduje widok bez przejmowania bufora. `String::from_utf8(Vec<u8>)` konsumuje bufor, a w błędzie zachowuje możliwość odzyskania bajtów. Stratna konwersja z `from_utf8_lossy` zastępuje błędy U+FFFD; przy poprawnym wejściu może zwrócić pożyczony `Cow`, a przy konieczności zastąpień tworzy posiadany tekst. To wybór polityki: w podglądzie logów bywa sensowny, w podpisanym dokumencie albo identyfikatorze może bezpowrotnie zmienić dane.

Teksty `é` oraz `e` z osobnym akcentem mogą wyglądać podobnie, ale nie muszą mieć identycznych bajtów. Biblioteka standardowa nie wykonuje normalizacji ani pełnego locale-aware case folding. `eq_ignore_ascii_case` dotyczy ASCII; nie jest porównaniem bez wielkości liter dla całego Unicode. Biblioteki **third-party** dla segmentacji i normalizacji trzeba dobierać według jawnej wersji danych Unicode oraz potrzeb domeny.

Nie normalizuj samowolnie danych binarnych, podpisów ani ścieżek systemowych. Nazwy plików nie zawsze dają się przedstawić jako Unicode: używaj `Path` i `OsStr` na granicy systemu, a tekst diagnostyczny twórz dopiero do wyświetlenia. Konwersja stratna nie może służyć jako unikalny klucz pliku.

## Diagnostyka kompilatora

`String` nie wspiera indeksowania pojedynczą liczbą. Kompilator nie wybiera za użytkownika znaczenia „pierwszego znaku”.

~~~compile_fail
fn main() {
    let tekst = String::from("żaba");
    println!("{}", tekst[0]);
}
~~~

Zakres `tekst.get(..1)` skompiluje się i zwróci `None`, bo granica leży wewnątrz dwubajtowego `ż`. Operacja `&tekst[..1]` skompiluje się, ale spanikuje; nie oznaczaj jej jako `compile_fail`. Jeśli dane mogą być niepoprawnym UTF-8, zaczynaj od `[u8]`, a nie od `from_utf8_unchecked`.

## Praktyka produkcyjna

Limituj bajty przed alokacją, a regułę widocznego skrótu określ osobno. Limit 100 grafemów nie ogranicza niezawodnie liczby bajtów, ponieważ sekwencje łączące mogą być długie. W interfejsie potrzebne mogą być dwa limity: transportowy i użytkowy.

Normalizację identyfikatorów stosuj konsekwentnie przy zapisie i wyszukiwaniu, zapisując również oryginalną postać do wyświetlania, jeśli domena tego wymaga. Normalizacja nie usuwa wszystkich podobnych wizualnie znaków. Nie wyprowadzaj z niej gwarancji bezpieczeństwa nazwy użytkownika. Testuj polskie litery, pusty tekst, sekwencje łączące, emoji oraz niepoprawne bajty.

## Sprawdź, czy rozumiesz

1. Dlaczego `len()` i `chars().count()` odpowiadają na różne pytania?
2. Kiedy stratna konwersja UTF-8 jest nieodpowiednia?
3. Czy limit scalar values jest jednocześnie limitem grafemów i bajtów?

## Ćwiczenia

- `A25-1` — podstawowe: porównaj liczbę bajtów i `char` tekstów `ą` oraz `a` z łączącym ogonkiem [Rozwiązanie](../rozwiazania/06_kolekcje_iteratory_i_closures/02_string_str_i_unicode.md#a25-1).
- `A25-2` — praktyczne: przekonwertuj niepoprawne bajty przez `String::from_utf8` i odzyskaj oryginalny wektor z błędu [Rozwiązanie](../rozwiazania/06_kolekcje_iteratory_i_closures/02_string_str_i_unicode.md#a25-2).
- `A25-3` — pogłębione: napisz funkcję zwracającą najdłuższy prefiks mieszczący się w limicie bajtów i kończący na granicy UTF-8 [Rozwiązanie](../rozwiazania/06_kolekcje_iteratory_i_closures/02_string_str_i_unicode.md#a25-3).

## Źródła i zakres stabilności

UTF-8 i własność bufora: [String](https://doc.rust-lang.org/std/string/struct.String.html). Walidacja widoku: [str::from_utf8](https://doc.rust-lang.org/std/str/fn.from_utf8.html). Granice i offsety: [str::char_indices](https://doc.rust-lang.org/std/primitive.str.html#method.char_indices).

## Powiązane tematy

- [Slices i `str`](../03_ownership_i_pamiec/04_slices_i_str.md)
- [Pliki i I/O](../13_io_siec_i_protokoly/01_pliki_io_i_procesy.md)
- [FFI, ABI i C strings](../22_ffi_i_interoperacyjnosc/01_ffi_abi_i_repr.md)
