[← Spis treści](../README.md)
<!-- status: expanded -->

# Makra proceduralne

## Cele

Po tym rozdziale potrafisz:

- rozróżnić trzy kontrakty transformacji tokenów;
- zaplanować diagnostykę i testy osobnego crate’a proc-macro;


Makro proceduralne jest funkcją wykonywaną przez kompilator, która przyjmuje
i zwraca `proc_macro::TokenStream`. Działa na tokenach, nie na wynikach
type checkingu.

## Trzy rodzaje

1. derive: `#[derive(MojTrait)]`;
2. atrybutowe: `#[moj_atrybut(...)]`;
3. function-like: `sql!(...)`.

Crate proceduralny ma osobny typ:

To fragment manifestu lub konfiguracji; wymaga właściwego projektu i nie jest samodzielnym doctestem.

~~~text
[lib]
proc-macro = true
~~~

Nie może normalnie eksportować dowolnego runtime API. Typowy projekt ma
osobny crate makra i osobny crate biblioteki używanej przez wygenerowany kod.

## Minimalne sygnatury

To szkic pliku lib crate’a proceduralnego:

~~~text
use proc_macro::TokenStream;

#[proc_macro_derive(MojTrait, attributes(moj_trait))]
pub fn derive_moj_trait(input: TokenStream) -> TokenStream {
    // parse, validate, generate
}

#[proc_macro_attribute]
pub fn trace(args: TokenStream, item: TokenStream) -> TokenStream {
    // zachowaj item i wygeneruj otoczkę
}

#[proc_macro]
pub fn zapytanie(input: TokenStream) -> TokenStream {
    // własna składnia
}
~~~

## Parse, validate, generate

Popularne crate’y **third-party** `syn` i `quote` parsują składnię oraz
generują tokeny. `proc-macro2` ułatwia testowanie poza kontekstem kompilatora.
Nie są częścią standard library.

Walidacja powinna:

- odrzucać unsupported input z precyzyjnym span;
- łączyć niezależne błędy, aby użytkownik poprawił je naraz;
- zachować generics, lifetimes i where clauses;
- nie panikować na błędnym kodzie użytkownika;
- generować absolutne lub konfigurowalne ścieżki do runtime crate’a.

## Spans i higiena

Span wiąże token z miejscem źródłowym i wpływa na diagnostykę oraz rozwiązywanie
nazw. `Span::call_site` nie jest uniwersalnym wyborem. Wygenerowane nazwy
pomocnicze powinny minimalizować kolizje, a publiczne elementy mieć stabilny,
udokumentowany kontrakt.

## Testowanie

- zwykłe testy parsera i generatora tokenów;
- testy integracyjne używające makra;
- testy kompilacji poprawnych i błędnych przypadków, często przez crate
  **third-party** `trybuild`;
- snapshoty tylko jako pomoc, nie substytut asercji semantycznych.

Testuj puste generics, where clauses, raw identifiers, różne visibilities,
atrybuty użytkownika i błędne wejście.

## Koszt i bezpieczeństwo

Makro wykonuje kod podczas kompilacji z uprawnieniami procesu budowania.
Jest częścią łańcucha dostaw. Złożone makra zwiększają czas kompilacji, a ich
wygenerowane API podlega SemVer jak kod ręczny.


## Model — transformacja składni bez wiedzy o typach

Derive dodaje elementy obok oryginalnego itemu, zwykle implementację traitu. Makro atrybutowe zastępuje dekorowany item swoim wynikiem i musi jawnie zachować go, jeśli tego wymaga kontrakt. Function-like zastępuje wywołanie w dozwolonym kontekście. Pomylenie tych modeli prowadzi do znikających struktur albo powielonych definicji. Wszystkie warianty operują na tokenach; nie otrzymują odpowiedzi na pytanie, jakie traits implementuje pole po inferencji.

Najprostsze działające makro function-like poniżej nie wymaga `syn` ani `quote`. To pełny plik crate’a z `[lib] proc-macro = true`, a nie samodzielny doctest: musi zostać skompilowany jako osobny pakiet i wywołany z konsumenta.

~~~text
use proc_macro::TokenStream;
#[proc_macro]
pub fn odpowiedz(input: TokenStream) -> TokenStream {
    if !input.is_empty() {
        return "compile_error!(\"odpowiedz! nie przyjmuje argumentów\")".parse().unwrap();
    }
    "42_u32".parse().unwrap()
}
~~~

