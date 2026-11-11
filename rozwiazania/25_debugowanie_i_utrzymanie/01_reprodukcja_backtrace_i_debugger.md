[← Spis treści](../../README.md)

# Rozwiązania: Reprodukcja błędu, backtrace i debugger

[Rozdział źródłowy](../../25_debugowanie_i_utrzymanie/01_reprodukcja_backtrace_i_debugger.md)

## D03-1

`para("język=zażółć=Rust")` daje `Ok(("język", "zażółć=Rust"))`. Test sprawdza brak cięcia po indeksach bajtowych i zachowanie tylko pierwszego separatora; nie sprawdza normalizacji Unicode, której kontrakt nie obiecuje.

## D03-2

Najpierw zachowaj wadliwy wiersz i wywołanie parsera. Usuń bazę, sieć i prezentację, potwierdzając tę samą panikę. Następnie zapisz oczekiwanie błędu `Separator` i zmień parser. Nie odrzucaj po cichu wiersza: ustal, czy importer ma przerwać plik, czy zwrócić raport odrzuconych rekordów.

## D03-3

Dołącz profil i flagi, target, wersję kompilatora, zgodne symbole, minimalne wejście oraz częstotliwość. Porównaj ten sam commit w dwóch profilach, potem pojedynczo ustawienia overflow-checks i optymalizacji, jeśli dotyczą objawu. Wynik eksperymentu ma wskazywać różnicę; nie uznawaj samej korelacji profilu za dowód błędu kompilatora.
