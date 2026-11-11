[← Spis treści](../../README.md)

# Rozwiązania: Formaty i walidacja

## C07-1

Dokument z `name: "Ala"` i dokument z `display_name: "Ala"` odczytają się jako `nazwa == "Ala"`. Przy braku `etykiety` wartość to pusta lista. Zapis używa wyłącznie `display_name`, więc stary odbiorca wymagający `name` może go odrzucić. `alias` rozszerza nazwy wejściowe nowego odbiorcy, a nie możliwości starego programu. Gdy dokument poda obie nazwy tego samego pola, nie zakładaj automatycznego wyboru jednej: derive może zgłosić duplikat; taki przypadek należy jawnie testować i odrzucać.

## C07-2

Dla funkcji z rozdziału asercje są następujące. Jest to fragment zestawu testów wymagający dołączenia `payload`; dlatego blok jest tekstowym szkicem, a nie osobnym doctestem.

~~~text
assert_eq!(payload(&[0, 0, 0], 4), Err("brak długości"));
assert_eq!(payload(&[0, 0, 0, 0], 4), Ok(&[][..]));
assert_eq!(payload(&[0, 0, 0, 0, 9], 4), Err("zła długość ramki"));
assert_eq!(payload(&[2, 0, 0, 0, 7, 8], 2), Ok(&[7, 8][..]));
~~~

Dodatkowy bajt jest błędem, ponieważ parser przyjmuje dokładnie jedną kompletną ramkę. W protokole wielu ramek ta polityka musi być zastąpiona raportowaniem zużytego prefixu. Pusty payload jest legalny i nie jest tym samym co brak nagłówka.

## C07-3

Koperta zawiera `wersja`, `typ`, `event_id` i `dane`; `typ` ma stabilną wartość `zamowienie_utworzone`. Wersja 1 przekazuje `kwota: "12.34"`, `waluta: "PLN"`; wersja 2 przekazuje `kwota_minor: 1234`, tę samą walutę i jawną skalę protokołu. Odbiorca najpierw czyta wersję i tag, potem wybiera DTO v1 lub v2, a oba konwertuje do jednego typu domenowego.

Parser kwoty v1 odrzuca znaki niedozwolone, więcej niż dwa miejsca po kropce, liczbę ujemną oraz przepełnienie mnożenia i dodawania. Nie parsuje przez `f64`. Test zachowuje rzeczywiste bajty starego dokumentu i sprawdza wynik dokładnie 1234, a nie tylko round-trip. Testy dodatkowe obejmują `0.01`, `12.345`, nieznaną wersję i brak waluty. Producent przechodzi na v2 dopiero po potwierdzeniu wsparcia odbiorców albo publikuje do osobnego, wersjonowanego kanału.
