# Rozbudowa kompendium Rust — etap 1: rdzeń języka Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ustanowić rygor rozbudowy i pogłębić działy 01–04 od wprowadzenia przez ownership do traits i trait objects, wraz z ćwiczeniami, rozwiązaniami oraz automatyczną walidacją.

**Architecture:** Jest to pierwszy z siedmiu niezależnie odbieranych etapów. Rozdziały są rozszerzane w miejscu i oznaczane komentarzem `<!-- status: expanded -->`; rozwiązania żyją w odpowiadających im plikach pod `rozwiazania/`, a walidator wymusza kontrakt tylko dla rozdziałów już oznaczonych jako rozbudowane.

**Tech Stack:** Markdown, Rust Edition 2024, Rust 1.98.1 jako opisywany stable, lokalny Rust 1.90.0 jako początkowy toolchain kontrolny, POSIX shell, Python 3 standard library, `rustdoc --test`, Cargo.

**Spec:** `docs/superpowers/specs/2026-09-10-rozbudowa-kompendium-rust-design.md`

## Global Constraints

- Treść jest po polsku; angielski termin pojawia się przy pierwszym użyciu.
- Opisywany stan to Rust 1.98.1 i Edition 2024, zweryfikowany 10 września 2026 r.
- Samowystarczalny kod używa bloku `rust`, oczekiwany błąd bloku `compile_fail`, a manifest lub szkic ekosystemu bloku `text`.
- Każdy rozbudowany rozdział zaczyna się od dotychczasowego linku do README, następnie znacznika `<!-- status: expanded -->`.
- Każdy rozbudowany rozdział ma cele, model lub reguły, przykład poprawny, diagnostykę błędu, praktykę produkcyjną, sekcję „Sprawdź, czy rozumiesz”, ćwiczenia i powiązane tematy.
- Każde ćwiczenie ma stabilny identyfikator i rozwiązanie z tym samym identyfikatorem.
- Stable, nightly i third-party są rozróżniane jawnie; informacje czasowe mają datę weryfikacji.
- Nie dodawaj zewnętrznych zależności do przykładów z działów 01–04.
- Każde zadanie kończy się testem zmienionych plików oraz małym commitem.

---

## Mapa plików etapu

- `docs/superpowers/audits/2026-09-11-rdzen-jezyka.md` — stan początkowy i macierz braków działów 01–04.
- `CONTRIBUTING.md` — kontrakt rozbudowanego rozdziału i polityka źródeł.
- `scripts/verify_content.py` — testowalne reguły struktury Markdown.
- `scripts/test_verify_content.py` — testy walidatora.
- `scripts/verify.sh` — orkiestracja walidacji Markdown i przykładów Rust.
- `01_wprowadzenie/*.md`–`04_typy_i_modelowanie/*.md` — 20 rozbudowanych rozdziałów.
- `rozwiazania/01_wprowadzenie/*.md`–`rozwiazania/04_typy_i_modelowanie/*.md` — rozwiązania ćwiczeń.
- `README.md` i `zrodla.md` — ścieżka nauki, wersja i źródła.

---

### Task 1: Utrwal stan początkowy i macierz braków

**Files:**
- Create: `docs/superpowers/audits/2026-09-11-rdzen-jezyka.md`

**Interfaces:**
- Consumes: wszystkie pliki `01_wprowadzenie`–`04_typy_i_modelowanie` oraz istniejący `scripts/verify.sh`.
- Produces: tabelę `plik | stan | najważniejsze braki | oficjalne źródła | priorytet` używaną przy Tasks 4–23.

- [ ] **Step 1: Uruchom kontrolę bazową**

Run: `bash scripts/verify.sh`

Expected: kod wyjścia 0; zapisz wersję `rustc` i wszystkie ostrzeżenia. Inny wynik wpisz do audytu jako konkretny stan początkowy.

- [ ] **Step 2: Zmierz rozdziały**

Run: `wc -l 01_wprowadzenie/*.md 02_podstawy_jezyka/*.md 03_pamiec_i_wlasnosc/*.md 04_typy_i_modelowanie/*.md`

Expected: audyt zawiera długość każdego z 20 rozdziałów.

- [ ] **Step 3: Zapisz audyt**

Wpisz osobny wiersz dla każdego pliku. W kolumnie „braki” używaj konkretnych nazw, np. „brak temporary lifetime extension, drop scope i ćwiczeń”. Dodaj ryzyka: wersja dokumentowana 1.98.1 przy lokalnym 1.90.0, duplikacja z atlasem i możliwość przestarzałych szczegółów Rustonomiconu.

- [ ] **Step 4: Sprawdź kompletność**

Run: `test "$(rg -c '^[|].*\\.md[[:space:]]*[|]' docs/superpowers/audits/2026-09-11-rdzen-jezyka.md)" -eq 20`

Expected: kod wyjścia 0.

- [ ] **Step 5: Commit**

Run: `git add docs/superpowers/audits/2026-09-11-rdzen-jezyka.md && git commit -m "docs: audit Rust language core chapters"`

### Task 2: Zdefiniuj kontrakt rozbudowanego rozdziału

**Files:**
- Modify: `CONTRIBUTING.md`

**Interfaces:**
- Consumes: obecny format bloków kodu i stabilności.
- Produces: znacznik `<!-- status: expanded -->`, format ćwiczenia `RCC-NN` i listę wymaganych sekcji.

