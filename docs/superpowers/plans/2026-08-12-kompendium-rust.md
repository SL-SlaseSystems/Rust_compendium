# Kompendium języka Rust — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stworzyć kompletne, polskojęzyczne kompendium Rusta w modularnych plikach Markdown, prowadzące od pierwszego programu do mechanizmów eksperckich.

**Architecture:** Projekt jest podręcznikiem i kompendium referencyjnym jednocześnie: numerowane katalogi wyznaczają kolejność nauki, a małe pliki tematyczne pozwalają szybko znaleźć konkretny temat. Przykłady znajdują się bezpośrednio w Markdown; samowystarczalne bloki są sprawdzane przez `rustdoc --test`, a celowo błędne używają `compile_fail`. Osobny katalog `zaawansowane` izoluje zagadnienia wymagające dobrej znajomości modelu typów, pamięci i kompilatora.

**Tech Stack:** Markdown, Rust 1.97.1 stable (stan na 2026-08-12), Rust Edition 2024, `rustdoc`, powłoka POSIX, oficjalna dokumentacja projektu Rust.

## Global Constraints

- Język treści: polski.
- Format: wyłącznie pliki Markdown i fragmenty kodu osadzone w tekście; brak osobnych projektów Cargo.
- Każdy temat zawiera intuicję, reguły, przykład, omówienie, typowe pułapki i dobre praktyki, o ile element ma zastosowanie.
- Funkcje niestabilne są oznaczane jako nightly; biblioteki zewnętrzne są odróżniane od języka i biblioteki standardowej.
- Podstawą merytoryczną są aktualne oficjalne materiały: The Rust Programming Language, Rust Reference, Standard Library, Cargo Book, Rustonomicon, Async Book, Edition Guide, rustc Book, rustdoc Book i Clippy Book.
- Każdy plik rozdziału ma na początku łącze do głównego spisu treści i na końcu sekcję „Powiązane tematy”.
- Samowystarczalne bloki `rust` muszą przechodzić `rustdoc --test --edition 2024`; przykłady błędów używają `compile_fail`, a szkice składni `text`.

---

## Mapa plików

### Nawigacja i materiały przekrojowe

- `README.md` — mapa całego materiału, ścieżki nauki i legenda oznaczeń.
- `slownik.md` — polsko-angielski słownik pojęć Rusta.
- `sciaga.md` — skondensowana składnia i najczęstsze operacje.
- `dalsza_nauka.md` — ścieżki specjalizacji.
- `zrodla.md` — oficjalne źródła wraz z zakresem ich użycia.
- `CONTRIBUTING.md` — reguły utrzymywania spójności dokumentacji.

### Rozdziały

