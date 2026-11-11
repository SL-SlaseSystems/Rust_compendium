[← Spis treści](../README.md)
<!-- status: expanded -->

# Przenośny rdzeń i weryfikacja wielu targetów

> Przykłady `rust`: biblioteka standardowa, Edition 2024. API narzędzi i bibliotek zewnętrznych opisano na podstawie źródeł sprawdzonych 11 listopada 2026 r.; szkice `text` wymagają wskazanego środowiska.

## Cele

Po tym rozdziale potrafisz:

- oddzielić algorytm od zegara, plików i transportu;
- stosować `cfg` bez pozostawiania niepoprawnego kodu w innej gałęzi;
- odróżnić test kompilacji od testu wykonania na targetach;

## Model — wspólne reguły, różne adaptery

Przenośność zaczyna się od kontraktu funkcji. Rdzeń przyjmuje dane, wykonuje obliczenie i zwraca wynik; adapter odpowiada za plik, żądanie HTTP, obiekt przeglądarki albo zegar urządzenia. Jeśli rdzeń sam otwiera pliki i odczytuje czas systemowy, testy muszą imitować znacznie więcej środowiska. Oddzielenie odpowiedzialności ułatwia równoczesne użycie tej samej logiki w CLI, serwerze i Wasm.

Nie wszystkie różnice platform są widoczne w typach. Inny może być rozmiar `usize`, kodowanie ścieżek, czułość nazw plików na wielkość liter i dostępność atomików. Bajty protokołu powinny mieć ustalone szerokości liczb i endianness. Nie serializuj natywnego layoutu struktury przez kopiowanie pamięci; padding i reprezentacja domyślna nie są formatem wymiany.

## Wstrzykiwanie środowiska zamiast globalnych odczytów

Czas jest wejściem do polityki, a nie ukrytą zależnością. Przykład modeluje termin jako licznik umownych jednostek. Adapter produkcyjny może przeliczać `Instant`, a test podaje konkretne liczby.

~~~rust
#[derive(Debug, PartialEq)]
enum Decyzja { Czekaj(u64), Wykonaj }

fn zaplanuj(teraz: u64, termin: u64) -> Decyzja {
    match termin.checked_sub(teraz) {
        Some(0) | None => Decyzja::Wykonaj,
        Some(pozostalo) => Decyzja::Czekaj(pozostalo),
    }
}

fn main() {
    assert_eq!(zaplanuj(10, 12), Decyzja::Czekaj(2));
    assert_eq!(zaplanuj(12, 12), Decyzja::Wykonaj);
    assert_eq!(zaplanuj(13, 12), Decyzja::Wykonaj);
}
~~~

Nie ma tutaj `sleep`, rzeczywistej godziny ani zależności od szybkości maszyny. `checked_sub` określa zachowanie po przekroczeniu terminu bez przepełnienia. W prawdziwej aplikacji ustal, czy potrzebujesz czasu monotonicznego do odmierzania okresu, czy kalendarzowego do znaczników zdarzeń. Cofnięcie zegara ściennego nie powinno nagle zwiększać budżetu timeoutu.

## `cfg` usuwa kod, `cfg!` daje wartość

Atrybut `#[cfg(...)]` włącza element wyłącznie przy spełnionym warunku. `cfg!` rozwija się do wartości logicznej, dlatego obie gałęzie zwykłego `if` nadal muszą być poprawne typowo. To częsta przyczyna błędu „działa na moim systemie”. `cfg!(windows)` nie sprawia, że nieistniejący na Unix symbol Windows staje się legalny.

Poniższy przykład pokazuje wybór implementacji, a nie obietnicę identycznego środowiska:

~~~rust
#[cfg(target_pointer_width = "64")]
fn szerokosc() -> u32 { 64 }
#[cfg(not(target_pointer_width = "64"))]
fn szerokosc() -> u32 { usize::BITS }

fn main() {
    assert_eq!(szerokosc(), usize::BITS);
}
~~~

