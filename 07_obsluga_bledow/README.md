[← Spis treści](../README.md)

# 7. Obsługa błędów

## Dla kogo i po co

Dla osób budujących niezawodne biblioteki i aplikacje, które muszą rozróżniać oczekiwane błędy od naruszonych invariants.

## Wymagania wstępne

Enumy, `match`, closures, iteratory i podstawy traits.

## Kolejność materiałów

1. [`Option` i `Result`](01_option_i_result.md)
2. [Propagacja i operator `?`](02_propagacja_i_operator_question_mark.md)
3. [`panic`, unwind i abort](03_panic_unwind_i_abort.md)
4. [Własne błędy i projektowanie API](04_wlasne_bledy_i_api.md)

## Po tym dziale

Potrafisz zaprojektować typ błędu, zachować jego źródło i dobrać propagację do granicy biblioteki lub aplikacji.

## Co dalej

Przejdź do modułów i Cargo. Traktuj `panic!` jako sygnał błędu programisty lub niemożliwego stanu, nie zwykły mechanizm sterowania.
