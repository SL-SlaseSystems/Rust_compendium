[← Spis treści](../../README.md)

# Rozwiązania: Pipeline CI, MSRV i macierz konfiguracji

[Rozdział źródłowy](../../28_ci_cd_i_release_engineering/01_pipeline_ci_msrv_i_targety.md)

## D09-1

Locked utrzymuje istniejący graf i zgłasza konieczność zmiany lockfile. Offline nie korzysta z sieci i ogranicza dostępne zależności do lokalnych. Frozen łączy oba ograniczenia; nie pobiera brakujących crateów i nie generuje brakującego lockfile.

## D09-2

MSRV: build/test wspieranej konfiguracji na minimalnym kompilatorze. Stable: testy, Clippy i doctesty konfiguracji domyślnej. Minimalny wariant: check bez default-features na odpowiednim targetcie; jeśli wymaga `alloc`, zaznacz to jawnie. Do tego test wykonania adaptera, jeżeli produkt go deklaruje.

## D09-3

Sprawdź bibliotekę osobno w małym projekcie konsumenckim z minimalnymi features, poza pakietem, który przypadkowo włącza `std`. Porównaj `cargo tree -e features` obu konfiguracji. Kryterium: minimalny kontrakt przechodzi bez dodatkowego aktywatora; samo zielone `--workspace --all-features` nie wystarcza.
