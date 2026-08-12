[← Spis treści](../README.md)

# Zagadnienia zaawansowane

Ta część jest dla czytelnika, który swobodnie rozumie ownership, lifetimes,
traits, współbieżność i podstawowe `Future`. Nie jest konieczna do większości
aplikacji. Jest konieczna, gdy tworzysz bezpieczne abstrakcje nad wskaźnikami,
FFI, lock-free, runtime, allocator lub kod embedded.

> `unsafe` nie wyłącza borrow checkera. Daje pięć dodatkowych możliwości i
> przenosi obowiązek utrzymania ich invariants z kompilatora na autora.

## Zalecana kolejność

### Fundament bezpieczeństwa

1. [`unsafe` i soundness](01_unsafe_i_soundness.md)
2. [Raw pointers, aliasing i provenance](02_raw_pointers_aliasing_i_provenance.md)
3. [Layout, alignment i niezainicjalizowana pamięć](03_layout_alignment_i_uninitialized_memory.md)
4. [Variance, subtyping i drop check](04_variance_subtyping_i_dropck.md)

### Zaawansowany system typów

5. [HRTB, GAT, RPIT i `impl Trait`](05_hrtb_gat_rpit_i_impl_trait.md)
6. [Dyn compatibility, vtables i dispatch](06_dyn_compatibility_vtables_i_dispatch.md)
7. [`Pin`, `Unpin` i typy self-referential](07_pin_unpin_i_self_referential.md)

### Współbieżność niskopoziomowa

8. [Atomiki i memory ordering](08_atomics_i_memory_ordering.md)
9. [Lock-free i problem ABA](09_lock_free_i_aba.md)

### Granice kompilatora i platformy

10. [Zaawansowane makra proceduralne](10_zaawansowane_makra_proceduralne.md)
11. [FFI, bezpieczne otoczki i UB](11_ffi_safe_wrappers_i_ub.md)
12. [`no_std`, allocatory i embedded](12_no_std_allocatory_i_embedded.md)
13. [Monomorfizacja, MIR, LLVM i optymalizacja](13_monomorfizacja_mir_llvm_i_optymalizacja.md)
14. [Borrow checker, Polonius i model pamięci](14_borrow_checker_polonius_i_model_pamieci.md)
15. [Nightly, unstable i feature gates](15_nightly_unstable_i_feature_gates.md)

## Jak czytać przykłady

Fragment pokazujący potencjalne undefined behavior jest blokiem `text` i nie
należy go uruchamiać. Blok `rust` lub `no_run` ma kompletne preconditions albo
nie wykonuje ryzykownej operacji. Komentarz `SAFETY` powinien uzasadniać
konkretne wywołanie, a nie mówić ogólnie „to jest bezpieczne”.

## Granice wiedzy

Rust Reference jest najbardziej szczegółowym oficjalnym opisem języka, lecz
nie jest formalną specyfikacją. Pełne reguły aliasingu i model pamięci nadal
są rozwijane. Gdy dokumentacja biblioteki standardowej podaje preconditions
konkretnej funkcji, są one ważniejsze niż uproszczony model mentalny z
podręcznika.

Sprawdzaj kod przez testy, Miri, sanitizery i przegląd, ale żadne pojedyncze
narzędzie nie dowodzi braku UB. Minimalizuj powierzchnię `unsafe` i testuj
bezpieczne API z nieprzyjaznymi wejściami.

## Powiązane tematy

- [Pamięć i własność](../03_pamiec_i_wlasnosc/01_stos_sterta_i_raii.md)
- [Traits i modelowanie](../04_typy_i_modelowanie/04_traits_i_associated_items.md)
- [Benchmarki, profilowanie i Miri](../08_testowanie_i_jakosc/04_benchmarki_profilowanie_i_miri.md)
- [Źródła](../zrodla.md)
