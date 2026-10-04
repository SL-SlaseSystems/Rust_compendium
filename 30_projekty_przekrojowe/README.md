[← Spis treści](../README.md)

# 30. Projekty przekrojowe

## Dla kogo i po co

Dla osób utrwalających wiedzę przez samodzielne dostarczenie skończonego artefaktu. Projekty są ułożone od pracy lokalnej po bezpieczną abstrakcję systemową.

## Wymagania wstępne

Przed startem wybierz projekt odpowiadający ukończonym działom. Każdy wymaga podstaw języka, ownership, błędów, Cargo, testów i dokumentacji.

## Kolejność materiałów

1. **Narzędzie CLI do przetwarzania danych**
   Wymagania: działy 13, 15 i 18. Ukończenie: udokumentowany interfejs, poprawne kody wyjścia, streaming dużych wejść, testy end-to-end i binarne wydanie.
2. **Parser i model domenowy**
   Wymagania: działy 4–7 i 26. Ukończenie: jawny AST, błędy ze spanami, testy właściwości, korpus fuzzera i brak paniki dla dowolnych bajtów.
3. **Biblioteka w workspace**
   Wymagania: działy 5, 8, 9 i 14. Ukończenie: stabilne publiczne API, przykłady rustdoc, kontrolowane features, polityka SemVer i pipeline jakości.
4. **System wielowątkowy**
   Wymagania: działy 10, 20 i 25. Ukończenie: opis invariants, kontrolowane zamykanie, testy przeciążeń, benchmark i profil uzasadniający architekturę.
5. **Usługa asynchroniczna**
   Wymagania: działy 11, 13 i 29. Ukończenie: timeouty, anulowanie, backpressure, graceful shutdown oraz skorelowane logi, metryki i trace'y.
6. **Usługa webowa z danymi i obserwowalnością**
   Wymagania: działy 16–18, 27–29. Ukończenie: migracje bazy, walidacja, model zagrożeń, testy API, SLO, artefakt wydania i procedura rollbacku.
7. **Bezpieczna abstrakcja nad `unsafe`**
   Wymagania: działy 19–23 i 26. Ukończenie: minimalna powierzchnia `unsafe`, spisane invariants i komentarze `SAFETY`, testy Miri/fuzzing oraz niezależny przegląd kontraktu.

## Po tym dziale

Masz portfolio pokazujące nie tylko składnię, lecz także projektowanie, weryfikację, utrzymanie i odpowiedzialność produkcyjną.

## Co dalej

Opublikuj kod z krótkim raportem decyzji i ograniczeń. Następnie wróć do najsłabszego kryterium ukończenia i popraw je na podstawie pomiarów lub przeglądu.
