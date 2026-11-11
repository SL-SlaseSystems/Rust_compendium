[← Spis treści](../README.md)
<!-- status: expanded -->

# Logi, metryki i ślady rozproszone

> Przykłady `rust`: biblioteka standardowa, Edition 2024. API narzędzi i bibliotek zewnętrznych opisano na podstawie źródeł sprawdzonych 11 listopada 2026 r.; szkice `text` wymagają wskazanego środowiska.

## Cele

Po tym rozdziale potrafisz:

- dobrać sygnał do pytania o zachowanie systemu;
- utrzymać kontekst żądania w kodzie async;
- kontrolować cardinality, koszt i ujawnianie danych;

## Model — obserwacja ma pomóc podjąć decyzję

Log odpowiada, co zdarzyło się w konkretnym punkcie. Metryka agreguje wielkość w czasie i między instancjami. Trace łączy fragmenty jednej operacji przez granice usług. Te sygnały uzupełniają się, gdy mają wspólną semantykę i kontrolowany kontekst. Gdy każdy komponent inaczej rozumie „sukces”, wykres i log mogą pozornie sobie przeczyć.

Zacznij od pytania operacyjnego: „Czy użytkownik może utworzyć zamówienie w zadanym czasie?” Następnie mierz wynik i opóźnienie tej ścieżki, a logami objaśniaj przyczyny błędów. Sam wzrost wykorzystania CPU nie mówi, czy usługa narusza kontrakt. Z kolei zdrowa średnia czasu odpowiedzi może ukryć wolny ogon rozkładu i małą grupę użytkowników.

## Zdarzenie jest strukturą, nie swobodnym zdaniem

Dobry event ma stabilną nazwę, poziom, kod wyniku i kilka przydatnych pól. Zmienny tekst utrudnia agregację. Loguj granice i ważne decyzje, nie każdą iterację. Dane wejściowe traktuj jako niezaufane: ogranicz długość, redaguj sekrety i nie pozwalaj znakom sterującym fałszować linii w odbiorcy.

Poniższy przykład std modeluje jawne pole wyniku. Nie jest zamiennikiem biblioteki telemetrycznej; pokazuje, że klasę błędu można ustalić bez ujawnienia prywatnej treści.

~~~rust
#[derive(Debug)]
enum Blad { NiepoprawneDane(String), Niedostepnosc }
fn kod(wynik: &Result<(), Blad>) -> &'static str {
    match wynik {
        Ok(()) => "ok",
        Err(Blad::NiepoprawneDane(_)) => "invalid_input",
        Err(Blad::Niedostepnosc) => "unavailable",
    }
}
fn main() {
    let wynik = Err(Blad::NiepoprawneDane("prywatne dane".into()));
    assert_eq!(kod(&wynik), "invalid_input");
    if let Err(Blad::NiepoprawneDane(tresc)) = &wynik {
        assert!(!tresc.is_empty());
    }
    assert_eq!(kod(&Err(Blad::Niedostepnosc)), "unavailable");
}
~~~

Rozdzielenie kodu od szczegółu pozwala utrzymać stabilną agregację nawet po zmianie komunikatu błędu. Nie loguj automatycznie całego `Debug` tylko dlatego, że typ go implementuje. Informację prywatną można zachować do kontrolowanej obsługi lokalnej, ale domyślna telemetria nie powinna jej transportować.

## Spany i async

`tracing` jest biblioteką **third-party**. Event opisuje moment, a span okres i kontekst pracy; subscriber odbiera i przetwarza te dane. Biblioteka emituje zdarzenia, a aplikacja zwykle konfiguruje odbiorcę. Zapobiega to przejmowaniu globalnej polityki logowania przez zależność.

Poniższy szkic wymaga `tracing` i rzeczywistej operacji async:

~~~text
use tracing::Instrument;
let span = tracing::info_span!("zamowienie", order_id = %id);
let wynik = wykonaj().instrument(span).await;
~~~

