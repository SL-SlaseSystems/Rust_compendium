[← Spis treści](../README.md)
<!-- status: expanded -->

# Granice zaufania, walidacja i kontrola zasobów

> Przykłady `rust`: biblioteka standardowa, Edition 2024. API narzędzi i bibliotek zewnętrznych opisano na podstawie źródeł sprawdzonych 11 listopada 2026 r.; szkice `text` wymagają wskazanego środowiska.

## Cele

Po tym rozdziale potrafisz:

- opisać aktywa, przeciwnika i granice zaufania;
- walidować reprezentację przed użyciem danych w domenie;
- ograniczać pamięć, czas i współbieżność niezależnie;

## Model — bezpieczna pamięć nie oznacza bezpiecznej operacji

Rust pomaga eliminować całe klasy błędów pamięci, lecz poprawnie typowany program może udostępnić cudze dane, wykonać nieautoryzowany przelew albo zaalokować więcej pamięci, niż ma host. Model zagrożeń zaczyna się od aktywów: co chronimy, przed kim i w jakich warunkach. Następnie zaznacza granice zaufania: wejście sieciowe, plik, argument procesu, zależność i poświadczenie usługi zewnętrznej.

Dla każdej operacji zapisz możliwość nadużycia i kontrolę. „Użytkownik wysyła wielką ramkę” prowadzi do limitu rozmiaru sprawdzanego przed alokacją. „Użytkownik pyta o cudzy rekord” prowadzi do autoryzacji na zasobie. „Wiele małych żądań zajmuje wszystkie taski” prowadzi do limitu współbieżności, kolejki i deadline. To różne zagrożenia; jeden timeout nie rozwiązuje wszystkich.

## Walidacja ma warstwy

Najpierw sprawdza się strukturę i ograniczenia reprezentacji, potem sens domenowy i uprawnienia. Dekodowanie poprawnego `u32` nie dowodzi, że użytkownik może wybrać taki identyfikator. Nie używaj rzutowania `as` do akceptowania długości z protokołu. Sprawdź konwersję, limit, rachunek długości oraz dostępność bajtów, zanim utworzysz obiekty domenowe.

~~~rust
#[derive(Debug, PartialEq)]
enum Blad { Naglowek, Limit, Niepelna, Nadmiar }

fn ramka(dane: &[u8], limit: usize) -> Result<&[u8], Blad> {
    let naglowek: [u8; 4] = dane.get(..4)
        .ok_or(Blad::Naglowek)?.try_into().unwrap();
    let n = usize::try_from(u32::from_be_bytes(naglowek))
        .map_err(|_| Blad::Limit)?;
    if n > limit { return Err(Blad::Limit); }
    let koniec = 4_usize.checked_add(n).ok_or(Blad::Limit)?;
    let wynik = dane.get(4..koniec).ok_or(Blad::Niepelna)?;
    if dane.len() != koniec { return Err(Blad::Nadmiar); }
    Ok(wynik)
}

fn main() {
    assert_eq!(ramka(&[0,0,0,2,65,66], 8), Ok(&b"AB"[..]));
    assert_eq!(ramka(&[0,0,0,9], 8), Err(Blad::Limit));
    assert_eq!(ramka(&[0,0,0,2,65], 8), Err(Blad::Niepelna));
}
~~~

`unwrap` dotyczy tutaj konwersji slice o już udowodnionej długości czterech bajtów. Nie pochodzi z założenia, że wejście jest poprawne. Funkcja pożycza payload, więc sama nie alokuje na podstawie długości. Zakłada dokładnie jedną kompletną ramkę; parser strumieniowy zamiast błędu nadmiaru zwracałby liczbę zużytych bajtów. Kontrakt musi tę różnicę nazywać.

## Budżety są wielowymiarowe

Limit skompresowanego body nie ogranicza rozmiaru po dekompresji. Limit bajtów nie ogranicza głębokości rekursji ani liczby elementów w małych rekordach. Kontroluj rozmiar wejścia, rozwiniętego wyniku, liczbę obiektów, głębokość i liczbę równocześnie aktywnych operacji. Zapisz, na którym etapie zasób jest rezerwowany i kiedy wraca do puli.

