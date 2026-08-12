# Dalsza nauka i ścieżki specjalizacji

[← Spis treści](README.md)

Najpierw przejdź podstawy wspólne: składnię, ownership, typy, błędy, moduły,
testy i narzędzia. Następnie wybierz ścieżkę. Nazwy crate’ów poniżej opisują
ekosystem **third-party** i szybko się zmieniają — przed decyzją sprawdź
aktualne wydania, maintenance, security advisories i licencję.

## Fundament dla każdego

1. [Wprowadzenie](01_wprowadzenie/01_czym_jest_rust.md)
2. [Podstawy języka](02_podstawy_jezyka/01_zmienne_stale_i_shadowing.md)
3. [Ownership i borrowing](03_pamiec_i_wlasnosc/02_ownership_move_i_copy.md)
4. [Typy, enumy i traits](04_typy_i_modelowanie/01_struktury_enumy_i_metody.md)
5. [Kolekcje i iteratory](05_kolekcje_i_iteratory/01_tablice_wektory_i_sekwencje.md)
6. [Błędy](06_bledy/01_option_i_result.md)
7. [Cargo](07_moduly_i_cargo/02_crates_pakiety_i_workspaces.md)
8. [Testowanie i jakość](08_testowanie_i_jakosc/01_testy_jednostkowe_i_integracyjne.md)

Po każdym dziale napisz małe narzędzie bez kopiowania rozwiązania. Dobre
ćwiczenia: parser konfiguracji, indeks plików, kolejka zadań, klient prostego
protokołu i biblioteka z publicznym API.

## CLI

Kolejność:

1. [Pliki, I/O i procesy](12_systemy_i_interoperacyjnosc/01_pliki_io_i_procesy.md)
2. [Własne błędy](06_bledy/04_wlasne_bledy_i_api.md)
3. [Projektowanie API](13_wzorce_i_architektura/03_projektowanie_api_i_semver.md)
4. [Wydajność](13_wzorce_i_architektura/05_wydajnosc_i_zero_cost.md)

Ekosystem do oceny: clap (argumenty), serde plus format konfiguracji, tracing
(diagnostyka), anyhow/miette (raportowanie w aplikacji). Naucz się exit codes,
stdout kontra stderr, sygnałów, ścieżek nie-UTF-8 i testowania procesu.

Projekt: rekursywny analizator katalogu z filtrowaniem, formatem JSON i testami
na katalogu tymczasowym.

## Backend i usługi

Kolejność:

1. [Async](10_async/01_future_async_i_await.md)
2. [Anulowanie i timeouty](10_async/04_anulowanie_timeouty_i_blocking.md)
3. [Sieć i protokoły](12_systemy_i_interoperacyjnosc/02_siec_i_protokoly.md)
4. [Architektura i DI](13_wzorce_i_architektura/04_architektura_aplikacji_i_di.md)
5. [Współbieżność](09_wspolbieznosc/03_arc_mutex_rwlock_i_condvar.md)

Ekosystem do oceny: Tokio jako runtime, axum/actix-web jako HTTP, tower jako
middleware, sqlx/diesel jako dane, serde jako serializacja, tracing jako
observability.

Ćwicz deadline propagation, bounded concurrency, graceful shutdown,
idempotency, migracje, pooling i backpressure. Projekt: API kolejki zadań z
limitem współbieżności, bazą danych i testem shutdown.

## Biblioteki

Kolejność:

1. [Moduły i widoczność](07_moduly_i_cargo/01_moduly_sciezki_i_widocznosc.md)
2. [Projektowanie API i SemVer](13_wzorce_i_architektura/03_projektowanie_api_i_semver.md)
3. [Testy dokumentacyjne](08_testowanie_i_jakosc/02_testy_dokumentacyjne_i_rustdoc.md)
4. [Crates.io i profile](07_moduly_i_cargo/04_profile_build_scripts_i_publikowanie.md)
5. [Idiomy i extension traits](13_wzorce_i_architektura/01_idiomy_newtype_i_extension_traits.md)

Przeczytaj Rust API Guidelines. Ustal MSRV, feature matrix i publiczne
invariants. Projekt: mały parser z pożyczonym wejściem, własnym typem błędu,
doctestami i fuzz targetem.

## Programowanie systemowe

Kolejność:

1. [Pamięć i smart pointery](03_pamiec_i_wlasnosc/06_smart_pointery_i_interior_mutability.md)
2. [Wątki, kanały i atomiki](09_wspolbieznosc/01_watki_i_scoped_threads.md)
3. [FFI i ABI](12_systemy_i_interoperacyjnosc/03_ffi_abi_i_repr.md)
4. [Cały dział zaawansowany](zaawansowane/README.md)

Pracuj z Miri i sanitizerami. Najpierw napisz bezpieczną wersję, potem profil.
Projekt: safe wrapper na małe C API z testami null, błędów, callbacku,
ownership i wielowątkowości.

## Embedded

Kolejność:

1. [WebAssembly, `no_std` i embedded](12_systemy_i_interoperacyjnosc/04_wasm_no_std_i_embedded.md)
2. [`no_std`, allocatory i embedded — zaawansowane](zaawansowane/12_no_std_allocatory_i_embedded.md)
3. [Atomiki](zaawansowane/08_atomics_i_memory_ordering.md)
4. [Pinning](zaawansowane/07_pin_unpin_i_self_referential.md)

Następnie Embedded Rust Book, discovery book dla płytki, embedded-hal oraz
dokumentacja PAC/HAL. Projekt: sterownik czujnika oparty na traitach,
testowany fake’em na hoście, z nieblokującą state machine.

## WebAssembly

Kolejność:

1. [WebAssembly](12_systemy_i_interoperacyjnosc/04_wasm_no_std_i_embedded.md)
2. [FFI i ABI](12_systemy_i_interoperacyjnosc/03_ffi_abi_i_repr.md)
3. [Wydajność](13_wzorce_i_architektura/05_wydajnosc_i_zero_cost.md)

Przeglądaj wasm-bindgen guide, WASI i dokumentację runtime’u. Mierz rozmiar
modułu, kopiowanie przez granicę JS/Wasm i startup. Projekt: parser
uruchamiany w przeglądarce, który przekazuje duże bufory w kilku operacjach,
a nie bajt po bajcie.

## Kompilator i język

Kolejność:

1. [Makra proceduralne](11_makra/03_makra_proceduralne.md)
2. [MIR i LLVM](zaawansowane/13_monomorfizacja_mir_llvm_i_optymalizacja.md)
3. [Borrow checker i Polonius](zaawansowane/14_borrow_checker_polonius_i_model_pamieci.md)
4. [Nightly i feature gates](zaawansowane/15_nightly_unstable_i_feature_gates.md)

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
