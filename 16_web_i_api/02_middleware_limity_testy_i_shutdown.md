[← Spis treści](../README.md)
<!-- status: expanded -->

# Middleware, limity, testy i kontrolowane zamykanie

## Cele

Po tym rozdziale potrafisz:

- ustawić osobne limity wielkości, współbieżności, kolejki i czasu;
- wyjaśnić wpływ kolejności middleware na pomiar oraz odpowiedź;
- przetestować router bez socketu i zaplanować zamknięcie z deadline.

## Model — Żądanie przechodzi przez warstwy

Middleware otacza usługę: może zobaczyć żądanie przed handlerem, zmodyfikować odpowiedź albo odrzucić pracę. Kolejność jest semantyką. Zewnętrzna warstwa śledzenia powinna obserwować także odrzucenia autoryzacji i przekroczenia limitów. Warstwa dekompresji zmienia rozmiar danych; limit liczony wyłącznie przed nią nie ogranicza rozpakowanego payloadu. Przemyśl osobny limit bajtów na drucie, rozpakowanego dokumentu i liczby rekordów domenowych.

Timeout handlera nie zastępuje limitu czasu odczytu body ani czasu wysyłania odpowiedzi do powolnego klienta. Future handlera może zakończyć się po utworzeniu odpowiedzi, podczas gdy body nadal jest strumieniowane. Zdefiniuj budżet całego żądania oraz osobne granice dla połączenia z zależnością, oczekiwania na pulę i wykonania zapytania. Kolejna warstwa nie powinna przydzielać pełnego budżetu od nowa: przekazuj pozostały czas lub wspólny deadline.

## Limity i przeciążenie

Limit współbieżności określa liczbę operacji aktywnych, a kolejka liczbę oczekujących. Nieograniczona kolejka zmienia chwilowe przeciążenie w rosnącą pamięć i opóźnienie. Gdy zasób jest zajęty, produkt może czekać w ograniczonej kolejce albo odrzucić pracę odpowiednim statusem. `429` pasuje do polityki limitu klienta; `503` do czasowej niedostępności usługi. Warunki ponawiania i ewentualny `Retry-After` powinny odpowiadać faktycznej polityce.

~~~rust
#[derive(Debug, PartialEq)]
enum Decyzja { Start, Kolejka, Odrzuc }
fn przyjmij(aktywne: usize, czekajace: usize,
            max_aktywne: usize, max_kolejka: usize) -> Decyzja {
    if aktywne < max_aktywne { Decyzja::Start }
    else if czekajace < max_kolejka { Decyzja::Kolejka }
    else { Decyzja::Odrzuc }
}
fn main() {
    assert_eq!(przyjmij(3, 0, 4, 2), Decyzja::Start);
    assert_eq!(przyjmij(4, 1, 4, 2), Decyzja::Kolejka);
    assert_eq!(przyjmij(4, 2, 4, 2), Decyzja::Odrzuc);
}
~~~

To model decyzji, nie synchronizacja licznika. W serwerze sprawdzenie i rezerwacja miejsca muszą stanowić jeden protokół, np. nabycie permitu semafora. Osobne „sprawdź licznik, potem zwiększ” przepuści równoczesne żądania ponad limit. Permit RAII zwracany po zakończeniu lub anulowaniu zapobiega utracie miejsca, ale odłączony task potrzebuje własnej kontroli żywotności.

