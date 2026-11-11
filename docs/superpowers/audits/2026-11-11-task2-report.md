# Task 2 — pogłębienie działów 07–14

Stan: 11 listopada 2026. Zakończono wszystkie 33 istniejące rozdziały, dodano 33 równoległe pliki rozwiązań i zaktualizowano osiem map. Zachowano istniejące ścieżki i wartościową treść. Każdy rozdział ma marker rozszerzenia, cele, model, diagnostykę, praktykę produkcyjną, pytania, trzy konkretne ćwiczenia oraz źródła. Identyfikatory: B01-1–B33-3 (99 zadań).

## Pliki

Dla każdego rozdziału utworzono rozwiązanie pod tą samą ścieżką względną w `rozwiazania/`.

| Rozdział | Zadania | Słowa w całym pliku |
|---|---|---:|
| `07_obsluga_bledow/01_option_i_result.md` | B01-1–B01-3 | 843 |
| `07_obsluga_bledow/02_propagacja_i_operator_question_mark.md` | B02-1–B02-3 | 842 |
| `07_obsluga_bledow/03_panic_unwind_i_abort.md` | B03-1–B03-3 | 902 |
| `07_obsluga_bledow/04_wlasne_bledy_i_api.md` | B04-1–B04-3 | 946 |
| `08_moduly_cargo_i_workspaces/01_moduly_sciezki_i_widocznosc.md` | B05-1–B05-3 | 909 |
| `08_moduly_cargo_i_workspaces/02_crates_pakiety_i_workspaces.md` | B06-1–B06-3 | 938 |
| `08_moduly_cargo_i_workspaces/03_zaleznosci_features_i_cfg.md` | B07-1–B07-3 | 926 |
| `08_moduly_cargo_i_workspaces/04_profile_build_scripts_i_publikowanie.md` | B08-1–B08-3 | 921 |
| `08_moduly_cargo_i_workspaces/05_nightly_unstable_i_feature_gates.md` | B09-1–B09-3 | 1011 |
| `09_dokumentacja_testowanie_i_jakosc/01_testy_jednostkowe_i_integracyjne.md` | B10-1–B10-3 | 887 |
| `09_dokumentacja_testowanie_i_jakosc/02_testy_dokumentacyjne_i_rustdoc.md` | B11-1–B11-3 | 896 |
| `09_dokumentacja_testowanie_i_jakosc/03_clippy_rustfmt_i_linty.md` | B12-1–B12-3 | 925 |
| `10_wspolbieznosc/01_watki_i_scoped_threads.md` | B13-1–B13-3 | 1123 |
| `10_wspolbieznosc/02_kanaly_i_message_passing.md` | B14-1–B14-3 | 852 |
| `10_wspolbieznosc/03_arc_mutex_rwlock_i_condvar.md` | B15-1–B15-3 | 1086 |
| `10_wspolbieznosc/04_send_sync_i_atomiki.md` | B16-1–B16-3 | 903 |
| `10_wspolbieznosc/05_atomics_i_memory_ordering.md` | B17-1–B17-3 | 1058 |
| `10_wspolbieznosc/06_lock_free_i_aba.md` | B18-1–B18-3 | 1040 |
| `11_async_rust/01_future_async_i_await.md` | B19-1–B19-3 | 893 |
| `11_async_rust/02_executor_waker_i_poll.md` | B20-1–B20-3 | 938 |
| `11_async_rust/03_taski_join_select_i_stream.md` | B21-1–B21-3 | 1488 |
| `11_async_rust/04_anulowanie_timeouty_i_blocking.md` | B22-1–B22-3 | 964 |
| `11_async_rust/05_pin_unpin_i_self_referential.md` | B23-1–B23-3 | 1068 |
| `12_makra/01_macro_rules.md` | B24-1–B24-3 | 911 |
| `12_makra/02_higiena_fragmenty_i_repetition.md` | B25-1–B25-3 | 936 |
| `12_makra/03_makra_proceduralne.md` | B26-1–B26-3 | 940 |
| `12_makra/04_zaawansowane_makra_proceduralne.md` | B27-1–B27-3 | 1115 |
| `13_io_siec_i_protokoly/01_pliki_io_i_procesy.md` | B28-1–B28-3 | 923 |
| `13_io_siec_i_protokoly/02_siec_i_protokoly.md` | B29-1–B29-3 | 923 |
| `14_idiomy_wzorce_i_architektura/01_idiomy_newtype_i_extension_traits.md` | B30-1–B30-3 | 942 |
| `14_idiomy_wzorce_i_architektura/02_builder_typestate_i_state_machine.md` | B31-1–B31-3 | 1012 |
| `14_idiomy_wzorce_i_architektura/03_projektowanie_api_i_semver.md` | B32-1–B32-3 | 961 |
| `14_idiomy_wzorce_i_architektura/04_architektura_aplikacji_i_di.md` | B33-1–B33-3 | 1026 |

