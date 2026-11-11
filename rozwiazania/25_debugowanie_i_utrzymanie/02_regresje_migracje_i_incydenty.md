[← Spis treści](../../README.md)

# Rozwiązania: Regresje, aktualizacje i utrzymanie po incydencie

[Rozdział źródłowy](../../25_debugowanie_i_utrzymanie/02_regresje_migracje_i_incydenty.md)

## D04-1

Awaria pobrania toolchainu albo brak systemowej biblioteki nie mówi nic o wyniku badanego obliczenia. Takie utożsamienie kieruje bisekcję do niewłaściwego przedziału. Potrzebny jest oddzielny wynik i jawna decyzja pominięcia albo naprawienia środowiska.

## D04-2

Najpierw parser akceptuje stare i nowe pole, definiując zachowanie obecności obu. Następnie nowe narzędzia zapisują nowe pole, a monitoring wykrywa użycia starego. Dopiero po zakończeniu okna zgodności usuwa się stary odczyt. Testy obejmują stare pliki, nowe pliki, konflikt i brak obu pól.

## D04-3

Wprowadź deadline uzyskania połączenia i test jego przekroczenia; metrykę liczby oczekujących z alertem na trwałe przeciążenie; test anulowania operacji pokazujący powrót zasobu do puli. Każde działanie ma właściciela oraz mierzalny wynik. Samo zwiększenie puli wymaga dowodu, że baza ma zapas przepustowości.
