[← Spis treści](../../README.md)

# Rozwiązania: Profile, build scripts i publikowanie

[Rozdział źródłowy](../../08_moduly_cargo_i_workspaces/04_profile_build_scripts_i_publikowanie.md).

## B08-1

~~~rust
fn deklaracja(n:u16)->String{format!("pub const LIMIT: u16 = {n};")}
fn main(){assert_eq!(deklaracja(5),"pub const LIMIT: u16 = 5;");assert_eq!(deklaracja(5),deklaracja(5));}
~~~
Generator zależy tylko od jawnego argumentu, bez czasu i sieci.

## B08-2

To kompletny zapis dyrektyw dla szkicu generatora, wymagający uruchomienia jako `build.rs`, więc nie jest doctestem.

~~~text
fn main() {
    println!("cargo::rerun-if-changed=schemas/protokol.txt");
    println!("cargo::rerun-if-env-changed=SCHEMA_MODE");
}
~~~
Wynik generatora zapisz do ścieżki z `OUT_DIR`. Zmianę trybu uwzględnij jawnie w generowaniu; same dyrektywy nie tworzą kodu.

## B08-3

Najpierw `cargo package --list` pokazuje, czy plik schematu znalazł się w zestawie. Sprawdź `include`, `exclude`, reguły ignorowania i ścieżki względne wobec manifestu. Następnie zbuduj pakiet przez `cargo package`, zachowując stderr. Jeśli analiza kodu przechodzi, a linkowanie nie, porównaj architekturę targetu, wersję linkera, `SDKROOT` i biblioteki natywne. Testuj poprawkę zmienną środowiska ograniczoną do polecenia. Nie maskuj problemu linkerowego przez ogłoszenie sukcesu po samym `cargo check`.