- `01_wprowadzenie/01_czym_jest_rust.md`
- `01_wprowadzenie/02_instalacja_i_toolchain.md`
- `01_wprowadzenie/03_pierwszy_program.md`
- `01_wprowadzenie/04_cargo_w_praktyce.md`
- `02_podstawy_jezyka/01_zmienne_stale_i_shadowing.md`
- `02_podstawy_jezyka/02_typy_i_konwersje.md`
- `02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md`
- `02_podstawy_jezyka/04_sterowanie_przeplywem.md`
- `02_podstawy_jezyka/05_operatory_komentarze_i_atrybuty.md`
- `03_pamiec_i_wlasnosc/01_stos_sterta_i_raii.md`
- `03_pamiec_i_wlasnosc/02_ownership_move_i_copy.md`
- `03_pamiec_i_wlasnosc/03_referencje_i_borrowing.md`
- `03_pamiec_i_wlasnosc/04_slices_i_str.md`
- `03_pamiec_i_wlasnosc/05_lifetimes.md`
- `03_pamiec_i_wlasnosc/06_smart_pointery_i_interior_mutability.md`
- `04_typy_i_modelowanie/01_struktury_enumy_i_metody.md`
- `04_typy_i_modelowanie/02_wzorce_i_match.md`
- `04_typy_i_modelowanie/03_generics_i_const_generics.md`
- `04_typy_i_modelowanie/04_traits_i_associated_items.md`
- `04_typy_i_modelowanie/05_konwersje_dst_i_trait_objects.md`
- `05_kolekcje_i_iteratory/01_tablice_wektory_i_sekwencje.md`
- `05_kolekcje_i_iteratory/02_string_str_i_unicode.md`
- `05_kolekcje_i_iteratory/03_mapy_zbiory_i_entry.md`
- `05_kolekcje_i_iteratory/04_closures_i_fn_traits.md`
- `05_kolekcje_i_iteratory/05_iteratory.md`
- `06_bledy/01_option_i_result.md`
- `06_bledy/02_propagacja_i_operator_question_mark.md`
- `06_bledy/03_panic_unwind_i_abort.md`
- `06_bledy/04_wlasne_bledy_i_api.md`
- `07_moduly_i_cargo/01_moduly_sciezki_i_widocznosc.md`
- `07_moduly_i_cargo/02_crates_pakiety_i_workspaces.md`
- `07_moduly_i_cargo/03_zaleznosci_features_i_cfg.md`
- `07_moduly_i_cargo/04_profile_build_scripts_i_publikowanie.md`
- `08_testowanie_i_jakosc/01_testy_jednostkowe_i_integracyjne.md`
- `08_testowanie_i_jakosc/02_testy_dokumentacyjne_i_rustdoc.md`
- `08_testowanie_i_jakosc/03_clippy_rustfmt_i_linty.md`
- `08_testowanie_i_jakosc/04_benchmarki_profilowanie_i_miri.md`
- `09_wspolbieznosc/01_watki_i_scoped_threads.md`
- `09_wspolbieznosc/02_kanaly_i_message_passing.md`
- `09_wspolbieznosc/03_arc_mutex_rwlock_i_condvar.md`
- `09_wspolbieznosc/04_send_sync_i_atomiki.md`
- `10_async/01_future_async_i_await.md`
- `10_async/02_executor_waker_i_poll.md`
- `10_async/03_taski_join_select_i_stream.md`
- `10_async/04_anulowanie_timeouty_i_blocking.md`
- `11_makra/01_macro_rules.md`
- `11_makra/02_higiena_fragmenty_i_repetition.md`
- `11_makra/03_makra_proceduralne.md`
- `12_systemy_i_interoperacyjnosc/01_pliki_io_i_procesy.md`
- `12_systemy_i_interoperacyjnosc/02_siec_i_protokoly.md`
- `12_systemy_i_interoperacyjnosc/03_ffi_abi_i_repr.md`
- `12_systemy_i_interoperacyjnosc/04_wasm_no_std_i_embedded.md`
- `13_wzorce_i_architektura/01_idiomy_newtype_i_extension_traits.md`
- `13_wzorce_i_architektura/02_builder_typestate_i_state_machine.md`
- `13_wzorce_i_architektura/03_projektowanie_api_i_semver.md`
- `13_wzorce_i_architektura/04_architektura_aplikacji_i_di.md`
- `13_wzorce_i_architektura/05_wydajnosc_i_zero_cost.md`

### Zagadnienia eksperckie

- `zaawansowane/README.md`
- `zaawansowane/01_unsafe_i_soundness.md`
- `zaawansowane/02_raw_pointers_aliasing_i_provenance.md`
- `zaawansowane/03_layout_alignment_i_uninitialized_memory.md`
- `zaawansowane/04_variance_subtyping_i_dropck.md`
- `zaawansowane/05_hrtb_gat_rpit_i_impl_trait.md`
- `zaawansowane/06_dyn_compatibility_vtables_i_dispatch.md`
- `zaawansowane/07_pin_unpin_i_self_referential.md`
- `zaawansowane/08_atomics_i_memory_ordering.md`
- `zaawansowane/09_lock_free_i_aba.md`
- `zaawansowane/10_zaawansowane_makra_proceduralne.md`
- `zaawansowane/11_ffi_safe_wrappers_i_ub.md`
- `zaawansowane/12_no_std_allocatory_i_embedded.md`
- `zaawansowane/13_monomorfizacja_mir_llvm_i_optymalizacja.md`
- `zaawansowane/14_borrow_checker_polonius_i_model_pamieci.md`
- `zaawansowane/15_nightly_unstable_i_feature_gates.md`

### Kontrola jakości

- `scripts/verify.sh` — sprawdza Markdown, linki względne, indeks, puste pliki oraz testy kodu wykonywane przez `rustdoc`.

---

### Task 1: Fundament projektu i kontrakt dokumentacji

**Files:**
- Create: `README.md`
- Create: `CONTRIBUTING.md`
- Create: `scripts/verify.sh`

**Interfaces:**
- Consumes: zatwierdzona specyfikacja w `docs/superpowers/specs/2026-08-12-kompendium-rust-design.md`.
- Produces: format rozdziałów, konwencje bloków kodu, strukturę spisu treści i jedno polecenie weryfikacyjne `bash scripts/verify.sh`.

- [ ] **Step 1: Zapisz szkielet nawigacji**

Utwórz `README.md` z opisem celu, legendą `rust`/`compile_fail`/`text`, trzema ścieżkami („od zera”, „mam doświadczenie”, „tematy eksperckie”) i tabelą wszystkich plików z mapy. Nie zostawiaj łączy do nieistniejących plików po zakończeniu Task 12.

- [ ] **Step 2: Zapisz reguły redakcyjne**

