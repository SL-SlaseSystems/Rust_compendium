[← Spis treści](../../README.md)

# Rozwiązania: Cargo w praktyce

## W04-1

To jest kompletny manifest analizowany w ćwiczeniu: ma jawny target biblioteczny i binarny. `[dependencies]` trafiają do normalnego builda biblioteki i binariów. `[dev-dependencies]` są dostępne przy testach, przykładach i benchmarkach, ale nie są zwykłą zależnością API biblioteki dla downstream. W tym manifeście `serde` jest zależnością normalną, a `pretty_assertions` — deweloperską. Blok jest manifestem, dlatego celowo nie jest testem Rust.

~~~text
[package]
name = "narzedzie-cli"
version = "0.1.0"
edition = "2024"
rust-version = "1.85"
resolver = "3"

[dependencies]
serde = "1"

[dev-dependencies]
pretty_assertions = "1"

[[bin]]
name = "admin"
path = "src/bin/admin.rs"

[lib]
path = "src/lib.rs"
~~~

`src/lib.rs` tworzy crate `narzedzie_cli`, więc bin `admin` i testy wywołują jego publiczne API. `serde` jest **third-party** i normalny build musi rozwiązać oraz skompilować tę zależność niezależnie od uruchomienia testów.


Target binarny korzystający z biblioteki wymaga publicznego API, ponieważ jest osobnym crate'em, nawet w tym samym package'u. Prywatna funkcja `etykieta` w `src/lib.rs` nie stanie się dostępna tylko dlatego, że oba pliki mają wspólny manifest. Testy jednostkowe wewnątrz modułu biblioteki i testy integracyjne spoza niej mają przez to różne uprawnienia dostępu.

## W04-2

Do szybkiej kontroli biblioteki wybierz `cargo check --lib`: sprawdza typy i zależności bez końcowego linkowania binarium. Do uruchomienia konkretnego targetu użyj `cargo run --bin admin`. CI wykrywające błędy w przykładach, testach, binariach i benchmarkach powinno dołączyć `cargo check --all-targets` i niezależne kroki formatowania, lintów, testów oraz dokumentacji.

~~~text
cargo fmt --check
cargo check --all-targets
cargo clippy --all-targets --all-features -- -D warnings
cargo test --locked
cargo doc --no-deps --locked
cargo run --bin admin -- status
~~~

`--all-features` pozostaw tylko wtedy, gdy unia funkcji jest wspierana. Gdy `postgres` i `sqlite` są celowo alternatywnymi backendami, uruchom dwa jawne przebiegi, na przykład `--features postgres` i `--features sqlite`, zamiast uznać ich wspólny build za kontrakt package'a.


Przejście `cargo check` nie dowodzi udanego linkowania zależności natywnych, a `cargo doc` bez testów nie dowodzi wykonania przykładów. Do sprawdzenia dokumentacji potrzebne jest również `cargo test --doc`. Dla workspace'a polecenia wymagają świadomego wyboru `--workspace` albo `-p`, bo domyślni członkowie mogą nie obejmować wszystkich produktów.

## W04-3

Commituj jeden `Cargo.lock` w rootowym workspace'ie z CLI, ponieważ jest on produktem wdrażalnym i zespół chce odtwarzać zatwierdzony graf. Publikowana biblioteka może współdzielić ten plik dla własnych testów, ale jej downstream nie dziedziczy go: resolver downstream wybiera wersje według własnego grafu i wymagań z `Cargo.toml` biblioteki.

W CI dodaj `--locked` do komend odtwarzających committowany plik. Brak pliku lub konieczność jego zmiany staje się wtedy błędem. Aktualizacja wersji to osobny, przeglądany commit (`cargo update` albo zmiana manifestu), po którym uruchamia się testy. Nie używaj bezwarunkowo `--frozen`: łączy ono `--locked` z trybem offline i zawiedzie, gdy runner nie ma indeksu lub paczek w cache.

Poniższy test pokazuje dobrą granicę odpowiedzialności: logika biblioteki jest niezależna od binarnego targetu, który ją wywoła.

~~~rust
pub fn wersja_raportu(wersja: &str) -> String {
    format!("raport {wersja}")
}

fn main() {
    assert_eq!(wersja_raportu("1.0.0"), "raport 1.0.0");
}
~~~


Powtarzalny graf nie jest jeszcze powtarzalnym artefaktem binarnym. Do wydania zapisujemy wersję kompilatora i linkera, target, wersje bibliotek systemowych oraz istotną konfigurację `build.rs`. Lockfile nie może zablokować zmian zewnętrznego systemowego SDK. Weryfikacja na świeżym runnerze pomaga wykryć zależność od lokalnego cache, ale nie zastępuje zapisu pochodzenia artefaktu.
