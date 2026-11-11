[← Spis treści](../../README.md)

# Rozwiązania: Migracje i odtwarzanie

## C06-1

Etap 1: dodaj nullable `email_normalized` i określ deterministyczną funkcję normalizacji oraz politykę kolizji. Wdróż wersję przejściową do wszystkich writerów, łącznie z workerami i importami: w jednej transakcji zapisuje `email` oraz jego znormalizowany odpowiednik, lecz nadal czyta `email`. Zanim ruszy backfill, potwierdź brak writerów zapisujących wyłącznie stare pole i zakończenie ich transakcji. Zablokuj powrót takiej wersji przez rollback. Fallback do starego pola nie zastępuje tej bariery.

Etap 2: po barierze uzgodnij wszystkie wiersze z bieżącym `email`, także nie-NULL `email_normalized`, które mogły się zdezaktualizować podczas mieszanego wdrożenia. Backfill oblicza wynik z aktualnego starego pola bezpośrednio w aktualizacji; działający równolegle writer atomowo zapisuje tę samą parę według tej samej funkcji. Sprawdź zgodność, kompletność i kolizje, a dopiero potem przełącz odczyty na nowe pole. Nie zmieniaj semantyki normalizacji między partiami bez wersjonowania.

Etap 3: po wycofaniu wszystkich starych czytelników oraz zakończeniu okna rollbacku usuń zależność aplikacji od starego pola; dopiero w osobnej migracji usuń kolumnę. Do tego czasu nowi writerzy utrzymują obie reprezentacje. Test regresji obejmuje zapis obu pól przez nową wersję, późniejszą zmianę tylko `email` przez starą wersję i nie-NULL, ale nieaktualny wynik normalizacji. Poprawiony protokół nie pozwala takiemu writerowi działać po barierze, a backfill naprawia rozbieżności powstałe przed nią. Sam test `email_normalized IS NULL` nie wykrywa tego błędu.

## C06-2

Zakresy to `0..4`, `4..8`, `8..11`. Po dwóch commitach następny start wynosi 8. Jeśli dane drugiej partii zatwierdzono, ale checkpoint pozostał na 4, restart ponawia `4..8`. Warunek `nowe_pole IS NULL` oraz deterministyczne przekształcenie sprawiają, że powtórzenie jest nieszkodliwe. Lepszy wariant zapisuje checkpoint w tej samej transakcji co aktualizacje, dzięki czemu nie ma stanu „dane tak, checkpoint nie”. Osobno sprawdź nowe rekordy wstawiane podczas przebiegu i sposób domknięcia granicy.

## C06-3

W izolowanym środowisku wybierz symulowany moment awarii T. Odtwórz bazową kopię i dziennik do punktu co najmniej T minus 15 minut. Zmierz osobno dostęp do kluczy i kopii, transfer, restore, odtworzenie logu, uruchomienie zgodnej aplikacji oraz walidację. Łączny czas od zgłoszenia awarii do potwierdzonej obsługi powinien być nie większy niż 60 minut.

Sprawdź sumy i integralność kopii, liczbę rekordów według kontrolnych zestawień, constraints, salda lub rezerwacje oraz spójność rekordów operacji z outboxem. Wykonaj odczyt i nowy zapis przez aplikację. Próba przegrywa, gdy ostatni odzyskany zatwierdzony zapis jest starszy niż 15 minut względem T, całe przywrócenie trwa ponad godzinę albo którykolwiek niezmiennik nie zachodzi. Sam komunikat „restore completed” nie spełnia kryterium. Zachowaj log pomiarów i popraw procedurę przed następną próbą.