Parsowane teksty są stałymi autora, nie interpolowanym kodem użytkownika. Dlatego ryzyko błędnego escaping jest tu ograniczone i `unwrap` opisuje wewnętrzne założenie. Dla danych wejściowych nie buduj generatora przez konkatenację dowolnego tekstu. Używaj tokenów i literałów zachowujących strukturę oraz spans.

Oto zwykły kod odpowiadający poprawnej ekspansji. Jest niezależnym testem zachowania wygenerowanego wyrażenia, nie testem wykonania samego proc macro.

~~~rust
fn main() {
    let wynik = 42_u32;
    assert_eq!(wynik, 42);
}
~~~

Właściwy test makra musi wywołać je z innego crate’a, także dla niepoprawnego wejścia. Minimalne makro `odpowiedz` zbudowano dodatkowo jako osobny projekt: poprawne wywołanie i alias zależności zadziałały, a argument został odrzucony oczekiwanym komunikatem. Pełny układ pakietów jest w rozwiązaniu drugiego ćwiczenia. Proc macro nie może być użyte jak zwykła lokalna funkcja generatora w tym samym crate. Rozdzielenie parsera i generatora do modułów testowanych na `proc_macro2` pomaga, lecz nie eliminuje potrzeby testu integracji z rustc.

Spans mają dwie role: pochodzenie dla diagnostyki oraz kontekst rozwiązywania nazw. Proceduralne makra są zasadniczo unhygienic; generowany kod trzeba projektować tak, jakby został wstawiony obok kodu użytkownika. Pełne ścieżki ograniczają zależność od importów. Unikalne helpery i konfigurowalna ścieżka runtime’u ograniczają kolizje, ale nie są automatycznym dowodem braku konfliktów.

Walidator wejścia powinien oddzielać błąd użytkownika od błędu implementacji. Nieobsługiwany enum, nieznany atrybut i sprzeczne opcje powinny prowadzić do precyzyjnego komunikatu, a nie panic. Złożone makro może agregować niezależne błędy, by użytkownik nie uruchamiał kompilatora wielokrotnie dla każdego pola.

## Diagnostyka kompilatora

`procedural macro panicked` wskazuje awarię implementacji makra lub niewłaściwe użycie panic do walidacji. „Cannot use a procedural macro from the same crate” wymaga osobnego konsumenta. Konflikt generowanej nazwy albo brak runtime crate’a często pojawia się dopiero w obcym projekcie. Nie uznawaj poprawnego snapshotu tokenów za dowód poprawnych bounds i widoczności; to sprawdza kompilacja ekspansji.

## Praktyka produkcyjna

Ogranicz zależności parsera do potrzebnych features, bo są kompilowane na hoście każdego użytkownika. Nie wykonuj sieci i nie czytaj przypadkowych plików podczas ekspansji. Makro ma uprawnienia procesu budowania, więc należy do powierzchni łańcucha dostaw. Testuj zgodność narzędzi i MSRV oraz publiczne API generowanego kodu. Jeśli wymaganie daje się wyrazić derive standardowym lub prostą funkcją, oszczędzasz konsumentom czas kompilacji i dodatkową warstwę diagnostyki.

## Sprawdź, czy rozumiesz

- Czym wynik derive różni się od wyniku makra atrybutowego?
- Dlaczego makro nie może wybrać implementacji po rozstrzygniętym typie pola?
- Którego błędu nie zobaczy snapshot samych tokenów?

## Ćwiczenia

- `B26-1` — podstawowe: Wskaż rodzaj makra dla derive, otoczki funkcji i DSL zapytania. [Rozwiązanie](../rozwiazania/12_makra/03_makra_proceduralne.md#b26-1).
- `B26-2` — praktyczne: Zaprojektuj pełne bezargumentowe makro zwracające `42_u32` i błąd dla argumentów. [Rozwiązanie](../rozwiazania/12_makra/03_makra_proceduralne.md#b26-2).
- `B26-3` — pogłębione: Rozpisz testy proc macro obejmujące osobnego konsumenta, błędne wejście oraz alias zależności. [Rozwiązanie](../rozwiazania/12_makra/03_makra_proceduralne.md#b26-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [Reference: procedural macros](https://doc.rust-lang.org/reference/procedural-macros.html)
- [proc_macro::TokenStream](https://doc.rust-lang.org/proc_macro/struct.TokenStream.html)

## Powiązane tematy

- [`macro_rules!`](01_macro_rules.md)
- [Zaawansowane makra proceduralne](../12_makra/04_zaawansowane_makra_proceduralne.md)
- [Build scripts](../08_moduly_cargo_i_workspaces/04_profile_build_scripts_i_publikowanie.md)
