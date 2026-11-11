[← Spis treści](../README.md)

# 18. Serializacja, konfiguracja i integracje

## Dla kogo i po co

Dla osób łączących aplikację z plikami konfiguracyjnymi, formatami danych, kolejkami i zewnętrznymi usługami.

## Wymagania wstępne

Dobra znajomość struktur i enumów, obsługi błędów, modułów oraz I/O.

## Kolejność materiałów

1. [Formaty danych, serializacja i walidacja granic](01_formaty_serializacja_i_walidacja.md) — ewolucja modelu, tekst, ramki binarne i walidacja.
2. [Konfiguracja, sekrety, retry i idempotencja integracji](02_konfiguracja_sekrety_i_odpornosc_integracji.md) — warstwy konfiguracji, rotacja i odporność na nieznany wynik.

Każdy rozdział zawiera trzy ćwiczenia z pełnymi rozwiązaniami; najpierw wykonaj je samodzielnie, potem porównaj kontrakty i przypadki graniczne.

## Po tym dziale

Potrafisz zaprojektować kompatybilny format, odróżnić konfigurację od sekretu i kontrolować awarie systemów zewnętrznych.

## Co dalej

Zastosuj te zasady w CLI, API lub pipeline danych. Nie loguj sekretów ani pełnych, niezweryfikowanych payloadów.