- [ ] **Step 1: Dodaj wzorzec nagłówka**

~~~markdown
[← Spis treści](../README.md)
<!-- status: expanded -->

# Tytuł

## Cele

Po tym rozdziale potrafisz:

- opisać konkretny rezultat;
- zastosować konkretną regułę.
~~~

- [ ] **Step 2: Dodaj kontrakt dydaktyczny**

Wymagane elementy to: `## Cele`, model lub reguły, poprawny blok `rust`, `## Diagnostyka kompilatora`, `## Praktyka produkcyjna`, `## Sprawdź, czy rozumiesz`, `## Ćwiczenia` i `## Powiązane tematy`.

- [ ] **Step 3: Dodaj kontrakt ćwiczeń**

Identyfikator ma postać `<dział><rozdział>-<numer>`, np. `O02-1`. Każdy wpis zawiera poziom „podstawowe”, „praktyczne” albo „pogłębione” i link do dokładnej kotwicy w `rozwiazania/`.

- [ ] **Step 4: Dodaj politykę aktualności**

Zapisz hierarchię: Reference i aktualne API przed Rustonomiconem; osobne oznaczenie stable/nightly/third-party; data przy twierdzeniu zależnym od wydania; zakaz twierdzenia „sprawdzone na 1.98.1” bez wykonania tym toolchainem.

- [ ] **Step 5: Zweryfikuj i commit**

Run: `rg -n 'status: expanded|Diagnostyka kompilatora|Sprawdź, czy rozumiesz|O02-1|Rust 1\\.98\\.1' CONTRIBUTING.md`

Expected: każde pojęcie zostaje znalezione.

Run: `git add CONTRIBUTING.md && git commit -m "docs: define expanded chapter contract"`

### Task 3: Dodaj testowalny walidator kontraktu

**Files:**
- Create: `scripts/verify_content.py`
- Create: `scripts/test_verify_content.py`
- Modify: `scripts/verify.sh`

**Interfaces:**
- Consumes: znacznik i sekcje z Task 2.
- Produces: `discover_markdown(root: Path) -> list[Path]`, `validate_markdown(root: Path, files: list[Path]) -> list[str]` i CLI zwracające 0 albo 1.

- [ ] **Step 1: Napisz test poprawnego rozdziału**

Użyj `unittest.TestCase` i `TemporaryDirectory`. Fixture zawiera `README.md`, rozdział ze znacznikiem, wszystkie wymagane sekcje, blok `rust` i istniejący link. Asercja: `validate_markdown(...) == []`.

- [ ] **Step 2: Uruchom test czerwony**

Run: `python3 -m unittest scripts/test_verify_content.py -v`

Expected: FAIL z powodu braku modułu lub funkcji `validate_markdown`.

- [ ] **Step 3: Dodaj testy negatywne**

Osobne testy obejmują: niedomknięty fence, martwy link względny, zły pierwszy link, znacznik bez `## Ćwiczenia`, ćwiczenie bez linku do `rozwiazania/`, brak identycznej kotwicy w rozwiązaniu oraz zduplikowany identyfikator. Każdy sprawdza konkretny fragment komunikatu.

- [ ] **Step 4: Zaimplementuj walidator**

`discover_markdown` pomija `.git`, `target` i `docs/superpowers`. `validate_markdown` zachowuje obecne reguły, a wymagane sekcje sprawdza wyłącznie po znaczniku. Linki z bloków kodu są ignorowane. Walidator zbiera identyfikatory ćwiczeń, odrzuca duplikaty i sprawdza, czy docelowy plik rozwiązania zawiera kotwicę o tym samym identyfikatorze.

- [ ] **Step 5: Podłącz wrapper**

`verify.sh` wywołuje `python3 "$project_root/scripts/verify_content.py" "$project_root"`, potem zachowuje `rustdoc --test --edition 2024`. Rozwiązania są testowane.

- [ ] **Step 6: Zweryfikuj**

Run: `python3 -m unittest scripts/test_verify_content.py -v && bash scripts/verify.sh`

Expected: wszystkie testy PASS i kod 0.

- [ ] **Step 7: Commit**

Run: `git add scripts/verify.sh scripts/verify_content.py scripts/test_verify_content.py && git commit -m "test: validate expanded Rust chapters"`

### Task 4: Rozbuduj „Czym jest Rust”

**Files:**
- Modify: `01_wprowadzenie/01_czym_jest_rust.md`
- Create: `rozwiazania/01_wprowadzenie/01_czym_jest_rust.md`

**Interfaces:** Produces: model kompromisów Rusta i ćwiczenia `W01-1`–`W01-3`.

- [ ] **Step 1: Utwórz katalogi rozwiązań etapu**

Run: `mkdir -p rozwiazania/01_wprowadzenie rozwiazania/02_podstawy_jezyka rozwiazania/03_pamiec_i_wlasnosc rozwiazania/04_typy_i_modelowanie`

Expected: cztery katalogi istnieją; nie dodawaj pustych plików.

- [ ] **Step 2: Sprawdź obecny przykład**

Run: `rustdoc --test --edition 2024 01_wprowadzenie/01_czym_jest_rust.md`

Expected: PASS.

- [ ] **Step 3: Rozbuduj treść**

