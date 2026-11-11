[← Spis treści](../README.md)

# 17. Bazy danych i persystencja

## Dla kogo i po co

Dla osób utrwalających stan aplikacji w bazach relacyjnych, magazynach klucz–wartość lub plikach.

## Wymagania wstępne

Obsługa błędów, async dla klientów asynchronicznych, serializacja i podstawy modelowania domeny.

## Kolejność materiałów

1. [Repozytoria, mapowanie typów, pule i transakcje](01_repozytoria_pule_i_transakcje.md) — granica domeny, połączenia, atomowość, izolacja i błędy.
2. [Migracje schematu, testy integracyjne i odtwarzanie danych](02_migracje_testy_i_odtwarzanie.md) — zgodność wersji, izolacja testów i próby odtworzenia.

Każdy rozdział zawiera trzy ćwiczenia z pełnymi rozwiązaniami; najpierw wykonaj je samodzielnie, potem porównaj kontrakty i przypadki graniczne.

## Po tym dziale

Potrafisz oddzielić domenę od sterownika bazy, zachować atomowość operacji i bezpiecznie rozwijać schemat.

## Co dalej

Połącz ten dział z web/API albo CLI. Mierz zapytania i rozmiar puli w warunkach zbliżonych do produkcji.
