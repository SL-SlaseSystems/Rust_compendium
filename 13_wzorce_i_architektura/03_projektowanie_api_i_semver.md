[← Spis treści](../README.md)

# Projektowanie API i SemVer

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

## Powiązane tematy

- [Moduły i widoczność](../07_moduly_i_cargo/01_moduly_sciezki_i_widocznosc.md)
- [Własne błędy](../06_bledy/04_wlasne_bledy_i_api.md)
- [`unsafe` i soundness](../zaawansowane/01_unsafe_i_soundness.md)
