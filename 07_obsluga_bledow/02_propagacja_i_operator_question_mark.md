[← Spis treści](../README.md)
<!-- status: expanded -->

# Propagacja i operator `?`

## Cele

Po tym rozdziale potrafisz:

- wyjaśnić granicę wcześniejszego powrotu `?`;
- dodać kontekst bez utraty źródła i częściowych efektów;


Operator `?` kończy bieżącą funkcję wcześniej przy `Err` lub `None`, a przy
sukcesie rozpakowuje wartość. Zachowuje czytelny „happy path”.

## Propagacja `Result`

~~~rust
use std::num::ParseIntError;

fn podwoj(tekst: &str) -> Result<i32, ParseIntError> {
    let liczba = tekst.trim().parse::<i32>()?;
    Ok(liczba * 2)
}

fn main() {
    assert_eq!(podwoj("21"), Ok(42));
    assert!(podwoj("x").is_err());
}
~~~

Rozwinięcie mentalne to `match`: dla `Ok` kontynuuj, dla `Err` wykonaj
wczesny return. Dokładna semantyka używa traits `Try` i `FromResidual`;
na stabilnym Rust własne implementacje tego mechanizmu są ograniczone.

## Automatyczna konwersja błędu

`?` wywołuje `From::from`, jeżeli błąd funkcji docelowej ma zostać zmieniony
na błąd funkcji bieżącej:

~~~rust
use std::fmt;
use std::num::ParseIntError;

#[derive(Debug)]
struct Blad(ParseIntError);

impl From<ParseIntError> for Blad {
    fn from(e: ParseIntError) -> Self { Self(e) }
}

impl fmt::Display for Blad {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "niepoprawna liczba: {}", self.0)
    }
}

fn wczytaj(s: &str) -> Result<i32, Blad> {
    Ok(s.parse::<i32>()?)
}

fn main() {
    assert_eq!(wczytaj("42").unwrap(), 42);
}
~~~

Nie twórz zbyt szerokiej implementacji `From`, która usuwa ważną informację.

## `?` z `Option`

~~~rust
fn drugie_slowo(tekst: &str) -> Option<&str> {
    let mut slowa = tekst.split_whitespace();
    slowa.next()?;
    slowa.next()
}

fn main() {
    assert_eq!(drugie_slowo("a b c"), Some("b"));
    assert_eq!(drugie_slowo("a"), None);
}
~~~

Zwykła funkcja zwracająca `Result` nie może bezpośrednio użyć `?` na
`Option`; najpierw nadaj brakowi znaczenie przez `ok_or`.

## Granice

`?` działa w funkcji, closure lub bloku, którego typ powrotu jest zgodny z
residual. `main` może zwracać `Result<(), E>`, a blok `try` pozostaje
funkcjonalnością niestabilną — sprawdzaj aktualny Unstable Book.

## Kontekst błędu

Propagacja bez kontekstu może zostawić użytkownika z „No such file” bez nazwy
operacji. Biblioteka może wzbogacić własny enum, a aplikacja użyć crate’a
**third-party** `anyhow` i `Context`. Kontekst dodawaj przy przejściu między
warstwami abstrakcji, nie w każdym wierszu.


## Model — granica powrotu i efekty

`?` jest operatorem przepływu sterowania, a nie skrótem zmieniającym dowolny typ w dowolny inny. Dla `Result<T, E>` kontynuuje z `T` lub zwraca błąd pasujący do wyniku otaczającej funkcji. Konwersja błędu przez `From` nie konwertuje automatycznie sukcesu. Jeżeli parser zwraca `u16`, a funkcja oczekuje `u32`, sukces trzeba przekształcić osobno, na przykład przez `u32::from`.

Granica jest leksykalna. `?` wewnątrz closure przekazanego do `map` kończy to closure, a nie funkcję, w której zapisano iterator. Dlatego częstym wzorcem jest iterator wyników i `collect::<Result<Vec<_>, _>>()`. Zbieranie zatrzymuje się na pierwszym błędzie i niszczy już zebrane wartości. Nie cofa jednak wcześniejszych zapisów do plików, wysłanych komunikatów ani mutacji zewnętrznego stanu.

