[← Spis treści](../README.md)
<!-- status: expanded -->

# Projektowanie API i SemVer

## Cele

Po tym rozdziale potrafisz:

- ocenić zmianę API z perspektywy istniejącego konsumenta;
- rozróżnić zgodność typów, zachowania, MSRV i auto traits;


Dobre API sprawia, że najłatwiejsza droga jest poprawna. Typy opisują
ownership, możliwość błędu, współbieżność i invariants.

## Wejścia

- `&str` zamiast `&String`;
- `&[T]` zamiast `&Vec<T>`;
- `impl Into<String>`, gdy funkcja zawsze przejmie i skonwertuje tekst;
- `impl AsRef<Path>` dla wygodnego, pożyczonego argumentu ścieżki;
- generyczny iterator, gdy nie potrzebujesz konkretnej kolekcji.

~~~rust
fn suma<I>(dane: I) -> i64
where
    I: IntoIterator<Item = i64>,
{
    dane.into_iter().sum()
}

fn main() {
    assert_eq!(suma([1, 2, 3]), 6);
    assert_eq!(suma(vec![4, 5]), 9);
}
~~~

Generics zwiększają elastyczność i monomorfizację; nie parametryzuj każdego
argumentu „na zapas”.

## Wyniki

Zwracaj konkretny typ, jeśli konsumenci potrzebują jego możliwości. `impl
Iterator` ukrywa implementację przy jednym typie wyniku. `Box<dyn Trait>`
umożliwia runtime polymorphism i stabilniejszą granicę kosztem alokacji oraz
dispatch.

Unikaj zwracania referencji powiązanej z nieoczywistym argumentem. Posiadany
wynik jest czasem prostszym, choć droższym kontraktem.

## Ewolucja

Zmiany potencjalnie łamiące:

- usunięcie lub zmiana publicznego elementu;
- dodanie pola do struktury konstruowanej literałem;
- dodanie wariantu do wyczerpująco matchowanego enumu;
- dodanie wymaganej metody traitu;
- zaostrzenie bounds lub zmiana auto traits `Send`/`Sync`;
- zmiana panic, błędów, kolejności lub wydajności obiecanej dokumentacją.

`#[non_exhaustive]` zachowuje miejsce na warianty/pola kosztem ergonomii.
Prywatne pola i konstruktory dają większą swobodę niż publiczny layout.

## MSRV, edition i features

Edition nie jest wersją biblioteki i nie łamie automatycznie interoperacyjności
crate’ów. MSRV jest osobnym kontraktem. Feature flags powinny być addytywne,
nie zmieniać znaczenia istniejącego API i nie być ukrytą selekcją platformy.

## Bezpieczeństwo

Publiczna `unsafe fn` musi mieć sekcję `# Safety` z warunkami wywołującego.
Bezpieczna funkcja może używać `unsafe` wewnątrz tylko wtedy, gdy sama
utrzymuje wszystkie invariants dla dowolnego bezpiecznego wejścia.

Nie eksportuj surowego wskaźnika, jeśli można zwrócić wrapper z `Drop`,
lifetimes lub `NonNull`. Nie implementuj `Send`/`Sync` bez audytu.

## Minimalna powierzchnia

Każde `pub` jest zobowiązaniem SemVer. Re-exportuj stabilną fasadę, ukryj
moduły implementacyjne i nie eksponuj obcego typu bez potrzeby — może on
związać twoją wersję z SemVer zależności.


## Model — API to zestaw programów i zachowań, które obiecujesz

Zgodność nie sprowadza się do zachowania nazw funkcji. Konsument może konstruować strukturę literałem, dopasowywać enum wyczerpująco, przesyłać wynik między wątkami i polegać na kolejności iteratora. Zmiana prywatnego pola na `Rc` może usunąć `Send`, mimo że żadna jawna sygnatura się nie zmieniła. Dlatego oceniaj istniejące sposoby użycia, a nie sam tekst eksportów.

~~~rust
mod api {
    #[non_exhaustive]
    #[derive(Debug, PartialEq)]
    pub enum Blad { Brak, ZlyFormat }
    pub struct Konfiguracja { limit: usize }
    impl Konfiguracja {
        pub fn nowa(limit: usize) -> Result<Self, Blad> {
            if limit == 0 { Err(Blad::ZlyFormat) } else { Ok(Self { limit }) }
        }
        pub fn limit(&self) -> usize { self.limit }
    }
}
fn main() {
    let c = api::Konfiguracja::nowa(8).unwrap();
    assert_eq!(c.limit(), 8);
    assert_eq!(api::Konfiguracja::nowa(0).err(), Some(api::Blad::ZlyFormat));
}
~~~

Prywatne pole pozostawia miejsce na dalszą reprezentację. `non_exhaustive` wymaga zapasowego ramienia u zewnętrznego konsumenta; przykład jest jednym crate’em, więc nie demonstruje ograniczenia między crate’ami. Tę gwarancję trzeba sprawdzić testem integracyjnym lub oddzielnym pakietem. Dodanie `non_exhaustive` dopiero do wcześniej otwartego enumu również może łamać istniejący kod.