**Third-party:** szkic wymaga axum 0.8, Tokio 1 z `net`, `signal` i runtime oraz tower-http 0.7 z feature `timeout`. Nie jest wykonywany przez rustdoc; pomija utworzenie routera i nasłuchu. Zweryfikowano API 2026-11-11 w [TimeoutLayer](https://docs.rs/tower-http/latest/tower_http/timeout/index.html) i [Serve::with_graceful_shutdown](https://docs.rs/axum/latest/axum/serve/struct.Serve.html).

~~~text
use axum::http::StatusCode;
use std::time::Duration;
use tower_http::timeout::TimeoutLayer;

let app = app.layer(TimeoutLayer::with_status_code(
    StatusCode::GATEWAY_TIMEOUT, Duration::from_secs(2),
));
axum::serve(listener, app)
    .with_graceful_shutdown(async {
        tokio::signal::ctrl_c().await.expect("nasluch Ctrl-C");
    })
    .await?;
~~~

Ta warstwa tworzy odpowiedź na przekroczenie czasu usługi. Nie cofa przelewu zatwierdzonego przez bazę ani nie zabija automatycznie pracy CPU uruchomionej poza jej future. Długie operacje procesora przenieś do ograniczonego executora blocking i zaprojektuj współpracujące anulowanie. Gdy wynik zapisu jest nieznany, klient potrzebuje klucza idempotencji lub możliwości sprawdzenia stanu.

## Diagnostyka kompilatora

Zwykły `tower::timeout` zmienia typ błędu usługi; axum wymaga odpowiedniego zamienienia go na odpowiedź. Niespełniony trait na `.layer()` może oznaczać brak takiego adaptera. Wariant HTTP w szkicu zwraca gotową odpowiedź i nie zmienia błędu usługi. Nie dodawaj przypadkowych konwersji do `Box<dyn Error>` bez ustalenia, kto zamieni timeout na status.

Inny problem to klonowanie stanu: `Router::clone()` zwykle współdzieli zasoby wskazywane przez uchwyty, a nie tworzy izolowanej bazy testowej. Kompilator potwierdzi typy, ale nie niezależność testów. Każdy test potrzebuje własnego magazynu albo jawnie resetowanego, serializowanego stanu.

## Testy kontraktowe i integracyjne

**Third-party:** `tower::ServiceExt::oneshot` pozwala wywołać usługę po uzyskaniu gotowości, bez otwierania socketu. Szkic wymaga feature `util`, istniejącego `app` i async testu; nie był tutaj wykonywany. Kontrakt sprawdzono w [ServiceExt](https://docs.rs/tower/latest/tower/util/trait.ServiceExt.html), 2026-11-11.

~~~text
use tower::ServiceExt;
use axum::{body::Body, http::{Request, StatusCode}};
let response = app.oneshot(
    Request::builder().uri("/health").body(Body::empty()).unwrap()
).await.unwrap();
assert_eq!(response.status(), StatusCode::OK);
~~~

Taki test obejmuje router i jego warstwy, ale pomija TCP, TLS i reverse proxy. Osobny test uruchomienia powinien użyć losowego lokalnego portu i sprawdzić gotowość, limit body, timeout zależności oraz zamknięcie. Test kontraktowy obejmuje także błędy, nagłówki i brak sekretów. Test obciążeniowy powinien ujawnić maksymalną długość kolejki i ogon opóźnień, a nie tylko średnią przepustowość.

## Praktyka produkcyjna

Kontrolowane zamykanie przebiega etapami: wyłącz gotowość, przestań przyjmować nową pracę, poczekaj na aktywne żądania, zatrzymaj producentów zadań, opróżnij ograniczone kolejki, zamknij pulę i flushuj telemetrię. Nadaj całości termin końcowy; niekończący się stream nie może blokować restartu bez końca. `with_graceful_shutdown` uruchamia protokół serwera, ale sam nie obejmuje wszystkich tasków aplikacji.

Przed wdrożeniem ustaw limity zgodne z proxy i bazą, sprawdź zaufanie do nagłówków forwarding oraz rozdziel liveness od readiness. Nie usuwaj zdrowego procesu z powodu chwilowego braku bazy w sposób wywołujący lawinę restartów. Mierz aktywne żądania, odrzucenia, czas kolejki i zależności. Identyfikator użytkownika jako etykieta metryki tworzy kosztowną, nieograniczoną liczbę szeregów.

## Sprawdź, czy rozumiesz

- Dlaczego timeout odpowiedzi nagłówkowej nie wystarcza dla nieskończonego streamu?
- Co sprawdza test `oneshot`, a co dopiero prawdziwy nasłuch?
- Jak zakończysz shutdown, gdy zadanie nie współpracuje z anulowaniem?

## Ćwiczenia

- `C04-1` — podstawowe: Dla limitu 8 aktywnych i 16 oczekujących podaj decyzje przy stanach (7,16), (8,15), (8,16). Wyjaśnij konieczność atomowej rezerwacji. [Rozwiązanie](../rozwiazania/16_web_i_api/02_middleware_limity_testy_i_shutdown.md#c04-1).
- `C04-2` — praktyczne: Zaprojektuj test przeciążenia z 2 permitami i bez kolejki: dwa żądania czekają na barierze, trzecie ma zostać odrzucone. Podaj kryteria końca testu. [Rozwiązanie](../rozwiazania/16_web_i_api/02_middleware_limity_testy_i_shutdown.md#c04-2).
- `C04-3` — pogłębione: Rozpisz zamknięcie usługi z otwartym streamem i workerem bazy w budżecie 10 sekund. Zdefiniuj termin i postępowanie z nieznanym wynikiem zapisu. [Rozwiązanie](../rozwiazania/16_web_i_api/02_middleware_limity_testy_i_shutdown.md#c04-3).

## Powiązane tematy

- [Model HTTP i błędy](01_http_routing_stan_i_bledy.md)
- [Anulowanie async](../11_async_rust/04_anulowanie_timeouty_i_blocking.md)
- [Integracje i idempotencja](../18_serializacja_konfiguracja_i_integracje/02_konfiguracja_sekrety_i_odpornosc_integracji.md)