W `CONTRIBUTING.md` zdefiniuj polską terminologię, obowiązkowe sekcje, sposób oznaczania stable/nightly/third-party i minimalny format przykładu:

````markdown
```rust
fn main() {
    println!("przykład samowystarczalny");
}
```
````

- [ ] **Step 3: Dodaj walidator**

Napisz `scripts/verify.sh` z `set -eu`, wyszukiwaniem pustych `.md`, niedomkniętych bloków, brakujących lokalnych celów Markdown i uruchomieniem `rustdoc --test --edition 2024` dla każdego pliku zawierającego testowalne bloki.

- [ ] **Step 4: Sprawdź wczesne błędy**

Run: `bash scripts/verify.sh`
Expected: skrypt może zgłosić brakujące rozdziały wyszczególnione w README, ale nie może zakończyć się błędem składni powłoki.

- [ ] **Step 5: Zapisz etap**

Run: `git add README.md CONTRIBUTING.md scripts/verify.sh && git commit -m "docs: scaffold Rust compendium"`

### Task 2: Wprowadzenie i podstawy języka

**Files:**
- Create: `01_wprowadzenie/01_czym_jest_rust.md`
- Create: `01_wprowadzenie/02_instalacja_i_toolchain.md`
- Create: `01_wprowadzenie/03_pierwszy_program.md`
- Create: `01_wprowadzenie/04_cargo_w_praktyce.md`
- Create: `02_podstawy_jezyka/01_zmienne_stale_i_shadowing.md`
- Create: `02_podstawy_jezyka/02_typy_i_konwersje.md`
- Create: `02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md`
- Create: `02_podstawy_jezyka/04_sterowanie_przeplywem.md`
- Create: `02_podstawy_jezyka/05_operatory_komentarze_i_atrybuty.md`

**Interfaces:**
- Consumes: format rozdziału i legenda z Task 1.
- Produces: fundament składni używany bez ponownego tłumaczenia w pozostałych częściach.

- [ ] **Step 1: Napisz cztery rozdziały startowe**

Uwzględnij cele języka, safety bez garbage collectora, toolchain stable/beta/nightly, komponenty `rustfmt` i `clippy`, anatomię `fn main`, makro `println!`, komendy Cargo, manifest i różnicę package/crate/target.

- [ ] **Step 2: Napisz pięć rozdziałów składniowych**

Obejmij mutowalność, stałe, shadowing, typy skalarne i złożone, inferencję, jawne konwersje, funkcje, diverging type `!`, bloki jako wyrażenia, `if`, pętle, `while`, `for`, zakresy, operatory, komentarze i atrybuty.

- [ ] **Step 3: Zweryfikuj przykłady**

Run: `for f in 01_wprowadzenie/*.md 02_podstawy_jezyka/*.md; do rustdoc --test --edition 2024 "$f"; done`
Expected: wszystkie testowalne przykłady przechodzą.

- [ ] **Step 4: Zapisz etap**

Run: `git add 01_wprowadzenie 02_podstawy_jezyka && git commit -m "docs: cover Rust introduction and syntax"`

### Task 3: Pamięć, własność i inteligentne wskaźniki

**Files:**
- Create: `03_pamiec_i_wlasnosc/01_stos_sterta_i_raii.md`
- Create: `03_pamiec_i_wlasnosc/02_ownership_move_i_copy.md`
- Create: `03_pamiec_i_wlasnosc/03_referencje_i_borrowing.md`
- Create: `03_pamiec_i_wlasnosc/04_slices_i_str.md`
- Create: `03_pamiec_i_wlasnosc/05_lifetimes.md`
- Create: `03_pamiec_i_wlasnosc/06_smart_pointery_i_interior_mutability.md`

**Interfaces:**
- Consumes: typy, funkcje i zakresy z Task 2.
- Produces: model ownership/borrowing wymagany przez wszystkie dalsze rozdziały.

- [ ] **Step 1: Wyjaśnij model pamięci i ownership**

Pokaż stos, stertę, RAII, `Drop`, move, clone, `Copy`, częściowe przeniesienie, zakres życia wartości i reguły przekazywania argumentów.

- [ ] **Step 2: Wyjaśnij borrowing, slices i lifetimes**

Pokaż `&T`, `&mut T`, reborrowing, regułę aliasowania, NLL, dangling references, `&[T]`, `&str`, elision, jawne parametry lifetime, `'static` i lifetime bounds.

- [ ] **Step 3: Wyjaśnij smart pointery**

Porównaj `Box<T>`, `Rc<T>`, `Arc<T>`, `Cell<T>`, `RefCell<T>`, `Mutex<T>`, `Weak<T>`, `Deref`, interior mutability i cykle referencji.

