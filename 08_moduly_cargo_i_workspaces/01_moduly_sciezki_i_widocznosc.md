[← Spis treści](../README.md)
<!-- status: expanded -->

# Moduły, ścieżki i widoczność

## Cele

Po tym rozdziale potrafisz:

- odróżnić organizację plików od publicznego drzewa nazw;
- ochronić niezmienniki przez prywatność i stabilną fasadę;


Moduły tworzą hierarchię nazw i granice prywatności. Nie są tym samym co
pliki: deklaracja `mod` włącza moduł do drzewa crate’a, a plik jest tylko
jednym ze sposobów przechowywania jego treści.

## Drzewo modułów

~~~rust
mod domena {
    pub mod konto {
        #[derive(Debug)]
        pub struct Konto {
            pub id: u64,
            saldo: i64,
        }

        impl Konto {
            pub fn nowe(id: u64) -> Self {
                Self { id, saldo: 0 }
            }

            pub fn saldo(&self) -> i64 {
                self.saldo
            }
        }
    }
}

fn main() {
    let konto = domena::konto::Konto::nowe(7);
    assert_eq!((konto.id, konto.saldo()), (7, 0));
}
~~~

Elementy są prywatne domyślnie. Rodzic nie może dowolnie czytać prywatnych
elementów dziecka, ale dziecko widzi elementy przodków. Prywatne pole
uniemożliwia zewnętrzne skonstruowanie struktury literałem.

## Ścieżki

- `crate::` — korzeń bieżącego crate’a;
- `self::` — bieżący moduł;
- `super::` — rodzic;
- nazwa crate’a — korzeń zależności lub własnego crate’a w wybranych
  kontekstach.

`use` wprowadza krótszą nazwę do zakresu. Idiomatycznie importuje się typ lub
moduł, a funkcję często pozostawia z modułem dla kontekstu. Konflikty rozwiąż
przez `as`.

~~~rust
mod formaty {
    pub fn json() -> &'static str { "json" }
}

use formaty as fmt_danych;

fn main() {
    assert_eq!(fmt_danych::json(), "json");
}
~~~

## Warianty `pub`

- `pub` — publiczne od korzenia crate’a;
- `pub(crate)` — tylko bieżący crate;
- `pub(super)` — moduł rodzica;
- `pub(in crate::sciezka)` — wskazany moduł-przodek.

Wybieraj najmniejszą widoczność. `pub(crate)` jest dobrym narzędziem do
wewnętrznych interfejsów bez obietnicy dla konsumenta.

## Re-exports i prelude

`pub use wewnetrzny::Typ` buduje publiczną fasadę niezależną od układu
modułów. Dzięki temu można reorganizować implementację bez zmiany ścieżek
użytkownika. Prelude to moduł importowany globem w kontrolowanym miejscu;
nie umieszczaj w nim wszystkiego.

## Pliki w Edition 2018+

`mod siec;` może wskazywać `siec.rs` lub `siec/mod.rs`. Współczesny styl
preferuje zwykle `siec.rs` z podmodułami w `siec/`. Sam plik bez deklaracji
`mod` nie staje się częścią crate’a.


## Model — osiągalność jest częścią kontraktu

`pub` na elemencie nie oznacza automatycznie, że konsument może dotrzeć do niego przez dowolną ścieżkę. Wszystkie istotne segmenty ścieżki muszą być dostępne albo trzeba udostępnić publiczny re-export. Prywatny moduł może zawierać publiczny typ używany wewnętrznie i eksportowany pod krótszą nazwą. Pozwala to rozdzielić drzewo implementacji od drzewa obietnic dla użytkownika.

~~~rust
mod implementacja {
    pub struct Limit(u16);
    impl Limit {
        pub fn nowy(n: u16) -> Option<Self> { (n > 0).then_some(Self(n)) }
        pub fn wartosc(&self) -> u16 { self.0 }
    }
}
pub use implementacja::Limit;
fn main() {
    let limit = Limit::nowy(8).unwrap();
    assert_eq!(limit.wartosc(), 8);
    assert!(Limit::nowy(0).is_none());
}
~~~

Konsument ma korzystać z `Limit`, a nie z nazwy folderu implementacyjnego. Prywatne pole wymusza przejście przez konstruktor. Re-export nie otwiera dostępu do tego pola; widoczność typu i jego pól to oddzielne decyzje. Test jednostkowy umieszczony w module potomnym może widzieć prywatne elementy przodka, dlatego sam taki test nie potwierdza ergonomii publicznego interfejsu. Do tego służy także osobny test integracyjny.

