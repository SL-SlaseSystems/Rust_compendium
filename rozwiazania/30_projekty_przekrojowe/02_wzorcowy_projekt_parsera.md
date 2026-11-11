[← Spis treści](../../README.md)

# Rozwiązania: Projekt referencyjny: parser konfiguracji z jawnym kontraktem

[Rozdział źródłowy](../../30_projekty_przekrojowe/02_wzorcowy_projekt_parsera.md)

## D14-1

`x=1
y=2
` ma dwa rekordy. `x=1

y=2` daje Separator w wierszu 2. `x=1
` ma jeden rekord. Te testy dokumentują semantykę str::lines oraz decyzję, że puste wiersze wewnątrz są błędem.

## D14-2

Po parsowaniu wyszukaj pole; brak ma osobny błąd. Użyj parse::<u16>(), a po nim sprawdź niezerowość lub NonZeroU16. Nie rzutuj liczby większej niż zakres przez as. Testy: brak, 0, 65535, 65536 i tekst nienumeryczny. Model domenowy może posiadać liczby niezależnie od inputu.

## D14-3

Utrzymuj ograniczony bufor aktualnego wiersza i własną mapę kluczy, bo bufor będzie nadpisywany. Pełne rekordy konwertuj do własnych wartości albo do modelu domenowego. Na EOF rozstrzygnij ostatni wiersz bez LF. Testuj każdy punkt podziału przykładowego dokumentu oraz przekroczenie limitu zanim kolejny bajt zostanie dodany.
