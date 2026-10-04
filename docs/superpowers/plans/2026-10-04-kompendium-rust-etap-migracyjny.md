# Kompendium Rust — etap migracyjny do 30 działów Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Zachować cały obecny materiał, przenieść go do zweryfikowanej struktury 30 rustowych działów i udostępnić kompletną nawigację będącą podstawą dalszej rozbudowy treści.

**Architecture:** Najpierw domykamy i utrwalamy zastany rozdział roboczy, następnie dodajemy maszynowo sprawdzany kontrakt 30 działów i manifest migracji. Treści są przenoszone przez Git do miejsc kanonicznych, a nowe działy otrzymują pełne mapy zakresu bez udawania, że brakujące rozdziały są już napisane.

**Tech Stack:** Markdown, Python 3 standard library, POSIX shell, Git, `rustdoc --test --edition 2024`, Rust Edition 2024.

**Spec:** `docs/superpowers/specs/2026-10-04-kompendium-rust-30-dzialow-design.md`

## Global Constraints

- Pracuj w istniejącym worktree gałęzi `codex/rozbudowa-rdzenia-rust`.
- Zachowaj zastane zmiany w `02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md` i odpowiadającym rozwiązaniu.
- Nie usuwaj wartościowej treści; każdy stary plik Markdown ma mieć wpis w manifeście migracji.
- Przenoś śledzone pliki przez `git mv`, aby historia pozostała czytelna.
- Treść pozostaje po polsku; terminy stable, nightly i third-party pozostają jawne.
- Atlas 150 mechanizmów, ściąga, słownik, dalsza nauka, źródła i rozwiązania pozostają materiałami przekrojowymi.
- Ten etap dostarcza strukturę i nawigację. Nie oznaczaj pustej mapy działu jako ukończonego rozdziału merytorycznego.
- Każdy commit obejmuje jeden niezależnie weryfikowalny rezultat.

## Review Focus

- Zastany rozdział roboczy i jego nieśledzone rozwiązanie nie mogą zniknąć ani trafić przypadkiem do commitu migracyjnego; Task 1 przypina oba pliki osobnym testem i commitem.
- Przeniesienia katalogów mogą zerwać linki względne w atlasie, rozwiązaniach i rozdziałach; Tasks 4–9 uruchamiają pełny walidator linków po każdej grupie ruchów.
- Rozdziały z dawnego `zaawansowane/` mogą zostać pominięte albo trafić do dwóch miejsc; Task 3 testuje unikalność źródeł i celów manifestu, a Task 5 sprawdza komplet 15 migracji.
- Nowe katalogi mogą istnieć bez `README.md` albo nie być dostępne z głównego indeksu; Task 2 dodaje testy dokładnie 30 map działów i 30 linków z korzenia.
- Walidator może błędnie potraktować link lub fence zagnieżdżony w liście po zmianie ścieżek; Task 2 zachowuje wszystkie 21 istniejących regresji i dodaje test repozytorium po migracji.

---

## Docelowe katalogi

Walidator i wszystkie późniejsze zadania używają dokładnie tych nazw:

```text
01_wprowadzenie_i_toolchain
02_podstawy_jezyka
03_ownership_i_pamiec
04_struktury_enumy_i_wzorce
05_generics_traits_i_system_typow
06_kolekcje_iteratory_i_closures
07_obsluga_bledow
08_moduly_cargo_i_workspaces
09_dokumentacja_testowanie_i_jakosc
10_wspolbieznosc
11_async_rust
12_makra
13_io_siec_i_protokoly
14_idiomy_wzorce_i_architektura
15_aplikacje_cli
16_web_i_api
17_bazy_danych_i_persystencja
18_serializacja_konfiguracja_i_integracje
19_runtime_pamiec_i_kompilator
20_wydajnosc_i_optymalizacja
21_unsafe_soundness_i_model_pamieci
22_ffi_i_interoperacyjnosc
23_no_std_allocatory_i_embedded
24_wasm_i_wieloplatformowosc
25_debugowanie_i_utrzymanie
26_testowanie_zaawansowane_fuzzing_i_miri
27_bezpieczenstwo_aplikacji
28_ci_cd_i_release_engineering
29_observability_i_produkcja
30_projekty_przekrojowe
```

### Task 1: Domknij i zabezpiecz zastany rozdział roboczy

**Files:**
- Modify: `02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md`
- Create: `rozwiazania/02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md`