Dodaj safety bez garbage collectora, ownership jako statyczny protokół zasobów, data-race freedom, zero-cost abstractions bez obietnicy automatycznie szybkiego kodu, AOT/LLVM oraz uczciwe koszty czasu kompilacji i złożoności typów. Porównaj decyzję o użyciu Rusta dla CLI, usługi sieciowej i komponentu systemowego bez tworzenia rankingu języków.

- [ ] **Step 4: Dodaj diagnostykę, pytania i ćwiczenia**

Wyjaśnij błąd ownership jako naruszenie kontraktu. Dodaj `W01-1`–`W01-3` z rozwiązaniami uzasadniającymi wybór technologii.

- [ ] **Step 5: Zweryfikuj i commit**

Run: `bash scripts/verify.sh`

Expected: PASS i kod 0.

Run: `git add 01_wprowadzenie/01_czym_jest_rust.md rozwiazania/01_wprowadzenie/01_czym_jest_rust.md && git commit -m "docs: deepen Rust language overview"`

### Task 5: Rozbuduj „Instalacja i toolchain”

**Files:**
- Modify: `01_wprowadzenie/02_instalacja_i_toolchain.md`
- Create: `rozwiazania/01_wprowadzenie/02_instalacja_i_toolchain.md`

**Interfaces:** Consumes: politykę wersji. Produces: powtarzalny model toolchainu i `W02-1`–`W02-3`.

- [ ] **Step 1: Zweryfikuj stan lokalny**

Run: `rustup show && rustc -Vv && cargo -V`

Expected: wynik zapisuje faktyczny lokalny toolchain; nie aktualizuj go w tym kroku.

- [ ] **Step 2: Rozbuduj treść**

Dodaj proxy `rustup`, kanały i datowane toolchainy, components, targets, overrides katalogowe, `rust-toolchain.toml`, cross-compilation, linker kontra target, dokumentację offline, `cargo install` kontra component oraz strategię aktualizacji w CI.

- [ ] **Step 3: Dodaj diagnostykę i ćwiczenia**

Omów brak targetu, brak linkera, niedostępny komponent i MSRV kontra wersja developerska. `W02-1` odczytuje override, `W02-2` projektuje `rust-toolchain.toml`, `W02-3` diagnozuje cross-linker.

- [ ] **Step 4: Zweryfikuj i commit**

Run: `bash scripts/verify.sh`

Expected: PASS i kod 0.

Run: `git add 01_wprowadzenie/02_instalacja_i_toolchain.md rozwiazania/01_wprowadzenie/02_instalacja_i_toolchain.md && git commit -m "docs: deepen Rust toolchain workflow"`

### Task 6: Rozbuduj „Pierwszy program”

**Files:**
- Modify: `01_wprowadzenie/03_pierwszy_program.md`
- Create: `rozwiazania/01_wprowadzenie/03_pierwszy_program.md`

**Interfaces:** Consumes: toolchain z Task 5. Produces: model kompilacji i `W03-1`–`W03-3`.

- [ ] **Step 1: Rozbuduj anatomię i kompilację**

Wyjaśnij crate root, prelude, `fn main`, statements kontra expressions, `println!`, formatowanie, kody wyjścia i `main -> Result`. Opisz parsing, name resolution, type checking, borrow checking, MIR, codegen i linking jako model mentalny.

- [ ] **Step 2: Dodaj diagnostykę i ćwiczenia**

Omów średnik zmieniający typ bloku, niedopasowanie typu zwrotnego i nierozpoznane makro. Dodaj `W03-1`–`W03-3`: przewidywanie wyniku, poprawa błędu i wariant `main -> Result`.

- [ ] **Step 3: Zweryfikuj i commit**

Run: `bash scripts/verify.sh`

Expected: PASS i kod 0.

Run: `git add 01_wprowadzenie/03_pierwszy_program.md rozwiazania/01_wprowadzenie/03_pierwszy_program.md && git commit -m "docs: explain first Rust program deeply"`

### Task 7: Rozbuduj „Cargo w praktyce”

**Files:**
- Modify: `01_wprowadzenie/04_cargo_w_praktyce.md`
- Create: `rozwiazania/01_wprowadzenie/04_cargo_w_praktyce.md`

**Interfaces:** Consumes: program i toolchain. Produces: codzienną pętlę pracy i `W04-1`–`W04-3`.

- [ ] **Step 1: Rozbuduj model i workflow**

Wyjaśnij package, crate, target, manifest, lockfile, registry, cache, resolver, typy dependencies, `cargo check` kontra build, profiles i `target/`. Pokaż kolejność `fmt --check`, `check`, `clippy -- -D warnings`, `test` i `doc --no-deps` oraz politykę `Cargo.lock`.

- [ ] **Step 2: Dodaj diagnostykę i ćwiczenia**

Omów conflict resolvera, brak targetu i różnicę nazw package/crate. Dodaj `W04-1`–`W04-3` dla manifestu, wyboru komendy i lockfile.

- [ ] **Step 3: Zweryfikuj i commit**

Run: `bash scripts/verify.sh`

Expected: PASS i kod 0.

Run: `git add 01_wprowadzenie/04_cargo_w_praktyce.md rozwiazania/01_wprowadzenie/04_cargo_w_praktyce.md && git commit -m "docs: expand practical Cargo workflow"`

### Task 8: Rozbuduj „Zmienne, stałe i shadowing”

