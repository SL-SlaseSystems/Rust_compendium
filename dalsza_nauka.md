# Dalsza nauka i ścieżki specjalizacji

[← Spis treści](README.md)

Najpierw przejdź podstawy wspólne: składnię, ownership, typy, błędy, moduły,
testy i narzędzia. Następnie wybierz ścieżkę. Nazwy crate’ów poniżej opisują
ekosystem **third-party** i szybko się zmieniają — przed decyzją sprawdź
aktualne wydania, maintenance, security advisories i licencję.

## Fundament dla każdego

1. [Wprowadzenie](01_wprowadzenie_i_toolchain/01_czym_jest_rust.md)
2. [Podstawy języka](02_podstawy_jezyka/01_zmienne_stale_i_shadowing.md)
3. [Ownership i borrowing](03_ownership_i_pamiec/02_ownership_move_i_copy.md)
4. [Typy, enumy i traits](04_struktury_enumy_i_wzorce/01_struktury_enumy_i_metody.md)
5. [Kolekcje i iteratory](06_kolekcje_iteratory_i_closures/01_tablice_wektory_i_sekwencje.md)
6. [Błędy](07_obsluga_bledow/01_option_i_result.md)
7. [Cargo](08_moduly_cargo_i_workspaces/02_crates_pakiety_i_workspaces.md)
8. [Testowanie i jakość](09_dokumentacja_testowanie_i_jakosc/01_testy_jednostkowe_i_integracyjne.md)

Po każdym dziale napisz małe narzędzie bez kopiowania rozwiązania. Dobre
ćwiczenia: parser konfiguracji, indeks plików, kolejka zadań, klient prostego
protokołu i biblioteka z publicznym API.

## CLI

Kolejność:

1. [Mapa aplikacji CLI](15_aplikacje_cli/README.md)
2. [Pliki, I/O i procesy](13_io_siec_i_protokoly/01_pliki_io_i_procesy.md)
3. [Własne błędy](07_obsluga_bledow/04_wlasne_bledy_i_api.md)
4. [Projektowanie API](14_idiomy_wzorce_i_architektura/03_projektowanie_api_i_semver.md)

Ekosystem do oceny: clap (argumenty), serde plus format konfiguracji, tracing
(diagnostyka), anyhow/miette (raportowanie w aplikacji). Naucz się exit codes,
stdout kontra stderr, sygnałów, ścieżek nie-UTF-8 i testowania procesu.

Projekt: rekursywny analizator katalogu z filtrowaniem, formatem JSON i testami
na katalogu tymczasowym.

## Backend i usługi

Kolejność:

1. [Mapa web i API](16_web_i_api/README.md)
2. [Async](11_async_rust/01_future_async_i_await.md)
3. [Bazy danych i persystencja](17_bazy_danych_i_persystencja/README.md)
4. [Serializacja, konfiguracja i integracje](18_serializacja_konfiguracja_i_integracje/README.md)
5. [Observability i produkcja](29_observability_i_produkcja/README.md)

Ekosystem do oceny: Tokio jako runtime, axum/actix-web jako HTTP, tower jako
middleware, sqlx/diesel jako dane, serde jako serializacja, tracing jako
observability.

Ćwicz deadline propagation, bounded concurrency, graceful shutdown,
idempotency, migracje, pooling i backpressure. Projekt: API kolejki zadań z
limitem współbieżności, bazą danych i testem shutdown.

## Biblioteki

Kolejność:

1. [Moduły i widoczność](08_moduly_cargo_i_workspaces/01_moduly_sciezki_i_widocznosc.md)
2. [Projektowanie API i SemVer](14_idiomy_wzorce_i_architektura/03_projektowanie_api_i_semver.md)
3. [Testy dokumentacyjne](09_dokumentacja_testowanie_i_jakosc/02_testy_dokumentacyjne_i_rustdoc.md)
4. [Crates.io i profile](08_moduly_cargo_i_workspaces/04_profile_build_scripts_i_publikowanie.md)
5. [Idiomy i extension traits](14_idiomy_wzorce_i_architektura/01_idiomy_newtype_i_extension_traits.md)

