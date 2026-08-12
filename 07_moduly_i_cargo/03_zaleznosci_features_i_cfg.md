[← Spis treści](../README.md)

# Zależności, features i `cfg`

Cargo rozwiązuje wersje zależności zgodnie z manifestem, lockfile i SemVer.
Zależności mogą pochodzić z registry, Git lub ścieżki lokalnej.

## Rodzaje zależności

~~~toml
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

~~~toml
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

## Powiązane tematy

- [Profile, build scripts i publikowanie](04_profile_build_scripts_i_publikowanie.md)
- [Clippy, rustfmt i linty](../08_testowanie_i_jakosc/03_clippy_rustfmt_i_linty.md)
- [`no_std` i allocatory](../zaawansowane/12_no_std_allocatory_i_embedded.md)
