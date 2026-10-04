[← Spis treści](../README.md)

# Clippy, rustfmt i linty

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

## Powiązane tematy

- [Testy jednostkowe](01_testy_jednostkowe_i_integracyjne.md)
- [Nightly i feature gates](../08_moduly_cargo_i_workspaces/05_nightly_unstable_i_feature_gates.md)
- [Projektowanie API i MSRV](../14_idiomy_wzorce_i_architektura/03_projektowanie_api_i_semver.md)
