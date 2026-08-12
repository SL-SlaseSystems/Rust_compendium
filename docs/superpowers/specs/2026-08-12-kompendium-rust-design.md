# Projekt kompendium języka Rust

## Cel

Utworzyć kompletne, polskojęzyczne kompendium języka Rust w postaci modularnych plików Markdown. Materiał ma prowadzić od absolutnych podstaw do tematów eksperckich, a jednocześnie nadawać się do późniejszego używania jako podręcznik i dokumentacja referencyjna.

## Odbiorca i sposób użycia

Kompendium jest przeznaczone dla osoby, która może zaczynać bez znajomości Rusta, ale chce dojść do samodzielnego rozumienia zaawansowanych mechanizmów języka. Rozdziały mają tworzyć zalecaną ścieżkę nauki, natomiast jednoznaczne nazwy katalogów, spis treści, słownik i ściąga umożliwią szybkie wyszukiwanie pojedynczych zagadnień.

## Zakres i format

- Język treści: polski.
- Format: wyłącznie pliki Markdown i fragmenty kodu osadzone w tekście.
- Bez osobnych, kompilowalnych projektów Cargo.
- Podstawa merytoryczna: aktualny stabilny Rust, Rust Edition 2024 oraz oficjalna dokumentacja projektu Rust.
- Zakres: składnia, semantyka, narzędzia, biblioteka standardowa, współbieżność, programowanie asynchroniczne, makra, programowanie systemowe, interoperacyjność, projektowanie API, wydajność i mechanizmy eksperckie.
- Elementy zależne od ekosystemu zewnętrznych bibliotek będą wyraźnie oddzielone od funkcji języka i biblioteki standardowej.
- Funkcjonalności niestabilne będą oznaczone jako nightly i nie będą przedstawiane jako dostępne w stabilnym kompilatorze.

## Organizacja treści

Katalog główny będzie zawierał `README.md` z pełnym spisem treści, instrukcją korzystania i sugerowanymi ścieżkami nauki. Główne rozdziały zostaną podzielone na następujące katalogi:

1. `01_wprowadzenie` — charakterystyka języka, instalacja toolchainu, `rustup`, `rustc`, Cargo i pierwszy program.
2. `02_podstawy_jezyka` — zmienne, mutowalność, typy, funkcje, wyrażenia, instrukcje, sterowanie przepływem i komentarze.
3. `03_pamiec_i_wlasnosc` — model pamięci, stos i sterta, ownership, przenoszenie, kopiowanie, borrowing, slices, lifetimes, RAII i destruktory.
4. `04_typy_i_modelowanie` — struktury, tuple structs, enumy, pattern matching, metody, generics, traits, associated types, const generics i konwersje.
5. `05_kolekcje_i_iteratory` — napisy, tablice, wektory, mapy, zbiory, closures, iteratory i lazy evaluation.
6. `06_bledy` — `Option`, `Result`, operator `?`, `panic!`, własne typy błędów, propagacja i projektowanie API błędów.
7. `07_moduly_i_cargo` — moduły, widoczność, crates, pakiety, workspaces, zależności, feature flags, profile i publikowanie.
8. `08_testowanie_i_jakosc` — testy jednostkowe, integracyjne i dokumentacyjne, organizacja testów, linting, formatowanie, dokumentacja, benchmarki i narzędzia diagnostyczne.
9. `09_wspolbieznosc` — wątki, scoped threads, kanały, współdzielenie stanu, muteksy, blokady, atomiki oraz cechy `Send` i `Sync`.
10. `10_async` — `Future`, `async`/`await`, pinning w praktyce, executory, taski, streamy, anulowanie, time-outy i typowe błędy.
11. `11_makra` — makra deklaratywne, higiena, fragment specifiers, repetition oraz przegląd makr proceduralnych.
12. `12_systemy_i_interoperacyjnosc` — wejście/wyjście, system plików, procesy, sieć, FFI, C ABI, WebAssembly, `no_std` i podstawy embedded.
13. `13_wzorce_i_architektura` — idiomy, newtype, builder, typestate, rozszerzanie traits, object safety/dyn compatibility, projektowanie publicznego API i organizacja większych aplikacji.
14. `zaawansowane` — osobny zbiór pogłębionych tematów opisanych poniżej.

Pliki `slownik.md`, `sciaga.md`, `dalsza_nauka.md` i `zrodla.md` uzupełnią główną ścieżkę.

