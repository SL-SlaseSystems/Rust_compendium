[← Spis treści](../README.md)
<!-- status: expanded -->

# Nightly, unstable i feature gates

## Cele

Po tym rozdziale potrafisz:

- oddzielić stabilność języka, API, edition i narzędzi;
- zaprojektować izolację eksperymentu bez deklarowania nieistniejących gwarancji;


Rust wydaje stable co około sześć tygodni, beta jako kandydat i nightly
codziennie. Edition jest osobnym mechanizmem zgodności i nie oznacza kanału.

## Wybór toolchainu

~~~text
rustup toolchain install stable beta nightly
cargo +stable test
cargo +nightly test
rustup override set nightly
rustup override unset
~~~

Lepszy od lokalnego override dla zespołu jest wersjonowany
`rust-toolchain.toml`:

To fragment manifestu lub konfiguracji; wymaga właściwego projektu i nie jest samodzielnym doctestem.

~~~text
[toolchain]
channel = "nightly-2026-08-01"
components = ["rustfmt", "clippy"]
profile = "minimal"
~~~

Przypięta data daje powtarzalność, ale wymaga regularnej, testowanej
aktualizacji ze względu na poprawki bezpieczeństwa.

## Feature gates

Niestabilna funkcja języka wymaga atrybutu crate:

~~~text
#![feature(type_alias_impl_trait)]

type Wynik = impl Iterator<Item = u32>;
~~~

Ten przykład jest **nightly** i nie jest testowany jako stable. Gate nie jest
obietnicą stabilizacji ani ostatecznej składni.

Przykładowe obszary nadal wymagające sprawdzenia w Unstable Book
(stan 2026-08-12):

- `type_alias_impl_trait`;
- `generic_const_exprs`;
- `trait_alias`;
- wybrane allocator APIs;
- liczne flagi `-Z` i compiler intrinsics.

Nie kopiuj tej listy jako wiecznej prawdy — sprawdź aktualny toolchain:

~~~text
rustc +nightly --version
rustc +nightly -Z help
rustup doc --toolchain nightly --path
~~~

## Unstable library features

API standard library oznaczone `#[unstable(feature = "...")]` także wymaga
odpowiedniego `#![feature(...)]`. Czasem stabilna alternatywa istnieje pod
inną nazwą. Sprawdź dokumentację wersji stable przed wprowadzeniem nightly.

## Ryzyko

- feature może zmienić składnię lub semantykę;
- nightly snapshot może mieć regresję;
- rustfmt i Clippy nightly zmieniają wyniki;
- zależność wymagająca nightly narzuca go całemu grafowi build;
- MSRV staje się niejasne;
- plugin/compiler-internal API ma szczególnie małą stabilność.

Nigdy nie ustawiaj `RUSTC_BOOTSTRAP`, aby obchodzić gates w produkcyjnym
projekcie. To wewnętrzny mechanizm bootstrappingu, nie wspierana ścieżka.

## Strategia izolacji

1. zamknij nightly za osobnym crate’em lub feature;
2. udostępnij stabilny fallback, jeśli możliwe;
3. przypnij toolchain z datą;
4. testuj aktualizację w CI;
5. śledź tracking issue i Unstable Book;
6. zapisz plan usunięcia gate po stabilizacji;
7. nie eksponuj niestabilnego typu w publicznym ABI.

## Migracja do stable

Po stabilizacji usuń `#![feature]`, podnieś MSRV do wersji stabilizującej,
uruchom testy stable i sprawdź release notes. Stabilna wersja może różnić się
od eksperymentalnej; sama zbieżność nazwy nie wystarcza.

## Kiedy nightly ma sens

- rozwój kompilatora i standard library;
- embedded/niestandardowy target wymagający konkretnej funkcji;
- eksperyment badawczy;
- narzędzie deweloperskie izolowane od artefaktu produkcyjnego;
- funkcja z jasno policzoną wartością i akceptowanym kosztem utrzymania.

Zwykła aplikacja nie potrzebuje nightly tylko dlatego, że „jest nowsze”.


## Model — cztery niezależne osie zgodności

Kanał wybiera zestaw dostępnych funkcji kompilatora. Edition wybiera spójny zestaw reguł składni i zgodności. `rust-version` komunikuje minimalne wspierane wydanie. Feature Cargo wybiera kod pakietu. Żadna z tych osi nie zastępuje pozostałych. `--features eksperyment` nie odblokuje `#![feature(...)]` na stable; może jedynie włączyć kod, który na tym kanale zostanie odrzucony.

Poniższy przykład używa stabilnego rozwiązania zamiast zależeć od nazwanego aliasu niejawnego typu. Funkcja ma jeden konkretny, ukryty typ iteratora, a odbiorca widzi jego kontrakt.

~~~rust
fn dodatnie(dane: &[i32]) -> impl Iterator<Item = i32> + '_ {
    dane.iter().copied().filter(|n| *n > 0)
}
fn main() {
    assert_eq!(dodatnie(&[-1, 0, 2, 4]).collect::<Vec<_>>(), [2, 4]);
}
~~~

