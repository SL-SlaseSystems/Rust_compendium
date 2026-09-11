[← Spis treści](../README.md)
<!-- status: expanded -->

# Instalacja i toolchain

> Baza dokumentacji: Rust 1.98.1, Edition 2024, zweryfikowane 10 września 2026 r. Lokalne polecenia wykonano na Rust 1.90.0; nie są potwierdzeniem działania na 1.98.1. Opis dotyczy **stable**, poza miejscami oznaczonymi inaczej.

## Cele

Po tym rozdziale potrafisz:

- ustalić, który toolchain wybierze `rustup` dla danego katalogu;
- przypiąć wersję, komponenty i targety projektu bez mylenia ich z linkerem;
- rozdzielić w CI kontrolę MSRV od kontroli bieżącego stable.

## Model — proxy, toolchain i projekt

`rustup` instaluje toolchainy i udostępnia proxy, czyli programy `cargo`, `rustc` i `rustdoc` znajdujące właściwy toolchain przed uruchomieniem rzeczywistego narzędzia. Wybór nie jest globalnie stały: zależy od katalogu i argumentów.

Pierwszeństwo jest następujące: skrót w wierszu poleceń, np. `cargo +beta`; `RUSTUP_TOOLCHAIN`; override katalogowy; najbliższy `rust-toolchain.toml` albo `rust-toolchain`; globalny default. `rustup` szuka pliku i override'u ku korzeniowi systemu; bliższe ustawienie projektu wygrywa. `rustup show` pokazuje rezultat. Pełne reguły opisuje [rustup: overrides](https://rust-lang.github.io/rustup/overrides.html).

Kanały `stable`, `beta` i `nightly` mają różne role. `stable` jest właściwy dla wydania, `beta` pomaga wykryć regresję przed następnym stable, a **nightly** jest codziennym wydaniem i może wymagać `#![feature(...)]`. Dla powtarzalności można użyć wersji `1.98.1` lub datowanego kanału, np. `nightly-2026-09-10`; data w nazwie nie jest deklaracją lokalnego wykonania.

## Reguły: komponenty, profile i konfiguracja