**Files:**
- Modify: `02_podstawy_jezyka/01_zmienne_stale_i_shadowing.md`
- Create: `rozwiazania/02_podstawy_jezyka/01_zmienne_stale_i_shadowing.md`

**Interfaces:** Produces: reguły bindingów, drop scope i `P01-1`–`P01-3`.

- [ ] **Step 1: Rozbuduj semantykę**

Dodaj wzorce w `let`, inicjalizację odroczoną, mutowalność bindingu kontra wnętrza wartości, shadowing ze zmianą typu, `const`, `static`, `static mut` jako unsafe oraz kolejność drop. Pokaż wpływ NLL na koniec pożyczki.

- [ ] **Step 2: Dodaj diagnostykę i ćwiczenia**

Omów E0381, E0384 i bezpieczny dostęp do `static mut`. Dodaj `P01-1`–`P01-3` dotyczące inicjalizacji, shadowing i drop scope.

- [ ] **Step 3: Zweryfikuj i commit**

Run: `bash scripts/verify.sh`

Expected: PASS i kod 0.

Run: `git add 02_podstawy_jezyka/01_zmienne_stale_i_shadowing.md rozwiazania/02_podstawy_jezyka/01_zmienne_stale_i_shadowing.md && git commit -m "docs: deepen Rust bindings and shadowing"`

### Task 9: Rozbuduj „Typy i konwersje”

**Files:**
- Modify: `02_podstawy_jezyka/02_typy_i_konwersje.md`
- Create: `rozwiazania/02_podstawy_jezyka/02_typy_i_konwersje.md`

**Interfaces:** Consumes: bindingi z Task 8. Produces: model wartości, reprezentacji i `P02-1`–`P02-3`.

- [ ] **Step 1: Rozbuduj typy i konwersje**

Dodaj pełne liczby, suffixes, overflow debug/release, wrapping/saturating/checked/overflowing arithmetic, `char`, tuple, arrays, unit i never. Rozróżnij coercion, `as`, `From`/`Into`, `TryFrom`/`TryInto`, parsowanie, inferencję i turbofish.

- [ ] **Step 2: Dodaj diagnostykę i ćwiczenia**

Omów ambiguous numeric type, mismatched types, utratę przy cast i zły typ indeksu. Dodaj `P02-1`–`P02-3`: overflow, bezpieczna konwersja i inferencja.

- [ ] **Step 3: Zweryfikuj i commit**

Run: `bash scripts/verify.sh`

Expected: PASS i kod 0.

Run: `git add 02_podstawy_jezyka/02_typy_i_konwersje.md rozwiazania/02_podstawy_jezyka/02_typy_i_konwersje.md && git commit -m "docs: deepen Rust types and conversions"`

### Task 10: Rozbuduj „Funkcje, wyrażenia i instrukcje”

**Files:**
- Modify: `02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md`
- Create: `rozwiazania/02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md`

**Interfaces:** Consumes: typy z Task 9. Produces: model value-oriented syntax i `P03-1`–`P03-3`.

- [ ] **Step 1: Rozbuduj semantykę**

Wyjaśnij item/statement/expression, tail expression, `return`, `!`, function item kontra function pointer, domyślne ABI, parametry jako irrefutable patterns i ograniczony wpływ inline. Pokaż blok ograniczający pożyczkę.

- [ ] **Step 2: Dodaj diagnostykę i ćwiczenia**

Omów semicolon-induced unit, coercion function item do pointer i unreachable code. Dodaj `P03-1`–`P03-3`.

- [ ] **Step 3: Zweryfikuj i commit**

Run: `bash scripts/verify.sh`

Expected: PASS i kod 0.

Run: `git add 02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md rozwiazania/02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md && git commit -m "docs: deepen Rust expressions and functions"`

### Task 11: Rozbuduj „Sterowanie przepływem”

**Files:**
- Modify: `02_podstawy_jezyka/04_sterowanie_przeplywem.md`
- Create: `rozwiazania/02_podstawy_jezyka/04_sterowanie_przeplywem.md`

**Interfaces:** Produces: kontrolę przepływu jako system wyrażeń i `P04-1`–`P04-3`.

- [ ] **Step 1: Rozbuduj konstrukcje i ownership**

Dodaj `if` jako expression, `loop` z wartością, labels, `while let`, `for` przez `IntoIterator`, ranges, `match`, stabilne let chains, `let else` oraz iterację przez `iter`, `iter_mut` i `into_iter`. Pokaż move w gałęzi i pattern przenoszący pole.

- [ ] **Step 2: Dodaj diagnostykę i ćwiczenia**

Omów różne typy gałęzi, częściowy move i użycie po pętli konsumującej. Dodaj `P04-1`–`P04-3`.

- [ ] **Step 3: Zweryfikuj i commit**

Run: `bash scripts/verify.sh`

Expected: PASS i kod 0.

Run: `git add 02_podstawy_jezyka/04_sterowanie_przeplywem.md rozwiazania/02_podstawy_jezyka/04_sterowanie_przeplywem.md && git commit -m "docs: deepen Rust control flow"`

### Task 12: Rozbuduj „Operatory, komentarze i atrybuty”

**Files:**
- Modify: `02_podstawy_jezyka/05_operatory_komentarze_i_atrybuty.md`
- Create: `rozwiazania/02_podstawy_jezyka/05_operatory_komentarze_i_atrybuty.md`

**Interfaces:** Produces: model desugaring i `P05-1`–`P05-3`.

