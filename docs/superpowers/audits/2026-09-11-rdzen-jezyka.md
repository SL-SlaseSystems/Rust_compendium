# Audyt stanu początkowego: rdzeń języka Rust

Data audytu: 2026-09-11. Zakres obejmuje 20 rozdziałów z katalogów
`01_wprowadzenie`–`04_typy_i_modelowanie`; macierz jest wejściem dla Tasks 4–23.
Docelowy stan: **Edition 2024 i Rust 1.98.1 — sprawdzone 2026-09-10**.

## Kontrola bazowa

- Lokalny kompilator: `rustc 1.90.0 (1159e78c4 2025-09-14)`.
- `bash scripts/verify.sh`: **FAIL, kod 1**. Weryfikator zakończył się przed
  uruchomieniem `rustdoc`, zgłaszając: `.superpowers/sdd/2026-09-11-rozbudowa-kompendium-rust-etap-1-rdzen-jezyka/progress.md: brak linku powrotnego na początku` oraz
  `.superpowers/sdd/2026-09-11-rozbudowa-kompendium-rust-etap-1-rdzen-jezyka/task-1-brief.md: brak linku powrotnego na początku`.
- Wynik bazowego weryfikatora nie zawiera ostrzeżeń kompilatora, ponieważ faza
  testów `rustdoc` nie została osiągnięta.
- Dodatkowa sonda istniejącego atlasu (bez jego modyfikowania):
  `rustdoc --test --edition 2024 150-zaawansowanych-mechanizmow-rust.md` po
  30 s nadal wykonywał 147 testów, raportując już m.in. błędne przykłady
  zależne od zewnętrznych crate'ów i nowszego API; proces przerwano sygnałem
  `SIGINT` (kod 130). Pełny `verify.sh` nie doszedł do tego miejsca z powodu
  wcześniejszych błędów linków, lecz atlas pozostaje znanym długotrwałym i
  niestabilnym elementem kontroli bazowej.

## Macierz braków

`Stan` zawiera liczbę linii z pomiaru `wc -l`; „szkic” oznacza, że rozdział
ma podstawowe przykłady i odsyłacze, ale nie pokrywa zaplanowanego modelu,
diagnostyki ani ćwiczeń z rozwiązaniami. Priorytety `P1` odpowiadają kolejności
Tasks 4–23.

Terminologia przy pierwszym użyciu: bezpieczeństwo pamięci (*safety*),
własność zasobu (*ownership*), brak wyścigów danych (*data-race freedom*),
kompilacja z wyprzedzeniem (*AOT*) i zestaw narzędzi (*toolchain*).
Pozostałe angielskie określenia opisowe znaczą odpowiednio: *resolver* —
mechanizm rozwiązywania wersji zależności; *profile* — profil kompilacji;
*lockfile* — plik blokady zależności; *drop scope* — zakres niszczenia wartości;
*freeze* — czasowe unieruchomienie przez pożyczkę; *fat pointer* — wskaźnik
z metadanymi; *code bloat* — wzrost rozmiaru kodu; *deadlock* — zakleszczenie;
*newtype* — jednoelementowy typ opakowujący. Nazwy składni i API Rusta, takie
jak `trait`, `crate`, `target`, `static mut` oraz `impl Trait`, pozostają
identyfikatorami kodu.
Skróty i narzędzia: `GC` to odśmiecacz pamięci, `LLVM` — zaplecze generowania
kodu, *override* — lokalne nadpisanie ustawień, *offline docs* — dokumentacja
dostępna bez sieci, *component* — składnik zestawu narzędzi, `CI` — ciągła
integracja, `MSRV` — minimalna wspierana wersja Rusta, a *linker* — program
łączący wynik kompilacji. Terminy semantyki użyte dalej mają następujące
znaczenia: *crate root* — moduł główny pakietu, *prelude* — automatycznie
importowany zestaw nazw, *borrow* — pożyczka, *coercion* — niejawne
dostosowanie typu, *reallocation* — ponowna alokacja, *layout* — układ w
pamięci, *lifetime* — czas życia referencji, a *object lifetime* — czas życia
obiektu cechy. Pozostałe nazwy zapisywane krojem kodu są nazwami składni,
traitów lub API.