- [ ] **Step 4: Zweryfikuj kod i terminologię**

Run: `for f in 03_pamiec_i_wlasnosc/*.md; do rustdoc --test --edition 2024 "$f"; done && rg -n "garbage collector|borrow checker|undefined behavior" 03_pamiec_i_wlasnosc`
Expected: testy przechodzą, a angielskie terminy są tłumaczone przy pierwszym użyciu.

- [ ] **Step 5: Zapisz etap**

Run: `git add 03_pamiec_i_wlasnosc && git commit -m "docs: explain memory ownership and borrowing"`

### Task 4: Modelowanie typami, wzorce i polimorfizm

**Files:**
- Create: `04_typy_i_modelowanie/01_struktury_enumy_i_metody.md`
- Create: `04_typy_i_modelowanie/02_wzorce_i_match.md`
- Create: `04_typy_i_modelowanie/03_generics_i_const_generics.md`
- Create: `04_typy_i_modelowanie/04_traits_i_associated_items.md`
- Create: `04_typy_i_modelowanie/05_konwersje_dst_i_trait_objects.md`

**Interfaces:**
- Consumes: ownership, referencje i lifetimes z Task 3.
- Produces: bazę dla błędów, iteratorów, architektury API i tematów eksperckich.

- [ ] **Step 1: Opisz typy użytkownika i pattern matching**

Uwzględnij structs, tuple/unit structs, enum variants, discriminants, metody, associated functions, destructuring, guards, `@`, `..`, refutable/irrefutable patterns, `let else` i exhaustiveness.

- [ ] **Step 2: Opisz abstrakcje statyczne**

Wyjaśnij parametry typów, bounds, `where`, turbofish, const generics, traits, default methods, supertraits, associated types/constants/functions, blanket implementations, coherence i orphan rule.

- [ ] **Step 3: Opisz konwersje i dynamiczny polimorfizm**

Pokaż `From`/`Into`, `TryFrom`/`TryInto`, `AsRef`/`Borrow`, coercions, `Sized`/`?Sized`, DST, fat pointers, `dyn Trait` i różnicę static/dynamic dispatch.

- [ ] **Step 4: Zweryfikuj przykłady i zapisz etap**

Run: `for f in 04_typy_i_modelowanie/*.md; do rustdoc --test --edition 2024 "$f"; done`
Expected: wszystkie testowalne przykłady przechodzą.

Run: `git add 04_typy_i_modelowanie && git commit -m "docs: cover Rust type modeling"`

### Task 5: Kolekcje, closures, iteratory i obsługa błędów

**Files:**
- Create: `05_kolekcje_i_iteratory/01_tablice_wektory_i_sekwencje.md`
- Create: `05_kolekcje_i_iteratory/02_string_str_i_unicode.md`
- Create: `05_kolekcje_i_iteratory/03_mapy_zbiory_i_entry.md`
- Create: `05_kolekcje_i_iteratory/04_closures_i_fn_traits.md`
- Create: `05_kolekcje_i_iteratory/05_iteratory.md`
- Create: `06_bledy/01_option_i_result.md`
- Create: `06_bledy/02_propagacja_i_operator_question_mark.md`
- Create: `06_bledy/03_panic_unwind_i_abort.md`
- Create: `06_bledy/04_wlasne_bledy_i_api.md`

**Interfaces:**
- Consumes: generics, traits i ownership z Tasks 3–4.
- Produces: idiomy przetwarzania danych i kontrakt błędów używany w rozdziałach systemowych.

- [ ] **Step 1: Napisz część o kolekcjach i Unicode**

Porównaj `[T; N]`, slices, `Vec`, `VecDeque`, `LinkedList`, `HashMap`, `BTreeMap`, `HashSet`, `BTreeSet`, `BinaryHeap`; omów pojemność, reallocation, indeksowanie, `Entry`, UTF-8, grapheme clusters i bezpieczne operacje na `String`/`str`.

- [ ] **Step 2: Napisz część funkcyjną**

Pokaż capture przez referencję/mutację/wartość, `move`, traits `Fn`/`FnMut`/`FnOnce`, adaptery iteratorów, konsumowanie, `collect`, `try_fold`, `IntoIterator`, implementację własnego iteratora i lazy evaluation.

- [ ] **Step 3: Napisz część o błędach**

Wyjaśnij combinators `Option`/`Result`, `?`, `FromResidual` na poziomie intuicyjnym, konwersję błędów, `panic!`, unwind/abort, panic safety, własne enumy błędów, `Error`, źródła błędów, boxed errors i granice użycia bibliotek zewnętrznych.

- [ ] **Step 4: Zweryfikuj i zapisz etap**

