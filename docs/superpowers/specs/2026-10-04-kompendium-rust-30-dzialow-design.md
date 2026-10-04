# Kompendium Rust — struktura 30 działów

## Cel

Rozwinąć istniejące polskojęzyczne kompendium Rust do kompletnej ścieżki
nauki i referencji inspirowanej organizacją repozytorium Python-Wiki, ale
dopasowanej do semantyki, narzędzi i typowych zastosowań Rusta. Repozytorium
ma prowadzić od pierwszego programu przez ownership i system typów do
zagadnień produkcyjnych, niskopoziomowych i projektów przekrojowych.

Przebudowa zachowuje wartościowe istniejące treści, w szczególności atlas
150 zaawansowanych mechanizmów, rozdziały eksperckie, rozwiązania ćwiczeń,
ściągę, słownik, źródła i walidator. Istniejące materiały są migrowane i
rozwijane, a nie zastępowane skrótową wersją pisaną od zera.

## Repozytorium i stan wejściowy

Prace odbywają się bezpośrednio w istniejącym repozytorium Git
`Rust_compendium`, w worktree gałęzi `codex/rozbudowa-rdzenia-rust`.
Punktem wyjścia jest najnowszy stan tego worktree, włącznie z zastanymi
niezacommitowanymi zmianami w rozdziale o funkcjach oraz odpowiadającym mu
rozwiązaniem.

Zastane zmiany należy najpierw utrwalić w osobnym, jednoznacznie opisanym
commicie. Nie wolno ich nadpisywać, przepisywać ani włączać przypadkowo do
commitu reorganizacyjnego.

Repozytorium Python-Wiki jest wzorcem nawigacji i szerokości ścieżki, nie
źródłem podziału jeden do jednego. Nazwy działów i zakres pozostają rustowe.

## Odbiorca i rezultat

Odbiorcą jest osoba znająca podstawy programowania lub ucząca się ich
równolegle, która chce przejść od składni do świadomego projektowania i
utrzymywania oprogramowania Rust. Repozytorium ma również działać jako
referencja dla programisty wracającego do konkretnego zagadnienia.

Po przejściu całości czytelnik powinien potrafić:

- pisać idiomatyczny, testowalny i udokumentowany kod Rust;
- rozumieć ownership, borrowing, lifetimes i model błędów;
- modelować domenę przez enumy, generics, traits i typestate;
- korzystać świadomie z Cargo, workspaces i narzędzi jakości;
- budować programy współbieżne, asynchroniczne i sieciowe;
- projektować CLI, API, warstwę danych i integracje;
- mierzyć wydajność oraz diagnozować zachowanie kompilatora i runtime'u;
- rozumieć granice bezpiecznego Rusta i audytować małe fragmenty `unsafe`;
- przygotować aplikację do CI/CD, obserwowalności i bezpiecznej eksploatacji.

## Docelowa architektura treści

Główna ścieżka składa się z 30 numerowanych działów:

1. Wprowadzenie i toolchain.
2. Podstawy języka.
3. Ownership, borrowing i lifetimes.
4. Struktury, enumy i pattern matching.
5. Generics, traits i zaawansowany system typów.
6. Kolekcje, iteratory i closures.
7. Obsługa błędów.
8. Moduły, crates, Cargo i workspaces.
9. Dokumentacja, testowanie i jakość.
10. Współbieżność.
11. Async Rust.
12. Makra.
13. Pliki, I/O, sieć i protokoły.
14. Idiomy, wzorce i architektura.
15. Aplikacje CLI.
16. Web i projektowanie API.
17. Bazy danych i persystencja.
18. Serializacja, konfiguracja i integracje.
19. Runtime, pamięć i wnętrze kompilatora.
20. Wydajność i optymalizacja.
21. `unsafe`, soundness i model pamięci.
22. FFI i interoperacyjność.
23. `no_std`, allocatory i embedded.
24. WebAssembly i wieloplatformowość.
25. Debugowanie i utrzymanie dużego kodu.
26. Zaawansowane testowanie, fuzzing i Miri.
27. Bezpieczeństwo aplikacji.
28. CI/CD, publikowanie i release engineering.
29. Observability i środowisko produkcyjne.
30. Projekty przekrojowe.

