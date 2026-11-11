[← Spis treści](../README.md)
<!-- status: expanded -->

# Slices i `str`

> Przykłady: **stable**, Rust 1.90.0, Edition 2024. Źródła sprawdzono 11 listopada 2026 r.

## Cele

Po tym rozdziale potrafisz:

- zaprojektować funkcję przyjmującą widok tablicy lub wektora bez alokacji;
- obsłużyć zakres poza długością i granicę wewnątrz kodowania UTF-8;
- zwrócić fragment wejścia z zachowaniem jego zależności od właściciela;

## Model — widok bez przejęcia bufora


Slice jest pożyczonym, ciągłym widokiem na sekwencję. `&[T]` zawiera wskaźnik
do pierwszego elementu oraz długość; nie posiada danych. Dzięki temu jedna
funkcja może przyjąć tablicę, `Vec<T>` lub część obu.

~~~rust
fn srednia(dane: &[f64]) -> Option<f64> {
    if dane.is_empty() {
        None
    } else {
        Some(dane.iter().sum::<f64>() / dane.len() as f64)
    }
}

fn main() {
    let tablica = [2.0, 4.0, 8.0];
    assert_eq!(srednia(&tablica[..2]), Some(3.0));
    assert_eq!(srednia(&Vec::<f64>::new()), None);
}
~~~

Mutowalny slice `&mut [T]` pozwala zmieniać elementy, lecz nie długość
sekwencji:

~~~rust
fn wyzeruj(dane: &mut [i32]) {
    dane.fill(0);
}

fn main() {
    let mut dane = [1, 2, 3, 4];
    wyzeruj(&mut dane[1..3]);
    assert_eq!(dane, [1, 0, 0, 4]);
}
~~~

Indeksowanie poza zakresem powoduje panic. Metoda `get` zwraca `Option` i
pozwala obsłużyć brak elementu.

## `String` i `str`

`String` posiada rozszerzalny bufor UTF-8. `str` jest typem niesized
reprezentującym poprawne bajty UTF-8; spotyka się go prawie zawsze przez
`&str`. Literał tekstowy ma typ `&'static str`.

~~~rust
fn powitanie(imie: &str) -> String {
    format!("Cześć, {imie}!")
}

fn main() {
    let posiadany = String::from("Ada");
    assert_eq!(powitanie(&posiadany), "Cześć, Ada!");
    assert_eq!(powitanie("Ferris"), "Cześć, Ferris!");
}
~~~

## Granice UTF-8

Zakres na `str` jest zakresem bajtów i musi wypaść na granicach kodowania
znaków. Dlatego `tekst[0]` nie jest dostępne: „znak” może oznaczać bajt,
Unicode scalar value albo grafem widoczny dla człowieka.

~~~rust
fn main() {
    let tekst = "żółw";
    assert_eq!(tekst.len(), 7); // bajty UTF-8: 2 + 2 + 2 + 1
    let znaki: Vec<char> = tekst.chars().collect();
    assert_eq!(znaki, ['ż', 'ó', 'ł', 'w']);
    assert_eq!(&tekst[0..2], "ż");
}
~~~

Rozcinaj tekst przez `char_indices`, `split` lub parser domenowy. Segmentacja
grafemów wymaga biblioteki **third-party**, np. `unicode-segmentation`.

## Wzorce na slices

~~~rust
fn opis(dane: &[i32]) -> &'static str {
    match dane {
        [] => "pusto",
        [_] => "jeden",
        [pierwszy, .., ostatni] if pierwszy == ostatni => "symetryczne końce",
        _ => "wiele",
    }
}

fn main() {
    assert_eq!(opis(&[1, 2, 1]), "symetryczne końce");
}
~~~

## Reguły — co gwarantuje widok

Sam slice `[T]` jest typem o rozmiarze znanym dopiero w czasie wykonania; codziennym uchwytem jest `&[T]` lub `&mut [T]`. Liczba elementów jest przechowywana w metadanych referencji i nie musi być stałą kompilacyjną. Wskazywany obszar musi być ciągły. Dwa fragmenty `VecDeque` nie stają się jednym slice tylko dlatego, że logicznie tworzą kolejkę.

Pożyczony widok nie potrafi wydłużyć sekwencji. `&mut [T]` może zastąpić element, zamienić kolejność lub wypełnić pamięć, ale nie może wykonać `push`. To ograniczenie daje bardziej ogólny interfejs: funkcja działa tak samo dla fragmentu tablicy, wektora i innego ciągłego bufora. `&Vec<T>` żądałoby dodatkowo określonego właściciela, choć implementacja go nie potrzebuje.

