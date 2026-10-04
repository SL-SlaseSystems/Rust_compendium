# Kompendium języka Rust

Polskojęzyczna ścieżka od pierwszego programu do projektowania produkcyjnych systemów w Rust. Materiał jest ułożony według mechanizmów języka i realnych zastosowań: ownership, system typów, async, backend, wydajność, `unsafe`, FFI, embedded, bezpieczeństwo i utrzymanie.

> Przykłady znajdują się bezpośrednio w rozdziałach. Zachowane materiały eksperckie są częścią odpowiednich działów, a nie osobnym dodatkiem bez kontekstu.

## Jak korzystać z kompendium

- **Pełna ścieżka:** przejdź działy 01–14, wybierz zastosowanie z 15–18, pogłęb mechanizmy w 19–29 i zakończ projektem z działu 30.
- **Ścieżka przyspieszona:** po instalacji przejdź przez działy 02–09, następnie 13–14 i od razu wybierz mapę specjalizacji.
- **Powtórka:** użyj [ściągi](sciaga.md), [słownika](slownik.md) i [atlasu 150 mechanizmów](150-zaawansowanych-mechanizmow-rust.md).
- **Nauka praktyczna:** po każdym bloku napisz mały program, uruchom testy i porównaj decyzje z kryteriami projektów przekrojowych.

## Pełna ścieżka 01–30

### Fundamenty języka

1. [Wprowadzenie i toolchain](01_wprowadzenie_i_toolchain/README.md) — instalacja, pierwszy program i codzienna praca z Cargo.
2. [Podstawy języka](02_podstawy_jezyka/README.md) — bindingi, typy, funkcje, wyrażenia i sterowanie przepływem.
3. [Ownership i pamięć](03_ownership_i_pamiec/README.md) — RAII, move, borrowing, lifetimes i smart pointery.
4. [Struktury, enumy i wzorce](04_struktury_enumy_i_wzorce/README.md) — modelowanie danych oraz wyczerpujące dopasowanie.
5. [Generics, traits i system typów](05_generics_traits_i_system_typow/README.md) — abstrakcje statyczne i dynamiczne, HRTB, GAT i vtables.
6. [Kolekcje, iteratory i closures](06_kolekcje_iteratory_i_closures/README.md) — przetwarzanie danych, tekst Unicode i potoki iteratorów.
7. [Obsługa błędów](07_obsluga_bledow/README.md) — `Option`, `Result`, propagacja, paniki i typy błędów.
8. [Moduły, Cargo i workspaces](08_moduly_cargo_i_workspaces/README.md) — granice pakietów, features, profile, publikowanie i nightly.
9. [Dokumentacja, testowanie i jakość](09_dokumentacja_testowanie_i_jakosc/README.md) — testy, rustdoc, Clippy i rustfmt.

### Współbieżność, async i architektura

10. [Współbieżność](10_wspolbieznosc/README.md) — wątki, kanały, blokady, atomiki i lock-free.
11. [Async Rust](11_async_rust/README.md) — futures, executory, taski, anulowanie i `Pin`.
12. [Makra](12_makra/README.md) — `macro_rules!`, higiena oraz makra proceduralne.
13. [I/O, sieć i protokoły](13_io_siec_i_protokoly/README.md) — pliki, procesy, gniazda, bufory i granice protokołów.
14. [Idiomy, wzorce i architektura](14_idiomy_wzorce_i_architektura/README.md) — newtype, typestate, SemVer i podział odpowiedzialności.

### Ścieżki aplikacyjne

15. [Aplikacje CLI](15_aplikacje_cli/README.md) — argumenty, konfiguracja, strumienie, sygnały i dystrybucja.
16. [Web i API](16_web_i_api/README.md) — routing, walidacja, middleware, limity i testy kontraktowe.
17. [Bazy danych i persystencja](17_bazy_danych_i_persystencja/README.md) — repozytoria, transakcje, migracje i testy integracyjne.
18. [Serializacja, konfiguracja i integracje](18_serializacja_konfiguracja_i_integracje/README.md) — formaty danych, sekrety, retry i idempotencja.

### Mechanizmy niskopoziomowe i platformy

19. [Runtime, pamięć i kompilator](19_runtime_pamiec_i_kompilator/README.md) — borrow checker, Polonius i granice modelu języka.
20. [Wydajność i optymalizacja](20_wydajnosc_i_optymalizacja/README.md) — pomiary, profilowanie, monomorfizacja, MIR i LLVM.
21. [`unsafe`, soundness i model pamięci](21_unsafe_soundness_i_model_pamieci/README.md) — invariants, raw pointers, provenance, layout i inicjalizacja.
22. [FFI i interoperacyjność](22_ffi_i_interoperacyjnosc/README.md) — ABI, `repr`, ownership na granicy i bezpieczne otoczki.
23. [`no_std`, allocatory i embedded](23_no_std_allocatory_i_embedded/README.md) — `core`, `alloc`, własne środowisko i ograniczone platformy.
24. [WASM i wieloplatformowość](24_wasm_i_wieloplatformowosc/README.md) — granica host–guest, przenośny rdzeń i testy targetów.

