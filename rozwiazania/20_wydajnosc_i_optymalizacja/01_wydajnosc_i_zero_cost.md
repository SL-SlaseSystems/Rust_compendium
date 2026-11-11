[← Spis treści](../../README.md)

# Rozwiązania: Wydajność i koszty

## C10-1

Nowy czas to `0,6 + 0,4 / 2 = 0,8` czasu bazowego. Opóźnienie spada o 20%, a przyspieszenie wynosi `1 / 0,8 = 1,25`. To rachunek przy niezmienionych pozostałych kosztach; większa presja cache lub synchronizacja mogłyby zmienić założenie.

## C10-2

Po użyciu i przekazaniu wyniku odbiorcy wykonaj `if bufor.capacity() > 1024 * 1024 { bufor = String::new(); }`, albo przenieś tę politykę na początek następnego wywołania, gdy poprzedni wynik nie jest już potrzebny. Nie zeruj bufora przed użyciem raportu. Jeśli funkcja przyjmuje `&mut String`, przypisanie ma postać `*bufor = String::new()` i wymaga zakończenia wszystkich widoków.

Test najpierw generuje mały raport, potem duży i ponownie mały; porównuje dokładne bajty, w tym końcowy newline. Po etapie sprzątania sprawdza, że nie zatrzymano wielkiej pojemności. Taka polityka ogranicza retencję między operacjami, nie szczyt pamięci w czasie generowania dużego raportu. Dla szczytu potrzebny jest streaming lub limit wyjścia.

## C10-3

Lista węzłów ma koszt oddzielnych alokacji i skoków po wskaźnikach; jej korzyść w tanim przepinaniu węzłów może być nieprzydatna dla sekwencyjnej sumy. `Vec<Rekord>` zapewnia ciągłość rekordów, lecz odczyt jednej małej kolumny może przenosić do cache także nieużywane pola. Układ kolumnowy zapewnia ciągłość samej sumowanej kolumny, za cenę trudniejszej obsługi pełnego rekordu i pilnowania zgodnych długości kolumn.

Zmierz czas sumowania w release, liczbę alokacji przy budowaniu, szczyt pamięci, cache misses i osobno koszt częstych aktualizacji. Użyj identycznych danych i semantyki przepełnienia. Zestaw obejmuje dane mieszczące się i niemieszczące się w cache. Wybór wynika z wyników całego workloadu, a nie z ogólnej tezy, że jedna struktura zawsze wygrywa.
