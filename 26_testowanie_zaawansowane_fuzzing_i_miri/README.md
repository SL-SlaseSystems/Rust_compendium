[← Spis treści](../README.md)

# 26. Testowanie zaawansowane, fuzzing i Miri

## Dla kogo i po co

Dla autorów parserów, protokołów, bibliotek i bezpiecznych abstrakcji nad kodem `unsafe`.

## Wymagania wstępne

Testy jednostkowe i integracyjne, projektowanie API, podstawy modelu pamięci oraz umiejętność tworzenia małych harnessów.

## Kolejność materiałów

1. Testy właściwości i generatory danych.
2. Fuzzing, korpus startowy, minimalizacja i test regresji.
3. Miri dla wykrywania części undefined behavior.
4. Sanitizery, loom i testy współbieżności zależne od modelu.

## Po tym dziale

Potrafisz dobrać technikę do klasy ryzyka i zamienić znaleziony przypadek w trwały test regresji.

## Co dalej

Włącz odpowiednie narzędzia do CI. Żadne pojedyncze narzędzie nie dowodzi braku UB ani wszystkich wyścigów danych.
