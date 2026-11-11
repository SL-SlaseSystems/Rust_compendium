[← Spis treści](../README.md)
<!-- status: expanded -->

# Własne błędy i projektowanie API

## Cele

Po tym rozdziale potrafisz:

- oddzielić klasyfikację błędu od raportu tekstowego;
- zaprojektować łańcuch przyczyn i politykę ewolucji;


Biblioteka powinna zwracać błąd, który wywołujący może sensownie rozróżnić.
Aplikacja może częściej agregować błędy i dodawać kontekst dla człowieka.

## Ręczny typ błędu

~~~rust
use std::error::Error;
use std::fmt;
use std::num::ParseIntError;

#[derive(Debug)]
enum BladKonfiguracji {
    BrakPortu,
    ZlyPort(ParseIntError),
}

impl fmt::Display for BladKonfiguracji {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::BrakPortu => write!(f, "brak pola port"),
            Self::ZlyPort(_) => write!(f, "port nie jest poprawną liczbą"),
        }
    }
}

impl Error for BladKonfiguracji {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            Self::ZlyPort(e) => Some(e),
            Self::BrakPortu => None,
        }
    }
}

impl From<ParseIntError> for BladKonfiguracji {
    fn from(e: ParseIntError) -> Self { Self::ZlyPort(e) }
}

fn port(input: Option<&str>) -> Result<u16, BladKonfiguracji> {
    Ok(input.ok_or(BladKonfiguracji::BrakPortu)?.parse()?)
}

fn main() {
    assert_eq!(port(Some("8080")).unwrap(), 8080);
    assert_eq!(port(None).unwrap_err().to_string(), "brak pola port");
}
~~~

`Debug` służy programiście, `Display` użytkownikowi, a `source` buduje łańcuch
przyczyn. Nie umieszczaj sekretów w żadnym z tych formatów.

## Enum czy opaque error

Publiczny enum pozwala dopasowywać warianty, ale dodanie wariantu może być
zmianą łamiącą wyczerpujący `match`. Opcje:

- stabilny enum z przemyślanymi kategoriami;
- `#[non_exhaustive]`, aby wymusić ramię zapasowe poza crate’em;
- prywatna reprezentacja i publiczne metody klasyfikujące;
- boxed `dyn Error` w małym programie, gdy typ nie jest częścią ważnego API.

## Biblioteki zewnętrzne

`thiserror` (**third-party**) generuje standardowe implementacje dla enumów
bibliotecznych. `anyhow` (**third-party**) upraszcza agregację i kontekst w
aplikacjach. Nie są częścią języka. Nadal trzeba zaprojektować kategorie,
komunikaty i źródła.

## Granularność

Nie każdy błąd systemowy powinien stać się osobnym wariantem. Wariant ma sens,
gdy wywołujący podejmie inną decyzję: retry, uwierzytelnienie, korekta danych,
brak zasobu. Dodaj dane diagnostyczne, lecz nie uzależniaj użytkownika od
niestabilnego tekstu `Display`.

## Zalecenia

- nie używaj `String` jako jedynego typu błędu biblioteki;
- zachowuj źródło przez `source` lub pole;
- dodawaj kontekst na granicy abstrakcji;
- oznaczaj transient/permanent metodą lub wariantem, jeśli klient robi retry;
- testuj warianty, nie całe komunikaty, chyba że tekst jest kontraktem;
- nie loguj i nie propaguj tego samego błędu bez potrzeby, bo powstają duplikaty.


## Model — odbiorca błędu ma podjąć decyzję

Projektuj błąd od reakcji klienta. Walidator formularza potrzebuje wskazania pola, mechanizm retry klasyfikacji przejściowości, a operator nazwy operacji i źródła. Jeden tekst zwykle nie spełnia wszystkich trzech ról. Publiczne metody mogą ujawniać stabilne kategorie, podczas gdy szczegół systemowy pozostaje źródłem diagnostycznym. Nie obiecuj, że każdy `io::ErrorKind` będzie miał osobny wariant twojego enumu.

Łańcuch `Error::source` powinien przedstawiać przyczynę, nie powtarzać tego samego zdania. `Display` opisuje bieżącą warstwę, a narzędzie raportujące przechodzi po źródłach. Nie ma automatycznej rekurencji w implementacji `Display`: jeżeli ręcznie wypiszesz wszystkie przyczyny i reporter zrobi to ponownie, raport będzie zawierał duplikaty. Nie parsuj `Display`, aby wybierać retry.

