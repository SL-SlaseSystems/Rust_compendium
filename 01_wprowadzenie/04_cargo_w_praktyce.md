[← Spis treści](../README.md)
<!-- status: expanded -->

# Cargo w praktyce

> Stan opisu: Rust 1.98.1, Edition 2024, zweryfikowany 10 września 2026 r. Polecenia dotyczą kanału **stable**, chyba że oznaczono inaczej.

## Cele

Po tym rozdziale potrafisz:

- rozdzielić package, crate i target oraz wskazać, co Cargo zbuduje;
- dobrać polecenie Cargo do edycji, kontroli jakości i powtarzalnego CI;
- uzasadnić politykę `Cargo.lock` dla aplikacji, workspace'a i biblioteki.

## Model — manifest, package, crate i target

`Cargo.toml` jest manifestem: opisuje package, metadane, zależności, funkcje (features), profile i targety. Package jest jednostką dystrybucji i konfiguracji. Crate jest pojedynczą jednostką kompilacji Rusta. Target jest źródłem, z którego Cargo tworzy crate: biblioteczny (`lib`), binarny (`bin`), przykładowy (`example`), integracyjny test (`test`) albo benchmark (`bench`). `build.rs` jest osobnym skryptem budowania, uruchamianym przed kompilacją package'a; nie jest zwykłym targetem API programu.

Cargo zwykle wykrywa targety z układu katalogów, ale można je opisać jawnie. Poniższy blok jest manifestem, więc celowo ma etykietę `text`, a nie jest przykładem Rust do wykonania.

~~~text
[package]
name = "narzedzie-cli"
version = "0.1.0"
edition = "2024"
rust-version = "1.85"
resolver = "3"

[dependencies]

[build-dependencies]

[dev-dependencies]

[[bin]]
name = "admin"
path = "src/bin/admin.rs"

[lib]
path = "src/lib.rs"
~~~

Jedna paczka może mieć najwyżej jeden `lib`, wiele binariów oraz wiele przykładów, testów i benchmarków. Nazwa package'a może zawierać myślnik, lecz domyślna nazwa crate'a bibliotecznego zastępuje go podkreśleniem: package `narzedzie-cli` importuje się jako `narzedzie_cli`.

Poniższy samowystarczalny kod to możliwa zawartość `src/lib.rs`; binaria, przykłady i testy mogą używać jego publicznego API.

~~~rust
pub fn etykieta(komenda: &str) -> String {
    format!("cargo {komenda}")
}

fn main() {
    assert_eq!(etykieta("check"), "cargo check");
}
~~~

## Zależności, rejestr i resolver

Zależność może pochodzić z rejestru (domyślnie crates.io), repozytorium Git albo ścieżki lokalnej. Rejestr publikuje indeks metadanych i paczki; Cargo przechowuje pobrany indeks oraz archiwa w cache `$CARGO_HOME/registry`, a zależności Git w `$CARGO_HOME/git`. To szczegół wewnętrznego układu cache, nie format, na którym powinien opierać się skrypt projektu.

Resolver wybiera wersje zgodne z wymaganiami SemVer, źródłami i ograniczeniami feature'ów, po czym zapisuje wynik w `Cargo.lock`. Kilka wersji tej samej paczki może istnieć, gdy graf nie daje się pogodzić; konflikt powstaje dopiero, gdy nie ma rozwiązania spełniającego wymagania. Dla wspólnej zależności Cargo unifikuje włączone features, dlatego powinny być addytywne. Edition 2024 używa `resolver = "3"`. Zachowuje on zakres unifikacji features z resolvera 2 — zwykłe zależności nie łączą bezwarunkowo features użytych wyłącznie przez build- lub dev-dependencies — i dodaje wybór wersji świadomy `rust-version`, z mechanizmem fallback dla niezgodnych wersji. W `cargo test` albo `cargo build --all-targets` zależności deweloperskie mogą jednak uczestniczyć w budowie i zmienić obserwowany zestaw features.

