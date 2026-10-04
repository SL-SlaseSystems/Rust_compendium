# Oficjalne źródła

[← Spis treści](README.md)

Stan linków i wersji sprawdzono 12 sierpnia 2026. Kompendium parafrazuje
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
  Rust 1.97.1.

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