**Interfaces:**
- Consumes: obecny kontrakt `<!-- status: expanded -->` i identyfikatory `P03-1`–`P03-3`.
- Produces: czysty, samodzielny commit zawierający cały zastany szkic i jego rozwiązania.

- [ ] **Step 1: Przypnij oczekiwany zakres zastanych zmian**

Run: `git status --short`

Expected: dokładnie zmodyfikowany rozdział `02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md`, nieśledzone odpowiadające rozwiązanie i śledzony osobno plik tego planu.

- [ ] **Step 2: Napraw dwa linki bez zmiany treści rozdziału**

Zmień cele `../03_ownership_i_pamiec/01_ownership_i_przenoszenie.md` oraz `../03_ownership_i_pamiec/02_pozyczanie_i_referencje.md` na istniejące przed migracją `../03_pamiec_i_wlasnosc/02_ownership_move_i_copy.md` i `../03_pamiec_i_wlasnosc/03_referencje_i_borrowing.md`.

- [ ] **Step 3: Zweryfikuj zastany materiał**

Run: `python3 -m unittest scripts/test_verify_content.py -v && bash scripts/verify.sh`

Expected: 21 testów `OK`, walidacja Markdown bez problemów i wszystkie wykonywane testy `rustdoc` zaliczone.

- [ ] **Step 4: Commit tylko zastanych materiałów**

```bash
git add 02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md rozwiazania/02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md
git commit -m "docs: deepen Rust functions and expressions"
```

### Task 2: Dodaj testowalny kontrakt struktury 30 działów

**Files:**
- Modify: `scripts/verify_content.py`
- Modify: `scripts/test_verify_content.py`

**Interfaces:**
- Produces: `EXPECTED_SECTION_DIRS: tuple[str, ...]` oraz `validate_section_structure(root: Path) -> list[str]`.
- Consumes: główny `README.md` i docelowe katalogi wymienione w tym planie.

- [ ] **Step 1: Napisz test brakujących map działów**

Dodaj `test_reports_missing_section_readmes`. Fixture ma pusty główny `README.md`; asercja wymaga problemu `brak README działu: 01_wprowadzenie_i_toolchain/README.md` i analogicznego problemu dla działu 30.

- [ ] **Step 2: Napisz test niepełnej nawigacji głównej**

Dodaj `test_reports_section_missing_from_root_navigation`. Fixture tworzy wszystkie 30 katalogów i ich `README.md`, ale główny indeks nie linkuje działu 17; asercja wymaga `README.md: brak linku do działu: 17_bazy_danych_i_persystencja/README.md`.

- [ ] **Step 3: Uruchom nowe testy i potwierdź porażkę**

Run: `python3 -m unittest scripts.test_verify_content.ValidateSectionStructureTests -v`

Expected: FAIL z powodu braku `validate_section_structure`.

- [ ] **Step 4: Zaimplementuj kontrakt struktury**

`validate_section_structure(root: Path) -> list[str]` sprawdza 30 katalogów, ich `README.md`, link z głównego `README.md` do każdej mapy oraz brak katalogu `zaawansowane/` po zakończonej migracji. Funkcja zwraca wszystkie problemy, nie zatrzymuje się na pierwszym. CLI wywołuje ją obok `validate_markdown`.

- [ ] **Step 5: Uruchom pełne testy walidatora**

Run: `python3 -m unittest scripts/test_verify_content.py -v`

Expected: wszystkie stare i nowe testy PASS; `bash scripts/verify.sh` nadal FAIL tylko dlatego, że repozytorium nie ma jeszcze nowej struktury.

- [ ] **Step 6: Commit**

```bash
git add scripts/verify_content.py scripts/test_verify_content.py
git commit -m "test: define thirty-section content layout"
```

### Task 3: Zapisz kompletny manifest migracji

**Files:**
- Create: `docs/superpowers/audits/2026-10-04-mapa-migracji-30-dzialow.md`
- Create: `docs/superpowers/audits/2026-10-04-mapa-migracji-30-dzialow.json`
- Modify: `scripts/verify_content.py`
- Modify: `scripts/test_verify_content.py`

