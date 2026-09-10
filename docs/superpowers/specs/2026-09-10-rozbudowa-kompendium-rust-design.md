# Rozbudowa kompendium języka Rust

## Cel

Rozwinąć istniejące polskojęzyczne kompendium tak, aby prowadziło od
intuicyjnego rozumienia Rusta do wiedzy eksperckiej, a jednocześnie uczyło
budowania i utrzymywania rzeczywistych programów. Materiał ma pozostać
podręcznikiem oraz dokumentacją referencyjną, lecz otrzymać głębsze
wyjaśnienia, ćwiczenia i kompilowalne projekty praktyczne.

## Odbiorca i rezultat nauki

Odbiorca zna już podstawy programowania albo poznaje je równolegle, ale chce
zrozumieć nie tylko składnię, lecz również decyzje kompilatora, model pamięci,
koszty abstrakcji i praktyki produkcyjne. Po przejściu materiału powinien:

- swobodnie czytać i projektować idiomatyczny kod Rust;
- rozumieć ownership, borrowing, lifetimes, traits i model błędów;
- diagnozować komunikaty kompilatora i świadomie poprawiać kod;
- projektować biblioteki, aplikacje współbieżne i programy async;
- rozumieć granice bezpiecznego Rusta oraz audytować małe abstrakcje `unsafe`;
- mierzyć wydajność i odróżniać koszt języka od kosztu wybranego projektu;
- budować, testować i dokumentować realne pakiety Cargo.

## Podstawa wersji i źródeł

Materiał opisuje Rust Edition 2024 i stabilny toolchain Rust 1.98.1 według
stanu na 10 września 2026 r. Informacje zależne od wydania muszą zawierać datę
weryfikacji. Pierwszeństwo mają oficjalne materiały projektu Rust:

- The Rust Programming Language — ścieżka dydaktyczna i podstawowe idiomy;
- Rust Reference — reguły składni i semantyki stabilnego języka;
- standard library documentation — kontrakty typów i funkcji;
- Cargo Book, rustc Book, rustdoc Book i Clippy documentation — narzędzia;
- Rustonomicon — zagadnienia `unsafe`, po sprawdzeniu z Reference i aktualną
  dokumentacją API;
- Edition Guide, Async Book, Embedded Book i Reference materiałów WebAssembly
  tam, gdzie dotyczą danego rozdziału.

Rustonomicon nie jest traktowany jako samodzielne, zawsze aktualne źródło.
Twierdzenia o nieustabilizowanych mechanizmach muszą być oznaczone jako
**nightly** albo opisane jako kierunek rozwoju, nie jako gwarancja.

## Architektura treści

Obecne katalogi `01`–`13` oraz `zaawansowane` pozostają główną osią
kompendium. Nie zmieniamy kolejności bez istotnego powodu dydaktycznego.
Rozbudowa odbywa się w miejscu, aby istniejące odsyłacze zachowały znaczenie.

Każdy rozdział, stosownie do tematu, otrzyma następujące warstwy:

1. cele i wymagania wstępne;
2. intuicję oraz model mentalny;
3. dokładne reguły języka albo kontrakty API;
4. przykłady rosnące od minimalnych do realistycznych;
5. analizę ownership, lifetime'ów, typów i przepływu danych;
6. celowo błędny kod oraz interpretację diagnostyki kompilatora;
7. idiomy produkcyjne, antywzorce i kompromisy;
8. koszty wykonania, alokacje, layout lub synchronizację, gdy są istotne;
9. pytania kontrolne i ćwiczenia na trzech poziomach;
10. powiązania z projektem praktycznym i wiedzą zaawansowaną.

Nie każda warstwa musi być osobnym nagłówkiem. Struktura służy wyjaśnieniu
tematu i nie może powodować mechanicznych powtórzeń.

## Zakres pogłębienia

Rozbudowa obejmuje wszystkie istniejące działy. Największy nacisk otrzymają:

