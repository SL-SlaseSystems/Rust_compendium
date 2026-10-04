# Mapa migracji do 30 działów

Data audytu: 4 października 2026 r.

## Stan bazowy

Mapa opisuje migrację z gałęzi `codex/rozbudowa-rdzenia-rust` po commicie
`4cc8531`. Obejmuje 77 plików Markdown: rozdziały 01–13, kompletną część
`zaawansowane/` oraz cztery rozwiązania działu wprowadzającego, których ścieżka
również się zmienia.

Przed audytem Task 1 zachował i zatwierdził rozbudowany rozdział
`02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md` wraz z rozwiązaniem.
Dwa wybiegające w przyszłość linki poprawiono na istniejące jeszcze ścieżki
`03_pamiec_i_wlasnosc/02_ownership_move_i_copy.md` i
`03_pamiec_i_wlasnosc/03_referencje_i_borrowing.md`. Podczas Task 4 zostaną
one ponownie skierowane do kanonicznego działu `03_ownership_i_pamiec`.

## Zasady

- `move` oznacza jedno kanoniczne przeniesienie przez Git.
- Wpis ze źródłem równym celowi przypina plik pozostający w miejscu.
- `merge` dotyczy mapy dawnej części eksperckiej: jej treść zostanie włączona
  do głównego README oraz map działów 5, 10–12 i 19–23.
- Manifest JSON jest źródłem maszynowym, a poniższa tabela jego widokiem do
  przeglądu.

## Ryzyka wymagające późniejszego podziału treści

- `04_benchmarki_profilowanie_i_miri.md` trafia najpierw do działu 20;
  materiał o Miri zostanie wydzielony do działu 26 w planie merytorycznym.
- `04_wasm_no_std_i_embedded.md` trafia najpierw do działu 23; materiał WASM
  zostanie wydzielony do działu 24.
- `zaawansowane/README.md` nie ma jednego odpowiednika tematycznego. Jego
  wymagania wstępne, kolejność i ostrzeżenia muszą zostać zachowane w kilku
  mapach, zanim stary plik zostanie usunięty.
- Ten etap zmienia ścieżki i nawigację. Nie przepisuje merytoryki rozdziałów,
  dzięki czemu review może osobno ocenić zachowanie treści i późniejsze
  rozszerzenia.

## Pełna tabela migracji