- [ ] **Step 1: Rozbuduj operatory i atrybuty**

Dodaj short-circuiting, traits operatorów, ranges, borrow/deref, `?`, `as`, raw borrow, doc comments, inner/outer attributes, `cfg`, lint levels, `derive`, `repr` i unsafe attributes w Edition 2024.

- [ ] **Step 2: Dodaj diagnostykę i ćwiczenia**

Omów brak implementacji traitu operatora, `?` w złym wyniku i źle umieszczony inner attribute. Dodaj `P05-1`–`P05-3`.

- [ ] **Step 3: Zweryfikuj i commit**

Run: `bash scripts/verify.sh`

Expected: PASS i kod 0.

Run: `git add 02_podstawy_jezyka/05_operatory_komentarze_i_atrybuty.md rozwiazania/02_podstawy_jezyka/05_operatory_komentarze_i_atrybuty.md && git commit -m "docs: deepen operators comments and attributes"`

### Task 13: Rozbuduj „Stos, sterta i RAII”

**Files:**
- Modify: `03_pamiec_i_wlasnosc/01_stos_sterta_i_raii.md`
- Create: `rozwiazania/03_pamiec_i_wlasnosc/01_stos_sterta_i_raii.md`

**Interfaces:** Consumes: drop scope z Task 8. Produces: model zasobów i `O01-1`–`O01-3`.

- [ ] **Step 1: Rozbuduj model i koszt**

Wyjaśnij stack frames jako model, heap allocation, layout wartości kontra bufor, ZST, RAII dla plików i blokad, deterministyczny `Drop`, kolejność pól/bindingów i brak gwarancji tail-call optimization. Prześledź `String` i `Vec`: nagłówek, bufor, capacity, reallocation i drop, rozdzielając kontrakt API od typowej implementacji.

- [ ] **Step 2: Dodaj diagnostykę i ćwiczenia**

Omów stack overflow, problem podwójnego ownership i `mem::forget` jako bezpieczny leak. Dodaj `O01-1`–`O01-3` dotyczące miejsca danych, kolejności drop i kosztu alokacji.

- [ ] **Step 3: Zweryfikuj i commit**

Run: `bash scripts/verify.sh`

Expected: PASS i kod 0.

Run: `git add 03_pamiec_i_wlasnosc/01_stos_sterta_i_raii.md rozwiazania/03_pamiec_i_wlasnosc/01_stos_sterta_i_raii.md && git commit -m "docs: deepen memory and RAII model"`

### Task 14: Rozbuduj „Ownership, move i Copy”

**Files:**
- Modify: `03_pamiec_i_wlasnosc/02_ownership_move_i_copy.md`
- Create: `rozwiazania/03_pamiec_i_wlasnosc/02_ownership_move_i_copy.md`

**Interfaces:** Consumes: model zasobów z Task 13. Produces: precyzyjne ownership i `O02-1`–`O02-4`.

- [ ] **Step 1: Rozbuduj reguły**

Dodaj place/value expressions na poziomie intuicyjnym, move paths, częściowe move, drop flags jako model kompilatora, `Copy` kontra `Clone`, typy z `Drop`, assignment niszczący starą wartość oraz transfer przez funkcje.

- [ ] **Step 2: Dodaj projektowanie API**

Porównaj `T`, `&T`, `&mut T`, `impl Into<T>` i zwrot ownership na przykładzie konfiguracji oraz kolejki. Wyjaśnij, dlaczego clone nie jest domyślną poprawką.

- [ ] **Step 3: Dodaj diagnostykę i ćwiczenia**

Omów use-after-move, partial move, cannot move out of borrowed content i `Copy` dla typu z `Drop`. Dodaj `O02-1`–`O02-4`: move paths, sygnatura, usunięcie clone i drop order.

- [ ] **Step 4: Zweryfikuj i commit**

Run: `bash scripts/verify.sh`

Expected: PASS i kod 0.

Run: `git add 03_pamiec_i_wlasnosc/02_ownership_move_i_copy.md rozwiazania/03_pamiec_i_wlasnosc/02_ownership_move_i_copy.md && git commit -m "docs: deepen ownership move and Copy"`

### Task 15: Rozbuduj „Referencje i borrowing”

**Files:**
- Modify: `03_pamiec_i_wlasnosc/03_referencje_i_borrowing.md`
- Create: `rozwiazania/03_pamiec_i_wlasnosc/03_referencje_i_borrowing.md`

**Interfaces:** Consumes: ownership z Task 14. Produces: model aliasing i `O03-1`–`O03-4`.

- [ ] **Step 1: Rozbuduj pożyczki**

Wyjaśnij shared/mutable reference, wyłączność `&mut`, freeze, reborrowing, deref coercion, NLL, two-phase borrows użytkowo, split borrows pól i granicę raw pointer. Pokaż metodę z `&self`/`&mut self`/`self` oraz pożyczone wyszukiwanie bez alokacji.

- [ ] **Step 2: Dodaj diagnostykę i ćwiczenia**

Omów konflikt shared/mutable, drugi `&mut`, referencję przeżywającą właściciela i mutację podczas iteracji. Dodaj `O03-1`–`O03-4`: zakres pożyczki, reborrow, receiver i poprawka bez clone.

- [ ] **Step 3: Zweryfikuj i commit**

Run: `bash scripts/verify.sh`

