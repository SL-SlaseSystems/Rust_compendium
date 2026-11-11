[← Spis treści](../README.md)
<!-- status: expanded -->

# Regresje, aktualizacje i utrzymanie po incydencie

> Przykłady `rust`: biblioteka standardowa, Edition 2024. API narzędzi i bibliotek zewnętrznych opisano na podstawie źródeł sprawdzonych 11 listopada 2026 r.; szkice `text` wymagają wskazanego środowiska.

## Cele

Po tym rozdziale potrafisz:

- izolować zmianę odpowiedzialną za regresję;
- zaplanować zgodną migrację API i zależności;
- zamienić ustalenia incydentu w trwałą poprawę;

## Model — zmienia się więcej niż kod aplikacji

Regresja jest pogorszeniem względem znanego punktu odniesienia. Zmienić mogły się źródła, graf zależności, kompilator, flagi, dane albo usługa zewnętrzna. Zapisz oba zestawy warunków. Dopiero odtwarzając błąd przy stałych danych możesz badać, która różnica ma znaczenie. Aktualizacja dziesięciu crate'ów i kompilatora w jednym kroku utrudnia to przypisanie.

`Cargo.lock` ustala konkretne wersje rozwiązanego grafu; nie ustala całego systemu, linkera ani danych z sieci. Zachowaj go wraz z wersją aplikacji i informacją o środowisku budowania. Gdy porównujesz wersje kompilatora, nie pozwól przypadkowo aktualizować zależności. Gdy porównujesz zależność, pozostaw kompilator i przypadek testowy niezmienne.

## Test jako predykat wyszukiwania

Bisekcja potrzebuje stabilnego rozróżnienia „dobry” i „zły”. Przypadkowy timeout albo benchmark o dużym szumie daje fałszywe podziały. Najpierw skonstruuj mały program kończący się kodem sukcesu przy oczekiwanym zachowaniu, potem szukaj zmiany. Nie myl braku możliwości zbudowania starej rewizji z reprodukcją badanego błędu.

Poniższy model jawnie rozróżnia wynik poprawny, regresję i brak rozstrzygnięcia. Odpowiada to praktyce, w której niezgodny toolchain nie może zostać automatycznie nazwany wadliwą wersją.

~~~rust
#[derive(Debug, PartialEq)]
enum Ocena { Dobra, Zla, Nierozstrzygnieta }

fn ocen(zbudowano: bool, wynik: Option<u32>) -> Ocena {
    if !zbudowano { return Ocena::Nierozstrzygnieta; }
    match wynik {
        Some(42) => Ocena::Dobra,
        Some(_) => Ocena::Zla,
        None => Ocena::Nierozstrzygnieta,
    }
}

fn main() {
    assert_eq!(ocen(true, Some(42)), Ocena::Dobra);
    assert_eq!(ocen(true, Some(41)), Ocena::Zla);
    assert_eq!(ocen(false, None), Ocena::Nierozstrzygnieta);
}
~~~

Narzędzie `cargo-bisect-rustc` jest **third-party** i służy do szukania regresji między kompilatorami. Jego skrypt reprodukcji musi wskazywać dokładnie badaną własność; pobieranie historycznych toolchainów i dostępność artefaktów stanowią oddzielne wymagania. Zwykła bisekcja historii projektu służy innemu zakresowi: zmianom w repozytorium aplikacji. Wybierz oś dopiero po ograniczeniu zmiennych.

## Migracja jest sekwencją zgodnych stanów

Przy zmianie API publicznej biblioteki najpierw zapewnij nową drogę, potem oznacz starą jako przestarzałą i dopiero według polityki SemVer usuń ją w wersji łamiącej kompatybilność. W aplikacji wdrażanej stopniowo wersje mogą współistnieć. Nowy serwer musi rozumieć dane tworzone przez stary, dopóki trwa okno zgodności. Zmiana schematu bazy i cofnięcie binarium mają różne skutki.