| Źródło | Cel | Sposób |
|---|---|---|
| `01_wprowadzenie/01_czym_jest_rust.md` | `01_wprowadzenie_i_toolchain/01_czym_jest_rust.md` | `move` |
| `01_wprowadzenie/02_instalacja_i_toolchain.md` | `01_wprowadzenie_i_toolchain/02_instalacja_i_toolchain.md` | `move` |
| `01_wprowadzenie/03_pierwszy_program.md` | `01_wprowadzenie_i_toolchain/03_pierwszy_program.md` | `move` |
| `01_wprowadzenie/04_cargo_w_praktyce.md` | `01_wprowadzenie_i_toolchain/04_cargo_w_praktyce.md` | `move` |
| `02_podstawy_jezyka/01_zmienne_stale_i_shadowing.md` | `02_podstawy_jezyka/01_zmienne_stale_i_shadowing.md` | `move` |
| `02_podstawy_jezyka/02_typy_i_konwersje.md` | `02_podstawy_jezyka/02_typy_i_konwersje.md` | `move` |
| `02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md` | `02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md` | `move` |
| `02_podstawy_jezyka/04_sterowanie_przeplywem.md` | `02_podstawy_jezyka/04_sterowanie_przeplywem.md` | `move` |
| `02_podstawy_jezyka/05_operatory_komentarze_i_atrybuty.md` | `02_podstawy_jezyka/05_operatory_komentarze_i_atrybuty.md` | `move` |
| `03_pamiec_i_wlasnosc/01_stos_sterta_i_raii.md` | `03_ownership_i_pamiec/01_stos_sterta_i_raii.md` | `move` |
| `03_pamiec_i_wlasnosc/02_ownership_move_i_copy.md` | `03_ownership_i_pamiec/02_ownership_move_i_copy.md` | `move` |
| `03_pamiec_i_wlasnosc/03_referencje_i_borrowing.md` | `03_ownership_i_pamiec/03_referencje_i_borrowing.md` | `move` |
| `03_pamiec_i_wlasnosc/04_slices_i_str.md` | `03_ownership_i_pamiec/04_slices_i_str.md` | `move` |
| `03_pamiec_i_wlasnosc/05_lifetimes.md` | `03_ownership_i_pamiec/05_lifetimes.md` | `move` |
| `03_pamiec_i_wlasnosc/06_smart_pointery_i_interior_mutability.md` | `03_ownership_i_pamiec/06_smart_pointery_i_interior_mutability.md` | `move` |
| `04_typy_i_modelowanie/01_struktury_enumy_i_metody.md` | `04_struktury_enumy_i_wzorce/01_struktury_enumy_i_metody.md` | `move` |
| `04_typy_i_modelowanie/02_wzorce_i_match.md` | `04_struktury_enumy_i_wzorce/02_wzorce_i_match.md` | `move` |
| `04_typy_i_modelowanie/03_generics_i_const_generics.md` | `05_generics_traits_i_system_typow/01_generics_i_const_generics.md` | `move` |
| `04_typy_i_modelowanie/04_traits_i_associated_items.md` | `05_generics_traits_i_system_typow/02_traits_i_associated_items.md` | `move` |
| `04_typy_i_modelowanie/05_konwersje_dst_i_trait_objects.md` | `05_generics_traits_i_system_typow/03_konwersje_dst_i_trait_objects.md` | `move` |
| `05_kolekcje_i_iteratory/01_tablice_wektory_i_sekwencje.md` | `06_kolekcje_iteratory_i_closures/01_tablice_wektory_i_sekwencje.md` | `move` |
| `05_kolekcje_i_iteratory/02_string_str_i_unicode.md` | `06_kolekcje_iteratory_i_closures/02_string_str_i_unicode.md` | `move` |
| `05_kolekcje_i_iteratory/03_mapy_zbiory_i_entry.md` | `06_kolekcje_iteratory_i_closures/03_mapy_zbiory_i_entry.md` | `move` |
| `05_kolekcje_i_iteratory/04_closures_i_fn_traits.md` | `06_kolekcje_iteratory_i_closures/04_closures_i_fn_traits.md` | `move` |
| `05_kolekcje_i_iteratory/05_iteratory.md` | `06_kolekcje_iteratory_i_closures/05_iteratory.md` | `move` |
| `06_bledy/01_option_i_result.md` | `07_obsluga_bledow/01_option_i_result.md` | `move` |
| `06_bledy/02_propagacja_i_operator_question_mark.md` | `07_obsluga_bledow/02_propagacja_i_operator_question_mark.md` | `move` |
| `06_bledy/03_panic_unwind_i_abort.md` | `07_obsluga_bledow/03_panic_unwind_i_abort.md` | `move` |
| `06_bledy/04_wlasne_bledy_i_api.md` | `07_obsluga_bledow/04_wlasne_bledy_i_api.md` | `move` |
| `07_moduly_i_cargo/01_moduly_sciezki_i_widocznosc.md` | `08_moduly_cargo_i_workspaces/01_moduly_sciezki_i_widocznosc.md` | `move` |
| `07_moduly_i_cargo/02_crates_pakiety_i_workspaces.md` | `08_moduly_cargo_i_workspaces/02_crates_pakiety_i_workspaces.md` | `move` |
| `07_moduly_i_cargo/03_zaleznosci_features_i_cfg.md` | `08_moduly_cargo_i_workspaces/03_zaleznosci_features_i_cfg.md` | `move` |
| `07_moduly_i_cargo/04_profile_build_scripts_i_publikowanie.md` | `08_moduly_cargo_i_workspaces/04_profile_build_scripts_i_publikowanie.md` | `move` |
| `08_testowanie_i_jakosc/01_testy_jednostkowe_i_integracyjne.md` | `09_dokumentacja_testowanie_i_jakosc/01_testy_jednostkowe_i_integracyjne.md` | `move` |
| `08_testowanie_i_jakosc/02_testy_dokumentacyjne_i_rustdoc.md` | `09_dokumentacja_testowanie_i_jakosc/02_testy_dokumentacyjne_i_rustdoc.md` | `move` |
| `08_testowanie_i_jakosc/03_clippy_rustfmt_i_linty.md` | `09_dokumentacja_testowanie_i_jakosc/03_clippy_rustfmt_i_linty.md` | `move` |
| `08_testowanie_i_jakosc/04_benchmarki_profilowanie_i_miri.md` | `20_wydajnosc_i_optymalizacja/02_benchmarki_profilowanie_i_miri.md` | `move` |
| `09_wspolbieznosc/01_watki_i_scoped_threads.md` | `10_wspolbieznosc/01_watki_i_scoped_threads.md` | `move` |
| `09_wspolbieznosc/02_kanaly_i_message_passing.md` | `10_wspolbieznosc/02_kanaly_i_message_passing.md` | `move` |
| `09_wspolbieznosc/03_arc_mutex_rwlock_i_condvar.md` | `10_wspolbieznosc/03_arc_mutex_rwlock_i_condvar.md` | `move` |
| `09_wspolbieznosc/04_send_sync_i_atomiki.md` | `10_wspolbieznosc/04_send_sync_i_atomiki.md` | `move` |
| `10_async/01_future_async_i_await.md` | `11_async_rust/01_future_async_i_await.md` | `move` |
| `10_async/02_executor_waker_i_poll.md` | `11_async_rust/02_executor_waker_i_poll.md` | `move` |
| `10_async/03_taski_join_select_i_stream.md` | `11_async_rust/03_taski_join_select_i_stream.md` | `move` |
| `10_async/04_anulowanie_timeouty_i_blocking.md` | `11_async_rust/04_anulowanie_timeouty_i_blocking.md` | `move` |
| `11_makra/01_macro_rules.md` | `12_makra/01_macro_rules.md` | `move` |
| `11_makra/02_higiena_fragmenty_i_repetition.md` | `12_makra/02_higiena_fragmenty_i_repetition.md` | `move` |
| `11_makra/03_makra_proceduralne.md` | `12_makra/03_makra_proceduralne.md` | `move` |
| `12_systemy_i_interoperacyjnosc/01_pliki_io_i_procesy.md` | `13_io_siec_i_protokoly/01_pliki_io_i_procesy.md` | `move` |
| `12_systemy_i_interoperacyjnosc/02_siec_i_protokoly.md` | `13_io_siec_i_protokoly/02_siec_i_protokoly.md` | `move` |
| `12_systemy_i_interoperacyjnosc/03_ffi_abi_i_repr.md` | `22_ffi_i_interoperacyjnosc/01_ffi_abi_i_repr.md` | `move` |
| `12_systemy_i_interoperacyjnosc/04_wasm_no_std_i_embedded.md` | `23_no_std_allocatory_i_embedded/01_wasm_no_std_i_embedded.md` | `move` |
| `13_wzorce_i_architektura/01_idiomy_newtype_i_extension_traits.md` | `14_idiomy_wzorce_i_architektura/01_idiomy_newtype_i_extension_traits.md` | `move` |
| `13_wzorce_i_architektura/02_builder_typestate_i_state_machine.md` | `14_idiomy_wzorce_i_architektura/02_builder_typestate_i_state_machine.md` | `move` |
| `13_wzorce_i_architektura/03_projektowanie_api_i_semver.md` | `14_idiomy_wzorce_i_architektura/03_projektowanie_api_i_semver.md` | `move` |
| `13_wzorce_i_architektura/04_architektura_aplikacji_i_di.md` | `14_idiomy_wzorce_i_architektura/04_architektura_aplikacji_i_di.md` | `move` |
| `13_wzorce_i_architektura/05_wydajnosc_i_zero_cost.md` | `20_wydajnosc_i_optymalizacja/01_wydajnosc_i_zero_cost.md` | `move` |
| `zaawansowane/01_unsafe_i_soundness.md` | `21_unsafe_soundness_i_model_pamieci/01_unsafe_i_soundness.md` | `move` |
| `zaawansowane/02_raw_pointers_aliasing_i_provenance.md` | `21_unsafe_soundness_i_model_pamieci/02_raw_pointers_aliasing_i_provenance.md` | `move` |
| `zaawansowane/03_layout_alignment_i_uninitialized_memory.md` | `21_unsafe_soundness_i_model_pamieci/03_layout_alignment_i_uninitialized_memory.md` | `move` |
| `zaawansowane/04_variance_subtyping_i_dropck.md` | `05_generics_traits_i_system_typow/04_variance_subtyping_i_dropck.md` | `move` |
| `zaawansowane/05_hrtb_gat_rpit_i_impl_trait.md` | `05_generics_traits_i_system_typow/05_hrtb_gat_rpit_i_impl_trait.md` | `move` |
| `zaawansowane/06_dyn_compatibility_vtables_i_dispatch.md` | `05_generics_traits_i_system_typow/06_dyn_compatibility_vtables_i_dispatch.md` | `move` |
| `zaawansowane/07_pin_unpin_i_self_referential.md` | `11_async_rust/05_pin_unpin_i_self_referential.md` | `move` |
| `zaawansowane/08_atomics_i_memory_ordering.md` | `10_wspolbieznosc/05_atomics_i_memory_ordering.md` | `move` |
| `zaawansowane/09_lock_free_i_aba.md` | `10_wspolbieznosc/06_lock_free_i_aba.md` | `move` |
| `zaawansowane/10_zaawansowane_makra_proceduralne.md` | `12_makra/04_zaawansowane_makra_proceduralne.md` | `move` |
| `zaawansowane/11_ffi_safe_wrappers_i_ub.md` | `22_ffi_i_interoperacyjnosc/02_ffi_safe_wrappers_i_ub.md` | `move` |
| `zaawansowane/12_no_std_allocatory_i_embedded.md` | `23_no_std_allocatory_i_embedded/02_no_std_allocatory_i_embedded.md` | `move` |
| `zaawansowane/13_monomorfizacja_mir_llvm_i_optymalizacja.md` | `20_wydajnosc_i_optymalizacja/03_monomorfizacja_mir_llvm_i_optymalizacja.md` | `move` |
| `zaawansowane/14_borrow_checker_polonius_i_model_pamieci.md` | `19_runtime_pamiec_i_kompilator/01_borrow_checker_polonius_i_model_pamieci.md` | `move` |
| `zaawansowane/15_nightly_unstable_i_feature_gates.md` | `08_moduly_cargo_i_workspaces/05_nightly_unstable_i_feature_gates.md` | `move` |
| `zaawansowane/README.md` | `README.md` | `merge` |
| `rozwiazania/01_wprowadzenie/01_czym_jest_rust.md` | `rozwiazania/01_wprowadzenie_i_toolchain/01_czym_jest_rust.md` | `move` |
| `rozwiazania/01_wprowadzenie/02_instalacja_i_toolchain.md` | `rozwiazania/01_wprowadzenie_i_toolchain/02_instalacja_i_toolchain.md` | `move` |
| `rozwiazania/01_wprowadzenie/03_pierwszy_program.md` | `rozwiazania/01_wprowadzenie_i_toolchain/03_pierwszy_program.md` | `move` |
| `rozwiazania/01_wprowadzenie/04_cargo_w_praktyce.md` | `rozwiazania/01_wprowadzenie_i_toolchain/04_cargo_w_praktyce.md` | `move` |