Ponadto zmieniono `README.md` w każdym dziale 07–14: mapy prowadzą do rozwiązań i objaśniają kolejność samodzielnej pracy oraz status bloków kodu. Poza własnym zakresem zapisano tylko niniejszy raport.

## Najważniejsze rozstrzygnięcia merytoryczne

- `Option`/`Result`: pełny kontrakt dzielenia podpisanych liczb obejmuje `MIN / -1`; leniwe kombinatory, własność, transpose i odróżnienie braku od złych danych.
- Propagacja: granica closure, collect wyników i brak rollbacku efektów przy `?`.
- Panic: RAII nie cofa stanu; ograniczenia UnwindSafe, hook, unwind/abort i FFI.
- Cargo: jawne dziedziczenie workspace, unifikacja features, resolver 3/MSRV, host/target build scriptu i różnica check/linkowanie/pakowanie.
- Współbieżność: RefCell może być Send, ale nie Sync; Arc nie synchronizuje dowolnego wnętrza. Dodano Barrier, thread_local, available_parallelism i OnceLock/LazyLock z odmiennym zachowaniem po panic.
- Atomiki: wskazane sequenced-before, reads-from, synchronizes-with i happens-before; ograniczenie jednorazowej flagi. compiler_fence nie zastępuje synchronizacji CPU/DMA. ABA może wystąpić bez allocatora; tagging nie zastępuje reclamation.
- Async: leniwe ciało a obliczanie argumentów, Send stanu future, brak gwarantowanego yield przy await, utracone wake, własność taska. Rozróżniono Drop future, detach Tokio JoinHandle, abort/drop JoinSet i nieprzerywalność rozpoczętego spawn_blocking. Rozwinięto LocalSet, Semaphore, mpsc/reserve, watch, broadcast/Lagged i aktora.
- Pin: ruch uchwytu a pointee, buffer String a obiekt String, strukturalna projekcja i Pin::set. Inicjalizacja edukacyjnej samoreferencji tworzy wskaźnik wewnątrz jednego mutowalnego reborrow, bez późniejszego nowego &mut całej struktury.
- Makra: pojedyncza ewaluacja nie nadaje Copy, pierwsze dopasowane ramię, higiena, expr_2021/Edition2024, bounds generics, alias runtime’u i testowanie faktycznej ekspansji.
- I/O: częściowe operacje, limit przed alokacją, reszta po ramce, trwałość a flush, EOF a niekompletność, lifecycle Child. Stały plik tymczasowy zastąpiono nazwą procesu i create_new, aby uniknąć nadpisania istniejącego pliku.
- Architektura: granice transakcji, nieznany wynik po timeout, idempotencja, właściciele zasobów, auto traits i behawioralna zgodność API.

## Faktycznie wykonane kontrole

1. `python3 scripts/verify_content.py .` — bez błędów po zapisaniu zakresu i aktualizacji nagłówków modelu.
2. Każdy z 66 plików rozdziałów/rozwiązań uruchomiono poleceniem `SDKROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk rustdoc --test --edition 2024 PLIK`: 162 doctesty, 66 plików bez błędów. Użyty `rustdoc 1.90.0 (1159e78c4 2025-09-14)`. Kontrole powtórzono po ostatnich zmianach samoreferencji i rozwiązania mediany.
3. Minimalny proc macro `odpowiedz` z rozwiązania B26-2 zbudowano w osobnym dwupakietowym workspace bez zależności zewnętrznych: `cargo run --offline -p konsument` zakończyło się kodem 0 i przeszła asercja wyniku. Konsument używa aliasu `makro` dla `odpowiedz_macro`. Niepoprawne `odpowiedz!(1)` w `cargo check --offline` dało kod 101 i dokładnie oczekiwany komunikat walidacji makra.
4. Ręcznie przejrzano granice własności i kontrakty wysokiego ryzyka; nie jest to formalny dowód soundness ani niezależny przegląd.

Pełne lokalne wyniki zakresowych doctestów zapisano w `/private/tmp/task2-rustdoc-results.json`, a testu proc macro w `/private/tmp/task2-macro-results.json`. To pomocnicze artefakty bieżącego wykonania, nie trwałe zależności dokumentacji. Zbiorcze `bash scripts/verify.sh` i niezależny przegląd wykonuje agent integrujący.

## Ograniczenia

