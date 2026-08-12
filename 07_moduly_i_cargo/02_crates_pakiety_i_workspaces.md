[← Spis treści](../README.md)

# Crates, pakiety i workspaces

## Pojęcia

- **crate** — jednostka kompilacji i korzeń drzewa modułów;
- **package** — manifest `Cargo.toml` oraz co najmniej jeden target;
- **target** — biblioteka, binarium, test, example, benchmark lub build script;
- **workspace** — grupa pakietów współdzieląca lockfile i katalog `target`.

Crate biblioteczny ma korzeń `src/lib.rs`. Domyślne binarium — `src/main.rs`.
Pliki `src/bin/*.rs` tworzą dodatkowe binaria.

## Biblioteka plus cienkie binarium

Duża aplikacja zyskuje, gdy logika znajduje się w lib crate, a `main` tylko
składa zależności, wczytuje konfigurację i mapuje błąd na exit code. Testy
integracyjne mogą wtedy wywoływać publiczne API bez uruchamiania procesu.

~~~rust
pub fn komunikat(nazwa: &str) -> String {
    format!("Witaj, {nazwa}")
}

fn main() {
    assert_eq!(komunikat("Ada"), "Witaj, Ada");
}
~~~

## Workspace

~~~toml
[workspace]
resolver = "3"
members = [
  "crates/domena",
  "crates/infrastruktura",
  "apps/serwer",
]

[workspace.package]
edition = "2024"
rust-version = "1.85"
license = "MIT OR Apache-2.0"

[workspace.dependencies]
serde = "1"
~~~

Pakiet dziedziczy dane przez `edition.workspace = true` lub zależność przez
`serde.workspace = true`. Workspace nie zamienia automatycznie wszystkich
crate’ów w jeden; każdy nadal ma publiczne granice i własne features.

## Virtual i root package

Manifest tylko z `[workspace]` jest virtual workspace. Manifest może też
opisywać root package. Jawnie ustaw resolver zgodny z edition, szczególnie
w virtual workspace.

## Zależności ścieżkowe

~~~toml
[dependencies]
domena = { path = "../domena" }
~~~

Cargo buduje graf zależności, ale cykle między pakietami są zabronione.
Jeśli dwa crate’y potrzebują siebie, wydziel wspólny kontrakt lub zmień
kierunek zależności. Nie dziel workspace’a na dziesiątki crate’ów bez realnej
granicy kompilacji, wersjonowania lub odpowiedzialności.

## Nazwy i import

Nazwa pakietu może zawierać myślnik, a nazwa crate’a w kodzie używa
podkreślenia. Manifest może jawnie ustawić `name` i `path` targetu. Unikaj
zaskakujących mapowań.

## Powiązane tematy

- [Cargo w praktyce](../01_wprowadzenie/04_cargo_w_praktyce.md)
- [Zależności, features i `cfg`](03_zaleznosci_features_i_cfg.md)
- [Architektura aplikacji](../13_wzorce_i_architektura/04_architektura_aplikacji_i_di.md)
