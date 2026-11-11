[← Spis treści](../README.md)
<!-- status: expanded -->

# Ownership, move i `Copy`

> Przykłady: **stable**, Rust 1.90.0, Edition 2024. Źródła sprawdzono 11 listopada 2026 r.

## Cele

Po tym rozdziale potrafisz:

- prześledzić właściciela bufora po przypisaniu, wywołaniu i zwrocie funkcji;
- wybrać pożyczkę, przeniesienie albo klonowanie na podstawie intencji API;
- odzyskać pole przez `take` lub `replace` bez naruszenia kompletności właściciela;

## Model — uprawnienie do użycia i obowiązek sprzątania


Każda wartość ma w danej chwili właściciela. Przypisanie lub przekazanie przez
wartość domyślnie przenosi (move) własność. Gdy właściciel wychodzi z zakresu,
wartość zostaje zniszczona.

## Przeniesienie

~~~rust
fn dlugosc(tekst: String) -> (String, usize) {
    let n = tekst.len();
    (tekst, n)
}

fn main() {
    let a = String::from("krab");
    let (a, n) = dlugosc(a);
    assert_eq!(n, 4);
    assert_eq!(a, "krab");
}
~~~

Przekazanie `a` do funkcji przeniosło wartość. Funkcja zwraca ją, aby
wywołujący ponownie przejął własność. W praktyce sam odczyt długości powinien
użyć referencji; przykład pokazuje mechanikę.

Po move stary binding nie może być użyty:

~~~compile_fail
fn main() {
    let pierwszy = String::from("dane");
    let drugi = pierwszy;
    println!("{pierwszy} i {drugi}");
}
~~~

Dzięki unieważnieniu `pierwszy` tylko jeden `String` zwolni wspólny bufor.

## `Clone` i `Copy`

`Clone::clone` wykonuje jawną logiczną kopię, która może alokować. `Copy` jest
markerem dla typów kopiowanych bitowo i bez destruktora, np. większości typów
skalarnych.

~~~rust
#[derive(Clone, Copy, Debug, PartialEq)]
struct Punkt {
    x: i32,
    y: i32,
}

fn main() {
    let p1 = Punkt { x: 2, y: 3 };
    let p2 = p1;
    assert_eq!(p1, p2);

    let s1 = String::from("x");
    let s2 = s1.clone();
    assert_eq!(s1, s2);
}
~~~

Typ implementujący `Drop` nie może implementować `Copy`. Nie dodawaj `Copy`
do typu tylko po to, aby uciszyć błąd move — decyzja jest częścią semantyki
API.

## Częściowe przeniesienie

Można przenieść jedno pole, a kopiować lub pożyczać inne:

~~~rust
struct Osoba {
    imie: String,
    wiek: u8,
}

fn main() {
    let osoba = Osoba { imie: "Ada".into(), wiek: 37 };
    let imie = osoba.imie;
    assert_eq!(osoba.wiek, 37);
    assert_eq!(imie, "Ada");
}
~~~

Nie można już użyć `osoba` jako całości. Dla typu implementującego `Drop`
przenoszenie pojedynczych pól jest ograniczone, bo destruktor oczekuje pełnej
wartości.

## Sposoby przekazywania

- `T` — funkcja przejmuje własność;
- `&T` — tylko czyta przez pożyczkę;
- `&mut T` — może zmieniać przez wyłączną pożyczkę;
- zwrot `T` — przekazuje własność wywołującemu.

To sygnatura, a nie komentarz, opisuje kontrakt zasobu.

## Reguły — move nie oznacza głębokiego kopiowania

Przeniesienie jest zmianą uprawnień do wartości w modelu języka. Kompilator może fizycznie skopiować nagłówek `String`, przekazać rejestry albo usunąć całą operację. Nie kopiuje przez to automatycznie bajtów posiadanego tekstu. Z punktu widzenia programu stara nazwa traci prawo użycia przeniesionej wartości. Jest to sprawdzane także wtedy, gdy późniejsza operacja wygląda na zwykły odczyt długości.

`Copy` jest trwałą obietnicą API: każda kopia może być używana niezależnie bez wywołania jawnego `clone`. Usunięcie tego traitu z publicznego typu może zepsuć kod klientów. Dodanie go do bardzo dużej tablicy może zachęcić do kosztownych kopii mimo braku alokacji. Referencje współdzielone są `Copy`; referencje wyłączne `&mut T` nim nie są, bo skopiowanie prawa do wyłącznej mutacji naruszyłoby kontrakt.

Słowo `clone` oznacza operację zdefiniowaną przez dany typ. Dla `Vec<String>` klonowane są elementy i ich bufory, dla `Arc<T>` powstaje kolejny uchwyt do tego samego `T`. Jeżeli potrzebujesz niezależnego stanu biznesowego, samo `Arc::clone` go nie tworzy. Dokumentuj to zwłaszcza przy obiektach zawierających jednocześnie bufor i współdzielony cache.

