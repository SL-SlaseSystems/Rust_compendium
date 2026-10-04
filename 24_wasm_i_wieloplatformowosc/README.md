[← Spis treści](../README.md)

# 24. WASM i wieloplatformowość

## Dla kogo i po co

Dla osób kompilujących Rust do WebAssembly lub utrzymujących wspólny rdzeń na wielu systemach i architekturach.

## Wymagania wstępne

Cargo, features i `cfg`, serializacja, FFI oraz podstawy środowiska docelowego.

## Kolejność materiałów

1. Zacznij od [wspólnego wprowadzenia do WebAssembly, `no_std` i embedded](../23_no_std_allocatory_i_embedded/01_wasm_no_std_i_embedded.md).
2. Oddziel przenośny rdzeń od adapterów platformowych.
3. Poznaj granicę host–guest, format danych i koszt kopiowania.
4. Testuj na rzeczywistych targetach oraz w środowisku uruchomieniowym hosta.

## Po tym dziale

Potrafisz rozdzielić logikę przenośną od integracji platformowej i świadomie zarządzać różnicami targetów.

## Co dalej

Rozwiń osobne materiały dla WASI, przeglądarki i wybranego toolchainu JavaScript. Nie zakładaj, że zachowanie natywne automatycznie przenosi się na WASM.