Stosuj migrację rozszerz–przełącz–usuń: dodaj nowe pole/format, obsłuż oba, przenieś odczyt i zapis, a dopiero później wycofaj stare. Unikaj jednoczesnego usunięcia pola i wdrożenia odbiorcy, który już go wymaga. Test zgodności powinien używać rzeczywistych reprezentatywnych danych poprzedniej wersji, a nie tylko nowych struktur Rust.

## Incydent kończy się po zweryfikowaniu naprawy

Najpierw ogranicz wpływ: wyłącz wadliwą funkcję, zmniejsz ruch albo przywróć zgodny artefakt. Następnie zbierz dane, odtwórz przyczynę i sprawdź poprawkę. Restart może przywrócić dostępność, ale nie ustala źródła wycieku pamięci. Raport po incydencie opisuje oś czasu, mechanizm awarii, warunki sprzyjające i działania z właścicielem. „Uważniej przeglądać kod” jest zbyt mało mierzalne.

Dług techniczny traktuj jako ryzyko z kosztem: brak testu kompatybilności, nieograniczona kolejka i nieudokumentowana zależność środowiskowa mają konkretne scenariusze awarii. Priorytet wynika z prawdopodobieństwa, wpływu i trudności odtworzenia. Każde działanie naprawcze powinno mieć kryterium akceptacji, np. test odrzucenia przeciążenia przed alokacją.

## Diagnostyka kompilatora

Nie naprawiaj ostrzeżeń migracyjnych zbiorowym `allow(warnings)`. Odczytaj klasę problemu i zmień najmniejszy fragment zachowujący semantykę. Gdy aktualizacja zmienia wybór metody traitu, porównaj typ odbiorcy i bounds. Gdy stara rewizja nie buduje się z nowym narzędziem, zapisz „nierozstrzygnięte” i odtwórz jej własne środowisko. Błąd budowania nie dowodzi regresji wykonania.

## Praktyka produkcyjna

Aktualizuj zależności małymi, opisanymi grupami i wykonuj testy kontraktu. Przechowuj poprzedni artefakt wraz z procedurą rollbacku i warunkami, w których jest on bezpieczny. Po zmianie kompilatora porównaj nie tylko testy funkcjonalne, lecz także ważny budżet opóźnień, pamięci lub rozmiaru. Ustal, kto usuwa tymczasowy kod zgodności; bez terminu adaptery migracyjne stają się kolejnym trwałym protokołem.

## Sprawdź, czy rozumiesz

1. Jak odróżnić błąd starego środowiska od badanego błędu?
2. Dlaczego cofnięcie binarium nie cofa migracji danych?
3. Co musi zawierać wykonywalne działanie po incydencie?

## Ćwiczenia

- `D04-1` — podstawowe: Wyjaśnij, czemu `Nierozstrzygnieta` nie może być potraktowana jako `Zla`. [Rozwiązanie](../rozwiazania/25_debugowanie_i_utrzymanie/02_regresje_migracje_i_incydenty.md#d04-1).
- `D04-2` — praktyczne: Ułóż migrację konfiguracji z pola `timeout_ms` na `deadline_ms`. [Rozwiązanie](../rozwiazania/25_debugowanie_i_utrzymanie/02_regresje_migracje_i_incydenty.md#d04-2).
- `D04-3` — pogłębione: Zaproponuj trzy działania po incydencie z wyczerpaniem puli bazy. [Rozwiązanie](../rozwiazania/25_debugowanie_i_utrzymanie/02_regresje_migracje_i_incydenty.md#d04-3).

## Źródła i granice weryfikacji

Narzędzie do regresji rustc: [cargo-bisect-rustc](https://rust-lang.github.io/cargo-bisect-rustc/). Ustalanie wersji grafu: [Cargo build: --locked](https://doc.rust-lang.org/cargo/commands/cargo-build.html). Opisana procedura utrzymania jest autorskim modelem pracy i nie wymaga uruchamiania narzędzi historycznych w testach kompendium.

## Powiązane tematy

- [Reprodukcja i debugger](01_reprodukcja_backtrace_i_debugger.md)
- [Release i rollback](../28_ci_cd_i_release_engineering/02_wydania_artefakty_i_rollback.md)
- [SemVer](../14_idiomy_wzorce_i_architektura/03_projektowanie_api_i_semver.md)
