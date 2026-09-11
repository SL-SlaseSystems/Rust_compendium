[← Spis treści](../../README.md)

# Rozwiązania: Instalacja i toolchain

## W02-1

Skrót `+beta` ma pierwszeństwo, więc `cargo +beta check` uruchamia beta niezależnie od pliku projektu i override'u katalogu nadrzędnego. Bez skrótu `rustup` wybierze najbliższy `rust-toolchain.toml`; dopiero gdy go nie znajdzie, rozważy override, a na końcu globalny default. Weryfikacja wymaga `rustup show` w tym katalogu oraz `cargo +beta --version` dla skrótu.

## W02-2

~~~toml
[toolchain]
channel = "1.98.1"
profile = "minimal"
components = ["rustfmt", "clippy", "rust-docs"]
targets = ["wasm32-unknown-unknown"]
~~~

Plik przypina wersję i zleca rustup doinstalowanie komponentów oraz `rust-std` targetu. Nie zapewnia sieci, zależności Cargo, edition, systemowego linkera, SDK ani narzędzi wymaganych przez zależności natywne. Sprawdziłbym wynik przez `rustup show`, `rustup component list` i `cargo build --target ...` w środowisku zbliżonym do CI.

## W02-3

Najpierw potwierdzam aktywny toolchain (`rustup show`) i obecność `armv7-unknown-linux-gnueabihf` właśnie w nim. Następnie czytam pełny komunikat linkera: brak `arm-linux-gnueabihf-gcc` wskazuje na brak narzędzia hosta, a brak pliku z sysrootu lub niezgodność formatu — na bibliotekę albo ABI targetu.

Minimalna naprawa instaluje linuxowy cross-linker i zgodny sysroot w obrazie CI, po czym wskazuje linker w `.cargo/config.toml` dla targetu. Test kompilacji nie zastępuje uruchomienia na ARM. Osobny job MSRV używa przypiętej najniższej wersji; przejście current stable nie może go zastąpić, ponieważ oba joby mogą rozwiązać inny kompatybilny graf zależności.
