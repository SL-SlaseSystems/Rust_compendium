[← Spis treści](../../README.md)

# Rozwiązania: Zależności, features i `cfg`

[Rozdział źródłowy](../../08_moduly_cargo_i_workspaces/03_zaleznosci_features_i_cfg.md).

## B07-1

~~~rust
#[cfg(debug_assertions)] fn tryb()->&'static str{"kontrola"}
#[cfg(not(debug_assertions))] fn tryb()->&'static str{"optymalizacja"}
fn main(){assert!(!tryb().is_empty());}
~~~
`debug_assertions` opisuje konfigurację kompilacji; nie należy z niego wywodzić uprawnień bezpieczeństwa.

## B07-2

To manifest z zależnością **third-party**, wymagający pakietu Cargo i nietestowany jako doctest.

~~~text
[features]
default = []
json = ["dep:serde_json"]
[dependencies]
serde_json = { version = "1", optional = true }
~~~
Kod funkcji korzystających z crate’a obejmij `#[cfg(feature = "json")]`. Nazwa zależności nie musi stać się publicznym feature.

## B07-3

Jeżeli aplikacja żąda `codec` bez defaultów, a adapter żąda `codec` z defaultami, wynik obejmuje domyślne features wymagane przez adapter. `--no-default-features` aplikacji nie odwraca żądania adaptera. Sprawdź `cargo tree -e features -i codec`, zmień deklarację adaptera, jeśli jego kontrakt pozwala, i testuj minimum oraz domyślne/all zgodne konfiguracje. W CI dodaj build konsumenta z samym minimalnym API; to wykrywa ukryte zależności od feature włączanego wyłącznie przez testy.

