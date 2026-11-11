[← Spis treści](../README.md)
<!-- status: expanded -->

# Sekrety, uprawnienia i bezpieczeństwo zależności

> Przykłady `rust`: biblioteka standardowa, Edition 2024. API narzędzi i bibliotek zewnętrznych opisano na podstawie źródeł sprawdzonych 11 listopada 2026 r.; szkice `text` wymagają wskazanego środowiska.

## Cele

Po tym rozdziale potrafisz:

- odróżnić uwierzytelnianie od autoryzacji;
- ograniczać przypadkowe ujawnienie sekretów w API i logach;
- oceniać raport podatności w kontekście używanego grafu i funkcji;

## Model — tożsamość nie jest uprawnieniem

Uwierzytelnienie odpowiada, kim jest wywołujący. Autoryzacja odpowiada, czy ta tożsamość może wykonać daną operację na konkretnym zasobie. Sam poprawny token nie uprawnia do odczytu wszystkich rekordów. Kontrolę umieść po ustaleniu tożsamości i przed wykonaniem skutku, korzystając z zaufanego kontekstu. Identyfikator właściciela z body requestu nie może sam nadawać uprawnienia.

Zasada najmniejszych uprawnień dotyczy też procesu, joba CI i integracji. Usługa odczytowa nie potrzebuje prawa publikacji paczek. Rozdziel tokeny środowisk, określ czas życia i możliwość unieważnienia. Test odmowy dla użytkownika innej organizacji jest równie ważny jak test sukcesu właściciela.

## Sekret ma kontrolowany przepływ

Sekrety nie powinny trafiać do repozytorium, argumentów wypisywanych w diagnostyce, pełnych payloadów ani automatycznego `Debug` struktur konfiguracji. Oddziel konfigurację zwykłą od poświadczeń. Newtype pozwala ograniczyć przypadkowe logowanie, choć sam nie gwarantuje wymazania z pamięci ani ochrony przed uprawnionym debuggerem.

~~~rust
use std::fmt;

struct Sekret(String);
impl Sekret {
    fn nowy(s: String) -> Result<Self, &'static str> {
        if s.is_empty() { Err("pusty sekret") } else { Ok(Self(s)) }
    }
    fn z_dostepem<R>(&self, f: impl FnOnce(&str) -> R) -> R {
        f(&self.0)
    }
}
impl fmt::Debug for Sekret {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str("Sekret([ukryto])")
    }
}
fn main() {
    let token = Sekret::nowy("token-testowy".into()).unwrap();
    assert_eq!(format!("{token:?}"), "Sekret([ukryto])");
    assert!(token.z_dostepem(|s| s.starts_with("token-")));
}
~~~

Jawna metoda dostępu pokazuje miejsce przekazania sekretu klientowi integracji. Closure może jednak skopiować go lub zalogować; API nie dowodzi poprawności konsumenta. Nie dodano `Clone`, bo kopiowanie tworzy kolejne miejsca wymagające kontroli. Ręczna implementacja `Debug` utrwala redakcję, ale nie zwalnia z testu logów i przeglądu struktur otaczających.

Rotacja wymaga protokołu: dostarczenia nowej wartości, przełączenia klientów, akceptacji w okresie przejściowym i unieważnienia starej. Zmiana pliku bez przeładowania procesu nie musi zmienić aktywnego klienta HTTP ani puli bazy. Zapisz, kto odświeża zasób i jak wykryjesz użycie starego poświadczenia, nie zapisując jego treści.

## Kryptografia przez kontrakt biblioteki

Nie implementuj własnego szyfru, generatora tokenów ani porównania haseł na podstawie krótkiego przykładu. Wybierz utrzymywaną bibliotekę o odpowiednim przeznaczeniu i sprawdź wymagania algorytmu: źródło losowości, niepowtarzalność nonce, zarządzanie kluczami oraz weryfikację danych. Bezpieczny język nie naprawia ponownego użycia nonce lub przyjęcia nieuwierzytelnionego komunikatu. Zmiana parametrów kryptografii wymaga aktualnej dokumentacji konkretnej implementacji i modelu zagrożeń.

## Graf zależności i raport podatności

