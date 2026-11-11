[← Spis treści](../README.md)
<!-- status: expanded -->

# Profile, build scripts i publikowanie

## Cele

Po tym rozdziale potrafisz:

- opisać wejścia i wyjścia powtarzalnego build scriptu;
- odróżnić pakowanie, weryfikację i nieodwracalne wydanie;


## Profile

Cargo ma profile `dev`, `release`, `test` i `bench`. Najważniejsze ustawienia
to poziom optymalizacji, debug info, LTO, liczba codegen units, overflow
checks, incremental i strategia panic.

To fragment manifestu lub konfiguracji; wymaga właściwego projektu i nie jest samodzielnym doctestem.

~~~text
[profile.release]
opt-level = 3
lto = "thin"
codegen-units = 1
strip = "debuginfo"

[profile.dev.package."*"]
opt-level = 1
~~~

Nie kopiuj profilu bez pomiaru. `opt-level = 3` może wygenerować wolniejszy
kod niż `2` przez większy rozmiar i cache pressure. Debug info jest przydatne
w profilowaniu produkcji.

## Build scripts

Plik `build.rs` kompiluje się i wykonuje przed pakietem. Może wykrywać
środowisko, generować kod do `OUT_DIR` lub linkować bibliotekę natywną.

~~~text
fn main() {
    println!("cargo::rerun-if-changed=schemas/protokol.txt");
    println!("cargo::rustc-env=PROTOKOL_WERSJA=1");
}
~~~

To szkic build scriptu. Nie zapisuj wygenerowanych plików do `src`; użyj
`OUT_DIR` i włącz przez `include!`. Emituj `rerun-if-changed` oraz
`rerun-if-env-changed`, aby uniknąć niepotrzebnych uruchomień.

Build script działa na hoście i jest kodem wykonywanym podczas budowania.
Traktuj zależności build jako część łańcucha dostaw. Cross-compilation wymaga
rozróżnienia zmiennych `HOST` i `TARGET`.

## Publikowanie

Przed `cargo publish`:

~~~text
cargo package --list
cargo package
cargo test --all-features
cargo publish --dry-run
~~~

Manifest biblioteki powinien mieć `description`, `license` lub
`license-file`, `repository`, `readme`, sensowne `keywords` i wykluczenia.
`cargo package` tworzy dokładnie artefakt publikowany — testuj go, nie tylko
checkout.

Publikacja wersji w registry jest trwała; wersję można yankować, ale nie
podmieniać treści. Yanking blokuje nowe rozwiązania, nie psuje istniejącego
`Cargo.lock`.

## SemVer i publiczne API

Zmiana sygnatury, usunięcie publicznego elementu, nowy wymagany element
traitu, nowe pole publicznej struktury używanej literałem albo zaostrzenie
bounds może łamać kompatybilność. Automatyczne narzędzia SemVer pomagają, ale
nie rozumieją całego kontraktu semantycznego.

## Dokumentacja i MSRV

Ustaw `rust-version`, jeśli deklarujesz MSRV. Nowa wersja crate’a może podnieść
MSRV według przyjętej polityki; zakomunikuj to w changelogu. Docs.rs korzysta
z metadanych manifestu i może wymagać konfiguracji features/targetów.


## Model — budowanie także wykonuje programy

`build.rs` jest programem hosta uruchamianym przez Cargo, a nie funkcją wykonywaną przez urządzenie docelowe. `cfg!(target_os = ...)` wewnątrz tego programu opisuje platformę kompilacji skryptu. Do generowania kodu dla targetu służą przekazane przez Cargo dane, w tym `TARGET` i odpowiednie `CARGO_CFG_*`. Przy cross-compilation pomylenie hosta z targetem może wygenerować niepoprawne bindingi mimo poprawnej kompilacji samego skryptu.

Wyjście skryptu ma protokół. Linie `cargo::...` wpływają na kompilację, linkowanie oraz decyzje o ponownym uruchomieniu. Zwykły diagnostyczny tekst nie powinien przypadkowo udawać dyrektywy. Kolejność instrukcji linkowania może mieć znaczenie dla narzędzi natywnych. Skrypt powinien odczytywać określone wejścia i zapisywać generowane artefakty do `OUT_DIR`, ponieważ katalog źródeł może być współdzielony albo tylko do odczytu.

Minimalny przykład poniżej demonstruje deterministyczne generowanie tekstu w pamięci. Nie wykonuje protokołu Cargo i nie zastępuje prawdziwego testu `build.rs`.

~~~rust
fn wygeneruj(wersja: u32) -> String {
    format!("pub const WERSJA: u32 = {wersja};\n")
}
fn main() {
    assert_eq!(wygeneruj(3), "pub const WERSJA: u32 = 3;\n");
    assert_eq!(wygeneruj(3), wygeneruj(3));
}
~~~

