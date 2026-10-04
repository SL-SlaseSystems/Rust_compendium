# Wynik migracji kompendium Rust do 30 działów

Data zakończenia: 4 października 2026 r.

## Wynik

Etap migracyjny zakończono. Repozytorium ma jeden kanoniczny układ 30
numerowanych działów, 30 map działów i główny spis treści. Zachowane materiały
eksperckie zostały włączone do właściwych ścieżek zamiast pozostać w osobnym
katalogu `zaawansowane/`.

Stan po migracji:

- 30 map działów oraz jeden główny `README.md`;
- 72 pliki rozdziałów w numerowanych działach;
- 7 plików rozwiązań;
- 77 wpisów w maszynowym manifeście migracji;
- dokładnie 7 projektów przekrojowych z wymaganiami i kryteriami ukończenia;
- pełna, przyspieszona oraz cztery specjalistyczne ścieżki czytania.

## Zachowanie treści eksperckiej

Materiały o variance, HRTB, GAT, vtables, `Pin`, atomikach, lock-free,
zaawansowanych makrach proceduralnych, MIR/LLVM, modelu pamięci, `unsafe`, FFI,
`no_std`, allocatorach i nightly mają docelowe, tematyczne lokalizacje.

Ostrzeżenia z dawnej mapy eksperckiej zachowano w mapach działów 5, 10–12 i
19–23. W szczególności mapy rozróżniają kod opisujący potencjalne UB od kodu
do uruchomienia, wymagają jawnych invariants oraz nie przedstawiają Miri jako
dowodu braku undefined behavior.

## Historia wykonania

| Commit | Zakres |
|---|---|
| `d1ab95e` | Zachowanie i rozwinięcie rozpoczętego rozdziału o funkcjach i wyrażeniach. |
| `4cc8531` | Kontrakt dokładnie 30 działów w walidatorze. |
| `b134874` | Manifest i audyt 77 elementów migracji. |
| `d70fe19` | Przeniesienie rdzenia języka do działów 01–14. |
| `bc66af8` | Integracja materiałów eksperckich z główną ścieżką. |
| `8ba132b` | Mapy fundamentów 01–14. |
| `8d51df8` | Mapy aplikacji i platform 15–24. |
| `43f6e3a` | Mapy produkcyjne 25–30 i projekty przekrojowe. |
| `3828dc6` | Główna nawigacja i automatyczna kontrola manifestu. |

## Macierz kontroli

Wynik końcowy przed zapisaniem audytu:

- `python3 -m unittest scripts/test_verify_content.py -v` — 27/27 testów PASS;
- `python3 scripts/verify_content.py .` — PASS;
- `bash scripts/verify.sh` z kompatybilnym lokalnym SDK — PASS;
- `git diff --check` — PASS;
- lista dawnych katalogów w `git ls-files` — pusta;
- `find . -maxdepth 2 -type f -name README.md` — główny plik i dokładnie 30 map.

Przykłady wykonano przez `rustdoc 1.90.0 (1159e78c4 2025-09-14)`. Na tym
hoście domyślny CommandLineTools SDK zawiera metadane nieobsługiwane przez ten
toolchain, dlatego lokalna weryfikacja użyła zainstalowanego Xcode 26 SDK przez
`SDKROOT`. Ścieżka SDK jest cechą tego hosta i nie została zapisana w repo.

Atlas `150-zaawansowanych-mechanizmow-rust.md` pozostaje jawnie pomijany przez
rustdoc do czasu dedykowanego etapu weryfikacji atlasu; walidator nadal sprawdza
jego linki i strukturę Markdown.

## Jawny backlog merytoryczny

Migracja tworzy docelową architekturę, ale nie udaje zakończenia całego rozwoju
treści. Następne plany powinny:

1. rozwinąć mapy 15–18 i 24–30 w pełne rozdziały z uruchamialnymi przykładami,
   diagnostyką, ćwiczeniami i rozwiązaniami;
2. wydzielić część Miri z połączonego materiału o benchmarkach do działu 26;
3. rozdzielić wspólne wprowadzenie WASM/`no_std` między działy 23 i 24;
4. rozszerzyć krótsze rozdziały rdzenia do kontraktu rozdziału rozszerzonego;
5. przygotować osobne projekty testowe dla przykładów **third-party**;
6. objąć 150-elementowy atlas dedykowaną walidacją wykonywalnych fragmentów;
7. okresowo aktualizować twierdzenia zależne od wersji, źródła i MSRV.

## Konkluzja

Zmiana jest kompletna jako etap strukturalno-migracyjny: nie ma dwóch
konkurencyjnych układów, nie ma martwych linków ani pominiętych celów manifestu,
a dalsza rozbudowa może odbywać się dział po dziale bez ponownego przenoszenia
zachowanych materiałów.
