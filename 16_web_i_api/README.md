[← Spis treści](../README.md)

# 16. Web i API

## Dla kogo i po co

Dla osób tworzących usługi HTTP, API i backendy działające asynchronicznie.

## Wymagania wstępne

Async Rust, sieć, serializacja, obsługa błędów i testowanie.

## Kolejność materiałów

1. [HTTP, routing, stan aplikacji i błędy API](01_http_routing_stan_i_bledy.md) — żądania, odpowiedzi, ekstrakcja, walidacja i jednolity model błędu.
2. [Middleware, limity, testy i kontrolowane zamykanie](02_middleware_limity_testy_i_shutdown.md) — kolejność warstw, timeouty, testy kontraktowe i start produkcyjny.

Każdy rozdział zawiera trzy ćwiczenia z pełnymi rozwiązaniami; najpierw wykonaj je samodzielnie, potem porównaj kontrakty i przypadki graniczne.

## Po tym dziale

Potrafisz zbudować usługę z cienką warstwą transportową, jawnie modelowanymi błędami i kontrolą zasobów.

## Co dalej

Dodaj persystencję, bezpieczeństwo aplikacji i obserwowalność. Framework wybieraj po poznaniu modelu HTTP i async, nie zamiast nich.