~~~rust
fn liczby(s: &str) -> Result<Vec<u16>, std::num::ParseIntError> {
    s.split(',').map(|element| element.trim().parse::<u16>()).collect()
}
fn main() {
    assert_eq!(liczby("1, 2,3").unwrap(), [1, 2, 3]);
    assert!(liczby("1,x,3").is_err());
}
~~~

Przykład nie tworzy `Vec<Result<...>>`, bo docelowy typ `collect` określa sposób obsługi błędów. Pierwszy błędny element kończy przetwarzanie; kolejnych parser już nie uruchamia. Jeśli interfejs importu ma zebrać wszystkie błędy, zastosuj jawny przebieg z numerem wiersza i oddzielnymi kolekcjami. „Wczesny powrót” jest decyzją o zachowaniu produktu.

Przy dodawaniu kontekstu potrzebnego tylko w jednym miejscu często lepsze jest `map_err` od globalnego `From`. Implementacja `From<io::Error>` nie wie, czy odczytywano konfigurację, czy zapisywano raport. Funkcja ma tę informację i może zapisać ścieżkę oraz przyczynę. Nie zastępuj przyczyny samym `format!(...)`, jeżeli kontrakt wymaga późniejszego sprawdzenia `ErrorKind` lub łańcucha `source`.

Wcześniejszy powrót uruchamia zwykłe niszczenie lokalnych wartości. Guard blokady zwalnia mutex, a plik zamyka uchwyt. RAII nie zapewnia wycofania całej operacji biznesowej. Transakcję projektuj oddzielnie: walidacja wszystkich danych przed mutacją, osobny bufor albo mechanizm transakcyjny zasobu. Operator `?` umieszczony między dwoma zapisami pozostawia pierwszy zapis wykonany.

## Diagnostyka kompilatora

Najczęstszy komunikat mówi, że `?` można użyć tylko w funkcji lub closure zwracającym zgodny typ. Jeśli `map` ma produkować liczby, closure nie może samowolnie zwrócić `Err`. Nie naprawiaj tego `unwrap`; zmień wynik closure na `Result` i świadomie wybierz `collect` albo agregację. Błąd o braku `From<Zrodlo>` oznacza brak wymaganej konwersji błędu. Dodaj ją tylko wtedy, gdy jest jednoznaczna; w przeciwnym razie użyj lokalnego `map_err`.

## Praktyka produkcyjna

W serwisie dodawaj kontekst przy zmianie odpowiedzialności, na przykład „wczytywanie konfiguracji”, a nie przy każdej instrukcji. Loguj na granicy obsługi żądania, by ten sam błąd nie trafił wielokrotnie do monitoringu. Zachowaj identyfikator operacji i klasę błędu, ale usuń sekrety. Ustal, czy pojedynczy błąd kończy partię, czy należy kontynuować. Dla importu danych raport wszystkich błędów może być użyteczniejszy, choć kosztuje pamięć i wymaga limitu liczby raportowanych usterek.

## Sprawdź, czy rozumiesz

- Co kończy `?` zapisany w closure iteratora?
- Które efekty pozostają po błędzie w połowie operacji?
- Kiedy `map_err` daje lepszy kontekst niż `From`?

## Ćwiczenia

- `B02-1` — podstawowe: Napisz parser pary `u16` rozdzielonej dwukropkiem; brak separatora ma być osobnym błędem. [Rozwiązanie](../rozwiazania/07_obsluga_bledow/02_propagacja_i_operator_question_mark.md#b02-1).
- `B02-2` — praktyczne: Zbierz listę tekstów w `Result<Vec<u32>, _>`, zatrzymując się na błędzie. [Rozwiązanie](../rozwiazania/07_obsluga_bledow/02_propagacja_i_operator_question_mark.md#b02-2).
- `B02-3` — pogłębione: Zaimplementuj import zbierający wszystkie indeksy błędnych elementów zamiast kończyć na pierwszym. [Rozwiązanie](../rozwiazania/07_obsluga_bledow/02_propagacja_i_operator_question_mark.md#b02-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [Operator propagacji błędu](https://doc.rust-lang.org/reference/expressions/operator-expr.html#the-try-propagation-expression)

## Powiązane tematy

- [`Option` i `Result`](01_option_i_result.md)
- [Własne błędy i API](04_wlasne_bledy_i_api.md)
- [Funkcje i wyrażenia](../02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md)
