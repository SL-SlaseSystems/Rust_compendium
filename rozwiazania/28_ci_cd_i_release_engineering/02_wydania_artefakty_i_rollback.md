[← Spis treści](../../README.md)

# Rozwiązania: Wydania, pochodzenie artefaktów i rollback

[Rozdział źródłowy](../../28_ci_cd_i_release_engineering/02_wydania_artefakty_i_rollback.md)

## D10-1

Rewizja źródła, Cargo.lock, pełna wersja toolchainu, target i flagi, a także obraz/systemowe zależności środowiska. Dla build.rs zachowaj wejściowe pliki i konfigurację. Sama nazwa gałęzi jest zmienna i nie identyfikuje źródła.

## D10-2

Test kontraktowy odczytuje zapisane przykłady poprzedniej wersji, a changelog opisuje nowe pola i politykę kompatybilności. Artefakt jest budowany raz, testowany i promowany. Kod wyjścia i rozdzielenie stdout/stderr są częścią kontraktu; debug log na stdout może złamać integrację bez zmiany JSON.

## D10-3

Najpierw sprawdź, czy poprzedni czytnik rozumie nowe dane. Jeśli nie, zatrzymaj nowe zapisy i wybierz przetestowaną migrację odwrotną albo naprawę do przodu. Uwzględnij operacje wykonane po backupie i wymagany czas odtworzenia. Nie przywracaj starego snapshotu bez decyzji, co stanie się z późniejszymi zapisami.
