# Raport działów 24–30

Zakres: 14 nowych opracowań i 14 plików rozwiązań, 42 ćwiczenia, aktualizacja siedmiu map działów i siedmiu indeksów rozwiązań.

## Materiał

- 24: host/guest, pamięć i ABI, przeglądarka/WASI, rdzeń przenośny, cfg i testy targetów.
- 25: redukcja problemu, backtrace, debugger, regresje, kompatybilne migracje i incydenty.
- 26: niezależne właściwości, shrinking, harness i korpus, Miri, sanitizery i małe modele Loom.
- 27: model zagrożeń, walidacja przed alokacją, limity, autoryzacja, sekrety i zależności.
- 28: CI, doctesty, MSRV/features/targety, cache, artefakty, provenance, zgodność danych i rollback.
- 29: eventy/spany/metryki/traces, cardinality, SLI/SLO, alerty i wielofazowy shutdown.
- 30: siedem kompletnych specyfikacji projektów oraz wykonywalny rdzeń parsera konfiguracji z kontraktem błędów, limitów i własności.

Każdy rozdział ma cele, model, samowystarczalny przykład std, diagnostykę, praktykę, pytania oraz trzy ćwiczenia z rozwiązaniami. Poziom: około 735–1050 słów na opracowanie, bez rozwiązań.

## Weryfikacja

14 plików rozdziałów przeszło rustdoc --test --edition 2024 lokalnym Rust 1.90.0 z SDKROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk. Po wykryciu wymogu regex zmieniono zapis `Model:` na `Model —`; zmiana jest redakcyjna. Źródła: dokumentacja Rust, Cargo, Tokio, tracing, wasm-bindgen, Proptest, Rust Fuzz Book, Miri, Loom, RustSec, OpenTelemetry i Google SRE; konkretne odnośniki znajdują się w rozdziałach.

Szkice integracji third-party, uruchomienia Wasm/embedded, Miri, Loom, sanitizerów, systemu alertowania i wdrożenia nie zostały uruchomione lokalnie. Kod std nie jest deklaracją przetestowania tych środowisk.