Run: `for f in 05_kolekcje_i_iteratory/*.md 06_bledy/*.md; do rustdoc --test --edition 2024 "$f"; done`
Expected: wszystkie testowalne przykłady przechodzą.

Run: `git add 05_kolekcje_i_iteratory 06_bledy && git commit -m "docs: explain collections iterators and errors"`

### Task 6: Moduły, Cargo, testy i jakość

**Files:**
- Create: `07_moduly_i_cargo/01_moduly_sciezki_i_widocznosc.md`
- Create: `07_moduly_i_cargo/02_crates_pakiety_i_workspaces.md`
- Create: `07_moduly_i_cargo/03_zaleznosci_features_i_cfg.md`
- Create: `07_moduly_i_cargo/04_profile_build_scripts_i_publikowanie.md`
- Create: `08_testowanie_i_jakosc/01_testy_jednostkowe_i_integracyjne.md`
- Create: `08_testowanie_i_jakosc/02_testy_dokumentacyjne_i_rustdoc.md`
- Create: `08_testowanie_i_jakosc/03_clippy_rustfmt_i_linty.md`
- Create: `08_testowanie_i_jakosc/04_benchmarki_profilowanie_i_miri.md`

**Interfaces:**
- Consumes: projektowanie modułów i błędów z Tasks 4–5.
- Produces: praktyki organizacji i walidacji projektów używane w pozostałych materiałach.

- [ ] **Step 1: Opisz system modułów i Cargo**

Obejmij `mod`, `use`, ścieżki, `pub` variants, re-exports, prelude, strukturę crate’ów, targets, workspaces, semver dependencies, lockfile, features jako addytywne, `cfg`, profiles, build scripts, registries i publikowanie.

- [ ] **Step 2: Opisz testowanie i dokumentację**

Pokaż `#[test]`, assertions, expected panic, `Result` w testach, moduły testowe, katalog `tests`, doctests, hidden lines, `should_panic`, `compile_fail`, dokumentowanie publicznego API i intra-doc links.

- [ ] **Step 3: Opisz narzędzia jakości i diagnostyki**

Omów `cargo fmt`, `cargo clippy`, lint levels, `cargo check`, `cargo test`, `cargo doc`, benchmarki stable i third-party, profiling, flame graphs, sanitizers/nightly, Miri/nightly i `cargo expand` jako narzędzie zewnętrzne.

- [ ] **Step 4: Zweryfikuj i zapisz etap**

Run: `for f in 07_moduly_i_cargo/*.md 08_testowanie_i_jakosc/*.md; do rustdoc --test --edition 2024 "$f"; done`
Expected: wszystkie testowalne przykłady przechodzą.

Run: `git add 07_moduly_i_cargo 08_testowanie_i_jakosc && git commit -m "docs: cover Cargo testing and quality"`

### Task 7: Współbieżność i async

**Files:**
- Create: `09_wspolbieznosc/01_watki_i_scoped_threads.md`
- Create: `09_wspolbieznosc/02_kanaly_i_message_passing.md`
- Create: `09_wspolbieznosc/03_arc_mutex_rwlock_i_condvar.md`
- Create: `09_wspolbieznosc/04_send_sync_i_atomiki.md`
- Create: `10_async/01_future_async_i_await.md`
- Create: `10_async/02_executor_waker_i_poll.md`
- Create: `10_async/03_taski_join_select_i_stream.md`
- Create: `10_async/04_anulowanie_timeouty_i_blocking.md`

**Interfaces:**
- Consumes: ownership, smart pointery, traits i błędy.
- Produces: model wykonania potrzebny przez atomiki, pinning i programowanie sieciowe.

- [ ] **Step 1: Napisz część o współbieżności synchronicznej**

Pokaż `thread::spawn`, `move`, `JoinHandle`, `thread::scope`, mpsc, `Arc`, `Mutex`, `RwLock`, `Condvar`, poisoning, deadlock, `Send`, `Sync` i podstawową rolę atomików.

- [ ] **Step 2: Napisz część asynchroniczną**

Wyjaśnij `Future`, `async fn`, `.await`, brak wbudowanego runtime’u, executor, task, `Poll`, `Context`, `Waker`, streamy jako pojęcie ekosystemu, join/select, cancellation safety, timeout i izolowanie pracy blokującej.

- [ ] **Step 3: Oznacz granice standard library/ekosystem**

Każdy przykład zależny od Tokio, futures lub async-std oznacz jako third-party i pokaż najpierw mechanizm ze standardowego `Future`, gdy jest to dydaktycznie użyteczne.

- [ ] **Step 4: Zweryfikuj i zapisz etap**

Run: `for f in 09_wspolbieznosc/*.md 10_async/*.md; do rustdoc --test --edition 2024 "$f"; done`
Expected: przykłady standard library przechodzą; szkice zależne od crate’ów są nietestowalnymi blokami `text` z opisem zależności.