Expected: PASS i kod 0.

Run: `git add 03_pamiec_i_wlasnosc/03_referencje_i_borrowing.md rozwiazania/03_pamiec_i_wlasnosc/03_referencje_i_borrowing.md && git commit -m "docs: deepen Rust borrowing model"`

### Task 16: Rozbuduj „Slices i str”

**Files:**
- Modify: `03_pamiec_i_wlasnosc/04_slices_i_str.md`
- Create: `rozwiazania/03_pamiec_i_wlasnosc/04_slices_i_str.md`

**Interfaces:** Consumes: borrowing. Produces: model widoków DST i `O04-1`–`O04-3`.

- [ ] **Step 1: Rozbuduj model i API**

Wyjaśnij fat pointer jako model, `[T]` i `str` jako DST, `&[T]`, `&mut [T]`, ranges, UTF-8, wzorce na slices, `split_at_mut` oraz bytes/scalar values/grapheme clusters. Pokaż `&str` zamiast `&String`, `&[T]` zamiast `&Vec<T>` i borrowed kontra owned result.

- [ ] **Step 2: Dodaj diagnostykę i ćwiczenia**

Omów indeksowanie `str`, cięcie na złej granicy i nakładające się mutable slices. Dodaj `O04-1`–`O04-3`.

- [ ] **Step 3: Zweryfikuj i commit**

Run: `bash scripts/verify.sh`

Expected: PASS i kod 0.

Run: `git add 03_pamiec_i_wlasnosc/04_slices_i_str.md rozwiazania/03_pamiec_i_wlasnosc/04_slices_i_str.md && git commit -m "docs: deepen slices and str"`

### Task 17: Rozbuduj „Lifetimes”

**Files:**
- Modify: `03_pamiec_i_wlasnosc/05_lifetimes.md`
- Create: `rozwiazania/03_pamiec_i_wlasnosc/05_lifetimes.md`

**Interfaces:** Consumes: referencje i slices. Produces: relacyjny model i `O05-1`–`O05-4`.

- [ ] **Step 1: Rozbuduj relacje**

Wyjaśnij input/output lifetimes, elision, outlives bounds, `T: 'a`, `'static` reference kontra `T: 'static`, struktury i `'_`. Pokaż niezależne lifetimes, metodę zwracającą pole, iterator po pożyczonych danych, HRTB jako zapowiedź i temporary lifetime extension.

- [ ] **Step 2: Dodaj diagnostykę i ćwiczenia**