- model pamięci, ownership, borrowing, reborrowing, lifetimes i drop order;
- modelowanie przez enumy, generics, traits, associated types, GAT i HRTB;
- iteratory, closures, konwersje i projektowanie błędów;
- moduły, workspaces, features, dokumentacja i stabilność publicznego API;
- testy jednostkowe, integracyjne, dokumentacyjne, property-based i fuzzing;
- wątki, kanały, blokady, atomiki, pamięć współdzielona i structured
  concurrency;
- `Future`, pinning, executory, anulowanie i zachowanie runtime'ów async;
- makra deklaratywne i proceduralne wraz z diagnostyką;
- I/O, sieć, FFI, WebAssembly, `no_std` i embedded;
- wydajność, layout, cache, monomorfizację, MIR i podstawy LLVM;
- soundness, provenance, niezainicjalizowaną pamięć, panic safety oraz audyt
  `unsafe`.

Rozdziały początkowe również zostaną pogłębione, ale bez zalewania początkującej
osoby detalami potrzebnymi dopiero później. Informacje eksperckie będą
wydzielone i połączone odsyłaczem.

## Atlas 150 mechanizmów

`150-zaawansowanych-mechanizmow-rust.md` pozostaje przekrojowym atlasem i
indeksem. Nie powinien równolegle odtwarzać całych rozdziałów. Każdy mechanizm
ma otrzymać:

- jednoznaczną nazwę i krótką definicję;
- wskazanie poziomu oraz wymagań wstępnych;
- odsyłacz do rozdziału z pełnym wyjaśnieniem;
- mały przykład tylko wtedy, gdy pomaga on korzystać z atlasu niezależnie.

Powtórzenia sprzeczne z rozdziałami zostaną usunięte albo zastąpione
odsyłaczem. Atlas będzie także listą kontrolną pokrycia materiału.

## Ćwiczenia i rozwiązania

Na końcu rozdziałów pojawią się trzy rodzaje zadań:

- **podstawowe** — sprawdzają jedną regułę lub składnię;
- **praktyczne** — wymagają połączenia kilku pojęć;
- **pogłębione** — każą uzasadnić kontrakt, koszt albo zachowanie kompilatora.

Rozwiązania znajdą się w osobnym katalogu `rozwiazania/` i będą linkowane w
sposób, który nie zdradza odpowiedzi podczas zwykłego czytania. Rozwiązanie
powinno wyjaśniać tok rozumowania, a nie tylko podawać działający kod.

## Projekty praktyczne

Nowy katalog `projekty/` zawiera prawdziwe pakiety lub workspace'y Cargo.
Każdy projekt ma instrukcję, kryteria ukończenia, testy, wersję podstawową i
opcjonalne rozszerzenia. Kolejność projektów:

1. narzędzie CLI — argumenty, I/O, błędy, testy i dokumentacja;
2. parser i model domenowy — enumy, wzorce, lifetimes, iteratory i dobre API;
3. biblioteka wielopakietowa — moduły, workspace, features i SemVer;
4. wielowątkowy system zadań — kanały, `Arc`, blokady, shutdown i testy;
5. usługa async — zadania, timeouty, anulowanie, backpressure i observability;
6. mała bezpieczna abstrakcja oparta na `unsafe` — invariants, `# Safety`,
   `SAFETY` comments, Miri i ręczny audyt.

Pierwszeństwo ma biblioteka standardowa. Zewnętrzne crate'y są dodawane tylko
tam, gdzie reprezentują realistyczną praktykę, i muszą być oznaczone jako
**third-party** wraz z uzasadnieniem.

## Ścieżka nauki i nawigacja

`README.md` otrzyma:

- główną ścieżkę od zera do poziomu eksperckiego;
- wariant przyspieszony dla programisty innego języka;
- kamienie milowe oraz projekty przypisane do działów;
- przybliżone wymagania wstępne dla części zaawansowanej;
- odsyłacze do ćwiczeń, rozwiązań, atlasu, ściągi i słownika.