| plik | stan | najważniejsze braki | oficjalne źródła | priorytet |
|---|---|---|---|---|
| 01_wprowadzenie/01_czym_jest_rust.md | 64 linii; szkic | brak bezpieczeństwa bez `GC`, własności jako protokołu zasobów, braku wyścigów danych, kompilacji z wyprzedzeniem (`AOT`)/`LLVM`, kosztów kompilacji i ćwiczeń `W01-1`–`W01-3` | [The Book, wprowadzenie](https://doc.rust-lang.org/book/ch00-00-introduction.html); [Rust Reference](https://doc.rust-lang.org/reference/) | P1 / Task 4 |
| 01_wprowadzenie/02_instalacja_i_toolchain.md | 98 linii; częściowe pokrycie | brak datowanych zestawów narzędzi, katalogowego nadpisania ustawień, dokumentacji dostępnej bez sieci, rozróżnienia `cargo install`/składnika, `CI` i diagnostyki `target`, programu linkującego oraz `MSRV`; brak `W02-1`–`W02-3` | [rustup book](https://rust-lang.github.io/rustup/); [rustc book: targets](https://doc.rust-lang.org/rustc/targets/) | P1 / Task 5 |
| 01_wprowadzenie/03_pierwszy_program.md | 84 linii; szkic | brak `crate root` i `prelude`, pełnego modelu etapów kompilacji (`MIR`, generowania kodu, linkowania), diagnostyki średnika/makra i ćwiczeń `W03-1`–`W03-3` | [The Book, program](https://doc.rust-lang.org/book/ch01-02-hello-world.html); [rustc dev guide: compilation](https://rustc-dev-guide.rust-lang.org/overview.html) | P1 / Task 6 |
| 01_wprowadzenie/04_cargo_w_praktyce.md | 94 linii; częściowe pokrycie | brak mechanizmu rozwiązywania zależności, typów zależności, profili i polityki pliku blokady, pełnej pętli jakości oraz diagnostyki konfliktu/`target`; brak `W04-1`–`W04-3` | [Cargo Book](https://doc.rust-lang.org/cargo/); [Cargo reference](https://doc.rust-lang.org/cargo/reference/) | P1 / Task 7 |
| 02_podstawy_jezyka/01_zmienne_stale_i_shadowing.md | 96 linii; częściowe pokrycie | brak wzorców w `let`, inicjalizacji odroczonej, `static mut` wymagającego kodu `unsafe`, zakresu niszczenia, `NLL` i konkretnych E0381/E0384; brak `P01-1`–`P01-3` | [Reference: variables](https://doc.rust-lang.org/reference/variables.html); [Reference: destructors](https://doc.rust-lang.org/reference/destructors.html) | P1 / Task 8 |
| 02_podstawy_jezyka/02_typy_i_konwersje.md | 89 linii; częściowe pokrycie | brak pełnych typów liczbowych i przyrostków, przepełnienia w profilach `debug`/`release` oraz metod arytmetyki, `char`/`unit`/`never`, `TryFrom`, parsowania i `turbofish`; brak `P02-1`–`P02-3` | [The Book, typy danych](https://doc.rust-lang.org/book/ch03-02-data-types.html); [Reference: type casts](https://doc.rust-lang.org/reference/expressions/operator-expr.html#type-cast-expressions) | P1 / Task 9 |
| 02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md | 101 linii; częściowe pokrycie | brak elementu/instrukcji/wyrażenia, nieobalalnych wzorców parametrów, konwencji binarnej wywołania (`ABI`) i ograniczeń `inline`, bloku skracającego pożyczkę oraz diagnostyki niejawnej konwersji/nieosiągalności; brak `P03-1`–`P03-3` | [Reference: functions](https://doc.rust-lang.org/reference/items/functions.html); [Reference: expressions](https://doc.rust-lang.org/reference/expressions.html) | P1 / Task 10 |
| 02_podstawy_jezyka/04_sterowanie_przeplywem.md | 112 linii; częściowe pokrycie | brak etykiet, `while let`, `IntoIterator`, zakresów, stabilnych `let chains` oraz porównania `iter`/`iter_mut`/`into_iter`; brak `P04-1`–`P04-3` | [The Book, control flow](https://doc.rust-lang.org/book/ch03-05-control-flow.html); [Reference: loop expressions](https://doc.rust-lang.org/reference/expressions/loop-expr.html) | P1 / Task 11 |
| 02_podstawy_jezyka/05_operatory_komentarze_i_atrybuty.md | 99 linii; częściowe pokrycie | brak krótkiego spięcia, cech operatorów, `?`, surowej pożyczki, komentarzy dokumentacyjnych, `cfg`, poziomów `lint`, `repr` i atrybutów `unsafe` w Edition 2024; brak `P05-1`–`P05-3` | [Reference: operators](https://doc.rust-lang.org/reference/expressions/operator-expr.html); [Reference: attributes](https://doc.rust-lang.org/reference/attributes.html) | P1 / Task 12 |
| 03_pamiec_i_wlasnosc/01_stos_sterta_i_raii.md | 95 linii; częściowe pokrycie | brak układu w pamięci wartości kontra bufora, `ZST`, kolejności pól/wiązań, `String`/`Vec` z ponowną alokacją, granic API/implementacji i ćwiczeń `O01-1`–`O01-3` | [The Book, ownership](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html); [Reference: destructors](https://doc.rust-lang.org/reference/destructors.html) | P1 / Task 13 |
| 03_pamiec_i_wlasnosc/02_ownership_move_i_copy.md | 104 linii; częściowe pokrycie | brak wyrażeń miejsca/wartości, ścieżek przeniesienia i flag niszczenia jako modeli, przypisania niszczącego starą wartość, projektowania API `T`/`&T`/`&mut T`/`Into<T>` oraz `O02-1`–`O02-4` | [The Book, ownership](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html); [Reference: expressions](https://doc.rust-lang.org/reference/expressions.html) | P1 / Task 14 |
| 03_pamiec_i_wlasnosc/03_referencje_i_borrowing.md | 97 linii; częściowe pokrycie | brak zamrożenia, wymuszeń przez `Deref`, `NLL`, dwufazowych pożyczek, rozdzielnych pożyczek pól i mutacji podczas iteracji; brak `O03-1`–`O03-4` | [The Book, references](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html); [Rustonomicon: aliasing](https://doc.rust-lang.org/nomicon/aliasing.html) | P1 / Task 15 |
| 03_pamiec_i_wlasnosc/04_slices_i_str.md | 101 linii; częściowe pokrycie | brak szerokiego wskaźnika jako modelu `DST`, `split_at_mut`, porównania bajtów/wartości skalarnych/klastrów grafemów, wyniku pożyczonego/własnego i ćwiczeń `O04-1`–`O04-3` | [The Book, slices](https://doc.rust-lang.org/book/ch04-03-slices.html); [Reference: DST](https://doc.rust-lang.org/reference/dynamically-sized-types.html) | P1 / Task 16 |
| 03_pamiec_i_wlasnosc/05_lifetimes.md | 105 linii; częściowe pokrycie | brak niezależnych czasów życia, metody zwracającej pole, iteratora po pożyczonych danych, `HRTB` jako zapowiedzi, tymczasowego wydłużenia czasu życia i ćwiczeń `O05-1`–`O05-4` | [The Book, lifetimes](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html); [Reference: lifetime elision](https://doc.rust-lang.org/reference/lifetime-elision.html) | P1 / Task 17 |
| 03_pamiec_i_wlasnosc/06_smart_pointery_i_interior_mutability.md | 96 linii; częściowe pokrycie | brak `Arc`, `Cell`, `Mutex`, `RwLock`, `Cow` i `Pin`, kosztów synchronizacji, drzewa z `Weak`, pamięci podręcznej z `RefCell`, zakleszczenia i ćwiczeń `O06-1`–`O06-4` | [The Book, smart pointers](https://doc.rust-lang.org/book/ch15-00-smart-pointers.html); [std::sync](https://doc.rust-lang.org/std/sync/) | P1 / Task 18 |
| 04_typy_i_modelowanie/01_struktury_enumy_i_metody.md | 119 linii; częściowe pokrycie | brak typów iloczynowych/sumowych, struktur krotkowych/jednostkowych, wartości rozróżniających bez obietnicy układu w pamięci, prywatnych pól z konstruktorem, typu opakowującego i `non_exhaustive` oraz `T01-1`–`T01-4` | [The Book, structs](https://doc.rust-lang.org/book/ch05-00-structs.html); [The Book, enums](https://doc.rust-lang.org/book/ch06-00-enums.html) | P1 / Task 19 |
| 04_typy_i_modelowanie/02_wzorce_i_match.md | 110 linii; częściowe pokrycie | brak `..`, `@`, zakresów, wzorców alternatywnych, strażników, trybów wiązań, ergonomii `match`, `match` po `&mut T` i diagnostyki nieosiągalnego wzorca; brak `T02-1`–`T02-4` | [The Book, patterns](https://doc.rust-lang.org/book/ch19-00-patterns.html); [Reference: patterns](https://doc.rust-lang.org/reference/patterns.html) | P1 / Task 20 |
| 04_typy_i_modelowanie/03_generics_i_const_generics.md | 104 linii; częściowe pokrycie | brak parametrów czasu życia, `where`, wartości domyślnych, wzrostu rozmiaru kodu i granic inferencji, typu fantomowego, tożsamości typu z `const` oraz generycznych wyrażeń stałych; brak `T03-1`–`T03-4` | [The Book, generics](https://doc.rust-lang.org/book/ch10-00-generics.html); [Reference: const generics](https://doc.rust-lang.org/reference/items/generics.html#const-generics) | P1 / Task 21 |
| 04_typy_i_modelowanie/04_traits_i_associated_items.md | 127 linii; częściowe pokrycie | brak implementacji ogólnych, `Self`/`Sized`/`?Sized`, automatycznych cech, `impl Trait` kontra typu nazwanego, cechy rozszerzającej i typu opakowującego; nieoddzielone stabilne przypadki od `nightly`, ujemnych granic i specjalizacji; brak `T04-1`–`T04-5` | [The Book, traits](https://doc.rust-lang.org/book/ch10-02-traits.html); [Reference: traits](https://doc.rust-lang.org/reference/items/traits.html) | P1 / Task 22 |
| 04_typy_i_modelowanie/05_konwersje_dst_i_trait_objects.md | 100 linii; częściowe pokrycie | brak `AsRef`/`Borrow`, osłabiania wskaźnika i konwersji do typu o nieznanym rozmiarze, `Sized`/`?Sized`, zgodności z `dyn` i czasu życia obiektu, porównania `impl Trait`/`T`/`&dyn Trait`/`Box<dyn Trait>` oraz `T05-1`–`T05-5` | [The Book, trait objects](https://doc.rust-lang.org/book/ch18-02-trait-objects.html); [Reference: trait objects](https://doc.rust-lang.org/reference/types/trait-object.html) | P1 / Task 23 |

## Ryzyka dla kolejnych zadań

- Dokumentacja celu opisuje Rust 1.98.1, natomiast lokalny zestaw narzędzi to
  1.90.0.
  Twierdzenia zależne od wydania trzeba oznaczać; nie wolno ich przedstawiać
  jako sprawdzonych na 1.98.1 bez takiego zestawu narzędzi.
- Atlas `150-zaawansowanych-mechanizmow-rust.md` dubluje część materiału
  rozdziałów 01–04. Rozdziały powinny być źródłem pełnego wyjaśnienia, a atlas
  krótkim odsyłaczem, aby nie powstały sprzeczne kopie.
- Rustonomicon jest pomocniczy dla `unsafe`, ale jego szczegóły mogą być
  przestarzałe. Dla normatywnych reguł pierwszeństwo mają Rust Reference i
  aktualne API biblioteki standardowej.