`get` dla elementu i `get` dla zakresu sprawdzają granice. Pusty zakres w dopuszczalnym miejscu daje pusty slice, a nie brak wyniku. Dla tekstu dochodzi dodatkowa walidacja granic UTF-8. To właśnie odróżnia `None` od `Some("")`: pierwsze oznacza niepoprawny zakres, drugie poprawny fragment o zerowej długości.

~~~rust
fn po_dwukropku(tekst: &str) -> Option<&str> {
    let (_, reszta) = tekst.split_once(':')?;
    Some(reszta.trim())
}
fn main() {
    let wejscie = String::from("nazwa: żółw");
    assert_eq!(po_dwukropku(&wejscie), Some("żółw"));
    assert_eq!(po_dwukropku("nazwa:"), Some(""));
    assert_eq!(po_dwukropku("bez separatora"), None);
}
~~~

Wynik jest widokiem na wejście, nie nową alokacją. `split_once` pracuje na separatorze tekstowym i nie wymaga ręcznego wyznaczania granicy bajtowej, a `trim` zwraca kolejny podwidok. Zniszczenie albo mutacja właściciela musi poczekać do ostatniego użycia wyniku. Jeśli parser ma przechować wynik niezależnie, jawnie zbuduj `String` na tej granicy.

Operacje `windows(n)` dają nakładające się widoki tylko do odczytu, a `chunks_mut(n)` rozłączne fragmenty do mutacji. Wielkość zero dla tych metod może panikować, dlatego nie przekazuj niezwalidowanego rozmiaru pakietu z sieci. Ostatni chunk może być krótszy; użyj `chunks_exact` i obsłuż `remainder`, gdy format wymaga pełnych rekordów.

## Diagnostyka kompilatora

Slice nie posiada operacji zmiany długości. Ten błąd to brak metody, a nie brak `mut` na bindingu: nawet mutowalny widok nie ma uprawnienia do realokacji bufora.

~~~compile_fail
fn dopisz(dane: &mut [u8]) {
    dane.push(0);
}
fn main() {}
~~~

`tekst[0]` również nie jest dostępne: indeksowanie tekstu liczbą nie określa, czy chodzi o bajt, scalar value czy grafem. `&tekst[..1]` może się skompilować, ale panikować dla `ż`; to błąd wykonania, a nie `compile_fail`. Do nieufnego zakresu użyj `get`, a do kolejnych scalar values — `chars` lub `char_indices`.

## Praktyka produkcyjna

Oddziel maksymalny rozmiar bufora od długości aktualnych danych. Funkcja przyjmująca `&mut [u8]` jako bufor odczytu może zapisać tylko prefiks; dalsze użycie całego widoku bez uwzględnienia liczby zapisanych bajtów jest błędem protokołu mimo poprawnej pamięci. W parserze przechowuj offsety jako zakresy bajtów i waliduj je przed ponownym użyciem.

Mały widok może utrzymywać pożyczkę bardzo dużego właściciela. W krótkiej analizie jest to zaletą, lecz w długo żyjącej kolejce drobnych rekordów kopiowanie potrzebnego fragmentu może zwolnić megabajtowy bufor wcześniej. Dobór widoku jest decyzją o czasie życia pamięci, a nie automatycznym zakazem alokacji.

## Sprawdź, czy rozumiesz

1. Czym różnią się `None` i `Some(&[][..])` przy wyborze zakresu?
2. Dlaczego `&mut [T]` nie ma `push`?
3. Kiedy skopiowanie krótkiego fragmentu zmniejszy zużycie pamięci całej aplikacji?

## Ćwiczenia

- `A13-1` — podstawowe: napisz funkcję zwracającą pierwszy element slice jako `Option<&T>` i sprawdź pustą tablicę [Rozwiązanie](../rozwiazania/03_ownership_i_pamiec/04_slices_i_str.md#a13-1).
- `A13-2` — praktyczne: podziel tekst `klucz=wartość` na dwa pożyczone fragmenty bez alokacji i bez indeksowania bajtów [Rozwiązanie](../rozwiazania/03_ownership_i_pamiec/04_slices_i_str.md#a13-2).
- `A13-3` — pogłębione: zdekoduj slice bajtów jako dwubajtowe liczby big-endian; odrzuć nieparzystą długość [Rozwiązanie](../rozwiazania/03_ownership_i_pamiec/04_slices_i_str.md#a13-3).

## Źródła i zakres stabilności

Kontrakty zakresów i chunków: [slice](https://doc.rust-lang.org/std/primitive.slice.html). Wymagania UTF-8: [str::get](https://doc.rust-lang.org/std/primitive.str.html#method.get).

## Powiązane tematy

- [Referencje i borrowing](03_referencje_i_borrowing.md)
- [`String`, `str` i Unicode](../06_kolekcje_iteratory_i_closures/02_string_str_i_unicode.md)
- [DST i trait objects](../05_generics_traits_i_system_typow/03_konwersje_dst_i_trait_objects.md)