`[dependencies]` opisuje kod docelowy package'a. `[build-dependencies]` budują się dla hosta, bo używa ich `build.rs`; przy cross-kompilacji nie są automatycznie bibliotekami dla targetu. Proceduralne makro użyte jako zwykła zależność także kompiluje się i wykonuje na hoście. `[dev-dependencies]` są dostępne dla testów, przykładów i benchmarków package'a, a nie dla jego normalnej biblioteki jako zależności innego package'a. Tabele `[target.'cfg(...)']` dobierają zależności zależnie od platformy.

## Pętla pracy, artefakty i profile

`cargo check` sprawdza wybrane targety bez końcowego linkowania artefaktów wykonywalnych, więc daje szybki sygnał podczas edycji. `cargo build` kompiluje i linkuje, `cargo run` buduje wybrany binarny target i go uruchamia, zaś `cargo test` buduje właściwe targety testowe i uruchamia harness. `check` nie zastępuje testów ani linkowania.

Domyślne profile `dev` i `release` sterują między innymi optymalizacją, informacją debugowania i panic strategy. `[profile.release]` w rootowym manifeście workspace'a może je zmienić; ustawienia profilu zależności są ograniczone, a nadrzędny package budujący może nadpisać część hints zależności. Nie zakładaj, że profil biblioteki wymusi ustawienia u jej użytkownika.

Cargo zapisuje pośrednie wyniki, dep-info i końcowe artefakty w `target/` (albo katalogu wskazanym przez `CARGO_TARGET_DIR`). To cache budowania, nie źródło prawdy: zwykle nie wersjonuje się go ani nie zakłada przenośności między hostami, targetami, profilami czy wersjami kompilatora.

Typowa pętla jakości dla package'a lub właściwie wybranego workspace'a:

~~~text
cargo fmt --check
cargo check
cargo clippy --all-targets --all-features -- -D warnings
cargo test
cargo doc --no-deps
~~~

`--all-targets` wykrywa kod, którego zwykły build nie obejmuje. `--all-features` jest dobrym dodatkowym przebiegiem dla addytywnych features, lecz nie musi być testem każdego produktu: może łączyć celowo alternatywne backendy, wymagania platformowe albo kosztowne opcje. Wtedy CI powinno mieć nazwane, zgodne zestawy features zamiast udawać, że ich unia jest wspierana.

## Powtarzalność i `Cargo.lock`

`Cargo.lock` utrwala wybrany graf. W aplikacji i zazwyczaj w workspace, który buduje wdrażalne binaria, commituj go: CI i zespół testują wtedy te same wersje. Biblioteka publikowana dla cudzych użytkowników zwykle nie wymusza swojego lockfile'a na downstream: ich resolver wybiera graf w granicach manifestu biblioteki. Można jednak wersjonować lockfile biblioteki dla powtarzalnych testów własnego repozytorium; nie jest to obietnica wersji dla konsumentów.

W CI `cargo ... --locked` kończy się błędem, jeśli lockfile nie istnieje albo musiałby się zmienić. `--frozen` oznacza zarazem `--locked` i `--offline`; ma sens tylko, gdy wymagany indeks i paczki są już w cache. Aktualizację wykonuj świadomie przez `cargo update` lub zmianę manifestu, przeglądaj diff lockfile'a i potem sprawdź nowy graf. `--offline` może wybrać inaczej niż tryb online, jeżeli lokalny cache nie zna nowszych danych.

## Diagnostyka kompilatora

Gdy resolver zgłasza konflikt wersji, najpierw czytaj łańcuch „required by” i manifesty wskazanych package'ów; przy istniejącym lockfile'u sprawdź też jego wpisy. `cargo tree -i nazwa` jest pomocne dopiero, gdy Cargo zdoła rozwiązać graf. Potem zdecyduj, czy podnieść wersję, zmienić feature, ujednolicić zależność czy rozdzielić package'e. Usunięcie wpisu z lockfile'a nie naprawia sprzeczności manifestów.