~~~rust
use std::{error::Error, fmt, num::ParseIntError};
#[derive(Debug)]
struct BladPola { pole: &'static str, przyczyna: ParseIntError }
impl fmt::Display for BladPola {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "niepoprawne pole {}", self.pole)
    }
}
impl Error for BladPola {
    fn source(&self) -> Option<&(dyn Error + 'static)> { Some(&self.przyczyna) }
}
fn liczba(s: &str) -> Result<u16, BladPola> {
    s.parse().map_err(|przyczyna| BladPola { pole: "port", przyczyna })
}
fn main() {
    let e = liczba("abc").unwrap_err();
    assert_eq!(e.to_string(), "niepoprawne pole port");
    assert!(e.source().is_some());
}
~~~

Błąd przechowuje przyczynę jako posiadany obiekt. Referencja zwracana przez `source` żyje tylko tak długo jak `&self`; dopisek `'static` przy `dyn Error` nie oznacza wiecznej referencji. Oznacza brak pożyczonych, krótkotrwałych danych w ukrytym typie źródła. Źródła pożyczające lokalne dane utrudniają takie API.

`Box<dyn Error>` upraszcza heterogeniczne błędy, lecz nie gwarantuje `Send` ani `Sync`. Jeżeli wynik przechodzi między taskami, kontrakt może potrzebować `Box<dyn Error + Send + Sync>`. Nie dodawaj takich ograniczeń bez potrzeby: błąd działający tylko lokalnie może zawierać inne dane. Koszt obejmuje zwykle alokację i dynamiczny dispatch, podczas gdy enum ma jawny zestaw wariantów i rozmiar zależny od największego wariantu.

Retry wymaga więcej niż flagi „tymczasowy”. Ten sam timeout może oznaczać, że operacja nie dotarła do serwera albo że zakończyła się po stronie serwera, ale odpowiedź zginęła. Klasyfikacja błędu nie zastępuje idempotencji protokołu. Publiczny błąd powinien informować o niepewności wyniku, jeśli ma to znaczenie biznesowe.

## Diagnostyka kompilatora

`impl Error` wymaga również `Debug` i `Display`; brak jednej z implementacji daje błąd boundu, który należy naprawić na typie błędu. Błąd czasu życia w `source` często oznacza, że próbowano zwrócić referencję do tymczasowego `format!` lub obiektu lokalnego. Przechowuj źródło w strukturze. Komunikat o braku `Send` przy `Box<dyn Error>` nie dowodzi problemu w runtime; sprawdź zestaw auto traits obiektu traitowego oraz konkretnych źródeł.

## Praktyka produkcyjna

Rozdziel raport wewnętrzny od komunikatu HTTP lub CLI. Nazwy plików, zapytania i zagnieżdżone błędy mogą zawierać dane poufne nawet przy niewinnym głównym komunikacie. Ustal politykę SemVer dla nowych wariantów, testuj klasyfikację i zachowanie `source`, a pełny tekst tylko wtedy, gdy jest częścią interfejsu. Przy błędzie operacji wieloetapowej zapisz etap i identyfikator, lecz unikaj kopiowania całego żądania. To zmniejsza koszt pamięci i ryzyko ujawnienia danych.

## Sprawdź, czy rozumiesz

- Czy `Box<dyn Error>` można zawsze wysłać do innego wątku?
- Co naprawdę oznacza `'static` w typie `source`?
- Dlaczego „błąd przejściowy” nie wystarcza do bezpiecznego retry płatności?

## Ćwiczenia

- `B04-1` — podstawowe: Zdefiniuj enum błędu walidacji z wariantami pustego tekstu i przekroczonej długości. [Rozwiązanie](../rozwiazania/07_obsluga_bledow/04_wlasne_bledy_i_api.md#b04-1).
- `B04-2` — praktyczne: Zaimplementuj `Display`, `Error` i `source` dla opakowanego `ParseIntError`. [Rozwiązanie](../rozwiazania/07_obsluga_bledow/04_wlasne_bledy_i_api.md#b04-2).
- `B04-3` — pogłębione: Zdefiniuj kategorię retry rozróżniającą odrzucenie, bezpieczne ponowienie i nieznany wynik operacji. [Rozwiązanie](../rozwiazania/07_obsluga_bledow/04_wlasne_bledy_i_api.md#b04-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [Error: wymagania i źródła](https://doc.rust-lang.org/std/error/trait.Error.html)

## Powiązane tematy

- [`Option` i `Result`](01_option_i_result.md)
- [Propagacja i operator `?`](02_propagacja_i_operator_question_mark.md)
- [Projektowanie API i SemVer](../14_idiomy_wzorce_i_architektura/03_projektowanie_api_i_semver.md)
