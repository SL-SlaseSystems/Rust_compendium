# Kompendium języka Rust

Kompendium prowadzi od pierwszego programu do tematów takich jak `unsafe`,
pinning, atomiki i model pamięci. Jest jednocześnie ścieżką nauki oraz
podręczną dokumentacją. Treść jest po polsku, bazuje na Rust Edition 2024 i
stabilnym Rust 1.97.1 (stan na 12 sierpnia 2026).

> Przykłady znajdują się bezpośrednio w rozdziałach. Nie trzeba pobierać
> dodatkowych projektów.

## Jak czytać

- **Od zera:** czytaj katalogi `01`–`13` w kolejności, a potem wybierz tematy
  z katalogu `zaawansowane`.
- **Masz doświadczenie w innym języku:** zacznij od
  [ownership](03_pamiec_i_wlasnosc/02_ownership_move_i_copy.md), następnie
  przejdź do [traits](04_typy_i_modelowanie/04_traits_i_associated_items.md),
  [błędów](06_bledy/01_option_i_result.md) i [Cargo](07_moduly_i_cargo/02_crates_pakiety_i_workspaces.md).
- **Szukasz konkretu:** użyj [ściągi](sciaga.md), [słownika](slownik.md) lub
  spisu poniżej.
- **Poziom ekspercki:** przeczytaj najpierw
  [mapę części zaawansowanej](zaawansowane/README.md).

## Legenda przykładów

- `rust` — samowystarczalny przykład sprawdzany przez `rustdoc`;
- `compile_fail` — przykład celowo odrzucany przez kompilator;
- `text` — szkic, manifest albo kod zależny od zewnętrznego środowiska;
- **nightly** — funkcjonalność niestabilna;
- **third-party** — API spoza języka i biblioteki standardowej.

## Spis treści

### 1. Wprowadzenie

1. [Czym jest Rust](01_wprowadzenie/01_czym_jest_rust.md)
2. [Instalacja i toolchain](01_wprowadzenie/02_instalacja_i_toolchain.md)
3. [Pierwszy program](01_wprowadzenie/03_pierwszy_program.md)
4. [Cargo w praktyce](01_wprowadzenie/04_cargo_w_praktyce.md)

### 2. Podstawy języka

1. [Zmienne, stałe i shadowing](02_podstawy_jezyka/01_zmienne_stale_i_shadowing.md)
2. [Typy i konwersje](02_podstawy_jezyka/02_typy_i_konwersje.md)
3. [Funkcje, wyrażenia i instrukcje](02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md)
4. [Sterowanie przepływem](02_podstawy_jezyka/04_sterowanie_przeplywem.md)
5. [Operatory, komentarze i atrybuty](02_podstawy_jezyka/05_operatory_komentarze_i_atrybuty.md)

### 3. Pamięć i własność

1. [Stos, sterta i RAII](03_pamiec_i_wlasnosc/01_stos_sterta_i_raii.md)
2. [Ownership, move i Copy](03_pamiec_i_wlasnosc/02_ownership_move_i_copy.md)
3. [Referencje i borrowing](03_pamiec_i_wlasnosc/03_referencje_i_borrowing.md)
4. [Slices i `str`](03_pamiec_i_wlasnosc/04_slices_i_str.md)
5. [Lifetimes](03_pamiec_i_wlasnosc/05_lifetimes.md)
6. [Smart pointery i interior mutability](03_pamiec_i_wlasnosc/06_smart_pointery_i_interior_mutability.md)

### 4. Typy i modelowanie

1. [Struktury, enumy i metody](04_typy_i_modelowanie/01_struktury_enumy_i_metody.md)
2. [Wzorce i `match`](04_typy_i_modelowanie/02_wzorce_i_match.md)
3. [Generics i const generics](04_typy_i_modelowanie/03_generics_i_const_generics.md)
4. [Traits i associated items](04_typy_i_modelowanie/04_traits_i_associated_items.md)
5. [Konwersje, DST i trait objects](04_typy_i_modelowanie/05_konwersje_dst_i_trait_objects.md)

### 5. Kolekcje i iteratory

1. [Tablice, wektory i sekwencje](05_kolekcje_i_iteratory/01_tablice_wektory_i_sekwencje.md)
2. [`String`, `str` i Unicode](05_kolekcje_i_iteratory/02_string_str_i_unicode.md)
3. [Mapy, zbiory i Entry](05_kolekcje_i_iteratory/03_mapy_zbiory_i_entry.md)
4. [Closures i rodzina `Fn`](05_kolekcje_i_iteratory/04_closures_i_fn_traits.md)
5. [Iteratory](05_kolekcje_i_iteratory/05_iteratory.md)

### 6. Błędy

1. [`Option` i `Result`](06_bledy/01_option_i_result.md)
2. [Propagacja i operator `?`](06_bledy/02_propagacja_i_operator_question_mark.md)
3. [`panic!`, unwind i abort](06_bledy/03_panic_unwind_i_abort.md)
4. [Własne błędy i projektowanie API](06_bledy/04_wlasne_bledy_i_api.md)

### 7. Moduły i Cargo

1. [Moduły, ścieżki i widoczność](07_moduly_i_cargo/01_moduly_sciezki_i_widocznosc.md)
2. [Crates, pakiety i workspaces](07_moduly_i_cargo/02_crates_pakiety_i_workspaces.md)
3. [Zależności, features i `cfg`](07_moduly_i_cargo/03_zaleznosci_features_i_cfg.md)
4. [Profile, build scripts i publikowanie](07_moduly_i_cargo/04_profile_build_scripts_i_publikowanie.md)

