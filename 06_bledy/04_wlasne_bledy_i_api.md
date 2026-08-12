[← Spis treści](../README.md)

# Własne błędy i projektowanie API

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

## Powiązane tematy

- [`Option` i `Result`](01_option_i_result.md)
- [Propagacja i operator `?`](02_propagacja_i_operator_question_mark.md)
- [Projektowanie API i SemVer](../13_wzorce_i_architektura/03_projektowanie_api_i_semver.md)