- Zmiana SDKROOT jest ograniczona do komend testowych. Nie modyfikowano ustawień systemowych. Domyślne SDK27 było niezgodne z lokalnym linkerem; SDK26.5 umożliwiło rzeczywiste kompilowanie i uruchamianie.
- Nie wykonywano szkiców Tokio ani innych third-party; nie instalowano zależności. Fragmenty wymagające runtime’u, pakietu Cargo lub środowiska oznaczono jako text, z wyjaśnieniem kontekstu. Wyjątek jawnie opisany powyżej to osobny projekt standardowego proc macro.
- Nie wykonywano Miri, Loom, sanitizerów, benchmarków, formalnego model checking ani testów wieloplatformowych. Stress test nie jest przedstawiany jako dowód atomików.
- Przykład TCP i uruchamianie zewnętrznego rustc są opisami integracji środowiskowej, nie zaliczonymi testami rustdoc. Parsery protokołu mają wykonywalne testy std bez socketów.
- Internetowe dokumentacje std wskazywały nowszą wersję niż 1.90. Nie deklarowano testów na 1.98/1.99. Kontrakty weryfikowano w źródłach, a przykłady wykonano lokalnie na 1.90. Dokumentacja Tokio podczas weryfikacji wskazywała 1.54.1.

## Źródła

Zweryfikowano w przeglądarce oficjalne dokumentacje std, Rust Reference, Cargo Book, Edition Guide oraz dokumentację utrzymywaną przez Tokio na docs.rs. Kluczowe odsyłacze są również w rozdziałach:

- [Ordering i model pamięci](https://doc.rust-lang.org/std/sync/atomic/enum.Ordering.html)
- [Future::poll](https://doc.rust-lang.org/std/future/trait.Future.html)
- [Pin i Drop guarantee](https://doc.rust-lang.org/std/pin/index.html)
- [Pin::set](https://doc.rust-lang.org/std/pin/struct.Pin.html#method.set)
- [catch_unwind](https://doc.rust-lang.org/std/panic/fn.catch_unwind.html)
- [Mutex i advisory poisoning](https://doc.rust-lang.org/std/sync/struct.Mutex.html)
- [Sync i RefCell](https://doc.rust-lang.org/std/marker/trait.Sync.html)
- [Condvar](https://doc.rust-lang.org/std/sync/struct.Condvar.html)
- [OnceLock](https://doc.rust-lang.org/std/sync/struct.OnceLock.html)
- [LazyLock](https://doc.rust-lang.org/std/sync/struct.LazyLock.html)
- [Barrier](https://doc.rust-lang.org/std/sync/struct.Barrier.html)
- [available_parallelism](https://doc.rust-lang.org/std/thread/fn.available_parallelism.html)
- [Wake](https://doc.rust-lang.org/std/task/trait.Wake.html)
- [Read](https://doc.rust-lang.org/std/io/trait.Read.html)
- [Write](https://doc.rust-lang.org/std/io/trait.Write.html)
- [Child](https://doc.rust-lang.org/std/process/struct.Child.html)
- [Reference: await](https://doc.rust-lang.org/reference/expressions/await-expr.html)
- [Reference: macro_rules](https://doc.rust-lang.org/reference/macros-by-example.html)
- [Reference: procedural macros](https://doc.rust-lang.org/reference/procedural-macros.html)
- [Edition Guide: fragmenty makr](https://doc.rust-lang.org/edition-guide/rust-2024/macro-fragment-specifiers.html)
- [Cargo features](https://doc.rust-lang.org/cargo/reference/features.html)
- [Cargo resolver](https://doc.rust-lang.org/cargo/reference/resolver.html)
- [Cargo build scripts](https://doc.rust-lang.org/cargo/reference/build-scripts.html)
- [Cargo SemVer](https://doc.rust-lang.org/cargo/reference/semver.html)
- [Cargo rust-version](https://doc.rust-lang.org/cargo/reference/rust-version.html)
- [Tokio spawn](https://docs.rs/tokio/latest/tokio/task/fn.spawn.html)
- [Tokio spawn_blocking](https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html)
- [Tokio JoinHandle](https://docs.rs/tokio/latest/tokio/task/struct.JoinHandle.html)
- [Tokio JoinSet](https://docs.rs/tokio/latest/tokio/task/struct.JoinSet.html)
- [Tokio LocalSet](https://docs.rs/tokio/latest/tokio/task/struct.LocalSet.html)
- [Tokio Semaphore](https://docs.rs/tokio/latest/tokio/sync/struct.Semaphore.html)
- [Tokio mpsc](https://docs.rs/tokio/latest/tokio/sync/mpsc/index.html)
- [Tokio watch](https://docs.rs/tokio/latest/tokio/sync/watch/index.html)
- [Tokio broadcast](https://docs.rs/tokio/latest/tokio/sync/broadcast/index.html)
- [Tokio select](https://docs.rs/tokio/latest/tokio/macro.select.html)

Dodatkowo zweryfikowano [Tokio try_join](https://docs.rs/tokio/latest/tokio/macro.try_join.html), [Sender::reserve](https://docs.rs/tokio/latest/tokio/sync/mpsc/struct.Sender.html#method.reserve) i [syn Generics::split_for_impl](https://docs.rs/syn/latest/syn/struct.Generics.html#method.split_for_impl), wskazując zagnieżdżone błędy JoinHandle oraz wymagane features syn 3.0.9. Po uzupełnieniu tekstu powtórzono doctesty dwóch zmienionych rozdziałów.