### Produkcja i praktyka

25. [Debugowanie i utrzymanie](25_debugowanie_i_utrzymanie/README.md) — minimalne reprodukcje, debugger, regresje i migracje.
26. [Testowanie zaawansowane, fuzzing i Miri](26_testowanie_zaawansowane_fuzzing_i_miri/README.md) — property tests, fuzzing, sanitizery i modele współbieżności.
27. [Bezpieczeństwo aplikacji](27_bezpieczenstwo_aplikacji/README.md) — model zagrożeń, limity, sekrety i łańcuch zależności.
28. [CI/CD i release engineering](28_ci_cd_i_release_engineering/README.md) — macierze testów, artefakty, wersjonowanie i rollback.
29. [Observability i produkcja](29_observability_i_produkcja/README.md) — logi, metryki, trace'y, SLO i graceful shutdown.
30. [Projekty przekrojowe](30_projekty_przekrojowe/README.md) — siedem projektów łączących język, jakość i eksploatację.

## Ścieżka przyspieszona

Jeżeli znasz już język z typami statycznymi, przejdź w tej kolejności:

1. [Toolchain](01_wprowadzenie_i_toolchain/README.md).
2. [Podstawy składni](02_podstawy_jezyka/README.md).
3. [Ownership i pamięć](03_ownership_i_pamiec/README.md).
4. [Modelowanie danych](04_struktury_enumy_i_wzorce/README.md) oraz [traits](05_generics_traits_i_system_typow/README.md).
5. [Kolekcje](06_kolekcje_iteratory_i_closures/README.md) i [błędy](07_obsluga_bledow/README.md).
6. [Cargo](08_moduly_cargo_i_workspaces/README.md), [testy](09_dokumentacja_testowanie_i_jakosc/README.md) i [architektura](14_idiomy_wzorce_i_architektura/README.md).
7. Wybrana ścieżka specjalistyczna i jeden [projekt przekrojowy](30_projekty_przekrojowe/README.md).

## Ścieżki specjalistyczne

### Backend i usługi

[Async Rust](11_async_rust/README.md) → [I/O i sieć](13_io_siec_i_protokoly/README.md) → [web/API](16_web_i_api/README.md) → [bazy danych](17_bazy_danych_i_persystencja/README.md) → [integracje](18_serializacja_konfiguracja_i_integracje/README.md) → [observability](29_observability_i_produkcja/README.md).

### Systems i embedded

[Współbieżność](10_wspolbieznosc/README.md) → [runtime i pamięć](19_runtime_pamiec_i_kompilator/README.md) → [`unsafe`](21_unsafe_soundness_i_model_pamieci/README.md) → [FFI](22_ffi_i_interoperacyjnosc/README.md) → [`no_std` i embedded](23_no_std_allocatory_i_embedded/README.md).

### Wydajność

[Iteratory](06_kolekcje_iteratory_i_closures/README.md) → [współbieżność](10_wspolbieznosc/README.md) → [wydajność i optymalizacja](20_wydajnosc_i_optymalizacja/README.md) → [testowanie zaawansowane](26_testowanie_zaawansowane_fuzzing_i_miri/README.md) → [produkcja](29_observability_i_produkcja/README.md).

### Bezpieczeństwo

[Obsługa błędów](07_obsluga_bledow/README.md) → [testowanie i jakość](09_dokumentacja_testowanie_i_jakosc/README.md) → [`unsafe` i soundness](21_unsafe_soundness_i_model_pamieci/README.md) → [fuzzing i Miri](26_testowanie_zaawansowane_fuzzing_i_miri/README.md) → [bezpieczeństwo aplikacji](27_bezpieczenstwo_aplikacji/README.md) → [release engineering](28_ci_cd_i_release_engineering/README.md).

## Legenda przykładów

- `rust` — samowystarczalny przykład sprawdzany przez `rustdoc`;
- `compile_fail` — przykład celowo odrzucany przez kompilator;
- `text` — szkic, manifest albo kod zależny od zewnętrznego środowiska;
- **nightly** — funkcjonalność niestabilna i jawnie oznaczona;
- **third-party** — API spoza języka i biblioteki standardowej.

## Materiały przekrojowe

- [Atlas 150 zaawansowanych mechanizmów Rust](150-zaawansowanych-mechanizmow-rust.md)
- [Ściąga](sciaga.md)
- [Słownik](slownik.md)
- [Dalsza nauka i specjalizacje](dalsza_nauka.md)
- [Oficjalne źródła](zrodla.md)
- [Zasady rozwijania kompendium](CONTRIBUTING.md)

## Weryfikacja

Pełna kontrola linków, struktury, manifestu migracji oraz wykonywalnych przykładów:

~~~text
bash scripts/verify.sh
~~~

Same testy walidatora treści:

~~~text
python3 -m unittest scripts/test_verify_content.py -v
~~~

Skrypt wypisuje używaną wersję `rustdoc`. Część materiałów oznaczonych jako **third-party**, narzędziowych lub wymagających konkretnej platformy pozostaje przykładem opisowym.
