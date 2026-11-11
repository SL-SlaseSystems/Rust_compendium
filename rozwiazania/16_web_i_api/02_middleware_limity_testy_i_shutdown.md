[← Spis treści](../../README.md)

# Rozwiązania: Limity i shutdown

## C04-1

Dla `(7,16)` decyzja to `Start`, bo jest wolne miejsce wykonania. `(8,15)` daje `Kolejka`, a `(8,16)` — `Odrzuc`. W rzeczywistej implementacji semafor lub lock musi jednocześnie potwierdzić i zająć miejsce. Dwa taski odczytujące `aktywne=7` nie mogą oba przyjąć ósmej operacji.

## C04-2

Handler nabywa permit przez try-acquire i po potwierdzeniu startu czeka na kontrolowanym kanale. Test uruchamia dwa żądania i oczekuje dwóch sygnałów „rozpoczęto”; sygnał jest wysyłany dopiero po rezerwacji. Dopiero potem wysyła trzecie i sprawdza udokumentowany status przeciążenia, brak wykonania przypadku użycia i krótki czas odpowiedzi względem deadline testu. Następnie zwalnia oba handlery, dołącza zadania i sprawdza powrót liczby permitów do dwóch.

Nie używaj arbitralnego `sleep`, aby zgadnąć, że żądania zajęły miejsca. Kanał i bariera ustalają porządek niezależnie od szybkości maszyny. Cały test ma własny limit czasu i sprzątanie tasków także po porażce asercji.

## C04-3

W chwili `t=0` readiness przechodzi na false, nasłuch przestaje przyjmować nową pracę, a producenci workerów kończą wysyłanie. Do `t=7 s` aktywne operacje mogą zakończyć się normalnie. Stream dostaje token zakończenia oraz, jeśli protokół pozwala, ostatnie zdarzenie z pozycją wznowienia. Worker kończy rozpoczętą transakcję albo jawnie ją wycofuje. `t=7..9 s` przeznacz na zamknięcie puli oraz flush telemetrii. `t=10 s` jest twardym terminem procesu; supervisor może wymusić zakończenie.

Nieznany wynik `commit` zachowaj jako nieznany: przerwane połączenie nie dowodzi rollbacku. Klient pyta o status klucza operacji albo ponawia z tym samym kluczem idempotencji. Rejestr klucza musi być zatwierdzany w tej samej transakcji co skutek. Zamknięcie procesu nie daje semantyki „dokładnie raz” dla odłączonych efektów zewnętrznych.
