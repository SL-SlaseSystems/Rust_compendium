# Oficjalne źródła

[← Spis treści](README.md)

Główne kontrakty i źródła rozbudowy sprawdzono 11 listopada 2026.
Aktualna dokumentacja stable wskazywała Rust 1.99.1; lokalnie dostępne
`rustc`, `cargo` i `rustdoc` miały wersję 1.90.0. Przykłady nowszego API
pozostają opisowe, jeśli nie mogły zostać uruchomione tym toolchainem. Kompendium parafrazuje
źródła i nie zastępuje dokumentacji konkretnego API/toolchainu. W razie
sprzeczności dla semantyki języka preferuj aktualny Rust Reference i
dokumentację konkretnej funkcji.

## Główna półka

- [Rust Documentation](https://doc.rust-lang.org/stable/) — katalog całej
  oficjalnej dokumentacji stable.
- [The Rust Programming Language](https://doc.rust-lang.org/stable/book/) —
  nauka od podstaw; Edition 2024, ownership, typy, współbieżność i async.
- [Rust By Example](https://doc.rust-lang.org/stable/rust-by-example/) —
  krótkie, uruchamialne przykłady składni.
- [Rust Reference](https://doc.rust-lang.org/stable/reference/) — szczegółowa
  składnia i semantyka języka; nie jest formalną specyfikacją.
- [Standard Library API](https://doc.rust-lang.org/stable/std/) — kontrakty,
  safety requirements i stabilność typów oraz funkcji.
- [Rust release announcements](https://blog.rust-lang.org/releases/) —
  oficjalna lista wydań. Na dzień weryfikacji najnowsza wersja stable to
  Rust 1.99.1, potwierdzona w [release notes](https://doc.rust-lang.org/stable/releases.html).

## Narzędzia

- [The Cargo Book](https://doc.rust-lang.org/stable/cargo/) — manifesty,
  pakiety, workspaces, features, profile, build scripts i publikowanie.
- [The rustc Book](https://doc.rust-lang.org/stable/rustc/) — kompilator,
  targety, linty i opcje codegen.
- [The rustdoc Book](https://doc.rust-lang.org/stable/rustdoc/) —
  dokumentacja, doctests i konfiguracja generowania.
- [The Clippy Book](https://doc.rust-lang.org/stable/clippy/) — linty,
  konfiguracja i rozwijanie Clippy.
- [The rustup Book](https://rust-lang.github.io/rustup/) — kanały, toolchainy,
  komponenty, targety i overrides.
- [Rust Style Guide](https://doc.rust-lang.org/stable/style-guide/) —
  styl realizowany głównie przez rustfmt.

## Editions i ewolucja

- [Rust Edition Guide](https://doc.rust-lang.org/stable/edition-guide/) —
  różnice editions i migracja, szczególnie Edition 2024.
- [The Rust RFC Book](https://rust-lang.github.io/rfcs/) — zaakceptowane
  projekty zmian; RFC nie zawsze opisuje końcową implementację.
- [The Unstable Book](https://doc.rust-lang.org/nightly/unstable-book/) —
  niepełny katalog feature gates nightly. Zawsze sprawdzaj też tracking issue
  oraz bieżący kompilator.
- [Rust Blog](https://blog.rust-lang.org/) i
  [Inside Rust Blog](https://blog.rust-lang.org/inside-rust/) — wydania,
  plany i aktualizacje zespołów. Plany nie są gwarancją terminu.

## Unsafe, pamięć i kompilator

- [The Rustonomicon](https://doc.rust-lang.org/stable/nomicon/) — unsafe,
  variance, FFI, atomiki i low-level. Sam dokument ostrzega, że jest niepełny;
  przy rozbieżności preferuj Reference.
- [Behavior considered undefined](https://doc.rust-lang.org/stable/reference/behavior-considered-undefined.html) —
  oficjalna, jawnie niewyczerpująca lista UB i granice obecnej specyfikacji.
- [`std::ptr` i provenance](https://doc.rust-lang.org/stable/std/ptr/) —
  validity pointerów, Strict oraz Exposed Provenance.
- [Rust Compiler Development Guide](https://rustc-dev-guide.rust-lang.org/) —
  HIR, MIR, type checking, borrow checking, codegen i praca nad rustc.
- [Polonius Book: current status](https://rust-lang.github.io/polonius/current_status.html) —
  eksperymentalny następca części analizy borrow i flaga `-Zpolonius`.

## Async i współbieżność

- [Async Book](https://rust-lang.github.io/async-book/) — futures,
  executory, pinning, wake i typowe wzorce; status poszczególnych API runtime’u
  sprawdzaj osobno.
- [`std::future::Future`](https://doc.rust-lang.org/stable/std/future/trait.Future.html) —
  normatywny kontrakt `poll`.
- [`std::task`](https://doc.rust-lang.org/stable/std/task/) — `Context`,
  `Poll`, `Waker` i `RawWaker`.
- [`std::sync::atomic::Ordering`](https://doc.rust-lang.org/stable/std/sync/atomic/enum.Ordering.html) —
  oficjalny opis memory orderings.

## API, embedded i WebAssembly

- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/) —
  konwencje projektowania publicznych bibliotek; traktuj jako wytyczne, nie
  składnię języka.
- [The Embedded Rust Book](https://docs.rust-embedded.org/book/) —
  bare metal, toolchain, urządzenia i wzorce embedded.
- [Rust and WebAssembly Book](https://rustwasm.github.io/docs/book/) —
  integracja Rust/Wasm; część narzędzi należy do ekosystemu.
- [Platform Support](https://doc.rust-lang.org/stable/rustc/platform-support.html) —
  poziomy wsparcia targetów i wymagania platform.

## Ekosystem i materiały produkcyjne

Poniższe źródła są dokumentacją ich autorów, a nie częścią standardowej biblioteki Rusta. Zmienność wersji zależności i wymagań platformowych wymaga osobnego sprawdzania. Szkic oznaczony `text` w kompendium nie jest deklaracją wykonania tej integracji.

- [Tokio](https://docs.rs/tokio/latest/tokio/) i [graceful shutdown](https://tokio.rs/tokio/topics/shutdown) — taski, synchronizacja, anulowanie i kończenie pracy.
- [axum](https://docs.rs/axum/latest/axum/) — warstwa HTTP i stan aplikacji.
- [SQLx](https://docs.rs/sqlx/latest/sqlx/) — sterowniki, pule, transakcje i migracje.
- [Serde](https://serde.rs/) — serializacja oraz mapowanie formatu na model.
- [Proptest Book](https://proptest-rs.github.io/proptest/intro.html) i [Rust Fuzz Book](https://rust-fuzz.github.io/book/cargo-fuzz.html) — strategie, shrinking, harness i odtwarzanie awarii.
- [Miri](https://github.com/rust-lang/miri), [Loom](https://docs.rs/loom/latest/loom/) i [sanitizery rustc](https://doc.rust-lang.org/unstable-book/compiler-flags/sanitizer.html) — zakres narzędzi, wymagania i ograniczenia interpretacji wyników.
- [RustSec](https://rustsec.org/) i [cargo-deny](https://embarkstudios.github.io/cargo-deny/) — advisory i polityki zależności.
- [tracing](https://docs.rs/tracing/latest/tracing/) i [OpenTelemetry](https://opentelemetry.io/docs/concepts/signals/) — eventy, spany oraz sygnały telemetryczne.
- [Google SRE: Service Level Objectives](https://sre.google/sre-book/service-level-objectives/) — definicje SLI/SLO oraz interpretacja celu usługi.
- [cargo-bisect-rustc](https://rust-lang.github.io/cargo-bisect-rustc/) — odtwarzalne wyszukiwanie regresji kompilatora.
- [wasm-bindgen](https://docs.rs/wasm-bindgen/latest/wasm_bindgen/) — wiązania JavaScript; osobno sprawdzaj [kontrakt targetu Wasm](https://doc.rust-lang.org/rustc/platform-support/wasm32-unknown-unknown.html) i [WASIp1](https://doc.rust-lang.org/rustc/platform-support/wasm32-wasip1.html).

## Co potwierdza weryfikacja

`rustdoc` uruchamia samowystarczalne bloki `rust` i potwierdza odrzucenie `compile_fail`; nie sprawdza sam z siebie konkretnego kodu błędu, jeśli nie został dodatkowo zweryfikowany. Kod zależny od third-party, urządzenia, obcej biblioteki, nowszego stable lub nightly wymaga opisanego środowiska. Przejście lokalnych doctestów nie stanowi testu bazy, serwera HTTP, przeglądarki ani embedded.

## Jak weryfikować twierdzenie

1. Znajdź element w aktualnej dokumentacji stable.
2. Sprawdź badge `since` i availability na targetach.
3. Dla składni przeczytaj odpowiedni rozdział Reference.
4. Dla `unsafe` przeczytaj sekcję `Safety` konkretnej funkcji.
5. Dla nightly sprawdź Unstable Book, tracking issue i przypięty toolchain.
6. Dla planów języka odróżnij zaakceptowany RFC, zaimplementowany feature i
   stabilizację w release notes.

## Powiązane tematy

- [Dalsza nauka](dalsza_nauka.md)
- [`unsafe`, soundness i model pamięci](21_unsafe_soundness_i_model_pamieci/README.md)
- [Testowanie zaawansowane, fuzzing i Miri](26_testowanie_zaawansowane_fuzzing_i_miri/README.md)
- [Bezpieczeństwo aplikacji](27_bezpieczenstwo_aplikacji/README.md)
- [Zasady rozwijania kompendium](CONTRIBUTING.md)