Elastyczne wejścia mają koszt. `impl Into<String>` jest wygodne przy przejmowaniu tekstu, ale dla `&str` zwykle oznacza alokację. `&str` jawnie pożycza i nie narzuca własności. Generyczny iterator może ograniczyć alokacje, lecz monomorfizuje funkcję dla różnych typów. Jeżeli gruba implementacja nie potrzebuje generyczności, mała generyczna otoczka może przekazywać prostą reprezentację do wspólnego kodu.

`impl Trait` ukrywa konkretny typ, ale nie usuwa wszystkich zobowiązań. Auto traits ukrytego typu mogą być obserwowalne przez bounds konsumenta. Dla zwracanego iteratora istotne są też czas życia, kolejność, leniwość i koszt każdego kroku. W Edition 2024 reguły przechwytywania parametrów przez return-position `impl Trait` wymagają uwagi przy migracji; zmiana przechwyceń może wpływać na pożyczanie.

MSRV jest deklaracją wsparcia, nie numerem edition. Podniesienie go podlega polityce projektu, którą trzeba jasno zakomunikować. Resolver może pomagać wybierać zależności, lecz dopiero test danym kompilatorem sprawdza realną konfigurację. Dane serializowane, format błędów maszynowych i zachowanie retry także mogą być publicznymi kontraktami, nawet jeśli nie widać ich w wygenerowanej liście itemów.

SemVer nie zastępuje oceny zmiany zachowania. Naprawa błędu może usunąć przypadkowo tolerowane wejście; opisz to i rozważ migrację. Nowa metoda domyślna traitu bywa potencjalnie kolizyjna z metodą innego traitu. Sformułowanie „dodawanie zawsze jest kompatybilne” jest za szerokie.

## Diagnostyka kompilatora

Błąd wyczerpującego `match` po dodaniu wariantu ujawnia brak planu ewolucji enumu. Utrata `Send` może pojawić się daleko od zmienionego pola, przy `spawn` konsumenta. Niejednoznaczne wywołanie metody po aktualizacji bywa skutkiem kolizji nowych elementów, a nie błędu importu u klienta. Narzędzia porównujące API pomagają, lecz nie rozpoznają całego kontraktu danych, opóźnień i skutków ubocznych.

## Praktyka produkcyjna

Utrzymuj małe programy konsumenckie dla najważniejszych zastosowań: minimalne features, oczekiwane auto traits, konstruowanie i obsługa błędów. Przed wydaniem czytaj diff dokumentacji i publicznych re-exportów. Nie eksportuj typów zależności bez powodu, bo wiążą politykę twojej wersji z jej zmianami. Dokumentuj gwarancje zamiast aktualnego algorytmu, jeśli implementację chcesz móc zmieniać. Testy kompatybilności powinny obejmować zapisane dane oraz ważne ścieżki behawioralne, nie tylko kompilację.

## Sprawdź, czy rozumiesz

- Jak prywatne pole może zmienić publiczny kontrakt Send?
- Dlaczego późniejsze dodanie non_exhaustive może być breaking change?
- Czy nowa domyślna metoda traitu zawsze jest bezpiecznym dodatkiem?

## Ćwiczenia

- `B32-1` — podstawowe: Zaprojektuj strukturę konfiguracji z prywatnym polem i konstruktorem. [Rozwiązanie](../rozwiazania/14_idiomy_wzorce_i_architektura/03_projektowanie_api_i_semver.md#b32-1).
- `B32-2` — praktyczne: Sprawdź statycznie oczekiwane Send i Sync publicznego wrappera. [Rozwiązanie](../rozwiazania/14_idiomy_wzorce_i_architektura/03_projektowanie_api_i_semver.md#b32-2).
- `B32-3` — pogłębione: Sklasyfikuj dodanie wariantu, prywatnego pola, wymaganego boundu i zmianę formatu danych. [Rozwiązanie](../rozwiazania/14_idiomy_wzorce_i_architektura/03_projektowanie_api_i_semver.md#b32-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [Cargo SemVer compatibility](https://doc.rust-lang.org/cargo/reference/semver.html)
- [Cargo rust-version](https://doc.rust-lang.org/cargo/reference/rust-version.html)
- [Edition 2024: impl Trait capture](https://doc.rust-lang.org/edition-guide/rust-2024/rpit-lifetime-capture.html)

## Powiązane tematy

- [Moduły i widoczność](../08_moduly_cargo_i_workspaces/01_moduly_sciezki_i_widocznosc.md)
- [Własne błędy](../07_obsluga_bledow/04_wlasne_bledy_i_api.md)
- [`unsafe` i soundness](../21_unsafe_soundness_i_model_pamieci/01_unsafe_i_soundness.md)