Nie trzymaj guarda `Span::enter` przez `await`: task może oddać wątek, a kontekst stosu wątku nie odpowiada wtedy okresowi aktywności tej future. Instrumentuj future lub użyj odpowiedniego atrybutu z pominięciem sekretów. Identyfikator trace propagowany przez sieć wymaga świadomego adaptera; sama obecność lokalnego spana nie tworzy śladu rozproszonego.

## Metryki i liczba szeregów

Licznik opisuje zdarzenia narastająco, gauge bieżącą wielkość, a histogram rozkład obserwacji. Etykiety tworzą dodatkowe szeregi. Jeśli każda z trzech etykiet ma sto wartości, potencjalna kombinacja to milion, zanim uwzględnisz instancje i bucket histogramu. Ogranicz klasy do skończonych kategorii: metoda, wzorzec trasy i klasa wyniku. Pełny URL z identyfikatorem użytkownika nie jest dobrym wymiarem metryki.

Nie uśredniaj percentyli z różnych instancji jako globalnego percentyla. Potrzebujesz odpowiedniego łączenia rozkładów albo obserwacji źródłowych. Wybór granic bucketów wynika z progów istotnych dla produktu; bardzo grube koszyki mogą ukryć zmianę w pobliżu SLO. Sampling trace'ów zmniejsza koszt, lecz pomija część ścieżek i zmienia interpretację danych.

## Diagnostyka kompilatora

Kompilator nie wykrywa błędnej nazwy metryki, braku propagacji trace ani zbyt dużej cardinality. Testuj adapter: event zawiera wymagane pola, sekret nie występuje, a liczba możliwych etykiet jest ograniczona. Szkic `Instrument` może wymagać odpowiednich features crate'a; sprawdź manifest i dokumentację wersji. Brak zdarzeń może oznaczać filtr lub brak subscribera, nie brak wykonania kodu.

## Praktyka produkcyjna

Dla ważnej operacji ustal jedno miejsce rejestracji wyniku, żeby nie liczyć wielokrotnie tego samego błędu w każdej warstwie. Obserwuj również utracone zdarzenia i koszt eksportera; awaria telemetrii nie powinna bez granic blokować aplikacji. Dokumentuj jednostki i znaczenie mianownika. Korelację po identyfikatorze requestu stosuj w logach i trace, a nie automatycznie jako etykietę każdej metryki.

## Sprawdź, czy rozumiesz

1. Dlaczego request_id jest przydatny w logu, ale ryzykowny jako etykieta metryki?
2. Co powoduje trzymanie guarda spana przez `await`?
3. Dlaczego średnia może ukryć degradację ważnej ścieżki?

## Ćwiczenia

- `D11-1` — podstawowe: Wybierz sygnał do ustalenia skali błędów i do analizy jednego requestu. [Rozwiązanie](../rozwiazania/29_observability_i_produkcja/01_logi_metryki_i_traces.md#d11-1).
- `D11-2` — praktyczne: Zaprojektuj etykiety metryki opóźnienia HTTP bez identyfikatorów użytkowników. [Rozwiązanie](../rozwiazania/29_observability_i_produkcja/01_logi_metryki_i_traces.md#d11-2).
- `D11-3` — pogłębione: Opisz test redakcji sekretów w instrumentacji funkcji. [Rozwiązanie](../rozwiazania/29_observability_i_produkcja/01_logi_metryki_i_traces.md#d11-3).

## Źródła i granice weryfikacji

Kontrakty eventów, spanów i async: [tracing API](https://docs.rs/tracing/latest/tracing/). Definicje sygnałów: [OpenTelemetry concepts](https://opentelemetry.io/docs/concepts/signals/). Model kodów błędu i dobór etykiet są autorskimi przykładami projektowymi; backend telemetryczny nie jest uruchamiany w doctestach.

## Powiązane tematy

- [SLO i działanie usługi](02_slo_shutdown_i_operacje.md)
- [Sekrety](../27_bezpieczenstwo_aplikacji/02_sekrety_uprawnienia_i_zaleznosci.md)
- [Async taski](../11_async_rust/03_taski_join_select_i_stream.md)