Run: `git add 09_wspolbieznosc 10_async && git commit -m "docs: cover concurrency and async Rust"`

### Task 8: Makra, systemy i interoperacyjność

**Files:**
- Create: `11_makra/01_macro_rules.md`
- Create: `11_makra/02_higiena_fragmenty_i_repetition.md`
- Create: `11_makra/03_makra_proceduralne.md`
- Create: `12_systemy_i_interoperacyjnosc/01_pliki_io_i_procesy.md`
- Create: `12_systemy_i_interoperacyjnosc/02_siec_i_protokoly.md`
- Create: `12_systemy_i_interoperacyjnosc/03_ffi_abi_i_repr.md`
- Create: `12_systemy_i_interoperacyjnosc/04_wasm_no_std_i_embedded.md`

**Interfaces:**
- Consumes: składnia wzorców, traits, błędy, Cargo i współbieżność.
- Produces: praktyczne podstawy dla zaawansowanych makr, FFI i `no_std`.

- [ ] **Step 1: Opisz makra**

Pokaż różnicę funkcja/makro, `macro_rules!`, metavariables, fragment specifiers, repetitions, separators, recursion, higienę oraz architekturę derive/attribute/function-like procedural macros z `TokenStream`.

- [ ] **Step 2: Opisz standardowe programowanie systemowe**

Pokaż `Read`, `Write`, `BufRead`, `Seek`, pliki, ścieżki, procesy, środowisko, TCP/UDP, framing, time-outy, endianess oraz regułę, że protokół jest czymś więcej niż pojedyncze `read`.

- [ ] **Step 3: Opisz granice platform i języków**

Omów `extern`, ABI, `#[unsafe(no_mangle)]` w Edition 2024, `repr(C)`, ownership przez FFI, C strings, WebAssembly, targety, `#![no_std]`, `core`, `alloc`, panic handler i podstawy embedded.

- [ ] **Step 4: Zweryfikuj i zapisz etap**

Run: `for f in 11_makra/*.md 12_systemy_i_interoperacyjnosc/*.md; do rustdoc --test --edition 2024 "$f"; done`
Expected: testowalne fragmenty przechodzą, a przykłady zależne od platformy są jawnie opisane.

Run: `git add 11_makra 12_systemy_i_interoperacyjnosc && git commit -m "docs: explain macros systems and interoperability"`

### Task 9: Wzorce, API, architektura i wydajność

**Files:**
- Create: `13_wzorce_i_architektura/01_idiomy_newtype_i_extension_traits.md`
- Create: `13_wzorce_i_architektura/02_builder_typestate_i_state_machine.md`
- Create: `13_wzorce_i_architektura/03_projektowanie_api_i_semver.md`
- Create: `13_wzorce_i_architektura/04_architektura_aplikacji_i_di.md`
- Create: `13_wzorce_i_architektura/05_wydajnosc_i_zero_cost.md`

**Interfaces:**
- Consumes: wszystkie podstawowe mechanizmy z Tasks 2–8.
- Produces: pomost od poprawnego kodu do utrzymywalnych bibliotek i aplikacji.

- [ ] **Step 1: Opisz idiomy i wzorce typów**

Pokaż newtype, extension traits, sealed traits, builder consuming/mutable, typestate, state machine z enumem, phantom types i zasadę making invalid states unrepresentable.

- [ ] **Step 2: Opisz publiczne API i architekturę**

Omów minimalną powierzchnię `pub`, ownership w sygnaturach, przyjmowanie `impl AsRef`, zwracanie konkretnych typów, błędy, object safety/dyn compatibility, SemVer, MSRV, feature flags, podział library/binary, dependency inversion przez traits i composition root.

- [ ] **Step 3: Opisz wydajność**

Wyjaśnij zero-cost abstractions, monomorfizację, alokacje, cache locality, iteratory, bounds checks, release profiles, LTO, codegen units i regułę „mierz przed optymalizacją”.

- [ ] **Step 4: Zweryfikuj i zapisz etap**

Run: `for f in 13_wzorce_i_architektura/*.md; do rustdoc --test --edition 2024 "$f"; done`
Expected: wszystkie testowalne przykłady przechodzą.

Run: `git add 13_wzorce_i_architektura && git commit -m "docs: present Rust design and architecture patterns"`

### Task 10: Zaawansowana pamięć i system typów

**Files:**
- Create: `zaawansowane/README.md`
- Create: `zaawansowane/01_unsafe_i_soundness.md`
- Create: `zaawansowane/02_raw_pointers_aliasing_i_provenance.md`
- Create: `zaawansowane/03_layout_alignment_i_uninitialized_memory.md`
- Create: `zaawansowane/04_variance_subtyping_i_dropck.md`
- Create: `zaawansowane/05_hrtb_gat_rpit_i_impl_trait.md`
- Create: `zaawansowane/06_dyn_compatibility_vtables_i_dispatch.md`
- Create: `zaawansowane/07_pin_unpin_i_self_referential.md`

