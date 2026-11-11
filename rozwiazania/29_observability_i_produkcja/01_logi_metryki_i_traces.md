[← Spis treści](../../README.md)

# Rozwiązania: Logi, metryki i ślady rozproszone

[Rozdział źródłowy](../../29_observability_i_produkcja/01_logi_metryki_i_traces.md)

## D11-1

Skala: licznik błędów i liczba wszystkich kwalifikujących się operacji, z ograniczonymi klasami wyniku. Jeden request: skorelowane logi i trace ze spanami zależności. Metryka wskazuje problem, trace pomaga wyjaśnić konkretną ścieżkę.

## D11-2

Metoda, wzorzec trasy `/orders/{id}` i ograniczona klasa statusu. Czas ma jedną udokumentowaną jednostkę. Pełną ścieżkę i identyfikator zachowaj tylko w kontrolowanym logu, jeśli są potrzebne i dopuszczone polityką danych.

## D11-3

Użyj wejścia z charakterystycznym fałszywym sekretem i testowego subscribera, wykonaj także ścieżkę błędu. Sprawdź wymagane pola oraz brak wartości sekretu we wszystkich eventach i spanach. Sam test ręcznej implementacji Debug nie obejmuje atrybutu instrument ani kontekstu błędu.