Kolejka bez granicy przenosi przeciążenie do pamięci. Kolejka ograniczona wymaga jawnej decyzji: odrzucenie, oczekiwanie z deadline albo ograniczenie producenta. Pomiar czasu powinien obejmować czekanie w kolejce; inaczej zadanie może zużyć budżet, zanim właściwa praca w ogóle ruszy. Retry w wielu warstwach może zwielokrotnić obciążenie awarii.

## Ścieżki, procesy i zapytania

Nie składaj polecenia powłoki z tekstu użytkownika. `Command::arg` omija interpretację powłoki, ale program docelowy nadal może interpretować argument jako opcję; stosuj reguły jego interfejsu. Parametryzacja SQL rozdziela wartości od zapytania, lecz dynamiczne nazwy tabel lub kolumn wymagają osobnej dozwolonej listy. Walidacja jednego znaku nie jest uniwersalną kontrolą wstrzyknięć.

Dla dostępu do plików proste `starts_with` na tekście ścieżki nie rozwiązuje symlinków i wyścigów między sprawdzeniem a otwarciem. Dobierz model katalogu i uprawnień do platformy, ogranicz możliwości procesu i testuj próby wyjścia poza dozwoloną przestrzeń. Granica zaufania ma być kontrolowana w miejscu wykonania skutku, a nie wyłącznie w warstwie prezentacji.

## Diagnostyka kompilatora

Kompilator wykryje niedopasowane typy i nielegalne pożyczki, ale nie odróżni automatycznie długości zaakceptowanej od niezweryfikowanej. Newtype z prywatnym polem może utrwalić zakończoną walidację. Negatywne testy powinny sprawdzać klasę błędu oraz brak skutku ubocznego. Panika na niepoprawnych danych jest naruszeniem kontraktu parsera, nawet jeżeli nie powoduje UB.

## Praktyka produkcyjna

Projektuj odrzucenie przed kosztownym krokiem. Loguj kod przyczyny i rozmiar, ograniczając treść danych wejściowych. Utrzymuj testy limitu dokładnie na granicy, o jeden powyżej oraz dla maksymalnej liczby w nagłówku. Pod obciążeniem mierz kolejkę i czas oczekiwania; sukces pojedynczego requestu nie świadczy o odporności na przeciążenie. Każdy wyjątek od limitu powinien mieć konkretny powód i ograniczony zakres.

## Sprawdź, czy rozumiesz

1. Dlaczego limit bajtów nie ogranicza każdej formy kosztu?
2. Kiedy `unwrap` w przykładzie ma lokalny dowód poprawności?
3. Czym różni się walidacja formatu od autoryzacji zasobu?

## Ćwiczenia

- `D07-1` — podstawowe: Dodaj test ramki zerowej oraz payloadu o dokładnie maksymalnej długości. [Rozwiązanie](../rozwiazania/27_bezpieczenstwo_aplikacji/01_granice_zaufania_walidacja_i_limity.md#d07-1).
- `D07-2` — praktyczne: Zaprojektuj limity importera skompresowanych rekordów JSON. [Rozwiązanie](../rozwiazania/27_bezpieczenstwo_aplikacji/01_granice_zaufania_walidacja_i_limity.md#d07-2).
- `D07-3` — pogłębione: Opisz przeciążenie usługi z trzema warstwami retry po trzy próby. [Rozwiązanie](../rozwiazania/27_bezpieczenstwo_aplikacji/01_granice_zaufania_walidacja_i_limity.md#d07-3).

## Źródła i granice weryfikacji

Kontrakty użytych mechanizmów: [std::process::Command](https://doc.rust-lang.org/std/process/struct.Command.html), [slice::get](https://doc.rust-lang.org/std/primitive.slice.html#method.get) oraz [u32](https://doc.rust-lang.org/std/primitive.u32.html). Model zagrożeń i parser są autorskimi przykładami; nie stanowią kompletnego serwera ani uniwersalnej ochrony plików.

## Powiązane tematy

- [Sekrety i zależności](02_sekrety_uprawnienia_i_zaleznosci.md)
- [Sieć i protokoły](../13_io_siec_i_protokoly/02_siec_i_protokoly.md)
- [Anulowanie i timeouty](../11_async_rust/04_anulowanie_timeouty_i_blocking.md)