**Interfaces:**
- Consumes: ownership, lifetimes, traits, `Future`, FFI i wzorce API.
- Produces: precyzyjne podstawy safety potrzebne przez pozostałe rozdziały eksperckie.

- [ ] **Step 1: Zbuduj mapę tematów eksperckich**

W `zaawansowane/README.md` dodaj wymagania wstępne, kolejność czytania i ostrzeżenie, że `unsafe` przesuwa obowiązek dowodu z kompilatora na programistę.

- [ ] **Step 2: Napisz część o pamięci niskopoziomowej**

Opisz pięć możliwości `unsafe`, safety invariants, soundness, UB, raw pointers, tworzenie vs dereferencję, aliasing, pointer provenance, layout, alignment, padding, `repr`, `MaybeUninit`, `NonNull` i drop częściowo zainicjalizowanych danych.

- [ ] **Step 3: Napisz część o zaawansowanych typach**

Wyjaśnij subtyping lifetime’ów, covariance/contravariance/invariance, `PhantomData`, drop check, HRTB `for<'a>`, GAT, RPIT/TAIT z oznaczeniem stabilności, `impl Trait`, vtables, dyn compatibility i dispatch.

- [ ] **Step 4: Napisz część o pinning**

Wyjaśnij adresową stabilność, `Pin<P>`, `Unpin`, bezpieczne projekcje, dlaczego self-referential structs są trudne oraz jak state machine `Future` korzysta z pinning.

- [ ] **Step 5: Zweryfikuj i zapisz etap**

Run: `for f in zaawansowane/{01,02,03,04,05,06,07}_*.md; do rustdoc --test --edition 2024 "$f"; done`
Expected: bezpieczne i kontrolowane przykłady przechodzą; fragmenty ilustrujące UB nie są wykonywane.

Run: `git add zaawansowane && git commit -m "docs: add advanced memory and type system chapters"`

### Task 11: Atomiki, lock-free, makra, FFI, no_std i kompilator

**Files:**
- Create: `zaawansowane/08_atomics_i_memory_ordering.md`
- Create: `zaawansowane/09_lock_free_i_aba.md`
- Create: `zaawansowane/10_zaawansowane_makra_proceduralne.md`
- Create: `zaawansowane/11_ffi_safe_wrappers_i_ub.md`
- Create: `zaawansowane/12_no_std_allocatory_i_embedded.md`
- Create: `zaawansowane/13_monomorfizacja_mir_llvm_i_optymalizacja.md`
- Create: `zaawansowane/14_borrow_checker_polonius_i_model_pamieci.md`
- Create: `zaawansowane/15_nightly_unstable_i_feature_gates.md`

**Interfaces:**
- Consumes: podstawy `unsafe`, provenance, layout, traits i systemy z Tasks 8–10.
- Produces: końcową warstwę ekspercką i jasne granice wiedzy stabilnej/eksperymentalnej.

- [ ] **Step 1: Opisz atomiki i lock-free**

Wyjaśnij atomicity vs ordering, Relaxed/Acquire/Release/AcqRel/SeqCst, happens-before, compare-exchange, CAS loop, ABA, reclamation pamięci, false sharing oraz powody wyboru mutexa przed własnym algorytmem lock-free.

- [ ] **Step 2: Pogłęb makra i FFI**

Opisz parsing/generation tokenów, spans, hygiene, derive helpers, diagnostykę procedural macros, kontrakty C ABI, unwind przez FFI, callbacki, opaque handles, ownership i wzorzec bezpiecznej otoczki.

- [ ] **Step 3: Pogłęb no_std i proces kompilacji**

Wyjaśnij `core`/`alloc`/`std`, global allocator, panic handler, target specs, monomorfizację, HIR/MIR/LLVM, optymalizację, borrow checking, NLL, status Poloniusa i ostrożne formułowanie modelu pamięci.

- [ ] **Step 4: Opisz nightly**

Pokaż kanały toolchainu, `rust-toolchain.toml`, feature gates, Unstable Book, ocenę ryzyka i migrację do stabilnego API. Każdy przykład niestabilny podpisz nazwą feature gate i datą weryfikacji.

- [ ] **Step 5: Zweryfikuj i zapisz etap**

Run: `for f in zaawansowane/{08,09,10,11,12,13,14,15}_*.md; do rustdoc --test --edition 2024 "$f"; done`
Expected: przykłady stable przechodzą, a nightly i szkice platformowe są poprawnie oznaczone.

