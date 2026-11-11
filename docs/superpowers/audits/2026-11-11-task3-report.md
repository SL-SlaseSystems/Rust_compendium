# Task 3 — zastosowania i mechanizmy 15–23

Data wykonania i weryfikacji źródeł: 2026-11-11. Zakres z planu wykonano w całości; na prośbę integratora dodano także kanoniczny rozdział o CTFE, SIMD, asm, algebraic float i NumBuffer.

## Wykonany zakres

- 8 nowych rozdziałów w działach 15–18: po dwa opracowania pokrywające wszystkie cztery zapowiedziane punkty każdej mapy.
- 11 istniejących rozdziałów 19–23 pogłębiono w zachowanych ścieżkach, z zachowaniem dotychczasowych wyjaśnień i przykładów poza wskazanymi niżej korektami merytorycznymi.
- 1 dodatkowy rozdział `20_wydajnosc_i_optymalizacja/04_const_eval_simd_i_asm.md` podłączył brakujące mechanizmy atlasu do pełnego opracowania.
- Łącznie 20 rozdziałów ze statusem expanded, 60 globalnie unikalnych ćwiczeń C01-1…C20-3 i 20 równoległych plików pełnych rozwiązań. Każdy rozdział ma cele, model, przykład, diagnostykę, praktykę produkcyjną, pytania i trzy zadania. Rozwiązania zaczynają się od backlinku do `../../README.md`.
- Zaktualizowano mapy `README.md` we wszystkich dziewięciu działach 15–23; w mapie 18 poprawiono także zastaną literówkę „Serdeczne opanowanie” na „Dobra znajomość”.

## Pliki rozdziałów i rozwiązań

Ścieżki są względne wobec katalogu projektu. Każdy wymieniony plik rozdziału ma odpowiadający mu plik pod prefiksem `rozwiazania/`, pokazany w ostatniej kolumnie.

