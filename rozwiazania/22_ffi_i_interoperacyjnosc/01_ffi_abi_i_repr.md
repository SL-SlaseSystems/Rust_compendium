[← Spis treści](../../README.md)

# Rozwiązania: FFI i ABI

## C16-1

Trzeba ustalić: czy wskaźnik może być null przy zerowej długości; czy długość jest w bajtach i obejmuje NUL; czy tekst jest zakończony NUL czy ograniczony długością; jakie jest kodowanie; czy funkcja czyta czy zapisuje i ile miejsca zapisu wymaga; kto posiada alokację; czy zachowuje wskaźnik po powrocie; jaka jest synchronizacja i co dzieje się przy błędzie. Samo `char*` nie wyraża żadnej z tych decyzji w sposób wystarczający dla bezpiecznej otoczki.

## C16-2

Przyjmij `&CStr`, jeśli wywołujący ma już zgodny napis; własność bufora pozostaje po jego stronie. Alternatywnie przyjmij `&str`, utwórz lokalny `CString::new`, zamień błąd wewnętrznego NUL na błąd API, a dopiero potem przekaż `as_ptr` na czas jednego wywołania. Po powrocie obca funkcja nie może przechowywać pointera, a wrapper nie może oddawać widoku do lokalnego CString. Obcy kod ma prawo wyłącznie czytać. Jeśli zapisuje lub zachowuje wskaźnik, potrzebny jest inny protokół własności i osobny dowód.

## C16-3

Najprostszy wynik bez wskaźnika wyjściowego to `#[repr(C)] struct Wynik { kod: u32, wartosc: u64 }`, z kodem 0 dla sukcesu i 1 dla przepełnienia oraz wartością 0 przy błędzie. Funkcja `extern "C" fn suma(a:u64,b:u64)->Wynik` używa `checked_add`, więc nie panikuje na overflow. Nagłówek C musi zawierać odpowiadający struct z `uint32_t` i `uint64_t`, zgodnie z targetowym ABI. Nie zakładaj braku paddingu ani określonego offsetu bez kontroli dla targetu.

Nie przekazuj `Result<u64, Blad>` ani samego `bool` jako dowolnego bajtu statusu. Jeśli ABI wymaga wyjściowego pointera, eksport staje się unsafe po stronie Rust i kontrakt musi określić non-null, alignment, ważność oraz moment inicjalizacji wyniku. W obu wariantach kolizję globalnej nazwy symbolu musi wykluczyć autor eksportu.