RustSec gromadzi advisory dotyczące ekosystemu. `cargo-audit` jest narzędziem **third-party**, które analizuje zależności pod kątem tej bazy; `cargo-deny` dostarcza także polityki grafu, licencji i źródeł. Raport bez znanych advisory nie dowodzi bezpieczeństwa kodu, a znalezione advisory wymaga sprawdzenia wersji, targetu, features i rzeczywiście używanej funkcjonalności.

Nie ograniczaj kontroli do zależności runtime. `build.rs`, makra proceduralne i narzędzia CI wykonują kod w środowisku budowania. Zmiana dependency może zatem dotknąć sekretów dostępnych podczas kompilacji, zanim powstanie binarium. Ogranicz uprawnienia i dostęp do sekretów w jobach obsługujących niezaufane zmiany.

Przy podatności ustal dotknięte produkty i artefakty, wybierz aktualizację lub ograniczenie ekspozycji, uruchom testy kompatybilności i wydajności, a potem potwierdź, że wdrożono poprawiony artefakt. Wyciszenie advisory powinno mieć uzasadnienie, właściciela i termin ponownego przeglądu. Nie zamieniaj stałego wyjątku w niezauważalną normę.

## Diagnostyka kompilatora

System typów może uniemożliwić przypadkowe przekazanie `String` zamiast typu sekretu, ale nie sprawdzi poprawności polityki dostępu. Użyj testów tabelarycznych ról i zasobów: właściciel, inny tenant, konto zablokowane, brak tożsamości. Przy błędzie autoryzacji testuj brak odczytu/zapisu w adapterze, nie wyłącznie status HTTP. Ujawnienia sekretu nie naprawia usunięcie jednej linii logu: oceń konieczność unieważnienia wartości.

## Praktyka produkcyjna

Redaguj pola przed wysłaniem do backendu telemetrii, a nie dopiero w widoku dashboardu. Nie dołączaj sekretów do `Display` błędu ani kontekstu paniki. Utrzymuj aktualny lockfile aplikacji, powtarzalną kontrolę advisory i mapę zależności dla wydanych artefaktów. Jeśli wymagana jest kontrola kopiowania lub zerowanie pamięci, użyj właściwych bibliotek **third-party** po przeglądzie ich gwarancji; przykład `Sekret` takich własności nie zapewnia.

## Sprawdź, czy rozumiesz

1. Dlaczego poprawny token nie wystarcza do odczytu dowolnego rekordu?
2. Czego ręczne `Debug` nie gwarantuje?
3. Dlaczego makro proceduralne jest częścią powierzchni zaufania?

## Ćwiczenia

- `D08-1` — podstawowe: Dodaj test, że `Debug` nie zawiera wejściowego tokenu. [Rozwiązanie](../rozwiazania/27_bezpieczenstwo_aplikacji/02_sekrety_uprawnienia_i_zaleznosci.md#d08-1).
- `D08-2` — praktyczne: Ułóż tabelę autoryzacji odczytu dokumentu między organizacjami. [Rozwiązanie](../rozwiazania/27_bezpieczenstwo_aplikacji/02_sekrety_uprawnienia_i_zaleznosci.md#d08-2).
- `D08-3` — pogłębione: Opisz reakcję na wyciek poświadczenia integracji w logach. [Rozwiązanie](../rozwiazania/27_bezpieczenstwo_aplikacji/02_sekrety_uprawnienia_i_zaleznosci.md#d08-3).

## Źródła i granice weryfikacji

Baza i narzędzia: [RustSec](https://rustsec.org/), [cargo-audit](https://github.com/rustsec/rustsec/tree/main/cargo-audit), [cargo-deny](https://embarkstudios.github.io/cargo-deny/). Przykład sekretu pokazuje redakcję `Debug`, nie pełny magazyn poświadczeń ani implementację kryptografii.

## Powiązane tematy

- [Walidacja i limity](01_granice_zaufania_walidacja_i_limity.md)
- [Konfiguracja i integracje](../18_serializacja_konfiguracja_i_integracje/README.md)
- [Wydania i artefakty](../28_ci_cd_i_release_engineering/02_wydania_artefakty_i_rollback.md)