Odtwarzalność nie wynika wyłącznie z lockfile. Wpływają na nią wersje kompilatorów C, SDK, zmienne środowiska i pliki czytane przez skrypty. `rerun-if-env-changed` dokumentuje zależność od zmiennej środowiska, ale nie utrwala jej wartości. Wartość pochodząca z czasu systemowego lub sieci wymaga osobnego uzasadnienia i psuje prosty model cache.

Profil definiuje kompromis czasu budowania, rozmiaru, diagnozowalności oraz szybkości. LTO i jedna jednostka codegen mogą zmniejszyć granice optymalizacji, lecz wydłużyć kompilację. `strip` usuwa informacje przydatne w analizie awarii. Zachowaj symboliczne artefakty zgodne z dokładnym binarium, jeśli usuwasz symbole z dystrybucji. Nie porównuj benchmarku `dev` z produkcyjnym `release` i nie przypisuj różnicy samemu algorytmowi.

Pakowanie sprawdza zawartość archiwum, nie tylko stan folderu roboczego. Plik ignorowany przez Git albo niewłaściwie wskazany `include` może nie trafić do wydania. Zależność ścieżkowa może wymagać wersji registry, gdy paczka ma być publikowana. `publish --dry-run` nie wysyła wydania, lecz nadal wykonuje odpowiednie przygotowanie i weryfikację; nie jest testem wszystkich platform ani wszystkich konfiguracji features.

Yanking zmienia dostępność wersji dla nowych rozwiązań. Nie usuwa skutków pobrania ani nie zastępuje poprawek bezpieczeństwa nowym wydaniem. Plan wydawniczy powinien obejmować kolejność publikacji zależnych pakietów, sprawdzenie dokumentacji i komunikat zmian zgodności.

## Diagnostyka kompilatora

Błąd linkera po poprawnej analizie Rust może pochodzić z niezgodnego SDK, architektury albo kolejności bibliotek natywnych. `cargo check` go nie wyklucza, bo nie wykonuje całego linkowania. Gdy skrypt nie przebudowuje artefaktu po zmianie schematu, sprawdź deklaracje `rerun-if-changed`. Jeśli pakowanie nie znajduje pliku, obejrzyj `cargo package --list`, zamiast dodawać kolejne wyjątki w kodzie generatora.

## Praktyka produkcyjna

Mierz profil w warunkach zbliżonych do wdrożenia i zachowuj dane do symbolizacji awarii. Dla build scriptu zapisz kontrakt host/target i wszystkie wejścia. Weryfikuj archiwum wydania oraz MSRV niezależnie od bieżącego kompilatora. Rozdziel uprawnienia publikowania od zwykłych zadań testowych CI. Wersja opublikowana w registry ma trwałą tożsamość, dlatego ostatni etap powinien korzystać z tego samego przygotowanego źródła i zestawu plików, który przeszedł kontrole.

## Sprawdź, czy rozumiesz

- Dlaczego `cfg!` w `build.rs` może opisywać niewłaściwą platformę?
- Jakich błędów nie wykryje samo `cargo check`?
- Dlaczego `Cargo.lock` nie gwarantuje odtwarzalnego generatora?

## Ćwiczenia

- `B08-1` — podstawowe: Napisz deterministyczny generator deklaracji stałej i sprawdź wynik. [Rozwiązanie](../rozwiazania/08_moduly_cargo_i_workspaces/04_profile_build_scripts_i_publikowanie.md#b08-1).
- `B08-2` — praktyczne: Rozpisz dyrektywy przebudowy generatora czytającego schemat i zmienną `SCHEMA_MODE`. [Rozwiązanie](../rozwiazania/08_moduly_cargo_i_workspaces/04_profile_build_scripts_i_publikowanie.md#b08-2).
- `B08-3` — pogłębione: Przygotuj procedurę diagnozy brakującego pliku w archiwum i niezgodnego linkera. [Rozwiązanie](../rozwiazania/08_moduly_cargo_i_workspaces/04_profile_build_scripts_i_publikowanie.md#b08-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [Build scripts: protokół i host](https://doc.rust-lang.org/cargo/reference/build-scripts.html)
- [Cargo profiles](https://doc.rust-lang.org/cargo/reference/profiles.html)
- [Publishing](https://doc.rust-lang.org/cargo/reference/publishing.html)

## Powiązane tematy

- [Wydajność i zero-cost abstractions](../20_wydajnosc_i_optymalizacja/01_wydajnosc_i_zero_cost.md)
- [Projektowanie API i SemVer](../14_idiomy_wzorce_i_architektura/03_projektowanie_api_i_semver.md)
- [Benchmarki i profilowanie](../20_wydajnosc_i_optymalizacja/02_benchmarki_profilowanie_i_miri.md)