| Rozdział | Słowa | Ćwiczenia | Rozwiązania |
|---|---:|---|---|
| `15_aplikacje_cli/01_komendy_argumenty_i_konfiguracja.md` | 893 | C01-1–C01-3 | `rozwiazania/15_aplikacje_cli/01_komendy_argumenty_i_konfiguracja.md` |
| `15_aplikacje_cli/02_strumienie_sygnaly_testy_i_dystrybucja.md` | 807 | C02-1–C02-3 | `rozwiazania/15_aplikacje_cli/02_strumienie_sygnaly_testy_i_dystrybucja.md` |
| `16_web_i_api/01_http_routing_stan_i_bledy.md` | 811 | C03-1–C03-3 | `rozwiazania/16_web_i_api/01_http_routing_stan_i_bledy.md` |
| `16_web_i_api/02_middleware_limity_testy_i_shutdown.md` | 865 | C04-1–C04-3 | `rozwiazania/16_web_i_api/02_middleware_limity_testy_i_shutdown.md` |
| `17_bazy_danych_i_persystencja/01_repozytoria_pule_i_transakcje.md` | 880 | C05-1–C05-3 | `rozwiazania/17_bazy_danych_i_persystencja/01_repozytoria_pule_i_transakcje.md` |
| `17_bazy_danych_i_persystencja/02_migracje_testy_i_odtwarzanie.md` | 920 | C06-1–C06-3 | `rozwiazania/17_bazy_danych_i_persystencja/02_migracje_testy_i_odtwarzanie.md` |
| `18_serializacja_konfiguracja_i_integracje/01_formaty_serializacja_i_walidacja.md` | 858 | C07-1–C07-3 | `rozwiazania/18_serializacja_konfiguracja_i_integracje/01_formaty_serializacja_i_walidacja.md` |
| `18_serializacja_konfiguracja_i_integracje/02_konfiguracja_sekrety_i_odpornosc_integracji.md` | 903 | C08-1–C08-3 | `rozwiazania/18_serializacja_konfiguracja_i_integracje/02_konfiguracja_sekrety_i_odpornosc_integracji.md` |
| `19_runtime_pamiec_i_kompilator/01_borrow_checker_polonius_i_model_pamieci.md` | 1088 | C09-1–C09-3 | `rozwiazania/19_runtime_pamiec_i_kompilator/01_borrow_checker_polonius_i_model_pamieci.md` |
| `20_wydajnosc_i_optymalizacja/01_wydajnosc_i_zero_cost.md` | 978 | C10-1–C10-3 | `rozwiazania/20_wydajnosc_i_optymalizacja/01_wydajnosc_i_zero_cost.md` |
| `20_wydajnosc_i_optymalizacja/02_benchmarki_profilowanie_i_miri.md` | 994 | C11-1–C11-3 | `rozwiazania/20_wydajnosc_i_optymalizacja/02_benchmarki_profilowanie_i_miri.md` |
| `20_wydajnosc_i_optymalizacja/03_monomorfizacja_mir_llvm_i_optymalizacja.md` | 1116 | C12-1–C12-3 | `rozwiazania/20_wydajnosc_i_optymalizacja/03_monomorfizacja_mir_llvm_i_optymalizacja.md` |
| `20_wydajnosc_i_optymalizacja/04_const_eval_simd_i_asm.md` | 1008 | C20-1–C20-3 | `rozwiazania/20_wydajnosc_i_optymalizacja/04_const_eval_simd_i_asm.md` |
| `21_unsafe_soundness_i_model_pamieci/01_unsafe_i_soundness.md` | 1086 | C13-1–C13-3 | `rozwiazania/21_unsafe_soundness_i_model_pamieci/01_unsafe_i_soundness.md` |
| `21_unsafe_soundness_i_model_pamieci/02_raw_pointers_aliasing_i_provenance.md` | 1134 | C14-1–C14-3 | `rozwiazania/21_unsafe_soundness_i_model_pamieci/02_raw_pointers_aliasing_i_provenance.md` |
| `21_unsafe_soundness_i_model_pamieci/03_layout_alignment_i_uninitialized_memory.md` | 1081 | C15-1–C15-3 | `rozwiazania/21_unsafe_soundness_i_model_pamieci/03_layout_alignment_i_uninitialized_memory.md` |
| `22_ffi_i_interoperacyjnosc/01_ffi_abi_i_repr.md` | 1086 | C16-1–C16-3 | `rozwiazania/22_ffi_i_interoperacyjnosc/01_ffi_abi_i_repr.md` |
| `22_ffi_i_interoperacyjnosc/02_ffi_safe_wrappers_i_ub.md` | 1268 | C17-1–C17-3 | `rozwiazania/22_ffi_i_interoperacyjnosc/02_ffi_safe_wrappers_i_ub.md` |
| `23_no_std_allocatory_i_embedded/01_wasm_no_std_i_embedded.md` | 1076 | C18-1–C18-3 | `rozwiazania/23_no_std_allocatory_i_embedded/01_wasm_no_std_i_embedded.md` |
| `23_no_std_allocatory_i_embedded/02_no_std_allocatory_i_embedded.md` | 1132 | C19-1–C19-3 | `rozwiazania/23_no_std_allocatory_i_embedded/02_no_std_allocatory_i_embedded.md` |

Oprócz powyższych czterdziestu plików zmieniono dziewięć map działów: `15_aplikacje_cli/README.md`, `16_web_i_api/README.md`, `17_bazy_danych_i_persystencja/README.md`, `18_serializacja_konfiguracja_i_integracje/README.md`, `19_runtime_pamiec_i_kompilator/README.md`, `20_wydajnosc_i_optymalizacja/README.md`, `21_unsafe_soundness_i_model_pamieci/README.md`, `22_ffi_i_interoperacyjnosc/README.md` oraz `23_no_std_allocatory_i_embedded/README.md`. Raport jest pięćdziesiątym plikiem zakresu. Nie edytowano wspólnego `zrodla.md`, głównego README, atlasu ani metadanych Git.

## Istotne decyzje i korekty

CLI oddziela silnik od procesu, zachowuje nie-UTF-8 ścieżki, kontroluje krótkie zapisy i opisuje ograniczenia read_until, sygnałów oraz testów potoków. Web zawiera konkretne szkice axum/Tower, walidator niezależny od frameworka, ograniczone kolejki, timeouty i shutdown. Bazy mają warunkowy UPDATE, mapowanie typów przez TryFrom, granicę transakcji, nieznany wynik commit, migrację expand–contract, testy izolowane i odtworzenie względem RPO/RTO. Serializacja odróżnia DTO od domeny, zgodność czytelnika i nadawcy, ma ograniczony parser ramki oraz protokoły retry i idempotencji.

