[← Spis treści](../README.md)
<!-- status: expanded -->

# Zależności, features i `cfg`

## Cele

Po tym rozdziale potrafisz:

- przewidzieć sumowanie features i ograniczenia ich wyłączania;
- rozróżnić wybór kodu przez `cfg` od warunku wykonywanego w programie;


Cargo rozwiązuje wersje zależności zgodnie z manifestem, lockfile i SemVer.
Zależności mogą pochodzić z registry, Git lub ścieżki lokalnej.

## Rodzaje zależności

To fragment manifestu lub konfiguracji; wymaga właściwego projektu i nie jest samodzielnym doctestem.

~~~text
[dependencies]
serde = { version = "1", features = ["derive"] }

[dev-dependencies]
proptest = "1"

[build-dependencies]
cc = "1"
~~~

`dev-dependencies` nie trafiają do normalnego grafu konsumenta biblioteki.
`build-dependencies` kompilują się dla hosta, niekoniecznie targetu.
Crate’y w przykładzie są **third-party**.

## Wymagania wersji

`"1.2.3"` domyślnie dopuszcza kompatybilne aktualizacje w ramach SemVer.
`=1.2.3` przypina dokładnie i powinno mieć konkretny powód. `Cargo.lock`
zapisuje rozwiązanie, a `cargo update -p nazwa` aktualizuje wybraną część.

`cargo tree -d` ujawnia zduplikowane wersje, a `cargo tree -e features`
pokazuje propagację features.

## Features są addytywne

To fragment manifestu lub konfiguracji; wymaga właściwego projektu i nie jest samodzielnym doctestem.

~~~text
[features]
default = ["std"]
std = []
serde = ["dep:serde"]

[dependencies]
serde = { version = "1", optional = true }
~~~

Włączone features tej samej wersji crate’a są unifikowane w grafie. Feature
nie powinien usuwać API ani przełączać dwóch wzajemnie wykluczających backendów
bez dodatkowej walidacji. Sprawdzaj kombinacje `--no-default-features`,
`--all-features` i istotne podzbiory.

## Kompilacja warunkowa

~~~rust
#[cfg(target_os = "linux")]
fn platforma() -> &'static str { "linux" }

#[cfg(not(target_os = "linux"))]
fn platforma() -> &'static str { "inna" }

fn main() {
    assert!(!platforma().is_empty());
}
~~~

`cfg!` zwraca bool, ale obie gałęzie otaczającego `if` nadal muszą być
poprawne typowo. `#[cfg(...)]` usuwa element przed dalszą analizą. Do
łączenia służą `all`, `any` i `not`.

~~~rust
#[cfg_attr(test, derive(PartialEq, Debug))]
struct Rekord(u32);

fn main() {
    let _ = Rekord(1);
}
~~~

Własne nazwy `cfg` ustawiane przez build script powinny być zgłoszone do
`check-cfg`, aby rustc wykrywał literówki.

## Bezpieczeństwo łańcucha dostaw

Minimalizuj zależności, przeglądaj licencje i advisory, aktualizuj lockfile
kontrolowanie. Narzędzia takie jak `cargo-audit` i `cargo-deny` są
**third-party**, lecz często używane w CI.


## Model — feature zwiększa zestaw możliwości

Features opisują możliwości pakietu, a nie prywatne przełączniki jednego klienta. Dwa zależne pakiety mogą żądać innych features tej samej wersji biblioteki; Cargo zwykle buduje sumę wymagań w danym kontekście unifikacji. `default-features = false` na jednej krawędzi nie odbiera feature włączonego przez drugą. Dlatego „secure” i „insecure” nie powinny przełączać przeciwstawnych zachowań istniejącej funkcji przez tę samą powierzchnię API.

Resolver `2` i `3` ograniczają pewne rodzaje unifikacji, między innymi między zależnościami budowania/proc-macro a zwykłymi oraz dla nieaktywnych targetów. Nie oznacza to, że każdy użytkownik zależności otrzymuje całkiem niezależny zestaw features. Gdy wynik zaskakuje, odczytaj graf przez `cargo tree -e features`, zamiast zakładać, że lokalny manifest jest jedynym źródłem konfiguracji.

`cfg` usuwa fragmenty składni przed sprawdzeniem typów aktywnego programu. `cfg!` daje wyrażenie boolowskie, więc obie gałęzie zwykłego `if` muszą przejść analizę typów i nazw. To ma znaczenie przy importach specyficznych dla systemu. Użycie `cfg!(unix)` nie pozwala bezwarunkowo odwołać się do API Unix na Windows.

