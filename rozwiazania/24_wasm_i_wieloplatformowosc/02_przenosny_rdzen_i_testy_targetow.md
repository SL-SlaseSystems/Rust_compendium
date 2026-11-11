[← Spis treści](../../README.md)

# Rozwiązania: Przenośny rdzeń i weryfikacja wielu targetów

[Rozdział źródłowy](../../24_wasm_i_wieloplatformowosc/02_przenosny_rdzen_i_testy_targetow.md)

## D02-1

Dla `(10,9)` i `(10,10)` wynikiem jest `Wykonaj`, dla `(10,11)` — `Czekaj(1)`. Sprawdź też `(u64::MAX, 0)`: wynik nadal jest jednoznaczny i nie wymaga arytmetyki zawijającej.

## D02-2

Rdzeń: `fn parse(input: &[u8]) -> Result<Model, ParseError>`, bez odczytu plików i globalnego logowania. CLI dostarcza ograniczony bufor ze stdin, przeglądarka konwertuje wejście przez adapter. Oba adaptery mapują ten sam błąd domenowy na właściwą prezentację; testy rdzenia są wspólne.

## D02-3

Linux i Windows: natywne testy oraz testy CLI/ścieżek. Wasm: check i build targetu oraz uruchomienie testów adaptera w przeglądarce. Osobno minimalne i domyślne features biblioteki. Sukces check bez runnera oznacza wyłącznie zgodność kompilacji; raport nie może nazywać go wykonanym testem przeglądarkowym.
