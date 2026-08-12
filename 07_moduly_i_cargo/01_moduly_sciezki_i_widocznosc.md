[← Spis treści](../README.md)

# Moduły, ścieżki i widoczność

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

## Powiązane tematy

- [Crates, pakiety i workspaces](02_crates_pakiety_i_workspaces.md)
- [Projektowanie API i SemVer](../13_wzorce_i_architektura/03_projektowanie_api_i_semver.md)
- [Architektura aplikacji](../13_wzorce_i_architektura/04_architektura_aplikacji_i_di.md)