Każdy dział ma własny `README.md`, który określa cel, wymagania wstępne,
rezultaty nauki, kolejność rozdziałów oraz naturalne następne kroki. Rozdziały
tematyczne pozostają osobnymi plikami Markdown. Projekty zawierające kod są
pakietami albo workspaces Cargo i żyją pod działem 30 lub są z niego
jednoznacznie linkowane.

## Materiały przekrojowe

W katalogu głównym pozostają materiały służące całemu kompendium:

- `150-zaawansowanych-mechanizmow-rust.md` jako atlas i indeks pokrycia;
- `sciaga.md` jako szybka referencja;
- `slownik.md` jako słownik polsko-angielskiej terminologii;
- `dalsza_nauka.md` jako mapa oficjalnych i specjalistycznych źródeł;
- `zrodla.md` jako rejestr źródeł i dat weryfikacji;
- `CONTRIBUTING.md` jako kontrakt jakości treści;
- `rozwiazania/` jako struktura równoległa do rozdziałów z ćwiczeniami.

Atlas nie powiela pełnych rozdziałów. Każdy mechanizm otrzymuje krótką
definicję, poziom, wymagania wstępne i link do kanonicznego omówienia.

## Kontrakt działu i rozdziału

`README.md` działu zawiera:

- krótki opis roli działu w całej ścieżce;
- wymagania wstępne;
- listę rozdziałów w zalecanej kolejności;
- konkretne rezultaty nauki;
- odsyłacze do ćwiczeń, projektu i dalszych działów.

Rozbudowany rozdział zawiera, odpowiednio do tematu:

1. cele;
2. intuicję lub model mentalny;
3. dokładne reguły języka albo kontrakty API;
4. poprawny, możliwie samowystarczalny przykład;
5. celowo błędny przykład i diagnostykę kompilatora;
6. praktykę produkcyjną, antywzorce oraz kompromisy;
7. koszty wykonania, alokacje, layout lub synchronizację, gdy są istotne;
8. pytania kontrolne;
9. ćwiczenia podstawowe, praktyczne i pogłębione;
10. powiązane tematy i naturalny następny krok.

Elementy te nie muszą być mechanicznym zestawem identycznych nagłówków, jeśli
inna organizacja lepiej służy tematowi. Każdy rozbudowany rozdział zachowuje
jednak istniejący, maszynowo sprawdzalny kontrakt oznaczony
`<!-- status: expanded -->`.

## Ścieżki czytania

Główne `README.md` udostępnia cztery sposoby korzystania z repozytorium:

- pełną ścieżkę od podstaw do produkcji;
- ścieżkę przyspieszoną dla programisty innego języka;
- ścieżki specjalizacyjne: backend, systems/embedded, wydajność i
  bezpieczeństwo;
- tryb referencyjny przez atlas, słownik i ściągę.

Każda ścieżka wskazuje wymagania i kamienie milowe. Tematy eksperckie są
włączone do głównej mapy, ale nie obciążają początkowych rozdziałów detalami,
których czytelnik jeszcze nie potrzebuje.

## Migracja istniejących materiałów

Przed przenoszeniem powstaje jawna mapa `stary plik -> nowy plik`. Każdy
istniejący rozdział musi zostać przypisany do jednego kanonicznego miejsca.
Przeniesienia są wykonywane przez Git, aby historia pozostała czytelna.

Migracja spełnia następujące zasady:

- żadna wartościowa treść nie znika bez świadomej decyzji zapisanej w audycie;
- zastane niezacommitowane zmiany są zachowane przed reorganizacją;
- po każdym przeniesieniu aktualizowane są linki przychodzące i wychodzące;
- duplikaty są scalane w jeden rozdział kanoniczny, a pozostałe miejsca linkują
  do niego;
- zawartość dawnego katalogu `zaawansowane/` jest rozdzielana głównie między
  działy 5 oraz 19–24 i 26;
- materiały stabilne, nightly i zależne od zewnętrznych crate'ów są oznaczane
  jawnie;
- twierdzenia zależne od wydania zawierają datę weryfikacji.

## Projekty praktyczne

Dział 30 spina teorię w rosnące projekty Cargo:

