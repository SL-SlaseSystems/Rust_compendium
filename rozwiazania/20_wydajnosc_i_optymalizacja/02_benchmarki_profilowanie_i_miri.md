[← Spis treści](../../README.md)

# Rozwiązania: Pomiary i narzędzia

## C11-1

Optymalizator może obliczyć wynik wcześniej, wynieść wywołanie poza pętlę albo usunąć je całkowicie. Przekaż wejście przez `black_box`, a wynik również zużyj przez `black_box` lub sumę kontrolną, która faktycznie trafia do obserwacji. Sam `black_box` wejścia nie wymusza użycia całkowicie odrzuconego rezultatu. Sprawdź dodatkowo, że timer obejmuje badaną pracę, a nie tworzenie danych i wypisywanie na terminal.

## C11-2

Macierz ma cztery klasy danych: krótki poprawny, krótki błędny, długi poprawny i długi błędny; dla błędnych dodaj pozycję błędu na początku i końcu. Zestawy powstają przed pomiarem, a każdy wariant dostaje identyczne bajty. Sprawdź zgodność wyniku lub kategorii błędu przed rozpoczęciem porównania. Oddziel benchmark samego parsowania od end-to-end z alokacją i I/O.

Mierz czas na rekord, przepustowość w bajtach na sekundę i alokacje oraz ich bajty. Raportuj rozrzut wielu powtórzeń i konfigurację release. Dla danych większych niż cache rotuj reprezentatywny zestaw zamiast wciąż czytać jeden rekord. Nie ogłaszaj jednego zwycięzcy przez średnią ukrywającą katastrofalny koszt błędnych dokumentów.

## C11-3

Najpierw z trace żądań rozdziel czas kolejki, nabycia połączenia, zapytania i wysyłania odpowiedzi. Zmierz wykorzystanie puli, czas trzymania locków, liczbę tasków oraz obciążenie zależności. Sprawdź wzrost p99 względem długości kolejki i limitów współbieżności. Profil CPU może pokazać koszt pracy aktywnej, ale niski CPU nie potwierdza wydajnego systemu.

Benchmark odtwarza hipotezę, np. wyczerpanie puli przez połączenia trzymane podczas HTTP. TSan jest zasadny przy podejrzeniu wyścigu danych, a Miri przy małej abstrakcji unsafe; żadne nie jest pierwszym narzędziem do mierzenia opóźnienia sieci. Zmiana limitu puli bez obserwacji bazy może jedynie przenieść kolejkę do serwera SQL.
