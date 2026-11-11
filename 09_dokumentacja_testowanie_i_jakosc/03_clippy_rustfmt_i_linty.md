[← Spis treści](../README.md)
<!-- status: expanded -->

# Clippy, rustfmt i linty

## Cele

Po tym rozdziale potrafisz:

- rozróżnić formatowanie, analizę typów, lint i test zachowania;
- ustalić lokalną politykę ostrzeżeń zgodną z wersją narzędzi;


Automatyczne narzędzia redukują dyskusje o stylu i wykrywają klasy błędów,
ale nie zastępują testów ani przeglądu projektu.

## Podstawowa pętla

~~~text
cargo fmt --all -- --check
cargo check --all-targets --all-features
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all-features
cargo doc --no-deps
~~~

W bibliotece „all features” może nie być jedyną ważną konfiguracją; testuj też
`--no-default-features` i kombinacje targetów.

## Poziomy lintów

`allow`, `warn`, `deny` i `forbid` sterują reakcją. `forbid` nie może być
obniżone w module potomnym, dlatego używaj go ostrożnie.

~~~rust
#![warn(missing_debug_implementations)]
#![deny(unsafe_op_in_unsafe_fn)]

#[derive(Debug)]
pub struct Id(pub u64);

fn main() {
    let _ = Id(1);
}
~~~

Edition 2024 wymaga większej jawności operacji unsafe wewnątrz `unsafe fn`.
Lint `unsafe_op_in_unsafe_fn` pomaga oddzielić kontrakt funkcji od każdego
konkretnego bloku `unsafe`.

## Clippy

Clippy ma grupy `clippy::correctness`, `suspicious`, `style`, `complexity`,
`perf`, `pedantic`, `nursery` i `restriction`. Nie włączaj całej grupy
`restriction` bez selekcji: część lintów reprezentuje przeciwstawne style.

Wyłączenie lintu powinno być lokalne:

~~~rust
#[allow(clippy::too_many_arguments)] // format narzucony przez stabilne ABI
fn rekord(a: u8, b: u8, c: u8, d: u8, e: u8, f: u8, g: u8, h: u8) -> u32 {
    [a, b, c, d, e, f, g, h].into_iter().map(u32::from).sum()
}

fn main() {
    assert_eq!(rekord(1, 1, 1, 1, 1, 1, 1, 1), 8);
}
~~~

Nie stosuj mechanicznie każdej sugestii. Sprawdź semantykę, publiczne API,
MSRV i wydajność.

## rustfmt

`cargo fmt` formatuje kod według style edition. Ustawienia w
`rustfmt.toml` powinny być minimalne; część opcji jest nightly-only.
Formatowanie osobnej wersji narzędzia może zmienić diff, więc CI i zespół
powinny używać zgodnego toolchainu.

## Linty rustc i rustdoc

Ważne linty: `unused_must_use`, `unreachable_patterns`, `missing_docs`,
`rust_2024_compatibility` i linty rustdoc. Cap lints chroni użytkowników
przed tym, aby ostrzeżenia zależności stawały się ich błędami, ale własny CI
może być surowszy.

## CI

Rozdziel szybkie `check`/format/lint od wolnych testów wieloplatformowych.
Nie używaj tylko lokalnego cache jako dowodu poprawności. W macierzy
uwzględnij stable, MSRV i wymagane targety; nightly tylko dla świadomie
niestabilnych narzędzi.


## Model — każda kontrola odpowiada na inne pytanie

`rustfmt` sprawdza uzgodniony zapis, `cargo check` analizuje aktywną konfigurację, Clippy wyszukuje określone wzorce, a test wykonuje scenariusz. Żadne z tych narzędzi nie dowodzi automatycznie kompletności projektu. Formatowany program może być błędny, a brak ostrzeżeń nie oznacza braku deadlocku. Warto utrzymywać szybkie kontrole, ponieważ wykrywają tanio inne klasy problemów niż kosztowne testy środowiskowe.

Politykę lintów ustal względem odpowiedzialności. `deny` zamienia ostrzeżenie w błąd, ale można je lokalnie obniżyć. `forbid` blokuje takie obniżenie w potomkach i jest przydatne dla świadomie bezwzględnego zakazu. `expect` dokumentuje oczekiwane ostrzeżenie; gdy przyczyna znika, odpowiedni lint może zgłosić niespełnione oczekiwanie. Pomaga to usuwać wyjątki, które po refaktoryzacji straciły uzasadnienie.

~~~rust
#![warn(unused_must_use)]
#[must_use = "wynik zawiera informację, czy operacja została przyjęta"]
fn przyjmij(n: u32) -> bool { n > 0 }
fn main() {
    let przyjeto = przyjmij(3);
    assert!(przyjeto);
}
~~~

