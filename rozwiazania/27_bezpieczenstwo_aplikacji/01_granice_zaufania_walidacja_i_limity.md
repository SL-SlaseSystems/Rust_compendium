[← Spis treści](../../README.md)

# Rozwiązania: Granice zaufania, walidacja i kontrola zasobów

[Rozdział źródłowy](../../27_bezpieczenstwo_aplikacji/01_granice_zaufania_walidacja_i_limity.md)

## D07-1

Nagłówek z zerem i brak payloadu daje pusty slice. Payload o długości równej limitowi jest akceptowany; o jeden większy jest odrzucony przed analizą zawartości. Dodaj też pusty input, który daje `Naglowek`, a nie panikę.

## D07-2

Oddziel limit przesyłanych bajtów, rozpakowanych bajtów, liczby rekordów, głębokości zagnieżdżenia i aktywnych importów. Dekompresuj strumieniowo z licznikiem wyjścia. Po przekroczeniu granicy przerwij i określ, czy już zapisane rekordy są wycofywane, czy raportowane jako częściowy wynik.

## D07-3

Jedna operacja może uruchomić do 27 prób w najgorszym zagnieżdżeniu. Wyznacz właściciela retry, całkowity deadline i budżet prób, dodaj backoff/jitter oraz rozróżnienie błędów trwałych i przejściowych. Każda ponawiana operacja skutkowa wymaga idempotencji lub innego protokołu kontroli duplikatów.
