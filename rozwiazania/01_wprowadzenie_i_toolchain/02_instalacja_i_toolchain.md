[← Spis treści](../../README.md)

# Rozwiązania: Instalacja i toolchain

## W02-1

W tym scenariuszu skrót `+beta` ma pierwszeństwo, więc `cargo +beta check` uruchamia beta niezależnie od pliku projektu i override'u katalogu nadrzędnego. Bez skrótu i bez `RUSTUP_TOOLCHAIN` o wyniku rozstrzyga bliskość pliku projektu i override'u: bliższy plik wygrywa z override'em rodzica, ale w tym samym katalogu override ma pierwszeństwo. Dopiero brak obu prowadzi do globalnego defaultu. Weryfikacja wymaga `rustup show` w tym katalogu oraz `cargo +beta --version` dla skrótu.


Do diagnozy zapisujemy również `rustc --version --verbose` oraz sprawdzamy `RUSTUP_TOOLCHAIN`. Jawne `+beta` ma pierwszeństwo także przed tą zmienną. Samo `rustup show` bez jawnego skrótu pokazuje wybór domyślny dla katalogu; dlatego dla konkretnego polecenia potwierdzamy też wersję `cargo +beta --version`. Nie trzeba usuwać ustawień innych projektów ani zmieniać globalnego defaultu.

## W02-2

~~~text
[toolchain]
channel = "1.98.1"
profile = "minimal"
components = ["rustfmt", "clippy", "rust-docs"]
targets = ["wasm32-unknown-unknown"]
~~~

Plik przypina wersję i zleca rustup doinstalowanie komponentów oraz `rust-std` targetu. Nie zapewnia sieci, zależności Cargo, edition, systemowego linkera, SDK ani narzędzi wymaganych przez zależności natywne. Sprawdziłbym wynik przez `rustup show`, `rustup component list` i `cargo build --target ...` w środowisku zbliżonym do CI.


Jest to konfiguracja żądana w treści zadania, a nie deklaracja lokalnej instalacji 1.98.1. Faktyczne przykłady rozwiązań sprawdzane są na Rust 1.90.0. `edition` i `rust-version` pozostają w manifeście Cargo: pierwsze wybiera reguły języka, drugie komunikuje najniższą wspieraną wersję, a żadne nie instaluje narzędzi automatycznie.

## W02-3

Najpierw potwierdzam aktywny toolchain (`rustup show`) i obecność `armv7-unknown-linux-gnueabihf` właśnie w nim. Następnie czytam pełny komunikat linkera: brak `arm-linux-gnueabihf-gcc` wskazuje na brak narzędzia hosta, a brak pliku z sysrootu lub niezgodność formatu — na bibliotekę albo ABI targetu.

Minimalna naprawa instaluje linuxowy cross-linker i zgodny sysroot w obrazie CI, po czym wskazuje linker w `.cargo/config.toml` dla targetu. Test kompilacji nie zastępuje uruchomienia na ARM. Osobny job MSRV używa przypiętej najniższej wersji i sprawdza składnię, API `std` oraz kompatybilność wybranych zależności; przejście current stable nie może go zastąpić. Ze wspólnym, zablokowanym `Cargo.lock` joby zwykle testują ten sam graf. Bez lockfile albo przy resolverze skonfigurowanym na uwzględnianie `rust-version` wybór wersji zależności może się zmienić, więc trzeba go sprawdzić w CI.


Wynik podzieliłbym na trzy dowody: kontrola typów dla właściwego targetu, udane linkowanie oraz uruchomienie na ARM lub odpowiednim środowisku testowym. Jeden zielony etap nie zastępuje następnego. MSRV musi ponadto obsługiwać edition pakietu; dla Edition 2024 minimum narzucone przez edition to 1.85, ale zależności mogą wymagać nowszej wersji.
