[← Spis treści](../../../README.md)

# Raport Task 1 — pogłębienie działów 01–06

Data: 11 listopada 2026 r. Zakres autora: wyłącznie działy 01–06, równoległe rozwiązania i ten raport. Nie zmieniano Git ani plików wspólnych.

## Zrealizowany zakres

- Pogłębiono wszystkie 28 istniejących rozdziałów, zachowując ścieżki oraz wartościową wcześniejszą treść.
- Każdy rozdział ma marker `expanded` w drugim wierszu, mierzalne cele, model, poprawny Rust, objaśnione `compile_fail`, praktykę produkcyjną, pytania i trzy zadania z pełnymi rozwiązaniami.
- Zachowano 21 zadań `W01-1`–`W04-3` oraz `P01-1`–`P03-3`. Dopisano 63 zadania z prefiksami `A08`–`A28`; łącznie 84 identyfikatory są unikalne w zakresie.
- Dodano 21 plików rozwiązań i pogłębiono 7 istniejących. Każdy ma poprawny backlink i dokładne nagłówki identyfikatorów.
- Zaktualizowano 6 map: tok lektury, zadania, punkt kontrolny, rezultat oraz link do kolejnego działu.
- Doprecyzowano m.in. bliskość override rustup, minimum Edition 2024, nagłówek `String` bez gwarancji fizycznego stosu, guardy i `Drop`, oddawanie konsumowanego wejścia przy błędzie, `Rc::get_mut`, exact-size jako bezpieczny kontrakt, capture RPIT i rozdzielenie `move` od `FnOnce`.

Rozdziały mają 786–1948 słów (mediana 1013; suma 30139). Większa objętość rozdziału o funkcjach zachowuje jego wcześniejsze szczegółowe omówienie ABI i typów elementów funkcyjnych.

## Faktycznie wykonana weryfikacja

1. Wczytano istniejący `scripts/verify_content.py` i uruchomiono `validate_markdown` na 62 plikach własnego zakresu. Wynik: **0 problemów**.
2. Dodatkowo sprawdzono drugi wiersz markera każdego z 28 rozdziałów, obecność `compile_fail`, dokładnie trzy identyfikatory ćwiczeń oraz ich unikalność: **84/84**.
3. Wykonano `rustdoc --test --edition 2024 PLIK` dla 56 plików rozdziałów i rozwiązań. Ostatni przebieg po uzupełnieniu istniejących rozwiązań: **56/56 plików, 230 testów zaliczonych, 0 błędów, 0 pominiętych**. W tej liczbie jest 192 zwykłych bloków Rust, 37 `compile_fail` oraz 1 `rust,no_run` kompilowany bez wykonania.
4. Po podstawowym przebiegu poprawiono prozę i linki oraz ponowiono walidację struktury i identyfikatorów: **0 problemów**. Późniejsze uzupełnienie trzech mechanizmów atlasu oraz jego osobne testy opisano poniżej.

Rzeczywiste narzędzia: `rustc 1.90.0 (1159e78c4 2025-09-14)` oraz `rustdoc 1.90.0 (1159e78c4 2025-09-14)`. Testy ustawiają jednorazowo `SDKROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk`. Nie zmieniano konfiguracji systemowej. Domyślny SDK 27 koliduje z dostępnym linkerem; rozwiązanie środowiskowe przekazał koordynator.

Powtórzenie testu pojedynczego pliku:

~~~text
SDKROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk rustdoc --test --edition 2024 03_ownership_i_pamiec/03_referencje_i_borrowing.md
~~~

## Źródła pierwotne

Źródła otwierano w narzędziu web 11 listopada 2026 r.; odsyłacze dodano także w tematycznych rozdziałach. Bieżąca internetowa dokumentacja API może prezentować nowszą wersję niż lokalny kompilator; zgodność przykładów z 1.90 potwierdzają wykonane doctesty, a nie numer nagłówka strony.