**Interfaces:**
- Produces: `LEGACY_SECTION_DIRS: tuple[str, ...]`, `load_migration_manifest(path: Path) -> list[dict[str, str]]` i `validate_migration_manifest(root: Path, entries: list[dict[str, str]]) -> list[str]`.
- Manifest JSON ma pola `version: 1` i `moves`, a każdy wpis `source`, `destination`, `disposition` (`move` albo `merge`).

- [ ] **Step 1: Napisz test duplikatu, brakującego celu i pominiętego źródła**

Dodaj fixture z dwoma wpisami o tym samym `source`, nieistniejącym `destination` oraz dodatkowym plikiem Markdown w dawnym katalogu bez wpisu w manifeście. Asercje wymagają problemów `zduplikowane źródło migracji`, `brak celu migracji` i `brak wpisu migracji dla`.

- [ ] **Step 2: Uruchom test czerwony**

Run: `python3 -m unittest scripts.test_verify_content.MigrationManifestTests -v`

Expected: FAIL z powodu braku interfejsów manifestu.

- [ ] **Step 3: Zaimplementuj odczyt i walidację manifestu**

Walidator odrzuca nieznaną wersję, nieznane `disposition`, zduplikowane źródło, zduplikowany cel dla `move`, istniejące po migracji źródło różne od celu oraz brak celu. Przed migracją skanuje `LEGACY_SECTION_DIRS` i raportuje każdy plik Markdown bez wpisu. Błędy JSON są zwracane jako problem z nazwą pliku zamiast tracebacku.

- [ ] **Step 4: Zapisz mapę plików bazowych**

W JSON dodaj każdy śledzony plik Markdown z katalogów `01_wprowadzenie`–`13_wzorce_i_architektura` oraz `zaawansowane/`. Pliki zachowujące nazwę używają `move`; `zaawansowane/README.md` używa `merge` z celem `README.md`, a audyt Markdown dodatkowo wskazuje mapy działów 5, 10–12 oraz 19–23, do których należy włączyć odpowiednie fragmenty.

Użyj reguł:

| Źródło | Cel |
|---|---|
| `01_wprowadzenie/*` | `01_wprowadzenie_i_toolchain/*` |
| `02_podstawy_jezyka/*` | bez zmiany |
| `03_pamiec_i_wlasnosc/*` | `03_ownership_i_pamiec/*` |
| `04_typy_i_modelowanie/01_*`–`02_*` | `04_struktury_enumy_i_wzorce/*` |
| `04_typy_i_modelowanie/03_*`–`05_*` | `05_generics_traits_i_system_typow/01_*`–`03_*` |
| `05_kolekcje_i_iteratory/*` | `06_kolekcje_iteratory_i_closures/*` |
| `06_bledy/*` | `07_obsluga_bledow/*` |
| `07_moduly_i_cargo/*` | `08_moduly_cargo_i_workspaces/*` |
| `08_testowanie_i_jakosc/01_*`–`03_*` | `09_dokumentacja_testowanie_i_jakosc/*` |
| `08_testowanie_i_jakosc/04_*` | `20_wydajnosc_i_optymalizacja/02_benchmarki_profilowanie_i_miri.md` |
| `09_wspolbieznosc/*` | `10_wspolbieznosc/*` |
| `10_async/*` | `11_async_rust/*` |
| `11_makra/*` | `12_makra/*` |
| `12_systemy_i_interoperacyjnosc/01_*`–`02_*` | `13_io_siec_i_protokoly/*` |
| `12_systemy_i_interoperacyjnosc/03_*` | `22_ffi_i_interoperacyjnosc/01_ffi_abi_i_repr.md` |
| `12_systemy_i_interoperacyjnosc/04_*` | `23_no_std_allocatory_i_embedded/01_wasm_no_std_i_embedded.md` |
| `13_wzorce_i_architektura/01_*`–`04_*` | `14_idiomy_wzorce_i_architektura/*` |
| `13_wzorce_i_architektura/05_*` | `20_wydajnosc_i_optymalizacja/01_wydajnosc_i_zero_cost.md` |

- [ ] **Step 5: Zapisz dokładne cele części eksperckiej**

Mapuj: `04_variance*`, `05_hrtb*`, `06_dyn*` do działu 5 jako pliki 04–06; `08_atomics*` i `09_lock_free*` do działu 10 jako 05–06; `07_pin*` do działu 11 jako 05; `10_zaawansowane_makra*` do działu 12 jako 04; `14_borrow_checker*` do działu 19 jako 01; `13_monomorfizacja*` do działu 20 jako 03; `01_unsafe*`–`03_layout*` do działu 21 jako 01–03; `11_ffi*` do działu 22 jako 02; `12_no_std*` do działu 23 jako 02; `15_nightly*` do działu 8 jako 05.

