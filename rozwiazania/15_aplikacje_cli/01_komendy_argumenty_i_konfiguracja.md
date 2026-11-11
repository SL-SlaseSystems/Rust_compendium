[← Spis treści](../../README.md)

# Rozwiązania: Komendy i konfiguracja

## C01-1

Bez flagi wygrywa środowisko: `limit=20 (środowisko)`. Po dodaniu `--limit 7` wygrywa CLI: `limit=7 (argument)`. Brak wartości w najwyższej warstwie oznacza zachowanie poprzedniej decyzji. Pochodzenie można przechowywać jako parę `(usize, Zrodlo)` i zmieniać tylko w gałęzi `Some`; wartość domyślna zaczyna z `Zrodlo::Domyslne`.

## C01-2

Przykładowy kontrakt tego narzędzia: sukces `0`, dane na stdout; niepoprawne argumenty `2`, krótki błąd i użycie na stderr; niepoprawny rekord `3`, numer rekordu na stderr; błąd pliku `1`, nazwa operacji i przyczyna na stderr. Wyniki częściowe wymagają osobnej decyzji: narzędzie atomowe nie publikuje wyniku przed sukcesem, strumieniowe może już wysłać wcześniejsze rekordy. Skrypt musi sprawdzać status, zamiast wnioskować o sukcesie z obecności danych. `--help` kończy się `0` i kieruje pomoc na stdout.

## C01-3

Walidacja wyniku pozwala poprawić zły limit pliku przez flagę. Walidacja każdej warstwy odrzuci plik przed scalaniem. Obie polityki są możliwe, lecz muszą być jawne. Minimalny test gotowej konfiguracji:

~~~rust
fn sprawdz(limit: usize, partia: usize) -> Result<(), &'static str> {
    if limit == 0 || partia == 0 { return Err("wartość zerowa"); }
    if partia > limit { return Err("partia przekracza limit"); }
    Ok(())
}
fn main() {
    assert_eq!(sprawdz(20, 20), Ok(()));
    assert_eq!(sprawdz(20, 21), Err("partia przekracza limit"));
    assert!(sprawdz(20, 0).is_err());
}
~~~

Pole `partia: Option<usize>` scala się tak samo jak `limit`, z dodatnią wartością domyślną. Nie wykonuj walidacji relacji po każdej nadpisanej pojedynczej właściwości: przejściowy stan może być niepoprawny, choć cała kolejna warstwa daje poprawną parę.
