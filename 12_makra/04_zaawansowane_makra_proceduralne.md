[← Spis treści](../README.md)
<!-- status: expanded -->

# Zaawansowane makra proceduralne

## Cele

Po tym rozdziale potrafisz:

- zachować generics i wyprowadzić minimalne bounds ekspansji;
- zaprojektować kompatybilność atrybutów, ścieżek i diagnostyki;


Makro proceduralne jest małym kompilatorem: ma język wejściowy, analizę,
diagnostykę, generowanie oraz kontrakt zgodności.

## Architektura

Rozdziel:

1. wejściowy `TokenStream`;
2. parser do własnego AST;
3. walidację semantyczną niezależną od generowania;
4. model pośredni gotowy do emisji;
5. generowanie tokenów;
6. testy kompilacji i runtime.

Taki podział pozwala testować parser bez uruchamiania rustc. Crate’y
**third-party** `syn`, `quote` i `proc-macro2` są popularne, ale analizuj
koszt features `syn`, bo pełny parser zwiększa czas kompilacji.

## Zachowanie generics

Derive powinien zachować parametry, lifetimes, const generics i where clause.
Szkic z `syn`/`quote`, niekompilowany bez zależności:

~~~text
let input: syn::DeriveInput = syn::parse(input)?;
let name = &input.ident;
let (impl_generics, ty_generics, where_clause) =
    input.generics.split_for_impl();

quote! {
    impl #impl_generics MojTrait for #name #ty_generics #where_clause {
        // ...
    }
}
~~~

Nie dodawaj bezwarunkowo `T: Trait` do każdego parametru. Bound powinien
wynikać z użytych pól. Phantom parameter albo pole pomijane atrybutem może
nie potrzebować tego boundu.

## Helper attributes

Derive deklaruje dozwolone atrybuty:

~~~text
#[proc_macro_derive(Koduj, attributes(koduj))]
~~~

Parser powinien wykryć nieznane klucze, duplikaty i sprzeczne opcje.
Nazwij przestrzeń atrybutów tak, aby nie kolidowała z innymi makrami.

## Spans i diagnostyka

Błąd powinien wskazywać token użytkownika, który trzeba zmienić. W `syn`
`Error::new_spanned` wiąże komunikat z node’em, a `combine` agreguje kilka
błędów. `panic!` w makrze daje zwykle gorszy komunikat i informację
„procedural macro panicked”.

Generowane tokeny dziedziczą spans z interpolowanych elementów albo otrzymują
span call-site. Dobór wpływa na rozwiązywanie nazw. Nie ma prostego,
uniwersalnego „higienicznego identyfikatora” dla wszystkich celów.

## Ścieżka do runtime crate’a

Kod `::moja_biblioteka::Trait` psuje się, jeśli konsument zmieni nazwę
zależności. Strategie:

- re-export runtime pod ukrytą ścieżką i generuj przez nią;
- pozwól podać nazwę crate’a atrybutem;
- użyj crate’a **third-party** wykrywającego nazwę pakietu;
- wygeneruj kod niewymagający runtime’u.

Testuj zwykłą nazwę, alias i wywołanie makra wewnątrz samego crate’a.

## Tokeny kontra tekst

Nie buduj kodu przez `format!` i ponowne parsowanie stringu. `quote!` zachowuje
strukturę i spans. Literal użytkownika konstruuj przez typy `LitStr`,
`Literal` itp., aby escaping był poprawny.

## Testy UI

Crate **third-party** `trybuild` kompiluje fixtures i porównuje stderr.
Stabilność pełnego tekstu diagnostyki rustc jest ograniczona, więc snapshoty
mogą wymagać aktualizacji toolchainu. Testuj co najmniej:

- poprawne struktury i enumy;
- puste/tuple/unit variants;
- generics i where clauses;
- raw identifiers i visibility;
- błędny atrybut, duplikat i unsupported input;
- brak kolizji nazw pomocniczych;
- zachowanie wygenerowanego kodu.

## Bezpieczeństwo i deterministyczność

Proc macro działa podczas kompilacji. Nie wykonuj sieci, nie zależ od bieżącego
czasu ani nie czytaj przypadkowych plików projektu. Taki efekt psuje
reproducibility, cache i bezpieczeństwo łańcucha dostaw. Duże dane generuj w
build script tylko, gdy to rzeczywiście potrzebne.


## Model — generator utrzymuje publiczny kontrakt

Derive implementujący trait dla struktury generycznej musi rozróżnić parametry deklaracji implementacji od argumentów użytych w nazwie typu. `impl<T> Trait for Typ<T>` nie jest tekstowym powtórzeniem jednej listy w obu miejscach. Dochodzą lifetimes, const generics i istniejące `where`. API `split_for_impl` w **third-party** `syn` pomaga rozdzielić te elementy, ale nie wybiera automatycznie właściwych dodatkowych bounds. W dokumentacji `syn` 3.0.9 sprawdzonej 11 listopada 2026 metoda wymaga feature `printing`; sam typ `Generics` jest udostępniany przy `derive` lub `full`. Szkic wymaga dobrania features zależności i nie jest deklarowany jako wykonany test parsera.

Bound powinien wynikać z wykonywanej operacji na polu. Jeżeli generator wywołuje `Koduj` na `Vec<T>`, zobowiązanie dotyczy odpowiednio `Vec<T>: Koduj`; prostsze `T: Koduj` bywa wystarczające, ale nie zawsze minimalne. Pole pominięte, marker `PhantomData` lub pole z własną funkcją serializacji może nie wymagać takiego samego ograniczenia. Nadmiarowe bounds są widoczne w publicznym API.