- Rust Reference: [type system](https://doc.rust-lang.org/reference/type-system.html), [traits](https://doc.rust-lang.org/reference/items/traits.html), [implementations/coherence](https://doc.rust-lang.org/reference/items/implementations.html), [impl Trait](https://doc.rust-lang.org/reference/types/impl-trait.html), [subtyping](https://doc.rust-lang.org/reference/subtyping.html), [generic parameters](https://doc.rust-lang.org/reference/items/generics.html).
- Rust Reference: [destructors](https://doc.rust-lang.org/reference/destructors.html), [patterns](https://doc.rust-lang.org/reference/patterns.html), [closure types](https://doc.rust-lang.org/reference/types/closure.html), [type coercions](https://doc.rust-lang.org/reference/type-coercions.html), [structs](https://doc.rust-lang.org/reference/items/structs.html), [enumerations](https://doc.rust-lang.org/reference/items/enumerations.html).
- Rust Reference: [loop expressions](https://doc.rust-lang.org/reference/expressions/loop-expr.html), [statements](https://doc.rust-lang.org/reference/statements.html), [conditional compilation](https://doc.rust-lang.org/reference/conditional-compilation.html), [diagnostics](https://doc.rust-lang.org/reference/attributes/diagnostics.html), [unsafety](https://doc.rust-lang.org/reference/unsafety.html).
- Rust Edition Guide: [Rust 2024 i wydanie 1.85](https://doc.rust-lang.org/edition-guide/rust-2024/index.html), [RPIT lifetime capture](https://doc.rust-lang.org/edition-guide/rust-2024/rpit-lifetime-capture.html), [match ergonomics](https://doc.rust-lang.org/edition-guide/rust-2024/match-ergonomics.html).
- Rustup Book: [overrides](https://rust-lang.github.io/rustup/overrides.html) i [components](https://rust-lang.github.io/rustup/concepts/components.html). Cargo Book: [resolver](https://doc.rust-lang.org/cargo/reference/resolver.html).
- API `std`: [collections](https://doc.rust-lang.org/std/collections/index.html), [Vec](https://doc.rust-lang.org/std/vec/struct.Vec.html), [HashMap](https://doc.rust-lang.org/std/collections/struct.HashMap.html), [String](https://doc.rust-lang.org/std/string/struct.String.html), [from_utf8](https://doc.rust-lang.org/std/str/fn.from_utf8.html), [cell](https://doc.rust-lang.org/std/cell/index.html), [Rc](https://doc.rust-lang.org/std/rc/struct.Rc.html), [Borrow](https://doc.rust-lang.org/std/borrow/trait.Borrow.html).
- API `std`: [Iterator](https://doc.rust-lang.org/std/iter/trait.Iterator.html), [ExactSizeIterator](https://doc.rust-lang.org/std/iter/trait.ExactSizeIterator.html), [Copy](https://doc.rust-lang.org/std/marker/trait.Copy.html), [Any](https://doc.rust-lang.org/std/any/trait.Any.html), [Termination](https://doc.rust-lang.org/std/process/trait.Termination.html).
- Granice eksperymentalne: [TAIT](https://doc.rust-lang.org/unstable-book/language-features/type-alias-impl-trait.html), [generic_const_exprs](https://doc.rust-lang.org/unstable-book/language-features/generic-const-exprs.html); uzupełnienie modelu destrukcji: [Rustonomicon dropck](https://doc.rust-lang.org/nomicon/dropck.html).

## Domknięcie kanonicznych odsyłaczy atlasu

Na prośbę koordynatora dodano trzy konkretne podsekcje, bez nowych plików ani zmiany identyfikatorów zadań:

- `06_kolekcje_iteratory_i_closures/04_closures_i_fn_traits.md`: `AsyncFn`, `AsyncFnMut` i `AsyncFnOnce`, pożyczanie środowiska przez zwracany future, różnica wobec `Fn() -> Fut`, stabilna składnia callbacku oraz przykład dwóch kolejnych `await` z jawnym jednorazowym pollingiem operacji natychmiast gotowych.
- `02_podstawy_jezyka/05_operatory_komentarze_i_atrybuty.md`: `#[track_caller]`, `Location::caller`, propagowanie lokalizacji przez warstwy, ograniczenie przy wskaźniku `fn` oraz sprawdzenie miejsca wywołania przez `line!()` i `file!()`.
- `05_generics_traits_i_system_typow/03_konwersje_dst_i_trait_objects.md`: `Cow<'a, str>`, rozróżnienie `Borrowed`/`Owned`, kopiowanie w `to_mut`, ponowna mutacja posiadanej wartości oraz `into_owned` i zachowanie oryginału.

Po zmianie uruchomiono tylko te trzy pliki przez identyczną komendę rustdoc i identyczny `SDKROOT`: **8 + 6 + 6 = 20 testów, wszystkie zaliczone**, w tym 3 nowe programy. Lokalna walidacja dokładnie tych trzech plików: **0 problemów**. Aktualny zakres ma łącznie 233 różne bloki testowe; pozostałe pliki nie zmieniły się od pełnego przebiegu 230 testów.

Dodatkowo otwarto źródła pierwotne: [AsyncFn](https://doc.rust-lang.org/std/ops/trait.AsyncFn.html), [Cow](https://doc.rust-lang.org/std/borrow/enum.Cow.html), [Reference: track_caller](https://doc.rust-lang.org/reference/attributes/codegen.html#the-track_caller-attribute) oraz [Location::caller](https://doc.rust-lang.org/std/panic/struct.Location.html#method.caller). Data weryfikacji: 11 listopada 2026 r. Przykład `AsyncFn` nie jest uniwersalnym wykonawcą I/O; `Waker::noop` służy wyłącznie do pokazanej natychmiast gotowej przyszłości.

## Ograniczenia weryfikacji

Nie instalowano ani nie uruchamiano Rust 1.98.1, nightly, bibliotek zewnętrznych ani targetów cross-kompilacji. Manifesty i polecenia środowiskowe są blokami `text`, a nie deklaracją przeprowadzenia ich pełnego scenariusza. Test typu callbacku `extern "C"` nie dowodzi kompletnej integracji z biblioteką obcą. Testy `unsafe` są przykładami zachowania, nie dowodem soundness dla dowolnego klienta. Nie uruchamiano pełnego `bash scripts/verify.sh`, ponieważ zakresy pozostałych działów były równolegle edytowane; pełna integracja należy do Task 5 koordynatora.

## Pliki rozdziałów

- [01_wprowadzenie_i_toolchain/01_czym_jest_rust.md](../../../01_wprowadzenie_i_toolchain/01_czym_jest_rust.md)
- [01_wprowadzenie_i_toolchain/02_instalacja_i_toolchain.md](../../../01_wprowadzenie_i_toolchain/02_instalacja_i_toolchain.md)
- [01_wprowadzenie_i_toolchain/03_pierwszy_program.md](../../../01_wprowadzenie_i_toolchain/03_pierwszy_program.md)
- [01_wprowadzenie_i_toolchain/04_cargo_w_praktyce.md](../../../01_wprowadzenie_i_toolchain/04_cargo_w_praktyce.md)
- [02_podstawy_jezyka/01_zmienne_stale_i_shadowing.md](../../../02_podstawy_jezyka/01_zmienne_stale_i_shadowing.md)
- [02_podstawy_jezyka/02_typy_i_konwersje.md](../../../02_podstawy_jezyka/02_typy_i_konwersje.md)
- [02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md](../../../02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md)
- [02_podstawy_jezyka/04_sterowanie_przeplywem.md](../../../02_podstawy_jezyka/04_sterowanie_przeplywem.md)
- [02_podstawy_jezyka/05_operatory_komentarze_i_atrybuty.md](../../../02_podstawy_jezyka/05_operatory_komentarze_i_atrybuty.md)
- [03_ownership_i_pamiec/01_stos_sterta_i_raii.md](../../../03_ownership_i_pamiec/01_stos_sterta_i_raii.md)
- [03_ownership_i_pamiec/02_ownership_move_i_copy.md](../../../03_ownership_i_pamiec/02_ownership_move_i_copy.md)
- [03_ownership_i_pamiec/03_referencje_i_borrowing.md](../../../03_ownership_i_pamiec/03_referencje_i_borrowing.md)
- [03_ownership_i_pamiec/04_slices_i_str.md](../../../03_ownership_i_pamiec/04_slices_i_str.md)
- [03_ownership_i_pamiec/05_lifetimes.md](../../../03_ownership_i_pamiec/05_lifetimes.md)
- [03_ownership_i_pamiec/06_smart_pointery_i_interior_mutability.md](../../../03_ownership_i_pamiec/06_smart_pointery_i_interior_mutability.md)
- [04_struktury_enumy_i_wzorce/01_struktury_enumy_i_metody.md](../../../04_struktury_enumy_i_wzorce/01_struktury_enumy_i_metody.md)
- [04_struktury_enumy_i_wzorce/02_wzorce_i_match.md](../../../04_struktury_enumy_i_wzorce/02_wzorce_i_match.md)
- [05_generics_traits_i_system_typow/01_generics_i_const_generics.md](../../../05_generics_traits_i_system_typow/01_generics_i_const_generics.md)
- [05_generics_traits_i_system_typow/02_traits_i_associated_items.md](../../../05_generics_traits_i_system_typow/02_traits_i_associated_items.md)
- [05_generics_traits_i_system_typow/03_konwersje_dst_i_trait_objects.md](../../../05_generics_traits_i_system_typow/03_konwersje_dst_i_trait_objects.md)
- [05_generics_traits_i_system_typow/04_variance_subtyping_i_dropck.md](../../../05_generics_traits_i_system_typow/04_variance_subtyping_i_dropck.md)
- [05_generics_traits_i_system_typow/05_hrtb_gat_rpit_i_impl_trait.md](../../../05_generics_traits_i_system_typow/05_hrtb_gat_rpit_i_impl_trait.md)
- [05_generics_traits_i_system_typow/06_dyn_compatibility_vtables_i_dispatch.md](../../../05_generics_traits_i_system_typow/06_dyn_compatibility_vtables_i_dispatch.md)
- [06_kolekcje_iteratory_i_closures/01_tablice_wektory_i_sekwencje.md](../../../06_kolekcje_iteratory_i_closures/01_tablice_wektory_i_sekwencje.md)
- [06_kolekcje_iteratory_i_closures/02_string_str_i_unicode.md](../../../06_kolekcje_iteratory_i_closures/02_string_str_i_unicode.md)
- [06_kolekcje_iteratory_i_closures/03_mapy_zbiory_i_entry.md](../../../06_kolekcje_iteratory_i_closures/03_mapy_zbiory_i_entry.md)
- [06_kolekcje_iteratory_i_closures/04_closures_i_fn_traits.md](../../../06_kolekcje_iteratory_i_closures/04_closures_i_fn_traits.md)
- [06_kolekcje_iteratory_i_closures/05_iteratory.md](../../../06_kolekcje_iteratory_i_closures/05_iteratory.md)

## Mapy działów

- [01_wprowadzenie_i_toolchain/README.md](../../../01_wprowadzenie_i_toolchain/README.md)
- [02_podstawy_jezyka/README.md](../../../02_podstawy_jezyka/README.md)
- [03_ownership_i_pamiec/README.md](../../../03_ownership_i_pamiec/README.md)
- [04_struktury_enumy_i_wzorce/README.md](../../../04_struktury_enumy_i_wzorce/README.md)
- [05_generics_traits_i_system_typow/README.md](../../../05_generics_traits_i_system_typow/README.md)
- [06_kolekcje_iteratory_i_closures/README.md](../../../06_kolekcje_iteratory_i_closures/README.md)

## Pliki rozwiązań

- [rozwiazania/01_wprowadzenie_i_toolchain/01_czym_jest_rust.md](../../../rozwiazania/01_wprowadzenie_i_toolchain/01_czym_jest_rust.md)
- [rozwiazania/01_wprowadzenie_i_toolchain/02_instalacja_i_toolchain.md](../../../rozwiazania/01_wprowadzenie_i_toolchain/02_instalacja_i_toolchain.md)
- [rozwiazania/01_wprowadzenie_i_toolchain/03_pierwszy_program.md](../../../rozwiazania/01_wprowadzenie_i_toolchain/03_pierwszy_program.md)
- [rozwiazania/01_wprowadzenie_i_toolchain/04_cargo_w_praktyce.md](../../../rozwiazania/01_wprowadzenie_i_toolchain/04_cargo_w_praktyce.md)
- [rozwiazania/02_podstawy_jezyka/01_zmienne_stale_i_shadowing.md](../../../rozwiazania/02_podstawy_jezyka/01_zmienne_stale_i_shadowing.md)
- [rozwiazania/02_podstawy_jezyka/02_typy_i_konwersje.md](../../../rozwiazania/02_podstawy_jezyka/02_typy_i_konwersje.md)
- [rozwiazania/02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md](../../../rozwiazania/02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md)
- [rozwiazania/02_podstawy_jezyka/04_sterowanie_przeplywem.md](../../../rozwiazania/02_podstawy_jezyka/04_sterowanie_przeplywem.md)
- [rozwiazania/02_podstawy_jezyka/05_operatory_komentarze_i_atrybuty.md](../../../rozwiazania/02_podstawy_jezyka/05_operatory_komentarze_i_atrybuty.md)
- [rozwiazania/03_ownership_i_pamiec/01_stos_sterta_i_raii.md](../../../rozwiazania/03_ownership_i_pamiec/01_stos_sterta_i_raii.md)
- [rozwiazania/03_ownership_i_pamiec/02_ownership_move_i_copy.md](../../../rozwiazania/03_ownership_i_pamiec/02_ownership_move_i_copy.md)
- [rozwiazania/03_ownership_i_pamiec/03_referencje_i_borrowing.md](../../../rozwiazania/03_ownership_i_pamiec/03_referencje_i_borrowing.md)
- [rozwiazania/03_ownership_i_pamiec/04_slices_i_str.md](../../../rozwiazania/03_ownership_i_pamiec/04_slices_i_str.md)
- [rozwiazania/03_ownership_i_pamiec/05_lifetimes.md](../../../rozwiazania/03_ownership_i_pamiec/05_lifetimes.md)
- [rozwiazania/03_ownership_i_pamiec/06_smart_pointery_i_interior_mutability.md](../../../rozwiazania/03_ownership_i_pamiec/06_smart_pointery_i_interior_mutability.md)
- [rozwiazania/04_struktury_enumy_i_wzorce/01_struktury_enumy_i_metody.md](../../../rozwiazania/04_struktury_enumy_i_wzorce/01_struktury_enumy_i_metody.md)
- [rozwiazania/04_struktury_enumy_i_wzorce/02_wzorce_i_match.md](../../../rozwiazania/04_struktury_enumy_i_wzorce/02_wzorce_i_match.md)
- [rozwiazania/05_generics_traits_i_system_typow/01_generics_i_const_generics.md](../../../rozwiazania/05_generics_traits_i_system_typow/01_generics_i_const_generics.md)
- [rozwiazania/05_generics_traits_i_system_typow/02_traits_i_associated_items.md](../../../rozwiazania/05_generics_traits_i_system_typow/02_traits_i_associated_items.md)
- [rozwiazania/05_generics_traits_i_system_typow/03_konwersje_dst_i_trait_objects.md](../../../rozwiazania/05_generics_traits_i_system_typow/03_konwersje_dst_i_trait_objects.md)
- [rozwiazania/05_generics_traits_i_system_typow/04_variance_subtyping_i_dropck.md](../../../rozwiazania/05_generics_traits_i_system_typow/04_variance_subtyping_i_dropck.md)
- [rozwiazania/05_generics_traits_i_system_typow/05_hrtb_gat_rpit_i_impl_trait.md](../../../rozwiazania/05_generics_traits_i_system_typow/05_hrtb_gat_rpit_i_impl_trait.md)
- [rozwiazania/05_generics_traits_i_system_typow/06_dyn_compatibility_vtables_i_dispatch.md](../../../rozwiazania/05_generics_traits_i_system_typow/06_dyn_compatibility_vtables_i_dispatch.md)
- [rozwiazania/06_kolekcje_iteratory_i_closures/01_tablice_wektory_i_sekwencje.md](../../../rozwiazania/06_kolekcje_iteratory_i_closures/01_tablice_wektory_i_sekwencje.md)
- [rozwiazania/06_kolekcje_iteratory_i_closures/02_string_str_i_unicode.md](../../../rozwiazania/06_kolekcje_iteratory_i_closures/02_string_str_i_unicode.md)
- [rozwiazania/06_kolekcje_iteratory_i_closures/03_mapy_zbiory_i_entry.md](../../../rozwiazania/06_kolekcje_iteratory_i_closures/03_mapy_zbiory_i_entry.md)
- [rozwiazania/06_kolekcje_iteratory_i_closures/04_closures_i_fn_traits.md](../../../rozwiazania/06_kolekcje_iteratory_i_closures/04_closures_i_fn_traits.md)
- [rozwiazania/06_kolekcje_iteratory_i_closures/05_iteratory.md](../../../rozwiazania/06_kolekcje_iteratory_i_closures/05_iteratory.md)

## Powiązane tematy

- [Plan wykonania](../plans/2026-11-11-poglebienie-30-dzialow.md)
- [Zasady współtworzenia](../../../CONTRIBUTING.md)
