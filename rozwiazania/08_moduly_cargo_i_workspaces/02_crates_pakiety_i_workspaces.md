[← Spis treści](../../README.md)

# Rozwiązania: Crates, pakiety i workspaces

[Rozdział źródłowy](../../08_moduly_cargo_i_workspaces/02_crates_pakiety_i_workspaces.md).

## B06-1

`src/lib.rs` jest domyślnym targetem bibliotecznym. `src/main.rs` jest domyślnym targetem binarnym. `tests/api.rs` jest targetem testu integracyjnego i osobnym crate’em. Wszystkie należą do tego samego pakietu z `Cargo.toml`, ale test integracyjny nie otrzymuje uprawnień do prywatnych pól biblioteki. Oddzielne targety nie są oddzielnymi pakietami workspace’a.

## B06-2

Manifesty są danymi projektu wieloplikowego i nie są doctestem.

~~~text
# Cargo.toml
[workspace]
members = ["domena"]
resolver = "3"
[workspace.package]
edition = "2024"

# domena/Cargo.toml
[package]
name = "domena"
version = "0.1.0"
edition.workspace = true
~~~
Dodaj pusty `domena/src/lib.rs`; bez targetu członek nie jest kompletnym pakietem.

## B06-3

Trait portu, na przykład `Repozytorium`, należy do domeny lub osobnego małego pakietu kontraktów. Adapter zależy od tego kontraktu i implementuje trait. Aplikacja zależy od domeny i adaptera, konstruuje oba w `main` i przekazuje implementację do serwisu. Domena nie importuje adaptera. Graf to aplikacja → adapter → domena oraz aplikacja → domena. Wydzielenie portu jest potrzebne tylko wtedy, gdy uzasadnia je realna współdzielona granica; nie dodawaj pustego pakietu dla samego ukrycia problemu.