Komponent jest częścią dystrybucji konkretnego toolchainu. `rustc` i `cargo` są podstawowe; `rustfmt`, `clippy`, `rust-docs`, `rust-src` i `rust-analyzer` są dodatkami, których dostępność może różnić się między kanałami i wydaniami. Profil `minimal` instaluje `rustc`, `rust-std` i `cargo`; `default` dodaje zwykłe narzędzia, w tym dokumentację, `rustfmt` i `clippy`; `complete` próbuje zainstalować wszystkie dostępne komponenty. Ten ostatni profil jest zwykle niepotrzebny i może być niedostępny, gdy brakuje komponentu dla kanału lub hosta. W CI wybieraj `minimal` i deklaruj wymagane komponenty jawnie. Sprawdzaj dostępność przez `rustup component list --toolchain <nazwa>`. Zobacz [model komponentów rustup](https://rust-lang.github.io/rustup/concepts/components.html).

Wersję współdzieloną przez zespół zapisuj w repozytorium. Ten blok jest konfiguracją, nie programem, dlatego używa `toml`.

~~~toml
[toolchain]
channel = "1.98.1"
profile = "minimal"
components = ["rustfmt", "clippy", "rust-docs"]
targets = ["wasm32-unknown-unknown"]
~~~

`rust-toolchain.toml` wybiera toolchain dla projektu i może dodać komponenty oraz targety. `rustup override set 1.98.1` zapisuje ustawienie lokalnie w konfiguracji rustup, więc nadaje się do eksperymentu, lecz nie komunikuje wymagania współpracownikom. Edition ustawia się niezależnie w `Cargo.toml`, np. `edition = "2024"`.

`cargo install` buduje i instaluje binarium z crate'a — często **third-party** — do katalogu binariów Cargo. Nie instaluje `clippy`, `rustfmt`, dokumentacji ani targetu; nimi zarządza `rustup component add` albo `rustup target add`.

## Host, target i linker

Host to platforma, na której działa `rustc`; target to platforma, dla której powstaje artefakt. Target triple, np. `aarch64-unknown-linux-gnu`, opisuje architekturę, system i środowisko ABI wyniku. [Tabele wsparcia platform](https://doc.rust-lang.org/rustc/platform-support.html) rozróżniają poziomy testowania i dostępność `std`; sama lista targetów nie gwarantuje uruchomienia produktu.

`rustup target add --toolchain 1.98.1 wasm32-unknown-unknown` instaluje dla tego toolchainu `rust-std` targetu. Jest to konieczne, lecz często niewystarczające. Linkowanie natywne może wymagać linkera, sysrootu, bibliotek i SDK targetu. Skonfiguruj linker w `.cargo/config.toml` albo przez zmienną środowiskową; dla `armv7-unknown-linux-gnueabihf` nazwa po normalizacji target triple to `CARGO_TARGET_ARMV7_UNKNOWN_LINUX_GNUEABIHF_LINKER`. Dla zależności z kodem C dobierz też zgodny kompilator C. [Cross-compilation w rustup](https://rust-lang.github.io/rustup/cross-compilation.html) ogranicza rolę `target add` do biblioteki standardowej.

Przykład sprawdza format części wersji bez zakładania, że linker targetu istnieje.

~~~rust
fn wersja_glowna_i_poboczna(wersja: &str) -> Option<(u32, u32)> {
    let numer = wersja.strip_prefix("rustc ")?.split_whitespace().next()?;
    let mut czesci = numer.split('.');
    Some((czesci.next()?.parse().ok()?, czesci.next()?.parse().ok()?))
}

fn main() {
    assert_eq!(wersja_glowna_i_poboczna("rustc 1.98.1 (hash)"), Some((1, 98)));
    assert_eq!(wersja_glowna_i_poboczna("nie-rustc"), None);
}
~~~

## Diagnostyka kompilatora

- Sugestia `rustup target add` lub `can't find crate for core` zwykle oznacza brak `rust-std` dla wybranego targetu i toolchainu.
- `linker ... not found` albo brak bibliotek systemowych oznacza późniejszą warstwę: brakuje linkera, SDK, sysrootu albo zgodności ABI. Ponowne `target add` tego nie naprawia.
- `component ... is unavailable` oznacza niedostępność składnika dla kanału, wersji lub hosta. Sprawdź listę komponentów i przypnij wersję.
- Gdy current stable przechodzi lokalnie, lecz CI wspiera niższe MSRV (minimalną wspieraną wersję Rusta), błąd może wynikać z API lub semantyki po MSRV. `package.rust-version` komunikuje MSRV Cargo; zobacz [Cargo: `rust-version`](https://doc.rust-lang.org/cargo/reference/rust-version.html).

## Praktyka produkcyjna

Dokumentację offline instaluje `rust-docs`; potem `rustup doc --std` lub `rustup doc --book` otwiera lokalną kopię. Przy pracy bez sieci potrzebne są wcześniej toolchainy, komponenty, targety i cache zależności — cache Cargo jest osobnym problemem od `rust-docs`.

W CI rozdziel dwa tory. Tor MSRV przypina dokładną najniższą wersję, np. `cargo +1.74.0 test`, i chroni deklarowaną kompatybilność. Tor current stable aktualizuje się świadomie i uruchamia zwykłą macierz testów, formatowanie oraz linty. **nightly** może być osobnym sygnałem wczesnego ostrzegania, ale nie zastępuje stable ani MSRV. Aktualizację `rust-toolchain.toml`, `Cargo.lock` i obrazu CI przeglądaj razem z wynikiem testów.

## Sprawdź, czy rozumiesz

1. Dlaczego `cargo +nightly check` może użyć innego toolchainu niż `cargo check` w tym samym katalogu?
2. Co instaluje `rustup target add`, a czego nie instaluje?
3. Dlaczego test MSRV i test bieżącego stable wykrywają różne klasy regresji?

## Ćwiczenia

- `W02-1` — podstawowe: w katalogu potomnym projektu opisz, który toolchain wybierze `cargo`, gdy projekt ma `rust-toolchain.toml`, katalog nadrzędny ma override, a polecenie brzmi `cargo +beta check`. Podaj kolejność dowodzenia i sposób sprawdzenia. Porównaj z [rozwiązaniem](../rozwiazania/01_wprowadzenie/02_instalacja_i_toolchain.md#w02-1).
- `W02-2` — praktyczne: zaprojektuj `rust-toolchain.toml` dla repozytorium używającego Rust 1.98.1, `rustfmt`, `clippy`, dokumentacji offline i targetu `wasm32-unknown-unknown`. Wyjaśnij, czego plik nie gwarantuje. Porównaj z [rozwiązaniem](../rozwiazania/01_wprowadzenie/02_instalacja_i_toolchain.md#w02-2).
- `W02-3` — pogłębione: CI hostowane na macOS nie linkuje programu dla `armv7-unknown-linux-gnueabihf` mimo zainstalowanego targetu. Ułóż kolejność diagnostyki i minimalny plan naprawy, uwzględniając linker, ABI i MSRV. Porównaj z [rozwiązaniem](../rozwiazania/01_wprowadzenie/02_instalacja_i_toolchain.md#w02-3).

## Powiązane tematy

- [Pierwszy program](03_pierwszy_program.md)
- [Cargo w praktyce](04_cargo_w_praktyce.md)
- [Crates, pakiety i workspaces](../07_moduly_i_cargo/02_crates_pakiety_i_workspaces.md)
- [Edition, nightly i feature gates](../zaawansowane/15_nightly_unstable_i_feature_gates.md)
