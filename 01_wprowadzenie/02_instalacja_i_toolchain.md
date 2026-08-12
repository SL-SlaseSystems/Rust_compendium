[← Spis treści](../README.md)

# Instalacja i toolchain

Oficjalnym menedżerem toolchainów jest `rustup`. Instaluje kompilator,
Cargo, dokumentację oraz pozwala przełączać wersje i platformy docelowe.

## Podstawowa instalacja

Aktualne polecenie instalacyjne zawsze sprawdzaj na oficjalnej stronie
`rustup.rs`. Po instalacji:

~~~text
rustc --version
cargo --version
rustup show
~~~

Na Windows instalator może poprosić o narzędzia linkera MSVC. Na Linuksie
zwykle potrzebny jest systemowy linker i pakiet deweloperski libc. Na macOS
zapewniają je Command Line Tools for Xcode.

## Kanały wydań

- `stable` — wydanie zalecane do normalnej pracy;
- `beta` — kandydat na następne stable;
- `nightly` — codzienny snapshot, potrzebny do eksperymentalnych features.

~~~text
rustup update stable
rustup toolchain install nightly
cargo +nightly check
~~~

Nie zakładaj, że feature nightly zostanie ustabilizowany w obecnej postaci.
Biblioteka publiczna powinna mieć świadomie określone MSRV, czyli minimalną
wspieraną wersję Rusta.

## Komponenty

Najczęściej używane komponenty:

~~~text
rustup component add rustfmt clippy
cargo fmt
cargo clippy --all-targets --all-features
~~~

`rust-src` udostępnia źródła biblioteki standardowej, a `rust-analyzer`
zapewnia analizę dla edytora. `rust-docs` instaluje dokumentację offline:

~~~text
rustup component add rust-src rust-docs rust-analyzer
rustup doc --book
rustup doc --std
~~~

## Targety i cross-compilation

Toolchain hosta generuje domyślnie kod dla bieżącego systemu. Inny target
dodaje się jawnie:

~~~text
rustup target list --installed
rustup target add wasm32-unknown-unknown
cargo build --target wasm32-unknown-unknown
~~~

Sama biblioteka standardowa targetu nie gwarantuje, że masz właściwy linker
lub biblioteki systemowe.

## Wersja przypięta do projektu

Plik `rust-toolchain.toml` zapewnia zespołowi spójny kanał:

~~~toml
[toolchain]
channel = "1.97.1"
components = ["rustfmt", "clippy"]
profile = "minimal"
~~~

Edition języka nie jest kanałem toolchainu. Ustawia się ją osobno w
`Cargo.toml`, np. `edition = "2024"`. Jeden aktualny kompilator obsługuje
również starsze editions.

## Dobre praktyki

- aktualizuj stable świadomie i uruchamiaj testy;
- przypinaj wersję w CI, jeśli wymagana jest powtarzalność;
- nie włączaj nightly tylko dla wygody jednego drobiazgu;
- zapisuj MSRV w manifeście i testuj je osobno.

## Powiązane tematy

- [Cargo w praktyce](04_cargo_w_praktyce.md)
- [Edition, nightly i feature gates](../zaawansowane/15_nightly_unstable_i_feature_gates.md)
- [Clippy, rustfmt i linty](../08_testowanie_i_jakosc/03_clippy_rustfmt_i_linty.md)