Ten wzorzec nie pokrywa każdego zastosowania eksperymentalnego TAIT. Pokazuje jednak, że potrzeba ukrycia typu nie oznacza automatycznie potrzeby nightly. Alternatywa może zmieniać ergonomię, koszt alokacji albo możliwe ograniczenia, więc porównuj rzeczywisty kontrakt, a nie tylko podobną nazwę.

Lista niestabilnych funkcji jest migawką, nie katalogiem do zapamiętania. Weryfikuj konkretny feature w Unstable Book, dokumentacji API i tracking issue dla wybranego toolchainu. Historyczna data nightly w manifeście także nie dowodzi, że snapshot oraz wszystkie komponenty są dostępne dla twojego hosta. Nie opisuj hipotetycznej daty stabilizacji jako zobowiązania zespołu Rust.

Gate językowy i niestabilna metoda biblioteki mają różne miejsca pochodzenia, ale oba wymagają świadomego wyboru kanału. Część narzędzi, takich jak sanitizery albo flagi `-Z`, może być używana wyłącznie w osobnym zadaniu CI bez narzucania nightly użytkownikom biblioteki. To wartościowa izolacja: produkcyjne źródło przechodzi testy stable, a dodatkowy audyt korzysta z wyspecjalizowanego środowiska.

Fallback także wymaga testów. Jeśli ścieżka stable jest rzadko używana, potrafi stać się niepoprawna, mimo że kompilacja nightly nadal przechodzi. Publiczne typy nie powinny zmieniać tożsamości i podstawowych gwarancji między konfiguracjami w sposób zaskakujący konsumenta. W przeciwnym razie „opcjonalny eksperyment” wciąga całą aplikację w dodatkowy kontrakt wersjonowania.

Przypięcie snapshotu ogranicza zmienność, ale tworzy obowiązek aktualizacji. Rejestr decyzji powinien zawierać potrzebną funkcję, alternatywę stable, korzyść, koszt utrzymania, właściciela oraz kryterium wycofania gate. Bez takiego opisu eksperymentalna zależność łatwo pozostaje na lata po zniknięciu pierwotnej przyczyny.

## Diagnostyka kompilatora

`E0554` na stable oznacza niedozwolony atrybut `#![feature]`. `E0658` zwykle wskazuje użycie niestabilnej funkcji; sprawdź jej dokładną nazwę i stan w dokumentacji. Nie każda sugestia flagi z internetowego przykładu pasuje do twojej wersji. Błąd braku komponentu dla snapshotu jest problemem dystrybucji narzędzi, a nie składni programu. Zawsze zapisz pełny wynik `rustc --version --verbose`, target i polecenie odtwarzające problem.

## Praktyka produkcyjna

Dla biblioteki wspierającej stable testuj stable i zadeklarowane MSRV jako osobne zadania. Eksperymentalną konfigurację uruchamiaj dodatkowo, z jawnym przypięciem daty. Aktualizacja snapshotu powinna przechodzić testy, dokumentację i sprawdzenie wygenerowanych artefaktów. Nie używaj wewnętrznych obejść gate jako rozwiązania produkcyjnego. Po stabilizacji sprawdź finalną semantykę, usuń gate, dostosuj MSRV i upewnij się, że konsumenci nie potrzebują już eksperymentalnego kompilatora.

## Sprawdź, czy rozumiesz

- Dlaczego Edition 2024 nie odblokowuje wszystkich funkcji nightly?
- Jak korzystać z narzędzia nightly bez narzucania kanału konsumentom?
- Co powinien zawierać plan wycofania gate?

## Ćwiczenia

- `B09-1` — podstawowe: Zastąp potrzebę nazwania iteratora przez stabilne `impl Iterator` w wyniku funkcji. [Rozwiązanie](../rozwiazania/08_moduly_cargo_i_workspaces/05_nightly_unstable_i_feature_gates.md#b09-1).
- `B09-2` — praktyczne: Rozpisz macierz CI: MSRV, stable i osobne narzędzie eksperymentalne. [Rozwiązanie](../rozwiazania/08_moduly_cargo_i_workspaces/05_nightly_unstable_i_feature_gates.md#b09-2).
- `B09-3` — pogłębione: Przygotuj konkretny rejestr decyzji o nightly wraz z mierzalnym kryterium powrotu do stable. [Rozwiązanie](../rozwiazania/08_moduly_cargo_i_workspaces/05_nightly_unstable_i_feature_gates.md#b09-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [Unstable Book](https://doc.rust-lang.org/unstable-book/)
- [Rustup: toolchains](https://rust-lang.github.io/rustup/concepts/toolchains.html)

## Powiązane tematy

- [Instalacja i toolchain](../01_wprowadzenie_i_toolchain/02_instalacja_i_toolchain.md)
- [HRTB, GAT, RPIT i TAIT](../05_generics_traits_i_system_typow/05_hrtb_gat_rpit_i_impl_trait.md)
- [Clippy, rustfmt i linty](../09_dokumentacja_testowanie_i_jakosc/03_clippy_rustfmt_i_linty.md)
