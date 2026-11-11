[← Spis treści](../README.md)
<!-- status: expanded -->

# WebAssembly: host, guest, przeglądarka i WASI

> Przykłady `rust`: biblioteka standardowa, Edition 2024. API narzędzi i bibliotek zewnętrznych opisano na podstawie źródeł sprawdzonych 11 listopada 2026 r.; szkice `text` wymagają wskazanego środowiska.

## Cele

Po tym rozdziale potrafisz:

- odróżnić format WebAssembly od środowiska udostępniającego I/O;
- zaprojektować kontrakt pamięci i błędów na granicy modułu;
- wybrać target na podstawie wymaganych możliwości;

## Model — moduł wykonuje kod, host udostępnia możliwości

WebAssembly (Wasm) jest formatem kodu wykonywanego przez silnik. Gość (guest) nie otrzymuje automatycznie plików, sieci ani obiektów JavaScript. Korzysta z importów dostarczonych przez gospodarza (host). Ten sam algorytm może działać w przeglądarce i poza nią, lecz jego adapter I/O oraz sposób uruchomienia będą inne. Wybór targetu jest zatem wyborem kontraktu środowiska, a nie tylko rozszerzenia pliku.

`wasm32-unknown-unknown` minimalizuje założenia wobec hosta. Udostępnia `core` i `alloc`; obecność `std` nie oznacza działającego systemowego I/O. Nie traktuj kompilacji `std::fs` jako dowodu, że w przeglądarce istnieje system plików procesu. WASI definiuje interfejsy środowiska. `wasm32-wasip1` zachowuje zgodność z WASIp1, a targety Component Model mają inny kontrakt uruchomienia. Sprawdź zgodność targetu, silnika i faktycznie potrzebnych importów w dokumentacji danej wersji.

## Granica danych jest częścią API

Najprostszy kontrakt ma małe wartości liczbowe i jawne błędy. Tablica bajtów wymaga już określenia, kto ją alokuje, jak długo żyje i kto ją zwalnia. Offset w pamięci liniowej gościa nie jest wskaźnikiem do pamięci procesu hosta. Para offset–długość nie dowodzi poprawności zakresu: sumowanie może się przepełnić, a zakres przekroczyć aktualną pamięć. Własność trzeba ustalić także przy błędzie i anulowaniu.

Poniższa funkcja jest przenośnym rdzeniem; jej test wykonuje się natywnie, bez silnika Wasm. Walidacja korzysta z odejmowania granicy i `get`, zamiast tworzyć referencję przez obcy wskaźnik.

~~~rust
#[derive(Debug, PartialEq)]
enum Blad { Zakres, Tekst }

fn czytaj(pamiec: &[u8], start: u32, dlugosc: u32) -> Result<&str, Blad> {
    let start = usize::try_from(start).map_err(|_| Blad::Zakres)?;
    let dlugosc = usize::try_from(dlugosc).map_err(|_| Blad::Zakres)?;
    let koniec = start.checked_add(dlugosc).ok_or(Blad::Zakres)?;
    let bajty = pamiec.get(start..koniec).ok_or(Blad::Zakres)?;
    std::str::from_utf8(bajty).map_err(|_| Blad::Tekst)
}

fn main() {
    assert_eq!(czytaj(b"Rust", 1, 3), Ok("ust"));
    assert_eq!(czytaj(b"Rust", 3, 2), Err(Blad::Zakres));
    assert_eq!(czytaj(&[255], 0, 1), Err(Blad::Tekst));
}
~~~

`TryFrom` nie zakłada szerokości `usize` hosta. `checked_add` osobno chroni rachunek adresów. `from_utf8` sprawdza reprezentację dopiero po sprawdzeniu zakresu. Oddzielenie tych błędów ułatwia testowanie i ustalenie, czy naruszono kontrakt bufora, czy format danych.

## JavaScript i koszt przekraczania granicy

`wasm-bindgen` jest narzędziem **third-party**, które generuje wiązania między Rustem i JavaScriptem. Nie jest częścią języka. Wybór typu wyniku wpływa na kod adaptera, kopiowanie i obsługę wyjątków. Wywoływanie funkcji dla każdego bajtu może kosztować więcej niż jednorazowe przekazanie całego bufora. Grupuj pracę, ale ogranicz maksymalny rozmiar wejścia oraz czas pojedynczego wywołania blokującego pętlę zdarzeń.

