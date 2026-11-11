[← Spis treści](../../README.md)

# Rozwiązania: SLI, SLO, graceful shutdown i procedury operacyjne

[Rozdział źródłowy](../../29_observability_i_produkcja/02_slo_shutdown_i_operacje.md)

## D12-1

Dopuszczona część to 0,05%, czyli 1000 operacji. Jest to budżet liczby zdarzeń w zdefiniowanym oknie, nie automatycznie czas niedostępności. Najpierw trzeba ustalić, które odpowiedzi wchodzą do licznika i mianownika.

## D12-2

Przejdź do drain, potwierdź odmowę nowej pracy, wyślij sygnał obu zadaniom i czekaj do wspólnego deadline. Szybki task potwierdza zakończenie; zawieszony wymusza politykę końcową. Test sprawdza wynik i stan danych, nie przypadkową liczbę milisekund z rzeczywistego scheduleru.

## D12-3

Potwierdź skalę i dotkniętą ścieżkę, sprawdź deadline, kolejki, liczbę prób oraz stan odbiorcy. Ogranicz retry/ruch zgodnie z planem, zachowując idempotencję. Porównaj po zmianie ten sam SLI oraz liczbę odrzuceń, aby nie uznać spadku ruchu za naprawę integracji. Eskaluj, jeśli ograniczenie nie przywraca kontroli zasobów.