Rozdziały będą linkować wstecz do wymagań i naprzód do naturalnych zastosowań.
Odsyłacze mają tworzyć graf nauki, ale główna numerowana kolejność pozostaje
jednoznaczna.

## Diagnostyka i błędy

Przykład błędu musi wyjaśnić:

1. która reguła została naruszona;
2. jak przeczytać najważniejsze części komunikatu `rustc`;
3. jaka poprawka usuwa przyczynę, a nie tylko objaw;
4. kiedy alternatywna konstrukcja lepiej wyraża intencję programu.

Nie utrwalamy pełnych komunikatów kompilatora, jeśli są zależne od wersji.
Stabilne kody błędów można podawać pomocniczo, lecz objaśnienie musi pozostać
zrozumiałe po zmianie brzmienia diagnostyki.

## Weryfikacja

Istniejący `scripts/verify.sh` zostanie rozszerzony. Kryteria jakości obejmują:

- sprawdzenie linków, pustych plików, struktury bloków i wpisów w indeksie;
- `rustdoc --test --edition 2024` dla samowystarczalnych przykładów;
- oczekiwane odrzucenie bloków `compile_fail`;
- `cargo fmt --check`, `cargo clippy --all-targets --all-features -- -D warnings`
  i `cargo test --all-targets --all-features` dla projektów;
- testy dokumentacyjne publicznego API projektów;
- Miri dla projektu `unsafe`, jeśli dostępny jest wymagany toolchain nightly;
- ręczny audyt zgodności treści z aktualnymi oficjalnymi źródłami;
- skan terminologii stable/nightly/third-party i dat w treściach zmiennych.

Brak opcjonalnego narzędzia, takiego jak Miri, ma być jawnie raportowany, a nie
udawany jako sukces. Podstawowa walidacja stable pozostaje obowiązkowa.

## Etapy realizacji

1. Audyt pokrycia, wersji, odsyłaczy i struktury rozdziałów.
2. Fundamenty języka, pamięć, ownership i typy.
3. Kolekcje, błędy, Cargo, testowanie i projektowanie API.
4. Współbieżność, async, systemy, makra i interoperacyjność.
5. Część ekspercka oraz uporządkowanie atlasu 150 mechanizmów.
6. Ćwiczenia, rozwiązania i sześć projektów praktycznych.
7. Audyt merytoryczny, pełna walidacja i aktualizacja ścieżek nauki.

Każdy etap kończy się zieloną walidacją odpowiednią do zmienionych plików.
Zmiany powinny być małymi, tematycznymi commitami, aby dało się je przeglądać
i w razie potrzeby odwrócić niezależnie.

## Kryteria ukończenia

Projekt jest ukończony, gdy:

- każdy istniejący rozdział realizuje odpowiednie warstwy dydaktyczne;
- kluczowe reguły mają poprawny przykład i co najmniej jeden omówiony błąd;
- wszystkie ćwiczenia mają wyjaśnione rozwiązania;
- wszystkie projekty kompilują się, przechodzą testy i dokumentują kompromisy;
- atlas 150 mechanizmów odsyła do pogłębionych rozdziałów bez sprzeczności;
- README prowadzi czytelnika przez teorię, praktykę i poziom ekspercki;
- obowiązkowa walidacja stable kończy się bez błędów;
- stan stabilności i informacje zależne od czasu są opisane uczciwie.

## Poza zakresem

- encyklopedyczne omówienie wszystkich crate'ów z crates.io;
- pełny kurs każdego runtime'u, frameworka webowego lub platformy embedded;
- gwarantowanie zachowania niestabilnych szczegółów implementacji kompilatora;
- zastępowanie dokumentacji systemów operacyjnych, protokołów i języka C.