W unsafe zachowano odróżnienie statycznego borrow checkingu od runtime validity i nieustalonej części modelu aliasingu. Doprecyzowano, że unsafe impl jest zaufaną deklaracją, a nie operacją wymagającą otaczającego bloku; lint Edition 2024 domyślnie ostrzega, nie jest bezwarunkowym błędem. Dowody obejmują puste zakresy, ZST, ownership, inicjalizację, panic i Drop. Początkowe tworzenie tablicy MaybeUninit zastąpiono bezpiecznym inline const. Dodano slot z jawną flagą inicjalizacji i poprawnym rozliczeniem odczytu oraz destrukcji.

W FFI usunięto niepoprawny wzorzec `safe fn abs`: minimalna liczba ze znakiem nie ma reprezentowalnego dodatniego wyniku w kontrakcie C. Eksport sumy ma jawną politykę wrapping zamiast potencjalnej panic na overflow. Doprecyzowano wymagania bool i zagnieżdżonego repr oraz transfer własności CString. Symulacja bufora FFI nie ustawia len przed inicjalizacją. Callbacki i DMA uwzględniają także bezpieczne mem::forget: soundness nie może zależeć od obowiązkowego Drop guarda pożyczającego pamięć ze stosu.

Rozdział dodatkowy rozdziela testowane na 1.90 const fn, inline const i const assertions od portable SIMD nightly, targetowego asm i nowych API 1.98. Algebraic float nie są przedstawione jako deterministyczny zamiennik zwykłych operatorów ani jako przesłanka soundness.

## Źródła pierwotne

Pełne odsyłacze i daty podano obok twierdzeń w rozdziałach. Najważniejsze sprawdzone źródła:

