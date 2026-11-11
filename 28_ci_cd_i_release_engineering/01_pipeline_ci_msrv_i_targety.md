[← Spis treści](../README.md)
<!-- status: expanded -->

# Pipeline CI, MSRV i macierz konfiguracji

> Przykłady `rust`: biblioteka standardowa, Edition 2024. API narzędzi i bibliotek zewnętrznych opisano na podstawie źródeł sprawdzonych 11 listopada 2026 r.; szkice `text` wymagają wskazanego środowiska.

## Cele

Po tym rozdziale potrafisz:

- zbudować krótką pętlę informacji zwrotnej;
- weryfikować MSRV niezależnie od najnowszego stable;
- rozróżnić pokrycie features, targetów i rodzajów testów;

## Model — pipeline sprawdza publiczne obietnice

Continuous integration (CI) powinno odpowiadać na pytania wynikające z kontraktu projektu: czy kod buduje się na deklarowanych platformach, czy API zachowuje zachowanie, czy przykłady dokumentacji są aktualne i czy minimalna wspierana wersja Rusta (MSRV) wystarcza. Jeden zielony job z najnowszym stable nie odpowiada na wszystkie te pytania. Liczba jobów sama w sobie nie jest miarą jakości.

Podziel kontrolę na szybkie sprawdzenia i droższe eksperymenty. Formatowanie i kompilacja zwykle dają szybszą informację niż wielominutowe testy integracyjne. Testy jednostkowe, integracyjne i dokumentacyjne mają inne punkty wejścia. `cargo test --all-targets` nie zastępuje jawnego joba doctestów. Zapisz, co dany job uruchamia i czego świadomie nie obejmuje.

## Przykładowa sekwencja poleceń

Poniższe polecenia są szkicem joba dla konkretnego workspace, który ma lockfile i dostępne komponenty. Trzeba ustalić features oraz uprawnienia środowiska; nie są to polecenia wykonywane automatycznie przez lekturę rozdziału.

~~~text
cargo fmt --all -- --check
cargo check --workspace --all-targets --locked
cargo clippy --workspace --all-targets --locked -- -D warnings
cargo test --workspace --all-targets --locked
cargo test --workspace --doc --locked
RUSTDOCFLAGS="-D warnings" cargo doc --workspace --no-deps --locked
~~~

`--locked` wymaga istniejącego, zgodnego lockfile i odmawia zmiany rozwiązania zależności. Nie jest tym samym co brak sieci: `--offline` ogranicza dostęp do sieci, a `--frozen` łączy obie własności. Tryb offline wymaga już dostępnych zależności. Żadna z tych flag nie ustala SDK ani systemowych bibliotek.

## Features to osobna oś

Features Cargo są w założeniu addytywne. Domyślna konfiguracja, brak domyślnych oraz wybrane kombinacje mogą kompilować inne moduły. `--all-features` włącza dużo kodu, ale może ukryć brak importu w wariancie minimalnym. Dla funkcji sprzętowych i konfliktujących adapterów definiuj wspierane kombinacje i jawnie odrzucaj inne, zamiast deklarować wszystkie jako równoważne.

Mały model pokazuje, że deklaracja wsparcia jest warunkiem wymagającym pokrycia. Przykład std nie odczytuje prawdziwej konfiguracji Cargo; ilustruje testowanie polityki.

~~~rust
#[derive(Clone, Copy)]
enum Target { Native, Wasm }
fn wspierane(target: Target, pliki: bool) -> bool {
    match target {
        Target::Native => true,
        Target::Wasm => !pliki,
    }
}
fn main() {
    assert!(wspierane(Target::Native, true));
    assert!(wspierane(Target::Wasm, false));
    assert!(!wspierane(Target::Wasm, true));
}
~~~

Do macierzy dodaj przypadek odmowy nieobsługiwanej konfiguracji, z jasnym komunikatem. Cicha pusta implementacja może przejść test budowania, a mimo to naruszyć obietnicę produktu.

## MSRV i toolchain to różne decyzje

