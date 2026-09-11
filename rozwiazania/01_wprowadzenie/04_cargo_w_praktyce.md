[← Spis treści](../../README.md)

# Rozwiązania: Cargo w praktyce

## W04-1

To jest kompletny manifest analizowany w ćwiczeniu: ma jawny target biblioteczny i binarny. `[dependencies]` trafiają do normalnego builda biblioteki i binariów. `[dev-dependencies]` są dostępne przy testach, przykładach i benchmarkach, ale nie są zwykłą zależnością API biblioteki dla downstream. W tym manifeście `serde` jest zależnością normalną, a `pretty_assertions` — deweloperską. Blok jest manifestem, dlatego celowo nie jest testem Rust.

~~~text
[package]
name = "raport-cli"
version = "0.1.0"
edition = "2024"

[dependencies]
serde = "1"

[dev-dependencies]
pretty_assertions = "1"

[[bin]]
name = "raport"
path = "src/main.rs"

[lib]
path = "src/lib.rs"
~~~

W package'u może istnieć także `src/lib.rs`; wtedy `raport` i testy wywołują publiczne API biblioteki. `serde` jest **third-party** i normalny build musi rozwiązać oraz skompilować tę zależność niezależnie od uruchomienia testów.

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
