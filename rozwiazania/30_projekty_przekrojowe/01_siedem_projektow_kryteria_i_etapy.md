[← Spis treści](../../README.md)

# Rozwiązania: Siedem projektów: zakres, etapy i kryteria ukończenia

[Rozdział źródłowy](../../30_projekty_przekrojowe/01_siedem_projektow_kryteria_i_etapy.md)

## D13-1

Dla CLI: stdin → parser jednego rekordu → wynik stdout, z niezerowym kodem błędu. Dla web: pojedyncza operacja na testowym repozytorium i odpowiedź HTTP. Kryterium obejmuje jedno wywołanie możliwe do powtórzenia bez ręcznej zmiany kodu.

## D13-2

Pierwszy: jedno zadanie, jeden wynik, poprawne join. Drugi: ograniczona kolejka i test pełnego bufora bez wycieku zadania. Trzeci: shutdown i błąd workera, z testem zakończenia przy aktywnym producencie. Benchmark dodaj po uzyskaniu poprawnej polityki, nie przed nią.

## D13-3

Wypisz invariant długości zainicjalizowanego prefiksu i odpowiedzialność za Drop. Sprawdź push do pełna, usuwanie, panikę tworzenia elementu i zniszczenie w każdym stanie. Użyj licznika destrukcji do wykrycia wycieku/dwukrotnego Drop oraz Miri dla błędów pamięci. Osobny przegląd musi rozważyć dowolne legalne sekwencje safe API.
