[← Spis treści](../README.md)
<!-- status: expanded -->

# Crates, pakiety i workspaces

## Cele

Po tym rozdziale potrafisz:

- rozróżnić pakiet, target i workspace przy diagnozie grafu;
- zaprojektować dziedziczenie ustawień bez ukrywania zależności;


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

To fragment manifestu lub konfiguracji; wymaga właściwego projektu i nie jest samodzielnym doctestem.

~~~text
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

To fragment manifestu lub konfiguracji; wymaga właściwego projektu i nie jest samodzielnym doctestem.

~~~text
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


## Model — granice kompilacji i wyboru pakietów

Workspace koordynuje pracę, lecz nie usuwa niezależności pakietów. Każdy ma nazwę, manifest i własny zestaw zależności. Biblioteka oraz binarium jednego pakietu są osobnymi crate’ami; kod biblioteki nie staje się automatycznie prywatną częścią binarium. Test integracyjny też kompiluje się jako osobny crate. Dlatego przeniesienie logiki do `lib.rs` daje testowalną granicę bez uruchamiania procesu.

Wspólny lockfile zapewnia wspólne rozwiązanie grafu, ale nie wymusza jednej wersji każdej zależności. Sprzeczne wymagania mogą sprowadzić dwie wersje, a typ z jednej wersji crate’a nie jest typem z drugiej. Wspólny katalog `target` poprawia ponowne użycie artefaktów, lecz zmiana features, profilu lub platformy nadal może tworzyć różne jednostki kompilacji.

Dziedziczenie jest jawne. Samo wpisanie `edition` do `[workspace.package]` nie zmienia edition wszystkich członków. Każdy członek musi wybrać `edition.workspace = true`. Podobnie `[workspace.dependencies]` jest katalogiem deklaracji do odziedziczenia, a nie listą zależności włączanych automatycznie wszędzie. Dzięki temu pakiet domenowy nie musi nieświadomie zależeć od klienta sieciowego aplikacji.

Polecenia poniżej opisują pracę w istniejącym workspace; nie są samodzielnym kodem Rust i nie uruchamiają tutaj publikacji.

~~~text
cargo metadata --no-deps --format-version 1
cargo check --workspace
cargo test -p domena
cargo run -p serwer --bin serwer
cargo tree -p serwer -d
~~~

`-p` wybiera pakiet, a `--bin` target binarny. Bez jawnego wyboru zachowanie zależy między innymi od bieżącego katalogu i `default-members`. Wirtualny root nie jest pakietem, więc nie ma własnego `src/lib.rs`. Jawny wybór w CI zapobiega sytuacji, w której lokalny test jednego członka zostaje uznany za weryfikację całego repozytorium.

Resolver `3`, dostępny od Rust 1.84 i domyślny dla Edition 2024, zmienia domyślną politykę traktowania wersji zależności niezgodnych z deklarowanym `rust-version` na fallback. Nie stanowi dowodu działania całego grafu na MSRV. Zależność może mieć niepełną deklarację, build script potrzebować nowszego narzędzia, a użyta kombinacja features wymagać innych możliwości. Rzeczywisty test minimalnego kompilatora nadal jest potrzebny. Wirtualny workspace powinien wskazywać resolver jawnie, bo nie ma edition pakietu głównego, z której można go wywnioskować.

Wydzielanie crate’a przynosi koszt: nowe publiczne API, manifest, ewentualne wydawanie oraz więcej kombinacji integracyjnych. Ma sens przy ponownym użyciu, oddzielnym targetcie lub kontroli zależności. Gdy chodzi wyłącznie o porządek folderów, zwykły moduł często daje ten sam efekt przy mniejszym obciążeniu.

## Diagnostyka kompilatora

`package ... not found in workspace` wskazuje wybór pakietu, a nie brak modułu. Błąd cyklu zależności wymaga zmiany grafu odpowiedzialności; kolejność wpisów w `members` go nie naprawia. „Expected type, found a different type” z dwiema ścieżkami do crate’a może oznaczać duplikat wersji; sprawdź `cargo tree -d`. Brak dziedziczonego pola to problem manifestu członka albo rootu, nie składni Rust.

## Praktyka produkcyjna

Ustal `default-members` i jawny zakres kontroli CI. Trzymaj domenę wolną od ciężkich zależności, jeśli chcesz szybko ją testować lub użyć w innym środowisku. Lockfile wersjonuj według polityki projektu, pamiętając, że konsument biblioteki rozwiązuje własny graf. Osobno testuj pakowanie każdego publikowanego członka: zależność `path` działa lokalnie, ale registry wymaga poprawnej wersji i dostępnego pakietu. Workspace nie jest pojedynczą jednostką publikacji ani transakcją wydawniczą.

## Sprawdź, czy rozumiesz

- Czy `[workspace.dependencies]` dodaje zależność każdemu członkowi?
- Dlaczego wspólny lockfile nie usuwa duplikatów typów między wersjami?
- Czego resolver uwzględniający `rust-version` nie dowodzi?

## Ćwiczenia

- `B06-1` — podstawowe: Sklasyfikuj `lib.rs`, `main.rs` i `tests/api.rs` jako targety/crate’y jednego pakietu. [Rozwiązanie](../rozwiazania/08_moduly_cargo_i_workspaces/02_crates_pakiety_i_workspaces.md#b06-1).
- `B06-2` — praktyczne: Zapisz komplet minimalnych manifestów rootu i członka dziedziczącego edition. [Rozwiązanie](../rozwiazania/08_moduly_cargo_i_workspaces/02_crates_pakiety_i_workspaces.md#b06-2).
- `B06-3` — pogłębione: Usuń cykl domena → adapter → domena przez wydzielenie portu i composition root. [Rozwiązanie](../rozwiazania/08_moduly_cargo_i_workspaces/02_crates_pakiety_i_workspaces.md#b06-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [Workspaces i dziedziczenie](https://doc.rust-lang.org/cargo/reference/workspaces.html)
- [Resolver i rust-version](https://doc.rust-lang.org/cargo/reference/resolver.html)

## Powiązane tematy

- [Cargo w praktyce](../01_wprowadzenie_i_toolchain/04_cargo_w_praktyce.md)
- [Zależności, features i `cfg`](03_zaleznosci_features_i_cfg.md)
- [Architektura aplikacji](../14_idiomy_wzorce_i_architektura/04_architektura_aplikacji_i_di.md)
