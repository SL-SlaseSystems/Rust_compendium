[← Spis treści](../../README.md)

# Rozwiązania: WebAssembly: host, guest, przeglądarka i WASI

[Rozdział źródłowy](../../24_wasm_i_wieloplatformowosc/01_wasm_host_guest_i_wasi.md)

## D01-1

Dla `b"Rust"` para `(4, 0)` powinna zwrócić pusty tekst, a `(5, 0)` błąd zakresu. Zero długości nie uprawnia do dowolnego offsetu. Osobno sprawdź `(0, 0)` i zakres kończący się dokładnie na granicy.

## D01-2

Host przekazuje dane przez kontrolowany adapter, gość waliduje długość przed kopiowaniem. Wariant prosty zwraca własny wynik przez wiązanie, które zarządza jego konwersją. Wariant uchwytowy wymaga funkcji zwolnienia, zakazu podwójnego zwolnienia i określenia zachowania nieprawidłowego uchwytu. Limit sprawdza się zarówno po stronie hosta, jak i gościa.

## D01-3

Utwórz widok przez docelowy adapter, wywołaj operację, która rzeczywiście powoduje wzrost pamięci, następnie odtwórz widok i porównaj dane. Test ma wykazać, że aplikacja nie używa starego widoku. Nie wyciągaj wniosku z samego zwiększenia `Vec::capacity`: realokacja wewnętrzna i wzrost pamięci liniowej to różne zdarzenia.
