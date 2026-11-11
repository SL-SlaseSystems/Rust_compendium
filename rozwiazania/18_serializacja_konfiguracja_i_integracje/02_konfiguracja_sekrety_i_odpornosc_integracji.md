[← Spis treści](../../README.md)

# Rozwiązania: Sekrety i retry

## C08-1

Wyniki: próba 0 — 100 ms, 1 — 200 ms, 4 — 1600 ms, 5 — 2000 ms po ograniczeniu. Kolejne też nie przekroczą dwóch sekund. Brakuje jitteru, limitu liczby prób, wspólnego deadline, klasyfikacji błędów i sprawdzenia idempotencji operacji. Sam backoff nie zapobiega nieskończonemu zadaniu ani ponowieniu niedozwolonego skutku.

## C08-2

Użyj charakterystycznego testowego tokenu, np. `TAJNE_TEST_7ec91`, oraz konfiguracji zawierającej endpoint z testowym hasłem w URL, aby wykryć dwa kanały wycieku. Sformatuj `Debug` całej konfiguracji i pełny łańcuch błędu klienta; każda postać musi nie zawierać tokenu, hasła ani nagłówka Authorization z wartością. Jednocześnie sprawdź obecność kategorii błędu i bezpiecznego identyfikatora operacji.

Jeśli błąd zewnętrznego klienta może zawierać pełny URL, nie wystarczy bezpieczny `Debug` pola sekretu: adapter błędu musi zredagować URL lub opublikować wyłącznie kategorię, a przyczynę przechować w kontrolowanym kanale. Test nie powinien używać prawdziwego sekretu. Redakcję sprawdź również w JSON telemetrii, jeśli konfiguracja lub błędy są serializowane.

## C08-3

Stany lokalne to `Przygotowana`, `Wyslana`, `WynikNieznany`, `Potwierdzona` i `Odrzucona`. Przed pierwszą próbą zapisz klucz operacji oraz fingerprint kwoty, waluty i odbiorcy. Po timeout przejdź do `WynikNieznany`; nie twórz nowej płatności. Odpytaj partnera po kluczu albo ponów identyczne żądanie z tym samym kluczem, jeżeli partner tak definiuje idempotencję.

Potwierdzenie partnera zapisuje jego identyfikator i zamyka operację. Użycie tego samego klucza z innym fingerprintem jest konfliktem wymagającym wyjaśnienia. Ręczne wznowienie zachowuje klucz; gdy minęła retencja deduplikacji partnera, operator najpierw uzgadnia historię, zamiast ślepo wysyłać ponownie. Własny wpis lokalny bez wsparcia lub sprawdzenia partnera nie dowodzi, że zdalny skutek się nie powtórzy. System eksponuje „nieznane” jako stan operacyjny wymagający uzgodnienia, nie zamienia go automatycznie na porażkę.