„No such target” i błąd kompilatora o nieznanej platformie to różne problemy. `cargo run --bin admin` wymaga targetu Cargo o nazwie `admin` w układzie plików albo `[[bin]]`; `cargo build --target aarch64-unknown-linux-gnu` wymaga platformy znanej `rustc` oraz, w praktyce, odpowiedniego std/linkera. Nazwa po `--bin` nie jest trójką targetu kompilacji.

Poniższy błąd pokazuje regułę nazw crate'a. Gdy manifest ma `name = "narzedzie-cli"`, import z myślnikiem nie jest składnią Rusta; użyj `narzedzie_cli` i upewnij się, że biblioteczny target istnieje.

~~~compile_fail
use narzedzie-cli::etykieta;

fn main() {
    let _ = etykieta("check");
}
~~~

## Praktyka produkcyjna

Ustal w repozytorium jeden manifest rootowy, minimalną wersję w `rust-version`, politykę aktualizacji i komendy CI. Używaj `--locked` w przebiegach odtwarzających zatwierdzony graf, lecz nie dodawaj `--frozen` bez przygotowanego cache. Przeglądaj `Cargo.toml` i `Cargo.lock`; zależność z rejestru jest **third-party**, więc jej aktualizacja zasługuje na testy i ocenę.

W dużym workspace wybieraj package'e jawnie (`-p`) i rozdzielaj szybki check od pełnego matrixu platform/features. Nie maskuj ostrzeżeń globalnie tylko po to, aby `-D warnings` przeszło: napraw ostrzeżenie albo uzasadnij precyzyjny `#[allow(...)]` przy kodzie.

Oficjalne szczegóły: [targety Cargo](https://doc.rust-lang.org/cargo/reference/cargo-targets.html), [resolver](https://doc.rust-lang.org/cargo/reference/resolver.html), [features](https://doc.rust-lang.org/cargo/reference/features.html), [profile](https://doc.rust-lang.org/cargo/reference/profiles.html) i [polecenie build](https://doc.rust-lang.org/cargo/commands/cargo-build.html).

## Sprawdź, czy rozumiesz

1. Dlaczego package może mieć wiele crate'ów, ale tylko jeden domyślny target `lib`?
2. Jak feature unification może zmienić kompilację testów względem zwykłego builda?
3. Co gwarantuje `--locked`, a czego nie gwarantuje `--frozen` bez cache?

## Ćwiczenia

- `W04-1` — podstawowe: przeanalizuj manifest z sekcji „Model” (`narzedzie-cli`, jawne `lib` i `bin`, `serde` oraz `pretty_assertions` w rozwiązaniu); wskaż, która zależność trafia do normalnego builda. Porównaj z [rozwiązaniem](../rozwiazania/01_wprowadzenie/04_cargo_w_praktyce.md#w04-1).
- `W04-2` — praktyczne: dobierz polecenie do szybkiej kontroli biblioteki, uruchomienia binarium `admin` i pełnej kontroli targetów w CI. Porównaj z [rozwiązaniem](../rozwiazania/01_wprowadzenie/04_cargo_w_praktyce.md#w04-2).
- `W04-3` — pogłębione: ustal politykę `Cargo.lock` dla workspace'a z CLI i publikowanej biblioteki oraz uzasadnij użycie `--locked`. Porównaj z [rozwiązaniem](../rozwiazania/01_wprowadzenie/04_cargo_w_praktyce.md#w04-3).

## Powiązane tematy

- [Instalacja i toolchain](02_instalacja_i_toolchain.md)
- [Pierwszy program](03_pierwszy_program.md)
- [Crates, pakiety i workspaces](../07_moduly_i_cargo/02_crates_pakiety_i_workspaces.md)
- [Zależności, features i `cfg`](../07_moduly_i_cargo/03_zaleznosci_features_i_cfg.md)
- [Testy jednostkowe i integracyjne](../08_testowanie_i_jakosc/01_testy_jednostkowe_i_integracyjne.md)