### 8. Testowanie i jakość

1. [Testy jednostkowe i integracyjne](08_testowanie_i_jakosc/01_testy_jednostkowe_i_integracyjne.md)
2. [Testy dokumentacyjne i rustdoc](08_testowanie_i_jakosc/02_testy_dokumentacyjne_i_rustdoc.md)
3. [Clippy, rustfmt i linty](08_testowanie_i_jakosc/03_clippy_rustfmt_i_linty.md)
4. [Benchmarki, profilowanie i Miri](08_testowanie_i_jakosc/04_benchmarki_profilowanie_i_miri.md)

### 9. Współbieżność

1. [Wątki i scoped threads](09_wspolbieznosc/01_watki_i_scoped_threads.md)
2. [Kanały i message passing](09_wspolbieznosc/02_kanaly_i_message_passing.md)
3. [`Arc`, `Mutex`, `RwLock` i `Condvar`](09_wspolbieznosc/03_arc_mutex_rwlock_i_condvar.md)
4. [`Send`, `Sync` i atomiki](09_wspolbieznosc/04_send_sync_i_atomiki.md)

### 10. Async

1. [`Future`, `async` i `await`](10_async/01_future_async_i_await.md)
2. [Executor, `Waker` i `poll`](10_async/02_executor_waker_i_poll.md)
3. [Taski, join, select i stream](10_async/03_taski_join_select_i_stream.md)
4. [Anulowanie, timeouty i kod blokujący](10_async/04_anulowanie_timeouty_i_blocking.md)

### 11. Makra

1. [`macro_rules!`](11_makra/01_macro_rules.md)
2. [Higiena, fragmenty i repetition](11_makra/02_higiena_fragmenty_i_repetition.md)
3. [Makra proceduralne](11_makra/03_makra_proceduralne.md)

### 12. Systemy i interoperacyjność

1. [Pliki, I/O i procesy](12_systemy_i_interoperacyjnosc/01_pliki_io_i_procesy.md)
2. [Sieć i protokoły](12_systemy_i_interoperacyjnosc/02_siec_i_protokoly.md)
3. [FFI, ABI i `repr`](12_systemy_i_interoperacyjnosc/03_ffi_abi_i_repr.md)
4. [WebAssembly, `no_std` i embedded](12_systemy_i_interoperacyjnosc/04_wasm_no_std_i_embedded.md)

### 13. Wzorce i architektura

1. [Idiomy, newtype i extension traits](13_wzorce_i_architektura/01_idiomy_newtype_i_extension_traits.md)
2. [Builder, typestate i state machine](13_wzorce_i_architektura/02_builder_typestate_i_state_machine.md)
3. [Projektowanie API i SemVer](13_wzorce_i_architektura/03_projektowanie_api_i_semver.md)
4. [Architektura aplikacji i dependency injection](13_wzorce_i_architektura/04_architektura_aplikacji_i_di.md)
5. [Wydajność i zero-cost abstractions](13_wzorce_i_architektura/05_wydajnosc_i_zero_cost.md)

### 14. Zagadnienia zaawansowane

1. [Mapa działu](zaawansowane/README.md)
2. [`unsafe` i soundness](zaawansowane/01_unsafe_i_soundness.md)
3. [Raw pointers, aliasing i provenance](zaawansowane/02_raw_pointers_aliasing_i_provenance.md)
4. [Layout, alignment i niezainicjalizowana pamięć](zaawansowane/03_layout_alignment_i_uninitialized_memory.md)
5. [Variance, subtyping i drop check](zaawansowane/04_variance_subtyping_i_dropck.md)
6. [HRTB, GAT, RPIT i `impl Trait`](zaawansowane/05_hrtb_gat_rpit_i_impl_trait.md)
7. [Dyn compatibility, vtables i dispatch](zaawansowane/06_dyn_compatibility_vtables_i_dispatch.md)
8. [`Pin`, `Unpin` i typy self-referential](zaawansowane/07_pin_unpin_i_self_referential.md)
9. [Atomiki i memory ordering](zaawansowane/08_atomics_i_memory_ordering.md)
10. [Lock-free i problem ABA](zaawansowane/09_lock_free_i_aba.md)
11. [Zaawansowane makra proceduralne](zaawansowane/10_zaawansowane_makra_proceduralne.md)
12. [FFI, bezpieczne otoczki i UB](zaawansowane/11_ffi_safe_wrappers_i_ub.md)
13. [`no_std`, allocatory i embedded](zaawansowane/12_no_std_allocatory_i_embedded.md)
14. [Monomorfizacja, MIR, LLVM i optymalizacja](zaawansowane/13_monomorfizacja_mir_llvm_i_optymalizacja.md)
15. [Borrow checker, Polonius i model pamięci](zaawansowane/14_borrow_checker_polonius_i_model_pamieci.md)
16. [Nightly, unstable i feature gates](zaawansowane/15_nightly_unstable_i_feature_gates.md)

## Materiały przekrojowe

- [Słownik](slownik.md)
- [Ściąga](sciaga.md)
- [Dalsza nauka](dalsza_nauka.md)
- [Źródła](zrodla.md)
- [Zasady rozwijania materiału](CONTRIBUTING.md)

## Weryfikacja

Jeżeli masz zainstalowany toolchain Rust, uruchom:

~~~text
bash scripts/verify.sh
~~~

Skrypt sprawdza lokalne linki, strukturę bloków kodu, puste pliki oraz
samowystarczalne przykłady Rust. Lokalny toolchain może być starszy niż
wersja opisana w kompendium; w takim przypadku skrypt poda wersję, na której
wykonywano testy.
