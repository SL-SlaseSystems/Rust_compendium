[← Spis treści](../../README.md)

# Rozwiązania: Sekrety, uprawnienia i bezpieczeństwo zależności

[Rozdział źródłowy](../../27_bezpieczenstwo_aplikacji/02_sekrety_uprawnienia_i_zaleznosci.md)

## D08-1

Zbuduj sekret o charakterystycznej treści, sformatuj `Debug` i sprawdź jednocześnie dokładną redakcję oraz brak wejściowej wartości. Test dotyczy wyłącznie tej ścieżki formatowania. Osobno przetestuj rzeczywiste zdarzenia logowania aplikacji.

## D08-2

Właściciel z właściwego tenanta: sukces. Inny użytkownik tego tenanta: wynik według jawnej roli. Użytkownik innego tenanta, nawet o tej samej lokalnej roli: odmowa. Konto zablokowane i brak tożsamości: odmowa. Test potwierdza, że przy odmowie nie pobrano wrażliwego payloadu do odpowiedzi.

## D08-3

Zablokuj dalsze ujawnianie, ogranicz dostęp do istniejących logów, unieważnij sekret i dostarcz nowy przez kontrolowany kanał. Sprawdź użycia i zakres uprawnień, a potem dodaj test redakcji oraz zasadę przeglądu instrumentacji. Usunięcie wpisu z logów nie unieważnia kopii, które już powstały.