- [ ] **Step 6: Zapisz czytelny audyt Markdown**

Audyt podaje stan bazowy, dwa linki naprawione w Task 1, tabelę wszystkich wpisów JSON, ryzyko plików łączących kilka przyszłych działów oraz decyzję, że ich podział treści nastąpi w późniejszych planach.

- [ ] **Step 7: Zweryfikuj schemat bez wymagania wykonanej migracji**

Run: `python3 -m unittest scripts/test_verify_content.py -v`

Expected: PASS. Pełny CLI nie włącza jeszcze manifestu automatycznie; nastąpi to w Task 9 po wykonaniu ruchów.

- [ ] **Step 8: Commit**

```bash
git add docs/superpowers/audits/2026-10-04-mapa-migracji-30-dzialow.md docs/superpowers/audits/2026-10-04-mapa-migracji-30-dzialow.json scripts/verify_content.py scripts/test_verify_content.py
git commit -m "docs: map content into thirty Rust sections"
```

### Task 4: Przenieś rdzeń języka do działów 01–14

**Files:**
- Move: rozdziały zgodnie z bazową częścią manifestu z Task 3.
- Move: `rozwiazania/01_wprowadzenie/*` -> `rozwiazania/01_wprowadzenie_i_toolchain/*`.
- Modify: wszystkie przenoszone pliki zawierające linki względne.

**Interfaces:**
- Consumes: zaakceptowany manifest migracji.
- Produces: kanoniczne katalogi 01–14 z zachowaną treścią oraz działające linki między nimi.

- [ ] **Step 1: Wykonaj ruchy przez `git mv`**

Przenieś katalogi jednorodne w całości, a katalog `04_typy_i_modelowanie` rozdziel między działy 4 i 5. Nie przenoś jeszcze plików kierowanych do działów 19–23.

- [ ] **Step 2: Zaktualizuj backlinki i linki ćwiczeń**

Każdy rozdział nadal zaczyna się linkiem do `../README.md`; rozwiązania zachowują `../../README.md`. Zastąp wszystkie odwołania do dawnych katalogów ich miejscami z manifestu, w tym dwa linki z Task 1 do docelowych ścieżek działu 3.

- [ ] **Step 3: Uruchom walidację Markdown z wyłączeniem nieutworzonych map działów**

Run: `python3 -m unittest scripts/test_verify_content.py -v && python3 scripts/verify_content.py .`

Expected: testy PASS; CLI raportuje wyłącznie brakujące `README.md` działów, brakujące linki głównej nawigacji oraz jeszcze istniejący katalog `zaawansowane/`, bez martwych linków pomiędzy przeniesionymi rozdziałami.

- [ ] **Step 4: Commit**

```bash
git add -A 01_wprowadzenie 01_wprowadzenie_i_toolchain 03_pamiec_i_wlasnosc 03_ownership_i_pamiec 04_typy_i_modelowanie 04_struktury_enumy_i_wzorce 05_generics_traits_i_system_typow 05_kolekcje_i_iteratory 06_kolekcje_iteratory_i_closures 06_bledy 07_obsluga_bledow 07_moduly_i_cargo 08_moduly_cargo_i_workspaces 08_testowanie_i_jakosc 09_dokumentacja_testowanie_i_jakosc 09_wspolbieznosc 10_wspolbieznosc 10_async 11_async_rust 11_makra 12_makra 12_systemy_i_interoperacyjnosc 13_io_siec_i_protokoly 13_wzorce_i_architektura 14_idiomy_wzorce_i_architektura rozwiazania
git commit -m "docs: migrate Rust core into numbered sections"
```

### Task 5: Rozmieść istniejące materiały eksperckie

**Files:**
- Move: `zaawansowane/*.md` do działów 5, 8, 10–12 i 19–23 zgodnie z manifestem.
- Move: pozostałe pliki z `08_testowanie_i_jakosc`, `12_systemy_i_interoperacyjnosc` i `13_wzorce_i_architektura` do działów 20, 22 i 23.
- Modify: wszystkie przeniesione pliki i ich linki.