Widok hosta na pamięć gościa ma ograniczony okres ważności. Wzrost pamięci albo zmiana właściciela bufora może wymagać odtworzenia widoku; reguły konkretnego wiązania sprawdzaj w jego dokumentacji. Nie przechowuj bezterminowo offsetu do `Vec`, który następne wywołanie może realokować. Na początek kopiowanie ma często lepszy kontrakt niż pozorne zero-copy o nieudowodnionym lifetime.

## Diagnostyka kompilatora

Błąd konwersji liczby, niezgodny typ eksportu i brak symbolu w loaderze to różne warstwy. Kompilator sprawdza kod Rust, narzędzie wiązań sprawdza obsługiwane sygnatury, a host sprawdza importy modułu. Zapisz cały komunikat wraz z etapem, zamiast zmieniać target metodą prób. Panika gościa nie jest automatycznie domenowym `Result`; zaprojektuj jawny wynik na granicy.

Przy niepoprawnym zakresie test oczekuje `Err`, nie paniki. Taka własność musi być testowana także w docelowym adapterze, ponieważ sam test rdzenia nie obejmuje mapowania wartości JavaScript ani dostępu do pamięci silnika.

## Praktyka produkcyjna

Ogranicz pamięć, czas wykonania i uprawnienia importów osobno. Sandbox modułu nie ochroni hosta, jeśli import pozwala mu bez kontroli otwierać dowolny plik. Rozpoczynaj od minimalnej listy możliwości i testu odmowy dostępu.

Utrzymuj testy rdzenia, test ładowania modułu oraz test integracji w rzeczywistej przeglądarce lub silniku WASI. Mierz rozmiar skompresowanego modułu, czas inicjalizacji, koszt kopii i opóźnienie całej operacji. Testy natywne w tym rozdziale nie potwierdzają działania na Wasm; do tego potrzeba targetu i hosta.

## Sprawdź, czy rozumiesz

1. Dlaczego kompilacja z `std` nie dowodzi dostępności plików?
2. Kto odpowiada za okres ważności offsetu przekazanego do hosta?
3. Których błędów nie wykryje natywny test funkcji `czytaj`?

## Ćwiczenia

- `D01-1` — podstawowe: Dodaj przypadki pustego zakresu na końcu bufora i zakresu zaczynającego się za końcem. [Rozwiązanie](../rozwiazania/24_wasm_i_wieloplatformowosc/01_wasm_host_guest_i_wasi.md#d01-1).
- `D01-2` — praktyczne: Zaprojektuj eksport przetwarzający do 1 MiB danych; określ alokację, zwalnianie i błędy. [Rozwiązanie](../rozwiazania/24_wasm_i_wieloplatformowosc/01_wasm_host_guest_i_wasi.md#d01-2).
- `D01-3` — pogłębione: Opisz test wykrywający użycie starego widoku po wzroście pamięci gościa. [Rozwiązanie](../rozwiazania/24_wasm_i_wieloplatformowosc/01_wasm_host_guest_i_wasi.md#d01-3).

## Źródła i granice weryfikacji

Kontrakty targetów: [wasm32-unknown-unknown](https://doc.rust-lang.org/rustc/platform-support/wasm32-unknown-unknown.html) i [wasm32-wasip1](https://doc.rust-lang.org/rustc/platform-support/wasm32-wasip1.html). Warstwa JavaScript: [dokumentacja wasm-bindgen](https://docs.rs/wasm-bindgen/latest/wasm_bindgen/). Przykład walidacji jest autorskim modelem granicy; nie implementuje ABI ani loadera.

## Powiązane tematy

- [Przenośny rdzeń i testy targetów](02_przenosny_rdzen_i_testy_targetow.md)
- [FFI i reprezentacja](../22_ffi_i_interoperacyjnosc/01_ffi_abi_i_repr.md)
- [Kontrakty buforów](../13_io_siec_i_protokoly/02_siec_i_protokoly.md)