~~~rust
#[cfg(target_pointer_width = "64")]
fn szerokosc() -> u32 { 64 }
#[cfg(not(target_pointer_width = "64"))]
fn szerokosc() -> u32 { usize::BITS }
fn main() {
    assert_eq!(szerokosc(), usize::BITS);
    let lista = [1, 2, 3];
    assert_eq!(lista.len(), 3);
}
~~~

Oddzielne definicje tej samej funkcji są poprawne, ponieważ aktywna pozostaje dokładnie jedna. Odbiorca korzysta z tego samego kontraktu niezależnie od platformy. Jeśli warianty platformowe mają inne ograniczenia, dokumentacja musi je nazwać zamiast ukryć pod wspólną nazwą.

Wymaganie wersji `"1.2.3"` to zakres zgodności, a nie obietnica dokładnie tej wersji. Dla `0.x` granica zgodności jest węższa: `0.2.3` nie dopuszcza `0.3.0`. Lockfile ustala konkretne rozwiązanie dla bieżącego projektu, lecz nie sprawia, że opublikowana biblioteka narzuca ten sam lockfile wszystkim konsumentom. Test minimalnych i aktualnych dopuszczalnych zależności wykrywa inne problemy niż samo `--locked`.

Opcjonalna zależność tworzy domyślnie feature o tej samej nazwie, chyba że kontrolujesz ją przez składnię `dep:`. Oddziel nazwę możliwości od szczegółu implementacji, gdy chcesz zachować swobodę zamiany crate’a w przyszłości. Samo ukrycie nazwy nie rozwiązuje jednak wycieku obcych typów w publicznych sygnaturach.

## Diagnostyka kompilatora

Ostrzeżenie `unexpected_cfgs` może wskazywać literówkę w nazwie feature albo brak deklaracji własnego `cfg` w `check-cfg`. Napraw deklarację zamiast globalnie wyłączać lint. Przy brakującym symbolu sprawdź aktywne targety i features w obu pakietach. `compile_error!` jest właściwe dla realnie niedozwolonej konfiguracji, ale para wzajemnie wykluczających features utrudnia `--all-features` i kompozycję grafu; najpierw rozważ osobne typy lub pakiety backendów.

## Praktyka produkcyjna

Macierz wszystkich kombinacji rośnie wykładniczo, dlatego wybierz reprezentatywne profile: minimum, domyślny, wszystkie zgodne i krytyczne podzbiory. Testuj brak domyślnych features osobno, bo maksymalny zestaw potrafi zamaskować brak importu lub przypadkową zależność od `std`. Dla platform sprawdzaj realny target, nie tylko ręcznie ustawiony `cfg`. Nowy feature nie powinien zmieniać istniejącego znaczenia danych ani osłabiać walidacji, ponieważ inni klienci mogą włączyć go nieświadomie przez sumowanie grafu.

## Sprawdź, czy rozumiesz

- Czy jedna deklaracja `default-features = false` gwarantuje brak feature w całym grafie?
- Dlaczego `cfg!(windows)` nie ukryje niepoprawnego importu Unix?
- Jak zakres `0.2.3` różni się od `1.2.3`?

## Ćwiczenia

- `B07-1` — podstawowe: Zapisz dwie rozłączne definicje funkcji przez `cfg`, zachowując wspólny typ wyniku. [Rozwiązanie](../rozwiazania/08_moduly_cargo_i_workspaces/03_zaleznosci_features_i_cfg.md#b07-1).
- `B07-2` — praktyczne: Zaprojektuj feature `json` uruchamiający opcjonalną zależność bez eksponowania jej automatycznej nazwy. [Rozwiązanie](../rozwiazania/08_moduly_cargo_i_workspaces/03_zaleznosci_features_i_cfg.md#b07-2).
- `B07-3` — pogłębione: Rozpisz przyczynę włączenia domyślnej zależności przez drugą krawędź i plan kontroli CI. [Rozwiązanie](../rozwiazania/08_moduly_cargo_i_workspaces/03_zaleznosci_features_i_cfg.md#b07-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [Cargo features i unifikacja](https://doc.rust-lang.org/cargo/reference/features.html)
- [Conditional compilation](https://doc.rust-lang.org/reference/conditional-compilation.html)

## Powiązane tematy

- [Profile, build scripts i publikowanie](04_profile_build_scripts_i_publikowanie.md)
- [Clippy, rustfmt i linty](../09_dokumentacja_testowanie_i_jakosc/03_clippy_rustfmt_i_linty.md)
- [`no_std` i allocatory](../23_no_std_allocatory_i_embedded/02_no_std_allocatory_i_embedded.md)