**Interfaces:**
- Consumes: szczegółowe cele części eksperckiej z Task 3.
- Produces: brak katalogu `zaawansowane/` i dokładnie 15 zachowanych rozdziałów eksperckich w miejscach kanonicznych.

- [ ] **Step 1: Przenieś 15 rozdziałów eksperckich i 4 rozdziały specjalistyczne**

Użyj docelowych numerów plików z Task 3. Nie dziel jeszcze treści `04_wasm_no_std_i_embedded.md` ani `04_benchmarki_profilowanie_i_miri.md`; ich późniejsze rozdzielenie należy do planów merytorycznych działów 20, 23, 24 i 26.

- [ ] **Step 2: Scal mapę dawnego katalogu eksperckiego**

Przenieś wymagania wstępne, ostrzeżenia o granicach wiedzy i kolejność czytania z `zaawansowane/README.md` do przygotowywanych map działów 5, 10–12 i 19–23. Usuń dawny plik dopiero po potwierdzeniu tych treści w diffie.

- [ ] **Step 3: Zaktualizuj wszystkie linki do części eksperckiej**

Run: `rg -n 'zaawansowane/|08_testowanie_i_jakosc|12_systemy_i_interoperacyjnosc|13_wzorce_i_architektura' --glob '*.md'`

Expected: brak linków do starych ścieżek; dopuszczalne są wyłącznie opisowe wzmianki bez składni linku w audycie migracji.

- [ ] **Step 4: Zweryfikuj komplet plików**

Run: `find 05_generics_traits_i_system_typow 08_moduly_cargo_i_workspaces 10_wspolbieznosc 11_async_rust 12_makra 19_runtime_pamiec_i_kompilator 20_wydajnosc_i_optymalizacja 21_unsafe_soundness_i_model_pamieci 22_ffi_i_interoperacyjnosc 23_no_std_allocatory_i_embedded -type f -name '*.md' | sort`

Expected: lista zawiera wszystkie cele części eksperckiej i specjalistycznej z manifestu.

- [ ] **Step 5: Commit**

```bash
git add -A zaawansowane 05_generics_traits_i_system_typow 08_moduly_cargo_i_workspaces 10_wspolbieznosc 11_async_rust 12_makra 19_runtime_pamiec_i_kompilator 20_wydajnosc_i_optymalizacja 21_unsafe_soundness_i_model_pamieci 22_ffi_i_interoperacyjnosc 23_no_std_allocatory_i_embedded
git commit -m "docs: integrate advanced Rust topics into learning path"
```

### Task 6: Dodaj mapy działów 01–14

**Files:**
- Create: `01_wprowadzenie_i_toolchain/README.md` through `14_idiomy_wzorce_i_architektura/README.md`.

**Interfaces:**
- Produces: mapę celu, wymagań, kolejności, rezultatów i następnych kroków dla każdego działu podstawowego.

- [ ] **Step 1: Dodaj wspólny kontrakt mapy bez mechanicznego kopiowania**

Każdy plik zawiera `# <numer>. <tytuł>`, sekcje `## Dla kogo i po co`, `## Wymagania wstępne`, `## Kolejność materiałów`, `## Po tym dziale` i `## Co dalej`. Lista materiałów linkuje wszystkie pliki `.md` danego katalogu dokładnie raz.

- [ ] **Step 2: Dodaj przejścia między działami**

Każde `Co dalej` prowadzi co najmniej do następnego działu i jednego odpowiedniego materiału przekrojowego albo projektu. Dział 14 prowadzi do zastosowań 15–18 i tematów 19–21.

- [ ] **Step 3: Zweryfikuj linki map podstawowych**

Run: `python3 scripts/verify_content.py .`

Expected: brak błędów linków w działach 01–14; pozostają tylko brakujące mapy 15–30 i główna nawigacja.

- [ ] **Step 4: Commit**

```bash
git add 0*/README.md 10_wspolbieznosc/README.md 11_async_rust/README.md 12_makra/README.md 13_io_siec_i_protokoly/README.md 14_idiomy_wzorce_i_architektura/README.md
git commit -m "docs: add learning maps for Rust foundations"
```

### Task 7: Dodaj mapy zastosowań i platform 15–24

**Files:**
- Create: `15_aplikacje_cli/README.md` through `24_wasm_i_wieloplatformowosc/README.md`.

**Interfaces:**
- Produces: jawny zakres przyszłych rozdziałów aplikacyjnych i systemowych oraz linki do istniejących podstaw.