Run: `git add zaawansowane && git commit -m "docs: complete expert Rust topics"`

### Task 12: Słownik, ściąga, dalsza nauka, źródła i pełna nawigacja

**Files:**
- Create: `slownik.md`
- Create: `sciaga.md`
- Create: `dalsza_nauka.md`
- Create: `zrodla.md`
- Modify: `README.md`
- Modify: wszystkie pliki rozdziałów, jeżeli brakuje odsyłaczy „Powiązane tematy”.

**Interfaces:**
- Consumes: wszystkie ukończone rozdziały.
- Produces: kompletne punkty wejścia do materiału i zamknięty graf nawigacji.

- [ ] **Step 1: Napisz materiały przekrojowe**

W słowniku uwzględnij co najmniej ownership, borrow, lifetime, move, trait, crate, soundness, UB, aliasing, provenance, pinning, variance, monomorphization i dispatch. W ściądze zbierz składnię deklaracji, typów, konwersji, iteratorów, błędów, testów, współbieżności i Cargo.

- [ ] **Step 2: Napisz ścieżki dalszej nauki**

Rozpisz osobne kolejności rozdziałów i oficjalne punkty startowe dla CLI, backendu, systemów, embedded, WebAssembly oraz tworzenia bibliotek.

- [ ] **Step 3: Zbuduj bibliografię źródeł pierwotnych**

W `zrodla.md` podaj bezpośrednie linki do oficjalnych książek, Reference, API standard library, bloga wydań i RFC Book; przy każdym źródle wskaż, do których tematów służy.

- [ ] **Step 4: Zamknij nawigację**

Uzupełnij główny spis treści, link powrotny na początku każdego pliku i 2–5 odsyłaczy „Powiązane tematy” na końcu. Sprawdź, że kolejność w README odpowiada nazwom katalogów.

- [ ] **Step 5: Zapisz etap**

Run: `git add README.md slownik.md sciaga.md dalsza_nauka.md zrodla.md 0* 1* zaawansowane && git commit -m "docs: complete navigation glossary and references"`

### Task 13: Pełna kontrola jakości i odbiór

**Files:**
- Modify: dowolny plik `.md`, w którym walidacja ujawni błąd.
- Modify: `scripts/verify.sh`, jeśli kontrola nie pokrywa któregoś kryterium specyfikacji.

**Interfaces:**
- Consumes: cały projekt.
- Produces: zweryfikowany artefakt końcowy bez pustych rozdziałów i martwych łączy.

- [ ] **Step 1: Uruchom globalny walidator**

Run: `bash scripts/verify.sh`
Expected: exit 0, brak martwych linków, pustych plików, niedomkniętych bloków i błędów `rustdoc`.

- [ ] **Step 2: Sprawdź kompletność mapy**

Run: `find . -type f -name '*.md' -not -path './.git/*' | sort`
Expected: wszystkie pliki z „Mapy plików” istnieją.

Run: `rg -L '^\[← Spis treści\]' 0*_/*.md 1*_/*.md zaawansowane/*.md`
Expected: brak pliku rozdziału bez łącza powrotnego.

- [ ] **Step 3: Sprawdź oznaczenia ryzykownych tematów**

Run: `rg -n 'unsafe|nightly|Tokio|Miri|undefined behavior' zaawansowane 10_async 12_systemy_i_interoperacyjnosc 08_testowanie_i_jakosc`
Expected: każde użycie nightly/third-party/UB ma lokalne wyjaśnienie statusu lub ryzyka.

- [ ] **Step 4: Sprawdź jakość redakcyjną**

Przejrzyj nagłówki, terminologię i duplikaty; usuń stwierdzenia absolutne sprzeczne z Rust Reference, rozbij nieczytelne akapity i upewnij się, że każdy temat ma przykład albo wyraźne uzasadnienie jego braku.

- [ ] **Step 5: Uruchom walidator po poprawkach**

Run: `bash scripts/verify.sh && git status --short`
Expected: walidator kończy się kodem 0; status pokazuje wyłącznie świadome poprawki odbiorowe.

- [ ] **Step 6: Zapisz wynik końcowy**

Run: `git add . && git commit -m "docs: verify complete Rust compendium"`

- [ ] **Step 7: Zbierz metryki odbiorowe**

Run: `find . -type f -name '*.md' -not -path './.git/*' | wc -l && wc -w README.md 0*_/*.md 1*_/*.md zaawansowane/*.md slownik.md sciaga.md dalsza_nauka.md zrodla.md | tail -1`
Expected: co najmniej 76 plików Markdown łącznie ze specyfikacją i planem; brak arbitralnego minimum słów, ale żaden plik merytoryczny nie jest szkieletem.