Omów missing lifetime specifier, borrowed value does not live long enough, zwrot referencji lokalnej i nadmierne związanie wejść jednym lifetime'em. Dodaj `O05-1`–`O05-4`: relacje, dwie adnotacje, owned/borrowed result i `'static`.

- [ ] **Step 3: Zweryfikuj i commit**

Run: `bash scripts/verify.sh`

Expected: PASS i kod 0.

Run: `git add 03_pamiec_i_wlasnosc/05_lifetimes.md rozwiazania/03_pamiec_i_wlasnosc/05_lifetimes.md && git commit -m "docs: deepen Rust lifetimes"`

### Task 18: Rozbuduj „Smart pointery i interior mutability”

**Files:**
- Modify: `03_pamiec_i_wlasnosc/06_smart_pointery_i_interior_mutability.md`
- Create: `rozwiazania/03_pamiec_i_wlasnosc/06_smart_pointery_i_interior_mutability.md`

**Interfaces:** Consumes: cały model ownership. Produces: matrycę wrapperów i `O06-1`–`O06-4`.

- [ ] **Step 1: Rozbuduj typy i koszty**

Porównaj `Box`, `Rc`, `Arc`, `Weak`, `Cell`, `RefCell`, `Mutex`, `RwLock`, `Cow`, `Deref`, `Drop` i `Pin` jako zapowiedź: ownership, synchronizację, koszt runtime i rolę. Pokaż drzewo z `Weak`, cache z `RefCell` i kontrast z `Arc<Mutex<T>>`.

- [ ] **Step 2: Dodaj diagnostykę i ćwiczenia**

Omów panic `RefCell`, brak `Send` dla `Rc`, deadlock i reference cycle. Dodaj `O06-1`–`O06-4`: dobór wrappera, usunięcie cyklu, konflikt runtime i koszt granicy wątków.

- [ ] **Step 3: Zweryfikuj i commit**

Run: `bash scripts/verify.sh`

Expected: PASS i kod 0.

Run: `git add 03_pamiec_i_wlasnosc/06_smart_pointery_i_interior_mutability.md rozwiazania/03_pamiec_i_wlasnosc/06_smart_pointery_i_interior_mutability.md && git commit -m "docs: deepen smart pointers and mutability"`

### Task 19: Rozbuduj „Struktury, enumy i metody”

**Files:**
- Modify: `04_typy_i_modelowanie/01_struktury_enumy_i_metody.md`
- Create: `rozwiazania/04_typy_i_modelowanie/01_struktury_enumy_i_metody.md`

**Interfaces:** Consumes: ownership i borrowing. Produces: product/sum types i `T01-1`–`T01-4`.

- [ ] **Step 1: Rozbuduj modelowanie**

Wyjaśnij product/sum types, tuple/unit structs, discriminants bez obietnic layoutu, associated functions, receiver forms, shorthand, struct update i move. Pokaż prywatne pola z walidującym konstruktorem, enum eliminujący niepoprawne stany, newtype kontra alias i `non_exhaustive`.

- [ ] **Step 2: Dodaj diagnostykę i ćwiczenia**

Omów brak pola, częściowy move, zły receiver i prywatne pole poza modułem. Dodaj `T01-1`–`T01-4`: model domenowy, update syntax, constructor invariant i wybór enum/struct.

- [ ] **Step 3: Zweryfikuj i commit**

Run: `bash scripts/verify.sh`

Expected: PASS i kod 0.

Run: `git add 04_typy_i_modelowanie/01_struktury_enumy_i_metody.md rozwiazania/04_typy_i_modelowanie/01_struktury_enumy_i_metody.md && git commit -m "docs: deepen structs enums and methods"`

### Task 20: Rozbuduj „Wzorce i match”

**Files:**
- Modify: `04_typy_i_modelowanie/02_wzorce_i_match.md`
- Create: `rozwiazania/04_typy_i_modelowanie/02_wzorce_i_match.md`

**Interfaces:** Consumes: enumy z Task 19. Produces: model wzorców i `T02-1`–`T02-4`.

- [ ] **Step 1: Rozbuduj wzorce i ownership**

Dodaj refutable/irrefutable contexts, destructuring, `..`, `@`, ranges, or-patterns, guards, binding modes, match ergonomics, `ref`, `let else` i exhaustiveness. Pokaż match po `T`, `&T` i `&mut T`, częściowy move i pożyczanie pola.

- [ ] **Step 2: Dodaj diagnostykę i ćwiczenia**

Omów non-exhaustive match, refutable pattern in let, moved value after match i unreachable pattern. Dodaj `T02-1`–`T02-4`.

- [ ] **Step 3: Zweryfikuj i commit**

Run: `bash scripts/verify.sh`

Expected: PASS i kod 0.

Run: `git add 04_typy_i_modelowanie/02_wzorce_i_match.md rozwiazania/04_typy_i_modelowanie/02_wzorce_i_match.md && git commit -m "docs: deepen Rust patterns and match"`

### Task 21: Rozbuduj „Generics i const generics”

**Files:**
- Modify: `04_typy_i_modelowanie/03_generics_i_const_generics.md`
- Create: `rozwiazania/04_typy_i_modelowanie/03_generics_i_const_generics.md`

**Interfaces:** Consumes: typy i wzorce. Produces: parametric polymorphism i `T03-1`–`T03-4`.

- [ ] **Step 1: Rozbuduj generics**

Dodaj type/lifetime/const parameters, bounds, `where`, turbofish, defaults, monomorphization, code bloat, inference boundaries i phantom type jako zapowiedź. Pokaż stabilny minimal const generics, wartości const w tożsamości typu i ograniczenia generic const expressions.

- [ ] **Step 2: Dodaj diagnostykę i ćwiczenia**

Omów type annotations needed, unsatisfied bound, różne długości tablic i niestabilne generic const expressions. Dodaj `T03-1`–`T03-4`: uogólnienie funkcji, `where`, typ const i koszt monomorfizacji.

- [ ] **Step 3: Zweryfikuj i commit**

Run: `bash scripts/verify.sh`

Expected: PASS i kod 0.

Run: `git add 04_typy_i_modelowanie/03_generics_i_const_generics.md rozwiazania/04_typy_i_modelowanie/03_generics_i_const_generics.md && git commit -m "docs: deepen generics and const generics"`

### Task 22: Rozbuduj „Traits i associated items”

**Files:**
- Modify: `04_typy_i_modelowanie/04_traits_i_associated_items.md`
- Create: `rozwiazania/04_typy_i_modelowanie/04_traits_i_associated_items.md`

**Interfaces:** Consumes: generics z Task 21. Produces: kontrakty statyczne i `T04-1`–`T04-5`.

- [ ] **Step 1: Rozbuduj traits i API**

Dodaj required/default methods, associated types/constants/functions, supertraits, blanket impls, coherence, orphan rule, UFCS, `Self`, `Sized`, `?Sized` i auto traits. Porównaj associated type z parametrem, `impl Trait` z nazwanym typem, extension trait, sealed trait i newtype.

- [ ] **Step 2: Oddziel stabilność**

Popraw negatywne granice: stabilne przypadki odróżnij od ogólnych negative bounds i specialization, które muszą być opisane jako nightly lub niedostępne.

- [ ] **Step 3: Dodaj diagnostykę i ćwiczenia**

Omów conflicting impls, trait not implemented, multiple applicable items i brak importu traitu. Dodaj `T04-1`–`T04-5`.

- [ ] **Step 4: Zweryfikuj i commit**

Run: `bash scripts/verify.sh`

Expected: PASS i kod 0.

Run: `git add 04_typy_i_modelowanie/04_traits_i_associated_items.md rozwiazania/04_typy_i_modelowanie/04_traits_i_associated_items.md && git commit -m "docs: deepen traits and associated items"`

### Task 23: Rozbuduj „Konwersje, DST i trait objects”

**Files:**
- Modify: `04_typy_i_modelowanie/05_konwersje_dst_i_trait_objects.md`
- Create: `rozwiazania/04_typy_i_modelowanie/05_konwersje_dst_i_trait_objects.md`

**Interfaces:** Consumes: traits i slices. Produces: coercion/dispatch i `T05-1`–`T05-5`.

- [ ] **Step 1: Rozbuduj konwersje i DST**

Porównaj `From`/`Into`, `TryFrom`/`TryInto`, `AsRef`, `Borrow`, `Deref` coercion, pointer weakening, unsizing i `as`. Wyjaśnij `Sized`, `?Sized`, `str`, slices, `dyn Trait`, fat pointer jako model, vtable bez gwarantowania layoutu, dyn compatibility i object lifetime.

- [ ] **Step 2: Dodaj API i wydajność**

Porównaj `impl Trait`, `T`, `&dyn Trait` i `Box<dyn Trait>` pod kątem ownership, heterogenicznych kolekcji, code size, inlining i stabilności API.

- [ ] **Step 3: Dodaj diagnostykę i ćwiczenia**

Omów trait not dyn compatible, unknown size, zły object lifetime i błędne `Borrow` zamiast `AsRef`. Dodaj `T05-1`–`T05-5`.

- [ ] **Step 4: Zweryfikuj i commit**

Run: `bash scripts/verify.sh`

Expected: PASS i kod 0.

Run: `git add 04_typy_i_modelowanie/05_konwersje_dst_i_trait_objects.md rozwiazania/04_typy_i_modelowanie/05_konwersje_dst_i_trait_objects.md && git commit -m "docs: deepen conversions DST and trait objects"`

### Task 24: Zaktualizuj źródła i nawigację

**Files:**
- Modify: `README.md`
- Modify: `zrodla.md`

**Interfaces:** Consumes: 20 rozbudowanych rozdziałów. Produces: ścieżkę „Rdzeń języka”, wersję i macierz źródeł.

- [ ] **Step 1: Zaktualizuj wersję uczciwie**

README podaje „opisuje stable 1.98.1, stan na 10 września 2026”; osobno najstarszy toolchain, na którym faktycznie zakończyła się lokalna walidacja. Nie deklaruj 1.98.1 jako przetestowanego bez wykonania tym toolchainem.

- [ ] **Step 2: Dodaj kamień milowy**

Dodaj ścieżkę „Rdzeń języka”, umiejętności po działach 01–04 i link do `rozwiazania`. Nie linkuj do nieistniejących projektów.

- [ ] **Step 3: Rozbuduj źródła**

Dodaj tabelę `obszar | źródło podstawowe | źródło uzupełniające | data weryfikacji` dla składni, ownership, lifetimes, traits, patterns, conversions, DST i dyn compatibility, używając bezpośrednich oficjalnych URL-i.

- [ ] **Step 4: Zweryfikuj i commit**

Run: `bash scripts/verify.sh`

Expected: kod 0 bez martwych linków.

Run: `git add README.md zrodla.md && git commit -m "docs: add Rust core learning path and sources"`

### Task 25: Odbiór etapu 1

**Files:**
- Modify only when verification reveals a defect: files changed in Tasks 1–24.

**Interfaces:** Consumes: cały etap. Produces: zielony punkt odniesienia dla etapu 2.

- [ ] **Step 1: Uruchom testy walidatora**

Run: `python3 -m unittest scripts/test_verify_content.py -v`

Expected: wszystkie testy PASS.

- [ ] **Step 2: Uruchom pełną walidację**

Run: `bash scripts/verify.sh`

Expected: kod 0; bloki `rust` i `compile_fail` w treści i rozwiązaniach przechodzą `rustdoc --test --edition 2024`.

- [ ] **Step 3: Sprawdź pokrycie**

Run: `test "$(rg -l '<!-- status: expanded -->' 01_wprowadzenie 02_podstawy_jezyka 03_pamiec_i_wlasnosc 04_typy_i_modelowanie | wc -l | tr -d ' ')" -eq 20`

Expected: kod 0.

- [ ] **Step 4: Sprawdź ćwiczenia**

Run: `python3 scripts/verify_content.py .`

Expected: kod 0, bez brakującego rozwiązania ani zduplikowanego identyfikatora.

- [ ] **Step 5: Sprawdź diff i stan**

Run: `git diff --check 9e4df5d..HEAD && git diff --check && git status --short`

Expected: brak błędów whitespace; stan zawiera wyłącznie świadome poprawki odbiorcze albo jest czysty.

- [ ] **Step 6: Commit poprawek odbiorczych**

Jeżeli kroki 1–5 wymagały zmian, uruchom:

`git add README.md CONTRIBUTING.md zrodla.md scripts 01_wprowadzenie 02_podstawy_jezyka 03_pamiec_i_wlasnosc 04_typy_i_modelowanie rozwiazania docs/superpowers/audits && git commit -m "docs: complete Rust core expansion phase"`

Expected: commit powstaje tylko dla rzeczywistych poprawek.

---

## Następne niezależne plany

Po odbiorze etapu 1 zapisz i wykonaj osobne plany:

1. kolekcje, iteratory, błędy, Cargo, testowanie i projektowanie API;
2. współbieżność i async;
3. makra, I/O, sieć, FFI, WebAssembly, `no_std` i embedded;
4. rozdziały eksperckie oraz atlas 150 mechanizmów;
5. sześć projektów Cargo;
6. pełny audyt merytoryczny, nawigacja i odbiór kompendium.

Każdy plan wskazuje dokładne pliki, identyfikatory ćwiczeń, źródła i komendy odbioru. Nie rozpoczynaj etapu przy czerwonej walidacji poprzedniego.