## Katalog zaawansowany

Osobne pliki opiszą co najmniej:

- kontrakty i uzasadnianie kodu `unsafe`;
- surowe wskaźniki, aliasing, wyrównanie, layout i niezainicjalizowaną pamięć;
- variance, subtyping i zaawansowane zależności lifetime’ów;
- HRTB, GAT, associated types, RPIT, `impl Trait` i trait objects;
- pinning, self-referential types i mechanikę `Future`;
- atomiki, porządki pamięci i podstawy programowania lock-free;
- makra proceduralne i model tokenów;
- FFI, ABI, repr oraz bezpieczne otoczki na kod obcy;
- `no_std`, allocatory i programowanie embedded;
- monomorfizację, dynamic dispatch, optymalizację i analizę wygenerowanego kodu;
- MIR, LLVM, borrow checker, drop checking i ogólny przebieg kompilacji;
- funkcje stabilne i niestabilne oraz świadome korzystanie z nightly.

## Szablon rozdziału

Każdy zwykły rozdział będzie stosował, gdy ma to sens, spójny układ:

1. Cel i intuicja.
2. Najważniejsze pojęcia i reguły.
3. Składnia.
4. Jeden lub kilka fragmentów kodu.
5. Objaśnienie kodu krok po kroku.
6. Typowe błędy kompilatora lub pułapki.
7. Dobre praktyki i wskazówki projektowe.
8. Powiązania z innymi rozdziałami.
9. Krótkie podsumowanie.

Nie każdy plik musi mechanicznie zawierać wszystkie sekcje. Struktura ma wspierać temat, a nie powodować sztuczne powtórzenia.

## Przykłady kodu

Przykłady będą krótkie, samowystarczalne na poziomie omawianego zagadnienia i oznaczone blokami `rust`. Kod wymagający zewnętrznego crate’a będzie zawierał nazwę zależności oraz wyjaśnienie, że nie należy ona do biblioteki standardowej. Przykłady błędnego kodu będą jawnie podpisane jako celowo niekompilujące się i uzupełnione oczekiwanym rodzajem błędu.

## Nawigacja

- Każdy plik będzie zawierał łącze do nadrzędnego spisu treści oraz odsyłacze do tematów powiązanych.
- `README.md` będzie zawierał kompletną kolejność czytania.
- `sciaga.md` będzie skróconym przypomnieniem składni i najczęstszych operacji, a nie powtórzeniem podręcznika.
- `slownik.md` wyjaśni terminologię angielską i jej polskie odpowiedniki.
- `dalsza_nauka.md` poda kolejne kroki według specjalizacji: backend, CLI, systemy, embedded, WebAssembly i biblioteki.
- `zrodla.md` zbierze przede wszystkim oficjalne źródła, wykorzystane do weryfikacji treści.

## Jakość i weryfikacja

- Wszystkie linki względne zostaną automatycznie sprawdzone.
- Bloki kodu Rust zostaną objęte kontrolą składni lub kompilacją tam, gdzie fragment jest samowystarczalny; fragmenty celowo błędne i pseudokod zostaną oznaczone metadanymi lub opisem i wyłączone z tego sprawdzenia.
- Zostanie wykonany skan brakujących tematów względem oficjalnych podręczników: The Rust Programming Language, Rust Reference, Rustonomicon, Async Book, Cargo Book, Edition Guide i biblioteki standardowej.
- Zostaną sprawdzone niespójne nazwy, puste pliki, niedomknięte bloki kodu i brakujące wpisy w spisie treści.
- Materiał nie będzie twierdził, że każde API ekosystemu jest częścią standardowego Rusta.

## Kryteria ukończenia

Projekt jest ukończony, gdy:

- wszystkie wymienione kategorie i tematy mają opisane miejsce w strukturze;
- każdy istotny temat zawiera co najmniej jeden użyteczny przykład lub uzasadnione objaśnienie, gdy przykład kodu nie ma zastosowania;
- katalog `zaawansowane` stanowi samodzielną, pogłębioną część materiału;
- `README.md` prowadzi przez całość bez martwych łączy;
- kontrole struktury, linków i przykładów nie wykazują niewyjaśnionych błędów;
- treść jest napisana po polsku i konsekwentnie rozróżnia pojęcia stabilne, nightly oraz elementy zewnętrznego ekosystemu.