- [ ] **Step 1: Dodaj mapy 15–18**

CLI obejmuje argumenty, terminal, I/O i dystrybucję; web obejmuje HTTP, routing, stan, błędy, autentykację i testy; bazy obejmują SQL, transakcje, pule, migracje i repozytoria; integracje obejmują Serde, formaty danych, konfigurację, sekrety i systemy wiadomości. Każdy planowany, jeszcze nieistniejący rozdział jest tekstem listy, nie martwym linkiem.

- [ ] **Step 2: Dodaj mapy 19–24**

Mapy linkują istniejące przeniesione rozdziały. Działy 20, 23 i 24 jawnie wskazują, że połączone materiały o benchmarkach/Miri oraz WASM/no_std zostaną rozdzielone w późniejszym etapie.

- [ ] **Step 3: Zweryfikuj mapy 15–24**

Run: `python3 scripts/verify_content.py .`

Expected: brak błędów linków w mapach 01–24; pozostają tylko brakujące mapy 25–30 i główna nawigacja.

- [ ] **Step 4: Commit**

```bash
git add 15_aplikacje_cli 16_web_i_api 17_bazy_danych_i_persystencja 18_serializacja_konfiguracja_i_integracje 19_runtime_pamiec_i_kompilator/README.md 20_wydajnosc_i_optymalizacja/README.md 21_unsafe_soundness_i_model_pamieci/README.md 22_ffi_i_interoperacyjnosc/README.md 23_no_std_allocatory_i_embedded/README.md 24_wasm_i_wieloplatformowosc
git commit -m "docs: map Rust application and platform tracks"
```

### Task 8: Dodaj mapy produkcyjne i projektowe 25–30

**Files:**
- Create: `25_debugowanie_i_utrzymanie/README.md` through `30_projekty_przekrojowe/README.md`.

**Interfaces:**
- Produces: zakres utrzymania, testowania systemowego, bezpieczeństwa, dostarczania, obserwowalności i siedmiu projektów ze specyfikacji.

- [ ] **Step 1: Dodaj mapy 25–29**

Każda mapa rozdziela mechanizmy biblioteki standardowej i narzędzi oficjalnych od ekosystemu third-party. Dział 26 linkuje do istniejących testów i materiału Miri; dział 28 linkuje do Cargo i SemVer; dział 29 linkuje do async, sieci i architektury.

- [ ] **Step 2: Dodaj mapę siedmiu projektów przekrojowych**

`30_projekty_przekrojowe/README.md` wymienia dokładnie: CLI, parser domenowy, bibliotekę workspace, system wielowątkowy, usługę async, usługę webową z danymi i observability oraz bezpieczną abstrakcję `unsafe`. Dla każdego podaje wymagane wcześniejsze działy i kryterium ukończenia, ale nie tworzy nieistniejącego linku do kodu.

- [ ] **Step 3: Zweryfikuj komplet 30 map**

Run: `python3 scripts/verify_content.py .`

Expected: brak komunikatów `brak README działu`; pozostają wyłącznie błędy braku linków z głównego `README.md`.

- [ ] **Step 4: Commit**

```bash
git add 25_debugowanie_i_utrzymanie 26_testowanie_zaawansowane_fuzzing_i_miri 27_bezpieczenstwo_aplikacji 28_ci_cd_i_release_engineering 29_observability_i_produkcja 30_projekty_przekrojowe
git commit -m "docs: map production topics and capstone projects"
```

### Task 9: Przebuduj główną nawigację i włącz manifest do walidacji

**Files:**
- Modify: `README.md`
- Modify: `150-zaawansowanych-mechanizmow-rust.md`
- Modify: `sciaga.md`
- Modify: `slownik.md`
- Modify: `dalsza_nauka.md`
- Modify: `zrodla.md`
- Modify: `CONTRIBUTING.md`
- Modify: `scripts/verify_content.py`
- Modify: `scripts/test_verify_content.py`

**Interfaces:**
- Consumes: 30 map działów i manifest Task 3.
- Produces: cztery ścieżki czytania oraz automatyczną kontrolę wykonanej migracji.

- [ ] **Step 1: Napisz test automatycznego użycia manifestu**

Dodaj `test_cli_reports_unfinished_migration`: fixture zawiera poprawny układ 30 działów i manifest, którego `source` nadal istnieje. CLI ma zwrócić 1 i wypisać `źródło nadal istnieje po migracji`.

