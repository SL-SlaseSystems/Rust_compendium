[← Spis treści](../README.md)
<!-- status: expanded -->

# HTTP, routing, stan aplikacji i błędy API

## Cele

Po tym rozdziale potrafisz:

- przeprowadzić żądanie przez routing, ekstrakcję, walidację i domenę;
- dobrać własność stanu współdzielonego między handlerami;
- odróżnić błąd składni żądania, odmowę domeny i awarię infrastruktury.

## Model — Żądanie i cienki adapter

Żądanie HTTP zawiera metodę, URI, nagłówki i ciało (body). Router wybiera handler na podstawie jawnego kontraktu trasy. Handler nie powinien zawierać całego procesu biznesowego: odczytuje DTO, uwierzytelnioną tożsamość i stan aplikacji, wywołuje przypadek użycia, następnie tworzy odpowiedź. Obiekt transportowy (data transfer object, DTO) może mieć pola tekstowe; domena powinna otrzymać już poprawny identyfikator, kwotę i dozwolony stan.

Ekstrakcja sprawdza reprezentację: czy identyfikator daje się odczytać jako `u64`, a body jest właściwym JSON-em. Walidacja określa sens: identyfikator nie może być zerem, nazwa ma dopuszczalną długość, użytkownik może wykonać operację. Udane parsowanie nie oznacza autoryzacji. Uprawnienie do odczytu konkretnego rekordu sprawdzaj w przypadku użycia lub odpowiednio zawężonym repozytorium; sama obecność tokenu nie wystarcza.

~~~rust
#[derive(Debug, PartialEq)]
struct Nazwa(String);
#[derive(Debug, PartialEq)]
enum Blad { PustaNazwa, ZbytDlugaNazwa }
impl TryFrom<String> for Nazwa {
    type Error = Blad;
    fn try_from(raw: String) -> Result<Self, Blad> {
        let nazwa = raw.trim();
        if nazwa.is_empty() { return Err(Blad::PustaNazwa); }
        if nazwa.chars().count() > 40 { return Err(Blad::ZbytDlugaNazwa); }
        Ok(Self(nazwa.to_owned()))
    }
}
fn main() {
    assert_eq!(Nazwa::try_from(String::from("  Ala ")), Ok(Nazwa("Ala".into())));
    assert_eq!(Nazwa::try_from(String::from(" ")), Err(Blad::PustaNazwa));
}
~~~

Konstruktor jest granicą niezmiennika. Dalsze funkcje przyjmujące `Nazwa` nie muszą ponownie odrzucać pustego tekstu. Limit wyrażono w skalarnych wartościach Unicode przez `chars`, nie w bajtach ani znakach widocznych dla człowieka; dla produktu wymagającego grapheme clusters potrzebny jest inny kontrakt i narzędzie. Ogranicz też liczbę bajtów body przed parsowaniem, bo 40 znaków domeny nie zabezpiecza przed wielkim dokumentem JSON.

## Konkretny szkic axum

