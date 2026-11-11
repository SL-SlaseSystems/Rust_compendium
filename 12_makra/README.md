[← Spis treści](../README.md)

# 12. Makra

## Dla kogo i po co

Dla osób automatyzujących powtarzalny kod i projektujących rozszerzenia składni z czytelną diagnostyką.

## Wymagania wstępne

Moduły, traits, generics i swobodne czytanie składni Rust.

## Kolejność materiałów

1. [`macro_rules!`](01_macro_rules.md)
2. [Higiena, fragmenty i repetition](02_higiena_fragmenty_i_repetition.md)
3. [Makra proceduralne](03_makra_proceduralne.md)
4. [Zaawansowane makra proceduralne](04_zaawansowane_makra_proceduralne.md)

## Po tym dziale

Potrafisz zdecydować, czy makro jest właściwym narzędziem, oraz budować makra z przewidywalną ekspansją i użytecznymi błędami.

## Praca z rozdziałami

Każdy rozdział zawiera model działania, przykłady, diagnostykę, decyzje produkcyjne i trzy zadania o rosnącym poziomie trudności. Najpierw przewiduj wynik kodu, następnie go uruchom, a dopiero potem porównaj rozwiązanie.

- [`macro_rules!`: rozwiązania](../rozwiazania/12_makra/01_macro_rules.md)
- [Higiena, fragmenty i repetition: rozwiązania](../rozwiazania/12_makra/02_higiena_fragmenty_i_repetition.md)
- [Makra proceduralne: rozwiązania](../rozwiazania/12_makra/03_makra_proceduralne.md)
- [Zaawansowane makra proceduralne: rozwiązania](../rozwiazania/12_makra/04_zaawansowane_makra_proceduralne.md)

Przykłady samowystarczalne odnoszą się do Rust 1.90, Edition 2024. Bloki `text` z zależnościami zewnętrznymi lub wymaganiami środowiskowymi opisują oddzielny kontrakt; nie są testami wykonanymi przez rustdoc.

## Co dalej

Stosuj makra oszczędnie w bibliotekach i aplikacjach. Zaawansowane makra proceduralne wymagają testów ekspansji oraz przypadków błędnych.