`rust-version` w manifeście dokumentuje wymaganie kompilatora. Zweryfikuj je przez rzeczywiste uruchomienie zadeklarowanej wersji z docelowym grafem. Nowa wersja zależności może podnieść własne MSRV; polityka aktualizacji lockfile i resolvera wpływa na wynik. Osobno kontroluj najnowszy stable, żeby wcześnie zauważyć przyszłe ostrzeżenia i problemy kompatybilności.

Edition określa reguły interpretacji kodu, nie śledzi automatycznie najnowszego wydania kompilatora. Przypięcie toolchainu narzędziowego poprawia powtarzalność, lecz wymaga świadomych aktualizacji. Narzędzia nightly, jak część sanitizerów, trzymaj w osobnym jobie: ich awaria nie powinna zostać pomylona z niespełnieniem kontraktu stable biblioteki.

## Cache przyspiesza, ale nie jest dowodem

Klucz cache powinien uwzględniać toolchain, target, konfigurację i istotne zależności. Po zmianie flag wykonaj kontrolę bez podejrzanego cache, jeśli wyniki są niespójne. Nie przechowuj sekretów ani nie ufaj artefaktom z niezaufanego joba publikacyjnego. Wygenerowany raport nie może być jedynym źródłem prawdy, jeśli job zakończył się przed uruchomieniem testów.

## Diagnostyka kompilatora

Wynik joba ma rozróżniać brak komponentu, błąd kompilacji i porażkę asercji. Przy Clippy z `-D warnings` nowe ostrzeżenie narzędzia może zatrzymać pipeline; przypięcie wersji i plan aktualizacji ułatwiają kontrolę. Nie zmieniaj testu funkcjonalnego, żeby naprawić brak linkera w macierzy. Oznacz dokładnie etap i zachowaj log, wersję narzędzia oraz komendę.

## Praktyka produkcyjna

Najpierw zdefiniuj minimalną macierz pokrywającą kontrakt, potem rozszerzaj ją o udokumentowane ryzyka. Ciężkie kampanie fuzzingu i benchmarki mają osobne budżety. Nowe PR-y uruchamiaj z ograniczonymi uprawnieniami; token publikacyjny pojawia się wyłącznie w kontrolowanym etapie wydania. Raportuj także pominięte testy, bo zielony pipeline z nieuruchomioną integracją nie oznacza zgodności środowiska produkcyjnego.

## Sprawdź, czy rozumiesz

1. Dlaczego `--all-features` nie zastępuje testu minimalnego wariantu?
2. Co oznacza zielony `cargo check` bez działającego linkera?
3. Jak odróżnić MSRV od Edition?

## Ćwiczenia

- `D09-1` — podstawowe: Wyjaśnij różnicę między `--locked`, `--offline` i `--frozen`. [Rozwiązanie](../rozwiazania/28_ci_cd_i_release_engineering/01_pipeline_ci_msrv_i_targety.md#d09-1).
- `D09-2` — praktyczne: Ułóż trzy joby dla biblioteki z MSRV, domyślnym `std` i wariantem `no_std`. [Rozwiązanie](../rozwiazania/28_ci_cd_i_release_engineering/01_pipeline_ci_msrv_i_targety.md#d09-2).
- `D09-3` — pogłębione: Zaprojektuj wykrycie regresji ukrytej przez unifikację features workspace. [Rozwiązanie](../rozwiazania/28_ci_cd_i_release_engineering/01_pipeline_ci_msrv_i_targety.md#d09-3).

## Źródła i granice weryfikacji

Opcje budowania: [Cargo build](https://doc.rust-lang.org/cargo/commands/cargo-build.html). Rodzaje testów: [Cargo test](https://doc.rust-lang.org/cargo/commands/cargo-test.html). Polityka wersji: [Cargo rust-version](https://doc.rust-lang.org/cargo/reference/rust-version.html). Sekwencja CI jest autorskim punktem wyjścia, nie gotowym workflow konkretnego dostawcy.

## Powiązane tematy

- [Artefakty i rollback](02_wydania_artefakty_i_rollback.md)
- [Cargo i features](../08_moduly_cargo_i_workspaces/03_zaleznosci_features_i_cfg.md)
- [Targety](../24_wasm_i_wieloplatformowosc/02_przenosny_rdzen_i_testy_targetow.md)