Zamknij różnice w kilku adapterach zamiast rozrzucać warunki po logice domenowej. Gdy platforma nie obsługuje wymaganej możliwości, jawny błąd konfiguracji bywa lepszy niż pusta implementacja zwracająca sukces.

## Macierz sprawdza obietnice produktu

`cargo check --target ...` sprawdza kod i zależności dla targetu, lecz nie uruchamia programu. Pełny build dodaje linkowanie; wykonanie testów wymaga zgodnego runnera, emulatora albo rzeczywistej maszyny. Test Wasm w silniku WASI nie zastępuje testu integracji z JavaScriptem w przeglądarce. Utrzymuj osobną informację, które pary target–host naprawdę wykonano.

Features także są osią konfiguracji. Sprawdź minimalne features, domyślne oraz istotne kombinacje; `--all-features` nie zastępuje testów wyłączonych modułów. Dla bibliotek przenośnych kontroluj, czy przypadkowa zależność nie włączyła `std` przez inny pakiet workspace. Testuj bibliotekę również osobno, w konfiguracji obiecanej użytkownikowi.

## Diagnostyka kompilatora

Błąd „unresolved import” w gałęzi `if cfg!(...)` naprawia się właściwym atrybutem `#[cfg]` na imporcie lub elemencie. Błąd braku linkera nie jest błędem systemu typów; sprawdź target, toolchain C i SDK. Zapisuj `rustc -Vv` oraz pełne polecenie. Nie zmieniaj sygnatury rdzenia tylko po to, by ukryć brak adaptera platformowego.

## Praktyka produkcyjna

Utrzymuj tabelę: target, poziom wsparcia produktu, kompilacja, wykonanie, testy integracji. Każda deklaracja wsparcia powinna mieć właściciela i działający job CI. Wspólne pliki testowe niech zawierają także nie-ASCII, puste wejście, największy rozmiar i liczby przekraczające zakres 32-bitowego indeksu. Przy nowych targetach najpierw uruchom mały smoke test importów oraz alokacji, a dopiero potem całą aplikację.

## Sprawdź, czy rozumiesz

1. Dlaczego `cfg!(...)` nie ukrywa błędu importu?
2. Co pozostaje niesprawdzone po `cargo check --target`?
3. Dlaczego `usize` jest dobrym indeksem, ale słabym formatem protokołu?

## Ćwiczenia

- `D02-1` — podstawowe: Wypisz wyniki `zaplanuj` dla terminów wcześniejszego, równego i późniejszego. [Rozwiązanie](../rozwiazania/24_wasm_i_wieloplatformowosc/02_przenosny_rdzen_i_testy_targetow.md#d02-1).
- `D02-2` — praktyczne: Zaprojektuj interfejs rdzenia parsera używanego przez CLI i przeglądarkę. [Rozwiązanie](../rozwiazania/24_wasm_i_wieloplatformowosc/02_przenosny_rdzen_i_testy_targetow.md#d02-2).
- `D02-3` — pogłębione: Ułóż macierz dla Linux, Windows i przeglądarkowego Wasm oraz wskaż cel każdego joba. [Rozwiązanie](../rozwiazania/24_wasm_i_wieloplatformowosc/02_przenosny_rdzen_i_testy_targetow.md#d02-3).

## Źródła i granice weryfikacji

Reguły warunków: [Rust Reference: conditional compilation](https://doc.rust-lang.org/reference/conditional-compilation.html). Zakres sprawdzania: [Cargo build](https://doc.rust-lang.org/cargo/commands/cargo-build.html). Dobór macierzy i rozdzielenie adapterów są decyzjami architektonicznymi zilustrowanymi własnymi przykładami.

## Powiązane tematy

- [Host i guest](01_wasm_host_guest_i_wasi.md)
- [Features i cfg](../08_moduly_cargo_i_workspaces/03_zaleznosci_features_i_cfg.md)
- [CI i targety](../28_ci_cd_i_release_engineering/01_pipeline_ci_msrv_i_targety.md)
