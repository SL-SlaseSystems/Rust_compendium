[← Spis treści](../README.md)
<!-- status: expanded -->

# Testy dokumentacyjne i rustdoc

## Cele

Po tym rozdziale potrafisz:

- napisać wykonywalny przykład publicznego kontraktu;
- odróżnić sprawdzanie kodu, linków i błędnych wywołań;


Komentarz `///` dokumentuje następny element, `//!` — element zawierający.
`cargo doc --open` generuje HTML dla crate’a i zależności.

## Przykład jako test

~~~rust
/// Dodaje podatek w punktach bazowych.
///
/// # Examples
///
/// ```
/// let brutto = z_podatkiem(10_000, 2300);
/// assert_eq!(brutto, 12_300);
/// ```
///
/// # Panics
///
/// Może wywołać panic przy przepełnieniu u64.
pub fn z_podatkiem(netto: u64, punkty_bazowe: u64) -> u64 {
    netto + netto * punkty_bazowe / 10_000
}

fn main() {
    assert_eq!(z_podatkiem(100, 1000), 110);
}
~~~

Rustdoc ukrywa wiersze zaczynające się od `# ` w renderowaniu, ale dołącza je
do kompilacji. To pozwala skrócić setup:

~~~text
/// ```
/// # use moja_biblioteka::Klient;
/// # let klient = Klient::testowy();
/// assert!(klient.zdrowy());
/// ```
~~~

## Rodzaje bloków

- `rust` — kompiluje i uruchamia;
- `no_run` — kompiluje bez uruchamiania;
- `compile_fail` — sukces, gdy kompilacja zostanie odrzucona;
- `should_panic` — oczekuje panic;
- `ignore` — pomija; używaj oszczędnie;
- `text` — nie jest kodem Rust.

`compile_fail` jest dobry do dokumentowania gwarancji typów:

~~~compile_fail
fn main() {
    let s = String::from("move");
    let t = s;
    println!("{s} {t}");
}
~~~

## Linki wewnętrzne

Intra-doc links, np. `[Vec]` lub `[modul::Typ::metoda]`, są sprawdzane przez
rustdoc. Lint `rustdoc::broken_intra_doc_links` warto ustawić na deny.
Dokumentuj re-exportowaną ścieżkę, którą ma widzieć użytkownik.

## Typowe sekcje

- `# Examples`;
- `# Errors` dla `Result`;
- `# Panics`;
- `# Safety` dla publicznego `unsafe fn`;
- `# Cancellation safety` dla operacji async, jeśli ma znaczenie.

Opis „co” bez „dlaczego” jest niewystarczający. Dokumentacja publiczna
powinna wyjaśniać ownership parametrów, koszt, side effects, porządek i
platformowe różnice.

## Prywatne elementy i cfg

`cargo doc --document-private-items` pomaga przeglądać architekturę. Elementy
wyłączone przez `cfg` nie pojawią się bez właściwej konfiguracji. Docs.rs
często buduje zestaw features określony w metadanych, więc sprawdzaj dokumenty
lokalnie w tej samej kombinacji.


## Model — dokumentacja ma konkretnego odbiorcę

Doctest pokazuje minimalny poprawny sposób użycia i sprawdza go mechanicznie. Nie zastępuje opisu własności, kosztu i ograniczeń. Przykład wywołujący funkcję bez asercji może przejść, choć funkcja zwraca błędny wynik. Przykład z ukrytym ważnym etapem inicjalizacji może być poprawny technicznie, lecz niezrozumiały dla czytelnika. Ukrywaj boilerplate, a nie zobowiązania konsumenta.

Komentarz zagnieżdżony wewnątrz bloku Rust nie oznacza, że narzędzie weryfikujące Markdown przetestuje rekurencyjnie wszystkie opisane w nim doctesty. Rzeczywisty test dokumentacji pakietu wykonuje `cargo test --doc`. W tym kompendium samodzielne bloki `rust` sprawdza dodatkowo rustdoc uruchamiany na pliku Markdown. To dwie różne warstwy kontroli.

~~~rust
/// Zwraca pierwszy bajt albo brak dla pustego wejścia.
/// Nie alokuje i nie przejmuje własności bufora.
fn pierwszy(dane: &[u8]) -> Option<u8> { dane.first().copied() }
fn main() {
    assert_eq!(pierwszy(b"Rust"), Some(b'R'));
    assert_eq!(pierwszy(b""), None);
}
~~~