Atrybut dokumentuje kontrakt wyniku, lecz nie wymusza właściwej reakcji biznesowej. Wywołujący może świadomie napisać `let _ = przyjmij(3);`. Taki kod nie stanie się semantycznie poprawny tylko dlatego, że lint zamilkł. Tak samo lokalne `allow` wymaga powodu wyjaśniającego, dlaczego sugestia nie pasuje do konkretnej granicy.

Grupy Clippy różnią się przeznaczeniem. Cała grupa `restriction` nie jest prostym „najwyższym poziomem jakości”; obejmuje selektywne ograniczenia, które mogą nie pasować do danego projektu. Sugestia poprawiająca styl może zmienić publiczne bounds, alokacje lub wymaganą wersję kompilatora. Przejrzyj poprawkę i uruchom adekwatne testy zamiast bezwarunkowo akceptować automatyczny fix.

Nowa wersja Clippy może dodawać ostrzeżenia do kodu, który wcześniej przechodził `-D warnings`. Dlatego powtarzalny CI powinien wskazywać wersję narzędzia, a aktualizacja toolchainu mieć własny przegląd. Globalne `-D warnings` u konsumentów biblioteki ma inny efekt niż kontrola twojego workspace’a; Rust stosuje także mechanizmy ograniczania lintów zależności.

Edition języka i style edition rustfmt są powiązanymi, ale odrębnymi ustawieniami. Zmiana formatowania może dać duży diff bez zmiany zachowania. Oddziel go od poprawki semantycznej, żeby recenzent mógł zobaczyć realny kontrakt. Nie stosuj formatowania do generowanego kodu, jeśli generator i plik wynikowy będą stale walczyć o zapis; wybierz jedno źródło prawdy.

## Diagnostyka kompilatora

Komunikat Clippy zawiera nazwę lintu, która pozwala ocenić zakres reguły i warunki wyjątku. Błąd `unsafe_op_in_unsafe_fn` wskazuje operację wymagającą osobnego bloku `unsafe`; sama sygnatura funkcji nie uzasadnia każdego dostępu. W Edition 2024 domyślny poziom tego lintu jest ostrzeżeniem, więc słowo „wymaga” w polityce projektu powinno wynikać z jawnego `deny`. Nie dopisuj pustych wyjątków tylko po to, aby przejść CI.

## Praktyka produkcyjna

Utrzymuj minimalny zestaw zasad, które zespół rozumie i egzekwuje. Wersjonuj konfigurację narzędzi, dokumentuj wyjątki obok kodu i sprawdzaj docelowe features. Dla kodu publicznego dodaj rustdoc i testy zachowania; dla kodu niskopoziomowego rozważ wyspecjalizowany audyt. Szybkie zadanie format/check/lint daje wczesną informację zwrotną, lecz przed wydaniem potrzebne są również linkowanie i odpowiednie testy. Cache może przyspieszyć kontrolę, ale nie powinien ukrywać niejawnych wejść budowania.

## Sprawdź, czy rozumiesz

- Czy brak lintów oznacza poprawną obsługę błędów?
- Dlaczego `restriction` wymaga wyboru reguł?
- Co może zmienić aktualizacja Clippy przy `-D warnings`?

## Ćwiczenia

- `B12-1` — podstawowe: Dodaj `#[must_use]` do funkcji i jawnie obsłuż wynik. [Rozwiązanie](../rozwiazania/09_dokumentacja_testowanie_i_jakosc/03_clippy_rustfmt_i_linty.md#b12-1).
- `B12-2` — praktyczne: Zapisz lokalny wyjątek lintu z uzasadnieniem stabilnego kontraktu. [Rozwiązanie](../rozwiazania/09_dokumentacja_testowanie_i_jakosc/03_clippy_rustfmt_i_linty.md#b12-2).
- `B12-3` — pogłębione: Rozpisz kolejność kontroli CI oraz klasę błędów, której każda kontrola nie wykrywa. [Rozwiązanie](../rozwiazania/09_dokumentacja_testowanie_i_jakosc/03_clippy_rustfmt_i_linty.md#b12-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [Rustc lint levels](https://doc.rust-lang.org/rustc/lints/levels.html)
- [Clippy: konfiguracja](https://doc.rust-lang.org/clippy/configuration.html)
- [Edition 2024 i unsafe_op_in_unsafe_fn](https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-op-in-unsafe-fn.html)

## Powiązane tematy

- [Testy jednostkowe](01_testy_jednostkowe_i_integracyjne.md)
- [Nightly i feature gates](../08_moduly_cargo_i_workspaces/05_nightly_unstable_i_feature_gates.md)
- [Projektowanie API i MSRV](../14_idiomy_wzorce_i_architektura/03_projektowanie_api_i_semver.md)