## Pobranie pola z zachowaniem poprawnego stanu

Przeniesienie całego pola przez `&mut self` pozostawiłoby dziurę w obiekcie. `mem::take` zastępuje pole wartością `Default`, a `mem::replace` wskazaną wartością. Właściciel pozostaje kompletny również wtedy, gdy dalsze przetwarzanie kończy się błędem.

~~~rust
#[derive(Default)]
struct Bufor { oczekujace: Vec<String> }
impl Bufor {
    fn pobierz(&mut self) -> Vec<String> {
        std::mem::take(&mut self.oczekujace)
    }
}
fn main() {
    let mut bufor = Bufor { oczekujace: vec!["A".into(), "B".into()] };
    let paczka = bufor.pobierz();
    assert_eq!(paczka, ["A", "B"]);
    assert!(bufor.oczekujace.is_empty());
    bufor.oczekujace.push("C".into());
}
~~~

Nie ma tu klonowania elementów. Cena projektu polega na tym, że stary bufor i jego pojemność przechodzą do odbiorcy, a w obiekcie zostaje nowy pusty wektor. Jeśli ważne jest ponowne użycie alokacji, lepsza może być wymiana dwóch buforów. Dla pola `Option<T>` metoda `take` naturalnie reprezentuje chwilowy brak zasobu.

## Diagnostyka kompilatora

Podstawowy błąd move pokazano wyżej. Inna sytuacja to E0507: nie można wyjąć posiadanego `String` z pożyczonego obiektu, pozostawiając jego pole niezainicjalizowane.

~~~compile_fail
struct Rekord { nazwa: String }
fn zabierz(r: &mut Rekord) -> String {
    r.nazwa
}
fn main() {}
~~~

Jeżeli pole może po pobraniu być puste, użyj `mem::take(&mut r.nazwa)`. Jeżeli musi pozostać poprawna niepusta nazwa, użyj `replace` z nową poprawną wartością albo zmień kontrakt, by konsumował cały `Rekord`. Dodanie `clone` byłoby inną operacją: właściciel nadal zachowałby oryginał.

## Praktyka produkcyjna

Sygnatura powinna rozstrzygać, kto może ponowić operację po błędzie. Funkcja konsumująca żądanie i zwracająca tylko błąd może odebrać klientowi dane potrzebne do ponowienia. Niekiedy właściwy jest wynik `Result<Odpowiedz, (Blad, Zadanie)>`; innym razem pożyczka wystarczy, bo zasób nie musi być przechowywany.

Częściowe przenoszenie jest użyteczne przy rozkładaniu rekordów, ale utrudnia późniejsze logowanie całego obiektu. Zaloguj potrzebne metadane przed konsumpcją lub przenieś pola do nazwanych części. Nie dodawaj `Copy` do typu reprezentującego unikalny uchwyt ani nie stosuj `clone` jako automatycznej odpowiedzi na każdy komunikat kompilatora.

## Sprawdź, czy rozumiesz

1. Czy move `String` wymaga kopiowania wszystkich bajtów tekstu?
2. Dlaczego `&T` jest `Copy`, a `&mut T` nie?
3. Jaki stan musi pozostać w obiekcie po `mem::take`?

## Ćwiczenia

- `A11-1` — podstawowe: napisz funkcję konsumującą `String` i zwracającą go wraz z długością; wskaż właściciela na każdym etapie [Rozwiązanie](../rozwiazania/03_ownership_i_pamiec/02_ownership_move_i_copy.md#a11-1).
- `A11-2` — praktyczne: napisz `pobierz(&mut self) -> Option<String>` dla struktury przechowującej `Option<String>` [Rozwiązanie](../rozwiazania/03_ownership_i_pamiec/02_ownership_move_i_copy.md#a11-2).
- `A11-3` — pogłębione: zaprojektuj konsumujące parsowanie `String`, które przy błędzie oddaje oryginalne wejście bez klonowania [Rozwiązanie](../rozwiazania/03_ownership_i_pamiec/02_ownership_move_i_copy.md#a11-3).

## Źródła i zakres stabilności

Przeniesienia: [Book: ownership](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html). Kontrakt kopiowania: [std::marker::Copy](https://doc.rust-lang.org/std/marker/trait.Copy.html). Zamiana pola: [std::mem::take](https://doc.rust-lang.org/std/mem/fn.take.html).

## Powiązane tematy

- [Referencje i borrowing](03_referencje_i_borrowing.md)
- [Closures i rodzina `Fn`](../06_kolekcje_iteratory_i_closures/04_closures_i_fn_traits.md)
- [`Send` i `Sync`](../10_wspolbieznosc/04_send_sync_i_atomiki.md)