Ten przykład zawiera sukces i istotną granicę wejścia. Dokumentacja nazywa koszt i własność bez opisywania implementacji pętli. Przy funkcji zapisującej plik potrzebne byłyby jeszcze efekty uboczne, błędy i gwarancje trwałości. Przy `unsafe fn` sekcja `# Safety` musi mówić o warunkach wywołującego, a nie tylko stwierdzać, że funkcja jest niebezpieczna.

`compile_fail` potwierdza, że kod nie kompiluje się w danej konfiguracji. Może jednak przejść z niewłaściwego powodu, na przykład brakującego importu zamiast oczekiwanego złamania lifetimes. Minimalizuj przykład, utrzymuj poprawne otoczenie i wyjaśnij konkretną naruszoną regułę. Jeżeli potrzebujesz stabilnie kontrolować diagnostykę makra, osobne testy kompilacyjne mogą być lepszym narzędziem.

`no_run` sprawdza kompilację, ale nie sprawdza zachowania, wymaganych plików i odpowiedzi serwera. `ignore` pomija jeszcze więcej i łatwo zamienia przykład w martwy tekst. Blok `text` jest uczciwy dla niepełnego szkicu zależnego od crate’a zewnętrznego, lecz powinien mieć opis brakującego kontekstu. Nie oznaczaj szkicu jako przetestowanego tylko dlatego, że przypomina poprawny kod.

Linki do elementów API rozwiązuje rustdoc w kontekście dokumentowanego elementu. Lokalny link Markdown do innego rozdziału jest inną kategorią niż intra-doc link do typu. Testy dokumentacji uruchamiaj z wymaganymi features; dokumentacja maksymalnej konfiguracji nie pokazuje, które elementy są dostępne w konfiguracji domyślnej.

## Diagnostyka kompilatora

`rustdoc::broken_intra_doc_links` może oznaczać nieznaną nazwę, zły kontekst albo element usunięty przez `cfg`. Popraw odsyłacz lub konfigurację, zamiast wyłączać sprawdzanie całego crate’a. Jeśli doctest nie widzi funkcji, sprawdź jej publiczną ścieżkę i import crate’a. Błąd użycia wartości po przeniesieniu w celowym `compile_fail` powinien wynikać z przeniesienia, a nie z niezdefiniowanej pomocniczej funkcji. Uruchom negatywny przykład oddzielnie, jeśli przyczyna odrzucenia jest niejasna.

## Praktyka produkcyjna

W CI rozdziel generowanie HTML od testowania przykładów: sukces jednego nie oznacza sukcesu drugiego. Sprawdzaj ostrzeżenia linków i minimalny zestaw features. Dokumentuj wersję i pochodzenie API zewnętrznego. Przy przykładach sieciowych preferuj samowystarczalny model parsera albo kontrolowane środowisko testowe, żeby dostępność zewnętrznego serwera nie decydowała o wydaniu biblioteki. Aktualizując publiczną ścieżkę, popraw także przykłady, re-exporty oraz linki z przewodnika użytkownika.

## Sprawdź, czy rozumiesz

- Jak `compile_fail` może przejść z niewłaściwego powodu?
- Czego nie weryfikuje `no_run`?
- Dlaczego poprawnie wygenerowany HTML nie dowodzi działania przykładów?

## Ćwiczenia

- `B11-1` — podstawowe: Napisz samodzielny przykład `Option` z asercją sukcesu i pustego wejścia. [Rozwiązanie](../rozwiazania/09_dokumentacja_testowanie_i_jakosc/02_testy_dokumentacyjne_i_rustdoc.md#b11-1).
- `B11-2` — praktyczne: Pokaż odrzucone użycie po przeniesieniu z minimalnym poprawnym otoczeniem. [Rozwiązanie](../rozwiazania/09_dokumentacja_testowanie_i_jakosc/02_testy_dokumentacyjne_i_rustdoc.md#b11-2).
- `B11-3` — pogłębione: Zaprojektuj sekcje dokumentacji dla funkcji zapisującej konfigurację oraz jej testów. [Rozwiązanie](../rozwiazania/09_dokumentacja_testowanie_i_jakosc/02_testy_dokumentacyjne_i_rustdoc.md#b11-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [Rustdoc: documentation tests](https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html)
- [Rustdoc: intra-doc links](https://doc.rust-lang.org/rustdoc/write-documentation/linking-to-items-by-name.html)

## Powiązane tematy

- [Testy jednostkowe i integracyjne](01_testy_jednostkowe_i_integracyjne.md)
- [Komentarze i atrybuty](../02_podstawy_jezyka/05_operatory_komentarze_i_atrybuty.md)
- [`unsafe` i soundness](../21_unsafe_soundness_i_model_pamieci/01_unsafe_i_soundness.md)
