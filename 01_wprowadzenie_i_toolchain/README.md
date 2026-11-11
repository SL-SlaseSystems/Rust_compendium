[← Spis treści](../README.md)

# 1. Wprowadzenie i toolchain

## Dla kogo i po co

Dla osoby zaczynającej naukę Rust. Dział wyjaśnia, czym język różni się od innych narzędzi systemowych, i przygotowuje działające środowisko pracy.

## Wymagania wstępne

Wystarczy podstawowa umiejętność pracy w terminalu i edytorze tekstu.

## Kolejność materiałów

1. [Czym jest Rust](01_czym_jest_rust.md)
2. [Instalacja i toolchain](02_instalacja_i_toolchain.md)
3. [Pierwszy program](03_pierwszy_program.md)
4. [Cargo w praktyce](04_cargo_w_praktyce.md)

## Po tym dziale

Potrafisz utworzyć projekt, zbudować go, uruchomić, przetestować i sprawdzić dokumentację zależności.

## Jak pracować z działem

Przejdź cztery rozdziały w podanej kolejności. Najpierw nazwij mierzalny cel wyboru języka, potem ustal aktywny toolchain i oddziel host od targetu. Pierwszy program wykorzystaj do zrozumienia wyrażeń i granicy procesu, a Cargo do opisania odtwarzalnej pętli pracy. Nie instaluj nowej wersji tylko dlatego, że występuje jako przykład konfiguracji.

Każdy rozdział zawiera trzy zadania ze stabilnymi identyfikatorami `W01`–`W04`, połączone z pełnymi rozwiązaniami w równoległym podkatalogu `rozwiazania/`. Najpierw przewidź wynik samodzielnie. Potem porównaj nie tylko kod, ale również powód wyboru ownership, politykę błędów i ograniczenia sprawdzenia.

## Punkt kontrolny

Potrafisz wskazać crate root, wyjaśnić `cargo check` wobec linkowania, odczytać wybór rustup oraz zaplanować `Cargo.lock`. Umiesz odróżnić gwarancję języka od limitu zasobów aplikacji. Samodzielnym sprawdzianem jest mały CLI z logiką w funkcji, jawnym błędem wejścia i zapisanymi komendami jakości.

Materiały używają Edition 2024, a samowystarczalne przykłady sprawdzane są na stable Rust 1.90.0. Pokazany plik konfiguracji innej wersji nie jest deklaracją wykonania testów na tej wersji.

## Co dalej

Przejdź do podstaw składni. Zachowaj stabilny toolchain jako domyślny; nightly włączaj tylko dla jawnie wymaganej funkcji.

Następny dział: [Podstawy języka](../02_podstawy_jezyka/README.md).