`use` nie włącza pliku i nie buduje zależności w Cargo. Skraca ścieżkę do istniejącego elementu. `mod` deklaruje element w drzewie crate’a; kopiowanie tej samej deklaracji do `main.rs` i `lib.rs` buduje dwa oddzielne drzewa, a nie współdzielony moduł. W pakiecie z biblioteką i binarium binarium powinno zwykle importować bibliotekę po nazwie crate’a. To zapobiega duplikowaniu typów, statycznych wartości i testów.

Ograniczona widoczność musi wskazywać przodka. `pub(in crate::domena)` nie jest systemem list dostępu pozwalającym wskazać dowolny moduł sąsiadujący. Ułatwia dzielenie dużego subsystemu bez obietnicy dla całego crate’a. Rozszerzanie widoczności tylko po to, by uciszyć błąd importu, może niepotrzebnie otworzyć konstrukcję niepoprawnych obiektów.

Importy globowe są użyteczne w małym, kontrolowanym prelude oraz w testach, lecz utrudniają ustalenie pochodzenia metody lub typu. Dodanie nowego eksportu do zależności może wprowadzić konflikt nazw. Jawny import z aliasem daje czytelną diagnostykę i mniej zależy od przyszłego wzrostu interfejsu. Moduły nie zapewniają izolacji procesu ani uprawnień systemowych: prywatność jest sprawdzaną przez kompilator granicą dostępu do nazw.

## Diagnostyka kompilatora

`E0603` zwykle wskazuje element prywatny, a `E0616` prywatne pole. Sprawdź zamierzoną ścieżkę eksportu i konstruktor przed dopisaniem `pub`. `E0432` lub `E0433` może oznaczać brak deklaracji `mod`, błędny import albo zależność niezadeklarowaną w manifeście; to różne warstwy. Komunikat o dwóch niezgodnych typach o podobnej nazwie może wynikać z powtórnego włączenia tego samego pliku do dwóch crate’ów.

## Praktyka produkcyjna

Najpierw projektuj małą publiczną fasadę, a dopiero potem układaj pliki według wygody zespołu. Przeniesienie prywatnego modułu jest zwykle łatwiejsze od zmiany eksportowanej ścieżki. Kontroluj publiczne re-exporty, bo również są zobowiązaniem wersjonowania. Dla szerokiego API sprawdzaj dokumentację wygenerowaną tak, jak widzi ją konsument. Unikaj cyklicznej logiki między modułami nawet wtedy, gdy kompilator akceptuje wzajemne odwołania; brak cyklu w Cargo nie gwarantuje prostego kierunku odpowiedzialności wewnątrz crate’a.

## Sprawdź, czy rozumiesz

- Dlaczego publiczny typ wewnątrz prywatnego modułu może być dostępny przez re-export?
- Co się stanie po zadeklarowaniu tego samego modułu w `lib.rs` i `main.rs`?
- Dlaczego `pub(in ...)` musi wskazywać przodka?

## Ćwiczenia

- `B05-1` — podstawowe: Zamknij dodatni limit w strukturze z prywatnym polem i walidowanym konstruktorem. [Rozwiązanie](../rozwiazania/08_moduly_cargo_i_workspaces/01_moduly_sciezki_i_widocznosc.md#b05-1).
- `B05-2` — praktyczne: Ukryj implementacyjny moduł i udostępnij typ przez publiczną fasadę. [Rozwiązanie](../rozwiazania/08_moduly_cargo_i_workspaces/01_moduly_sciezki_i_widocznosc.md#b05-2).
- `B05-3` — pogłębione: Wyjaśnij i rozpisz drzewo plików biblioteki z cienkim binarium bez podwójnego `mod`. [Rozwiązanie](../rozwiazania/08_moduly_cargo_i_workspaces/01_moduly_sciezki_i_widocznosc.md#b05-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [Prywatność i widoczność](https://doc.rust-lang.org/reference/visibility-and-privacy.html)

## Powiązane tematy

- [Crates, pakiety i workspaces](02_crates_pakiety_i_workspaces.md)
- [Projektowanie API i SemVer](../14_idiomy_wzorce_i_architektura/03_projektowanie_api_i_semver.md)
- [Architektura aplikacji](../14_idiomy_wzorce_i_architektura/04_architektura_aplikacji_i_di.md)