- [ ] **Step 2: Uruchom test czerwony**

Run: `python3 -m unittest scripts.test_verify_content.CliTests.test_cli_reports_unfinished_migration -v`

Expected: FAIL, ponieważ CLI nie ładuje jeszcze manifestu.

- [ ] **Step 3: Włącz manifest do CLI**

Jeśli istnieje `docs/superpowers/audits/2026-10-04-mapa-migracji-30-dzialow.json`, CLI ładuje go i dołącza problemy `validate_migration_manifest` do wspólnego raportu.

- [ ] **Step 4: Przepisz główny `README.md`**

Dodaj krótkie omówienie każdego działu z linkiem do jego `README.md`, pełną ścieżkę 01–30, ścieżkę przyspieszoną oraz ścieżki backend, systems/embedded, wydajność i bezpieczeństwo. Zachowaj legendę przykładów, materiały przekrojowe i komendy walidacji.

- [ ] **Step 5: Zaktualizuj materiały przekrojowe**

Zastąp wszystkie stare linki nowymi celami. Atlas pozostaje indeksem; na tym etapie nie przepisuj jego 150 opisów, tylko napraw nawigację i dodaj linki do map nowych obszarów produkcyjnych.

- [ ] **Step 6: Uruchom pełną walidację treści**

Run: `python3 -m unittest scripts/test_verify_content.py -v && python3 scripts/verify_content.py . && bash scripts/verify.sh`

Expected: wszystkie testy PASS, manifest nie raportuje źródeł ani brakujących celów, wszystkie linki są poprawne, a testy `rustdoc` kończą się sukcesem.

- [ ] **Step 7: Commit**

```bash
git add README.md 150-zaawansowanych-mechanizmow-rust.md sciaga.md slownik.md dalsza_nauka.md zrodla.md CONTRIBUTING.md scripts/verify_content.py scripts/test_verify_content.py
git commit -m "docs: publish thirty-section Rust learning paths"
```

### Task 10: Przeprowadź audyt końcowy etapu migracyjnego

**Files:**
- Create: `docs/superpowers/audits/2026-10-04-wynik-migracji-30-dzialow.md`
- Modify: `docs/superpowers/audits/2026-10-04-mapa-migracji-30-dzialow.md`

**Interfaces:**
- Consumes: wynik pełnej walidacji i historię commitów Tasks 1–9.
- Produces: dowód kompletności migracji i jawny backlog planów merytorycznych.

- [ ] **Step 1: Sprawdź brak dawnych katalogów i komplet nowych**

Run: `git ls-files | rg '^(01_wprowadzenie|03_pamiec_i_wlasnosc|04_typy_i_modelowanie|05_kolekcje_i_iteratory|06_bledy|07_moduly_i_cargo|08_testowanie_i_jakosc|09_wspolbieznosc|10_async|11_makra|12_systemy_i_interoperacyjnosc|13_wzorce_i_architektura|zaawansowane)/'`

Expected: brak wyniku i kod 1.

Run: `find . -maxdepth 2 -type f -name README.md | sort`

Expected: główny `README.md` oraz dokładnie 30 map działów.

- [ ] **Step 2: Uruchom końcową macierz kontroli**

Run: `git diff --check HEAD~9..HEAD && python3 -m unittest scripts/test_verify_content.py -v && bash scripts/verify.sh`

Expected: brak błędów whitespace, wszystkie testy jednostkowe i obowiązkowe kontrole treści PASS.

- [ ] **Step 3: Zapisz wynik i backlog**

Raport zawiera: identyfikatory commitów Tasks 1–9, liczbę przeniesionych plików, wynik testów, użyty `rustc -Vv`, ewentualne pominięte narzędzia opcjonalne oraz osobne następne plany dla: rdzenia 01–14, zastosowań 15–18, internals 19–24, produkcji 25–29 i projektów 30.

- [ ] **Step 4: Oznacz manifest jako wykonany**

W audycie Markdown dopisz datę zakończenia oraz link do raportu wynikowego. Nie zmieniaj historycznych ścieżek w JSON.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/audits/2026-10-04-mapa-migracji-30-dzialow.md docs/superpowers/audits/2026-10-04-wynik-migracji-30-dzialow.md
git commit -m "docs: record completed Rust content migration"
```