1. narzędzie CLI z I/O, błędami, testami i dokumentacją;
2. parser i model domenowy wykorzystujący enumy, iteratory i dobre API;
3. biblioteka w workspace z features i polityką SemVer;
4. wielowątkowy system zadań z kontrolowanym shutdownem;
5. usługa async z timeoutami, anulowaniem i backpressure;
6. usługa webowa z warstwą danych, konfiguracją i observability;
7. mała bezpieczna abstrakcja nad `unsafe`, sprawdzana przez Miri, jeśli jest
   dostępne odpowiednie środowisko.

Każdy projekt ma instrukcję, kryteria ukończenia, testy, wariant podstawowy i
opcjonalne rozszerzenia. Zewnętrzne zależności są dodawane tylko tam, gdzie
odzwierciedlają realistyczną praktykę i są opisane jako **third-party**.

## Walidacja i obsługa błędów

Walidacja jest częścią architektury, a nie końcowym dodatkiem. Obejmuje:

- sprawdzenie lokalnych linków, pustych plików, fence'ów Markdown i nawigacji;
- kontrolę wymaganych sekcji rozbudowanych rozdziałów;
- zgodność identyfikatorów ćwiczeń z kotwicami rozwiązań;
- testy jednostkowe walidatora treści;
- `rustdoc --test --edition 2024` dla samowystarczalnych przykładów;
- oczekiwane odrzucenie przykładów `compile_fail`;
- `cargo fmt --check`, `cargo clippy --all-targets --all-features -- -D warnings`
  i `cargo test --all-targets --all-features` dla projektów;
- dokumentację publicznego API projektów;
- Miri dla odpowiedniego projektu `unsafe`, jeżeli wymagany toolchain jest
  dostępny;
- skan statusów stable, nightly, third-party oraz dat przy informacjach
  zależnych od wersji.

Brak narzędzia opcjonalnego jest raportowany jako pominięta kontrola, nie jako
sukces. Błąd obowiązkowej walidacji blokuje zamknięcie danego etapu. Przy
niezgodności wersji lokalnego toolchainu raport podaje wersję faktycznie użytą
do testów i nie przypisuje jej wyników nowszemu wydaniu.

## Etapy realizacji

1. Zabezpieczenie zastanych zmian, audyt i mapa migracji.
2. Utworzenie struktury 01–30 oraz nawigacji bez utraty treści.
3. Ujednolicenie działów 1–14 i dokończenie rozpoczętego rdzenia języka.
4. Dodanie warstwy aplikacyjnej: CLI, web, bazy danych i integracje.
5. Rozwinięcie runtime'u, wydajności, `unsafe`, FFI, embedded i WASM.
6. Dodanie utrzymania, testowania systemowego, bezpieczeństwa, CI/CD i
   observability.
7. Implementacja projektów przekrojowych i odpowiadających im ćwiczeń.
8. Uporządkowanie atlasu 150 mechanizmów oraz pełny audyt końcowy.

Każdy etap kończy się walidacją odpowiednią do zmienionych plików i małymi,
tematycznymi commitami. Implementacja może być odbierana etapami; nie wolno
ogłaszać ukończenia całego kompendium po utworzeniu samych katalogów lub
szkieletów.

## Kryteria ukończenia

Przebudowa jest ukończona, gdy:

- wszystkie 30 działów ma kompletne mapy i co najmniej jeden kanoniczny
  rozdział lub jawnie określony zakres projektu;
- każdy istniejący materiał ma udokumentowane miejsce docelowe;
- wartościowe treści i przykłady zaawansowane zostały zachowane;
- główne ścieżki czytania są kompletne i nie zawierają martwych linków;
- rozbudowane rozdziały spełniają kontrakt dydaktyczny;
- ćwiczenia mają odpowiadające rozwiązania;
- projekty kompilują się i przechodzą obowiązkowe testy;
- atlas prowadzi do kanonicznych rozdziałów bez sprzecznych duplikatów;
- pełna obowiązkowa walidacja kończy się kodem wyjścia 0;
- ograniczenia narzędzi i status niestabilnych mechanizmów są opisane uczciwie.

## Poza zakresem

- encyklopedyczny katalog wszystkich crate'ów z crates.io;
- pełny kurs każdego frameworka webowego, runtime'u lub platformy embedded;
- kopiowanie podziału Python-Wiki jeden do jednego;
- gwarantowanie niestabilnych szczegółów implementacji kompilatora;
- zastępowanie oficjalnej dokumentacji systemów operacyjnych, protokołów i C;
- usuwanie historii Git albo zastanych zmian w celu uproszczenia migracji.
