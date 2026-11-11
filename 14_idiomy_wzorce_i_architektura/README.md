[← Spis treści](../README.md)

# 14. Idiomy, wzorce i architektura

## Dla kogo i po co

Dla osób przechodzących od pojedynczych modułów do bibliotek i aplikacji z trwałymi granicami odpowiedzialności.

## Wymagania wstępne

Ownership, traits, obsługa błędów, moduły, testy i doświadczenie z co najmniej jednym małym projektem.

## Kolejność materiałów

1. [Idiomy, newtype i extension traits](01_idiomy_newtype_i_extension_traits.md)
2. [Builder, typestate i maszyna stanów](02_builder_typestate_i_state_machine.md)
3. [Projektowanie API i SemVer](03_projektowanie_api_i_semver.md)
4. [Architektura aplikacji i dependency injection](04_architektura_aplikacji_i_di.md)

## Po tym dziale

Potrafisz oddzielić domenę od infrastruktury, zakodować część invariants w typach i ocenić wpływ zmiany API na użytkowników.

## Praca z rozdziałami

Każdy rozdział zawiera model działania, przykłady, diagnostykę, decyzje produkcyjne i trzy zadania o rosnącym poziomie trudności. Najpierw przewiduj wynik kodu, następnie go uruchom, a dopiero potem porównaj rozwiązanie.

- [Idiomy, newtype i extension traits: rozwiązania](../rozwiazania/14_idiomy_wzorce_i_architektura/01_idiomy_newtype_i_extension_traits.md)
- [Builder, typestate i state machine: rozwiązania](../rozwiazania/14_idiomy_wzorce_i_architektura/02_builder_typestate_i_state_machine.md)
- [Projektowanie API i SemVer: rozwiązania](../rozwiazania/14_idiomy_wzorce_i_architektura/03_projektowanie_api_i_semver.md)
- [Architektura aplikacji i dependency injection: rozwiązania](../rozwiazania/14_idiomy_wzorce_i_architektura/04_architektura_aplikacji_i_di.md)

Przykłady samowystarczalne odnoszą się do Rust 1.90, Edition 2024. Bloki `text` z zależnościami zewnętrznymi lub wymaganiami środowiskowymi opisują oddzielny kontrakt; nie są testami wykonanymi przez rustdoc.

## Co dalej

Wybierz ścieżkę praktyczną: CLI, web/API, bazy danych albo systemy niskopoziomowe.
