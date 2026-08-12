[← Spis treści](../README.md)

# Profile, build scripts i publikowanie

## Profile

Cargo ma profile `dev`, `release`, `test` i `bench`. Najważniejsze ustawienia
to poziom optymalizacji, debug info, LTO, liczba codegen units, overflow
checks, incremental i strategia panic.

~~~toml
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

## Powiązane tematy

- [Wydajność i zero-cost abstractions](../13_wzorce_i_architektura/05_wydajnosc_i_zero_cost.md)
- [Projektowanie API i SemVer](../13_wzorce_i_architektura/03_projektowanie_api_i_semver.md)
- [Benchmarki i profilowanie](../08_testowanie_i_jakosc/04_benchmarki_profilowanie_i_miri.md)
