[← Spis treści](../README.md)

# Zaawansowane makra proceduralne

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

## Powiązane tematy

- [Podstawy makr proceduralnych](../12_makra/03_makra_proceduralne.md)
- [Higiena makr deklaratywnych](../12_makra/02_higiena_fragmenty_i_repetition.md)
- [Profile, build scripts i publikowanie](../08_moduly_cargo_i_workspaces/04_profile_build_scripts_i_publikowanie.md)
