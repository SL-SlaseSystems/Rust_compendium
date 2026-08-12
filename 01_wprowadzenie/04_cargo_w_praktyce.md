[← Spis treści](../README.md)

# Cargo w praktyce

Cargo jest menedżerem pakietów, narzędziem budowania i wspólnym interfejsem
dla testów, dokumentacji oraz wielu rozszerzeń.

## Nowy pakiet

~~~text
cargo new witaj
cd witaj
cargo run
~~~

`cargo new` tworzy manifest `Cargo.toml` i target binarny `src/main.rs`.
`cargo new --lib nazwa` tworzy bibliotekę z `src/lib.rs`.

Minimalny manifest:

~~~toml
[package]
name = "witaj"
version = "0.1.0"
edition = "2024"
rust-version = "1.85"

[dependencies]
~~~

**Pakiet** jest jednostką opisaną manifestem. **Crate** jest jednostką
kompilacji. Pakiet może zawierać bibliotekę i wiele binariów. **Target**
określa konkretny artefakt: lib, bin, test, example lub benchmark.

## Codzienne polecenia

~~~text
cargo check
cargo build
cargo run -- argument-programu
cargo test
cargo doc --open
cargo fmt --check
cargo clippy --all-targets --all-features
~~~

`cargo check` wykonuje analizę bez końcowego linkowania i dlatego jest
zwykle najlepszą komendą podczas edycji. `cargo build --release` używa
profilu zoptymalizowanego.

## Zależności i lockfile

Zależność dodaje się do `[dependencies]` albo poleceniem `cargo add`.
`Cargo.lock` zapisuje rozwiązany graf wersji. Dla aplikacji należy go
commitować. Biblioteki także mogą go przechowywać dla powtarzalnych testów,
ale konsumenci biblioteki i tak rozwiązują własny graf zależności.

~~~toml
[dependencies]
serde = { version = "1", features = ["derive"] }
~~~

Serde jest crate’em **third-party**, nie częścią standard library.
Wersja `"1"` jest wymaganiem zgodnym z SemVer, a nie żądaniem jednej
konkretnej wersji.

## Układ większego pakietu

~~~text
src/lib.rs
src/main.rs
src/bin/admin.rs
tests/api.rs
examples/klient.rs
benches/przepustowosc.rs
build.rs
~~~

Kod współdzielony przez binaria umieszczaj w bibliotece pakietu. Ułatwia to
testowanie i zapobiega kopiowaniu modułów.

## Dobre praktyki

- używaj `cargo check` często, `cargo test` przed integracją;
- trzymaj features addytywne — włączenie feature nie powinno wyłączać API;
- w bibliotece ograniczaj zależności publiczne i powierzchnię `pub`;
- nie edytuj ręcznie `Cargo.lock`;
- sprawdzaj `cargo tree`, gdy graf zależności jest zaskakujący.

## Powiązane tematy

- [Crates, pakiety i workspaces](../07_moduly_i_cargo/02_crates_pakiety_i_workspaces.md)
- [Zależności, features i `cfg`](../07_moduly_i_cargo/03_zaleznosci_features_i_cfg.md)
- [Testy jednostkowe i integracyjne](../08_testowanie_i_jakosc/01_testy_jednostkowe_i_integracyjne.md)