- [ExitCode](https://doc.rust-lang.org/std/process/struct.ExitCode.html), [set_var](https://doc.rust-lang.org/std/env/fn.set_var.html), [Write](https://doc.rust-lang.org/std/io/trait.Write.html), [BufWriter](https://doc.rust-lang.org/std/io/struct.BufWriter.html).
- [axum 0.8](https://docs.rs/axum/0.8.7/axum/), [ekstraktory axum 0.8.9](https://docs.rs/axum/latest/axum/extract/), [graceful shutdown](https://docs.rs/axum/latest/axum/serve/struct.Serve.html), [tower-http timeout](https://docs.rs/tower-http/latest/tower_http/timeout/index.html), [ServiceExt](https://docs.rs/tower/latest/tower/util/trait.ServiceExt.html).
- [SQLx 0.8.6 Pool](https://docs.rs/sqlx/0.8.6/sqlx/struct.Pool.html), [Transaction](https://docs.rs/sqlx/0.8.6/sqlx/struct.Transaction.html), [query!](https://docs.rs/sqlx/0.8.6/sqlx/macro.query.html), [test](https://docs.rs/sqlx/0.8.6/sqlx/attr.test.html), [izolacja PostgreSQL](https://www.postgresql.org/docs/current/transaction-iso.html), [zmiany tabel](https://www.postgresql.org/docs/current/ddl-alter.html).
- [Serde data model](https://serde.rs/data-model.html), [field attributes](https://serde.rs/field-attrs.html), [container attributes](https://serde.rs/container-attrs.html), [enum representations](https://serde.rs/enum-representations.html), [RFC 9110 idempotency](https://www.rfc-editor.org/rfc/rfc9110.html#name-idempotent-methods).
- [Two-phase borrows](https://rustc-dev-guide.rust-lang.org/borrow-check/two-phase-borrows.html), [status Poloniusa](https://rust-lang.github.io/polonius/current_status.html), [compiler overview](https://rustc-dev-guide.rust-lang.org/overview.html), [monomorphization](https://rustc-dev-guide.rust-lang.org/backend/monomorph.html), [Cargo profiles](https://doc.rust-lang.org/cargo/reference/profiles.html), [PGO](https://doc.rust-lang.org/rustc/profile-guided-optimization.html), [Miri](https://github.com/rust-lang/miri), [sanitizers](https://doc.rust-lang.org/unstable-book/compiler-flags/sanitizer.html), [black_box](https://doc.rust-lang.org/std/hint/fn.black_box.html).
- [Reference UB](https://doc.rust-lang.org/reference/behavior-considered-undefined.html), [ptr](https://doc.rust-lang.org/std/ptr/index.html), [from_raw_parts_mut](https://doc.rust-lang.org/std/slice/fn.from_raw_parts_mut.html), [MaybeUninit](https://doc.rust-lang.org/std/mem/union.MaybeUninit.html), [ManuallyDrop](https://doc.rust-lang.org/std/mem/struct.ManuallyDrop.html), [read](https://doc.rust-lang.org/std/ptr/fn.read.html), [read_unaligned](https://doc.rust-lang.org/std/ptr/fn.read_unaligned.html), [forget](https://doc.rust-lang.org/std/mem/fn.forget.html), [layout](https://doc.rust-lang.org/reference/type-layout.html), [unsafe-op lint](https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-op-in-unsafe-fn.html).
- [External blocks](https://doc.rust-lang.org/reference/items/external-blocks.html), [CString](https://doc.rust-lang.org/std/ffi/struct.CString.html), [Rustonomicon FFI](https://doc.rust-lang.org/nomicon/ffi.html), [C11 draft N1570 §7.22.6.1](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf#page=374).
- [Embedded no_std](https://docs.rust-embedded.org/book/intro/no-std.html), [embedded concurrency](https://docs.rust-embedded.org/book/concurrency/), [embedded-hal 1.0](https://docs.rs/embedded-hal/1.0.0/embedded_hal/), [alloc](https://doc.rust-lang.org/alloc/index.html), [GlobalAlloc](https://doc.rust-lang.org/std/alloc/trait.GlobalAlloc.html), [Layout](https://doc.rust-lang.org/core/alloc/struct.Layout.html), [target_has_atomic](https://doc.rust-lang.org/reference/conditional-compilation.html#target_has_atomic), [read_volatile](https://doc.rust-lang.org/std/ptr/fn.read_volatile.html), [wasm target](https://doc.rust-lang.org/rustc/platform-support/wasm32-unknown-unknown.html).
- [CTFE](https://doc.rust-lang.org/reference/const_eval.html), [const blocks](https://doc.rust-lang.org/reference/expressions/block-expr.html#const-blocks), [inline assembly](https://doc.rust-lang.org/reference/inline-assembly.html), [portable SIMD](https://doc.rust-lang.org/std/simd/index.html), [f32 algebraic](https://doc.rust-lang.org/std/primitive.f32.html#algebraic-operators), [NumBuffer](https://doc.rust-lang.org/std/fmt/struct.NumBuffer.html), [u64::format_into](https://doc.rust-lang.org/std/primitive.u64.html#method.format_into), [release 1.98](https://blog.rust-lang.org/2026/08/20/Rust-1.98.0/).

## Weryfikacja

- Faktyczne wersje: `rustc 1.90.0 (1159e78c4 2025-09-14)` i odpowiadający `rustdoc 1.90.0`; Edition 2024.
- `python3 scripts/verify_content.py .`: exit 0 po wszystkich zmianach zakresu, także w integrującym się drzewie. Sprawdza nawigację, kotwice, identyfikatory i kontrakt expanded.
- Wszystkie 29 plików zakresu zawierające bloki rust/compile_fail uruchomiono przez `SDKROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk rustdoc --test --edition 2024 <plik>`: **51 testów przeszło, zero porażek**. Pozostałe pliki rozwiązań zawierają konkretne analizy lub jawnie oznaczone, zależne szkice tekstowe.
- Pierwszy przebieg ujawnił E0283 w przykładzie web przez `.into()` przy przeciążonym TryFrom. Zmieniono wejście na jawne String::from, powtórzono ten test i następnie cały zakres: wynik powyżej jest z końcowego przebiegu.
- Osobna kontrola metadanych potwierdziła 20 rozdziałów, po 3 ćwiczenia, 60 unikalnych ID i komplet 20 odpowiadających plików rozwiązań. Typowa długość 807–1134 słowa; rozbudowany rozdział otoczek FFI 1268.
- Pełne `bash scripts/verify.sh` dla całego kompendium pozostaje centralną kontrolą integratora; nie przedstawiam testu własnego zakresu jako testu wszystkich działów.

## Ograniczenia

Nie instalowano zależności, targetów ani nowszego toolchainu. Nie uruchamiano serwera axum, PostgreSQL, SQLx, testów Serde, Miri, sanitizerów, profilerów, PGO, portable SIMD, targetowego asm, firmware ani runtime’u Wasm. Ich przykłady są oznaczone text i objaśniają wymagania; są weryfikacją dokumentacji, nie deklaracją wykonania. API od 1.98 porównano ze źródłami, lecz nie testowano kompilatorem 1.98. Hostowe doctesty unsafe nie dowodzą soundness dla wszystkich ścieżek, targetów i kontraktów obcej biblioteki. SDKROOT ustawiano wyłącznie dla procesu testującego; nie zmieniano systemowej konfiguracji narzędzi.

## Poprawki po niezależnym przeglądzie — 2026-11-11

Zakres ograniczono do dwóch wskazanych rozdziałów, rozwiązania C06-1 w istniejącym pliku rozwiązań oraz niniejszego dopisku. Nie zmieniono identyfikatorów ćwiczeń ani pozostałych plików.

1. `17_bazy_danych_i_persystencja/02_migracje_testy_i_odtwarzanie.md`: potwierdzono kontrprzykład starego writera zmieniającego tylko dawne pole po backfillu. Wersja przejściowa czyta stare pole i atomowo zapisuje oba; backfill zaczyna się dopiero po potwierdzeniu zgodności wszystkich writerów oraz zakończeniu starych transakcji. Zabroniono powrotu niezgodnego writera przez rollback wdrożenia. Backfill uzgadnia również nie-NULL wartości powstałe podczas mieszanego wdrożenia, przez `IS DISTINCT FROM`, zamiast naprawiać wyłącznie NULL. Dodano przeplot `(Ala,NULL) → (Ala,Ala) → (Beata,Ala)` oraz konceptualny test obu porządków backfillu i poprawnego dual-write. Spójnie poprawiono C06-1 w `rozwiazania/17_bazy_danych_i_persystencja/02_migracje_testy_i_odtwarzanie.md`.
2. `21_unsafe_soundness_i_model_pamieci/03_layout_alignment_i_uninitialized_memory.md`: dodano pełną podsekcję `spare_capacity_mut`, z właściwym typem `&mut [MaybeUninit<T>]`, rezerwacją przed pożyczką i rozróżnieniem inicjalizacji od publikacji długości. Nowy przykład `dopisz<T: Clone>` zawiera dowód SAFETY oraz test pustego wejścia i trzech String z zachowaniem istniejącego prefixu. Publikuje długość po każdym poprawnie zainicjalizowanym elemencie, więc panic kolejnego Clone pozostawia poprawny częściowy wynik. Omówiono także guard wymagany przy odkładaniu set_len do końca i brak automatycznego sprzątania zasobów w MaybeUninit.

Ponownie sprawdzono pierwotne źródła: [Vec::spare_capacity_mut](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.spare_capacity_mut), [Vec::reserve](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.reserve), [Vec::set_len](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.set_len), [PostgreSQL ALTER TABLE](https://www.postgresql.org/docs/current/ddl-alter.html), [izolacja i konkurujące UPDATE](https://www.postgresql.org/docs/current/transaction-iso.html) oraz [IS DISTINCT FROM](https://www.postgresql.org/docs/current/functions-comparison.html). Bariera wdrożeniowa wynika z kontraktu aplikacji; nie przedstawiono jej jako automatycznej gwarancji silnika SQL.

Weryfikacja ograniczona do zmienionych plików:

- `rustdoc --test --edition 2024` z procesowym SDKROOT wskazującym MacOSX26.5.sdk, na Rust 1.90.0: **7 doctestów przeszło** — 1 w migracjach oraz 6 w layout/init, w tym celowo odrzucany przykład. Zmieniony plik rozwiązań ma 0 bloków wykonywalnych i poprawny wynik rustdoc.
- `validate_markdown(root, [trzy zmienione pliki treści])`: brak problemów kontraktu, linków i kotwic. Nie uruchamiano ponownie testów całego kompendium.
- Funkcję `dopisz` wyodrębniono bez zmian z nowego bloku i uruchomiono z kontrolowanie panikującym Clone oraz licznikiem Drop. Po panic wektor zachował dokładnie jeden poprawnie dodany klon; po sprzątnięciu odnotowano trzy destrukcje: jeden klon i dwie wartości źródłowe, każdą raz. Próba przeszła na Rust 1.90.0, Edition 2024.

Nie uruchamiano bazy PostgreSQL: harmonogram migracji jest jawnie opisanym testem konceptualnym i planem testu integracyjnego na dwóch połączeniach. Hostowy test panic/Drop pozostaje uzupełnieniem dowodu niezmienników, a nie dowodem wszystkich możliwych zachowań T.