Przeczytaj Rust API Guidelines. Ustal MSRV, feature matrix i publiczne
invariants. Projekt: mały parser z pożyczonym wejściem, własnym typem błędu,
doctestami i fuzz targetem.

## Programowanie systemowe

Kolejność:

1. [Pamięć i smart pointery](03_ownership_i_pamiec/06_smart_pointery_i_interior_mutability.md)
2. [Wątki, kanały i atomiki](10_wspolbieznosc/01_watki_i_scoped_threads.md)
3. [FFI i ABI](22_ffi_i_interoperacyjnosc/01_ffi_abi_i_repr.md)
4. [Ścieżka `unsafe` i modelu pamięci](21_unsafe_soundness_i_model_pamieci/README.md)
5. [Debugowanie i utrzymanie](25_debugowanie_i_utrzymanie/README.md)

Pracuj z Miri i sanitizerami. Najpierw napisz bezpieczną wersję, potem profil.
Projekt: safe wrapper na małe C API z testami null, błędów, callbacku,
ownership i wielowątkowości.

## Embedded

Kolejność:

1. [Mapa `no_std`, allocatorów i embedded](23_no_std_allocatory_i_embedded/README.md)
2. [`no_std`, allocatory i embedded — zaawansowane](23_no_std_allocatory_i_embedded/02_no_std_allocatory_i_embedded.md)
3. [Atomiki](10_wspolbieznosc/05_atomics_i_memory_ordering.md)
4. [Pinning](11_async_rust/05_pin_unpin_i_self_referential.md)

Następnie Embedded Rust Book, discovery book dla płytki, embedded-hal oraz
dokumentacja PAC/HAL. Projekt: sterownik czujnika oparty na traitach,
testowany fake’em na hoście, z nieblokującą state machine.

## WebAssembly

Kolejność:

1. [Mapa WASM i wieloplatformowości](24_wasm_i_wieloplatformowosc/README.md)
2. [FFI i ABI](22_ffi_i_interoperacyjnosc/01_ffi_abi_i_repr.md)
3. [Wydajność](20_wydajnosc_i_optymalizacja/01_wydajnosc_i_zero_cost.md)

Przeglądaj wasm-bindgen guide, WASI i dokumentację runtime’u. Mierz rozmiar
modułu, kopiowanie przez granicę JS/Wasm i startup. Projekt: parser
uruchamiany w przeglądarce, który przekazuje duże bufory w kilku operacjach,
a nie bajt po bajcie.

## Kompilator i język

Kolejność:

1. [Makra proceduralne](12_makra/03_makra_proceduralne.md)
2. [MIR i LLVM](20_wydajnosc_i_optymalizacja/03_monomorfizacja_mir_llvm_i_optymalizacja.md)
3. [Borrow checker i Polonius](19_runtime_pamiec_i_kompilator/01_borrow_checker_polonius_i_model_pamieci.md)
4. [Nightly i feature gates](08_moduly_cargo_i_workspaces/05_nightly_unstable_i_feature_gates.md)

Następnie rustc-dev-guide, rustc contributor guide i RFC Book. Zacznij od
diagnostic issue, lintu lub testu UI, nie od nowej składni języka.

## Praktyka celowa

- odtwarzaj mechanizm w małej wersji, ale produkcyjnie używaj sprawdzonego API;
- czytaj komunikat rustc oraz `rustc --explain`;
- sprawdzaj wygenerowaną dokumentację;
- rób property tests i fuzzing parserów;
- profiluj przed `unsafe` i mikrooptymalizacją;
- czytaj źródła standard library, ale nie zakładaj stabilności ich wnętrza;
- zapisuj dowody `SAFETY` pełnymi zdaniami.

## Powiązane tematy

- [Źródła](zrodla.md)
- [Ściąga](sciaga.md)
- [Słownik](slownik.md)
- [Projekty przekrojowe](30_projekty_przekrojowe/README.md)