**Third-party:** poniższy szkic używa `axum` 0.8, Tokio 1 i Serde 1 z derive. Nie jest doctestem: wymaga manifestu, runtime’u i dołączenia implementacji `Nazwa` z poprzedniego przykładu. Nie był uruchamiany jako serwer. Semantykę handlerów oraz `State` porównano 2026-11-11 z [dokumentacją axum](https://docs.rs/axum/0.8.7/axum/).

~~~text
use axum::{Router, Json, extract::State, routing::post,
           http::StatusCode};
use serde::{Deserialize, Serialize};
use std::sync::Arc;

struct AppState { nazwa_uslugi: String }
#[derive(Deserialize)]
struct Wejscie { nazwa: String }
#[derive(Serialize)]
struct Wyjscie { nazwa: String, usluga: String }

async fn utworz(
    State(stan): State<Arc<AppState>>,
    Json(dto): Json<Wejscie>,
) -> Result<(StatusCode, Json<Wyjscie>), (StatusCode, &'static str)> {
    let nazwa = Nazwa::try_from(dto.nazwa)
        .map_err(|_| (StatusCode::UNPROCESSABLE_ENTITY, "zla_nazwa"))?;
    Ok((StatusCode::CREATED, Json(Wyjscie {
        nazwa: nazwa.0, usluga: stan.nazwa_uslugi.clone(),
    })))
}
let app = Router::new().route("/osoby", post(utworz))
    .with_state(Arc::new(AppState { nazwa_uslugi: "katalog".into() }));
~~~

W pokazanym kontrakcie `POST /osoby` waliduje dane i zwraca reprezentację; pełne tworzenie zasobu wymaga zapisu oraz stabilnego identyfikatora, zwykle także nagłówka `Location`. Szkic celowo pokazuje samą granicę transportową. Nie deklaruj trwałego utworzenia przed zatwierdzeniem transakcji.

## Diagnostyka kompilatora

W axum ekstraktor konsumujący body, np. `Json`, umieszczaj jako ostatni. Strumienia nie da się ogólnie skonsumować dwukrotnie. Gdy wymagania traitu `Handler` nie są spełnione, sprawdź kolejność ekstraktorów, typ odpowiedzi i to, co pozostaje żywe przez `.await`. Te reguły potwierdza [dokumentacja ekstraktorów axum 0.8.9](https://docs.rs/axum/latest/axum/extract/), zweryfikowana 2026-11-11.

`MutexGuard` z `std::sync::Mutex` zachowany przez `.await` może uczynić future nieodpowiednim dla executora wymagającego `Send`. Wyodrębnij krótki blok odczytu, skopiuj potrzebny stan i zakończ guard przed operacją asynchroniczną. Samo dodanie `Arc` nie zapewnia bezpiecznej mutacji: `Arc<T>` dzieli własność, a sposób synchronizacji zależy od `T`. Długie sekcje krytyczne serializują żądania.

## Praktyka produkcyjna

Stan aplikacji zawiera współdzielone klienty HTTP, pulę bazy i niezmienną konfigurację. Tworzenie klienta lub puli przy każdym żądaniu traci reuse połączeń. Nie umieszczaj całej aplikacji pod jednym mutexem. Dla mutowalnego cache porównaj krótki lock, oddzielny task właścicielski i wyspecjalizowaną strukturę; każda opcja ma koszt pamięci, kolejki lub synchronizacji.

Ujednolić trzeba również odrzucenia ekstraktorów, błędy middleware i brak trasy. Sam `Result` handlera nie obejmie sytuacji, gdy handler nie został wywołany. Zdefiniuj strukturę błędu z maszynowym kodem, bezpiecznym opisem i identyfikatorem korelacji. Wybór między `400` i `422` jest częścią kontraktu API; konflikt unikalności może być `409`, brak zasobu `404`, a nieoczekiwana awaria `500`. Nie ujawniaj SQL, tokenów i backtrace klientowi. Log techniczny może zachować łańcuch przyczyn z odpowiednią redakcją.

Stabilizuj także sukces: typ mediów, nazwy pól, paginację i znaczenie pustej listy. Testy porównują semantyczny JSON oraz status i nagłówki, zamiast formatowania mapy. Przypadki użycia testuj bez sieci, a adapter osobno. Dzięki temu zmiana frameworka nie zmusza do przepisania reguł biznesowych.

## Sprawdź, czy rozumiesz

- Kiedy poprawny JSON nadal zasługuje na odmowę?
- Dlaczego błąd ekstraktora nie trafia do `map_err` wewnątrz handlera?
- Jaki koszt ma jeden wspólny mutex trzymany podczas wywołania bazy?

## Ćwiczenia

- `C03-1` — podstawowe: Przypisz odpowiedzi dla: niepoprawnego JSON, pustej nazwy, istniejącego już loginu i niedostępnej bazy. Określ bezpieczne body. [Rozwiązanie](../rozwiazania/16_web_i_api/01_http_routing_stan_i_bledy.md#c03-1).
- `C03-2` — praktyczne: Dodaj walidator identyfikatora użytkownika większego od zera oraz testy 0 i 1. Wyjaśnij granicę między walidacją i autoryzacją. [Rozwiązanie](../rozwiazania/16_web_i_api/01_http_routing_stan_i_bledy.md#c03-2).
- `C03-3` — pogłębione: Zaprojektuj jednolity typ błędu obejmujący handler, odrzucenie Json i brak trasy. Podaj trzy asercje testu kontraktowego. [Rozwiązanie](../rozwiazania/16_web_i_api/01_http_routing_stan_i_bledy.md#c03-3).

## Powiązane tematy

- [Limity i produkcja](02_middleware_limity_testy_i_shutdown.md)
- [Repozytorium i transakcje](../17_bazy_danych_i_persystencja/01_repozytoria_pule_i_transakcje.md)
- [Ewolucja danych](../18_serializacja_konfiguracja_i_integracje/01_formaty_serializacja_i_walidacja.md)