Poniższa ręczna implementacja odpowiada jednemu możliwemu wynikowi generatora. Jest wykonywalnym testem zamierzonego kontraktu, nie testem parsera `syn` ani makra derive.

~~~rust
use std::marker::PhantomData;
trait Nazwany { fn nazwa() -> &'static str; }
struct Opis<'a, T, const N: usize> { dane: &'a [u8; N], marker: PhantomData<T> }
impl<'a, T, const N: usize> Nazwany for Opis<'a, T, N> {
    fn nazwa() -> &'static str { "Opis" }
}
struct BezTraitu;
fn main() {
    assert_eq!(Opis::<BezTraitu, 3>::nazwa(), "Opis");
    let x = Opis::<BezTraitu, 3> { dane: b"abc", marker: PhantomData };
    assert_eq!(x.dane.len(), 3);
}
~~~

Typ parametru nie implementuje `Nazwany`, lecz wynikowa implementacja go nie potrzebuje. Test z takim typem wykrywa nieuzasadnione ograniczenie, którego zwykły przykład z `u32` mógłby nie ujawnić. W prawdziwym derive sprawdź także istniejące `where` i pola o własnych typach skojarzonych.

Atrybuty pomocnicze są małym językiem. Określ dozwolone klucze, powtórzenia, konflikty, domyślne wartości i reguły wersjonowania. Nieznany klucz powinien być błędem, jeśli ciche pominięcie zmieniłoby format danych. Dodanie nowego znaczenia staremu, wcześniej ignorowanemu tekstowi może być zmianą semantyczną. Walidator powinien wskazywać span konkretnej opcji i zebrać niezależne błędy.

Ścieżka runtime’u musi uwzględniać aliasy zależności. Sam re-export w runtime crate nie pomaga, jeśli wygenerowana ścieżka nadal zaczyna się od nieistniejącej nazwy pakietu. Potrzebujesz uzgodnionego parametru ścieżki, wykrywania nazwy lub ekspansji z makra deklaratywnego korzystającego z `$crate`. Każdy wariant ma własny kontrakt i powinien być przetestowany u zewnętrznego konsumenta.

Snapshoty kodu pomagają zauważyć zmianę, ale nie dowodzą jakości generics, spójności traits ani poprawnego życia referencji. Testy UI, pozytywne kompilacje i asercje zachowania rozwiązują różne problemy. Wygenerowany `unsafe` wymaga takiego samego audytu jak ręcznie napisany; pochodzenie z makra nie zmniejsza odpowiedzialności.

## Diagnostyka kompilatora

Zbyt szerokie bounds ujawnią się często dopiero dla nietypowego konsumenta, na przykład markera bez derive. Błąd „missing lifetime specifier” może wynikać z zgubienia parametrów przez generator. `syn::Error` powinien kończyć się tokenami diagnostyki, nie `unwrap` na danych użytkownika. Stabilność pełnego stderr zależy od rustc; przy zmianie snapshotu sprawdź, czy zmieniła się tylko forma, czy rzeczywista przyczyna odrzucenia.

## Praktyka produkcyjna

Przy projektowaniu derive utrzymuj małe fixtures dla każdej obietnicy, w tym aliasu runtime’u, pustych generics i nieobsługiwanego atrybutu. Kontroluj rozmiar generowanego kodu oraz czas kompilacji na realistycznych typach. Zmiana domyślnego formatu serializacji może łamać dane mimo zachowanej kompilacji, więc wersjonuj również semantykę. Biblioteki `syn`, `quote`, `proc-macro2` i `trybuild` są **third-party**; przykłady wymagające ich grafu nie są tutaj zaliczane do wykonanych doctestów standardowej biblioteki.

## Sprawdź, czy rozumiesz

- Jak wykryć nadmiarowy bound na parametrze PhantomData?
- Dlaczego sam re-export nie naprawia dowolnego aliasu zależności?
- Co należy sprawdzić przy aktualizacji snapshotu stderr?

## Ćwiczenia

- `B27-1` — podstawowe: Zapisz ręczną implementację traitu dla typu z lifetime i const generic. [Rozwiązanie](../rozwiazania/12_makra/04_zaawansowane_makra_proceduralne.md#b27-1).
- `B27-2` — praktyczne: Zaprojektuj walidację atrybutu z kluczami rename i skip, odrzucając konflikty. [Rozwiązanie](../rozwiazania/12_makra/04_zaawansowane_makra_proceduralne.md#b27-2).
- `B27-3` — pogłębione: Przygotuj komplet testów wykrywających nadmiarowe bounds i błędną ścieżkę runtime’u. [Rozwiązanie](../rozwiazania/12_makra/04_zaawansowane_makra_proceduralne.md#b27-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [Reference: proc macro hygiene](https://doc.rust-lang.org/reference/procedural-macros.html#procedural-macro-hygiene)
- [syn Generics::split_for_impl](https://docs.rs/syn/latest/syn/struct.Generics.html#method.split_for_impl)

## Powiązane tematy

- [Podstawy makr proceduralnych](../12_makra/03_makra_proceduralne.md)
- [Higiena makr deklaratywnych](../12_makra/02_higiena_fragmenty_i_repetition.md)
- [Profile, build scripts i publikowanie](../08_moduly_cargo_i_workspaces/04_profile_build_scripts_i_publikowanie.md)
