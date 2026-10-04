[← Spis treści](../README.md)

# Makra proceduralne

Makro proceduralne jest funkcją wykonywaną przez kompilator, która przyjmuje
i zwraca `proc_macro::TokenStream`. Działa na tokenach, nie na wynikach
type checkingu.

## Trzy rodzaje

1. derive: `#[derive(MojTrait)]`;
2. atrybutowe: `#[moj_atrybut(...)]`;
3. function-like: `sql!(...)`.

Crate proceduralny ma osobny typ:

~~~toml
[lib]
proc-macro = true
~~~

Nie może normalnie eksportować dowolnego runtime API. Typowy projekt ma
osobny crate makra i osobny crate biblioteki używanej przez wygenerowany kod.

## Minimalne sygnatury

To szkic pliku lib crate’a proceduralnego:

~~~text
use proc_macro::TokenStream;

#[proc_macro_derive(MojTrait, attributes(moj_trait))]
pub fn derive_moj_trait(input: TokenStream) -> TokenStream {
    // parse, validate, generate
}

#[proc_macro_attribute]
pub fn trace(args: TokenStream, item: TokenStream) -> TokenStream {
    // zachowaj item i wygeneruj otoczkę
}

#[proc_macro]
pub fn zapytanie(input: TokenStream) -> TokenStream {
    // własna składnia
}
~~~

## Parse, validate, generate

Popularne crate’y **third-party** `syn` i `quote` parsują składnię oraz
generują tokeny. `proc-macro2` ułatwia testowanie poza kontekstem kompilatora.
Nie są częścią standard library.

Walidacja powinna:

- odrzucać unsupported input z precyzyjnym span;
- łączyć niezależne błędy, aby użytkownik poprawił je naraz;
- zachować generics, lifetimes i where clauses;
- nie panikować na błędnym kodzie użytkownika;
- generować absolutne lub konfigurowalne ścieżki do runtime crate’a.

## Spans i higiena

Span wiąże token z miejscem źródłowym i wpływa na diagnostykę oraz rozwiązywanie
nazw. `Span::call_site` nie jest uniwersalnym wyborem. Wygenerowane nazwy
pomocnicze powinny minimalizować kolizje, a publiczne elementy mieć stabilny,
udokumentowany kontrakt.

## Testowanie

- zwykłe testy parsera i generatora tokenów;
- testy integracyjne używające makra;
- testy kompilacji poprawnych i błędnych przypadków, często przez crate
  **third-party** `trybuild`;
- snapshoty tylko jako pomoc, nie substytut asercji semantycznych.

Testuj puste generics, where clauses, raw identifiers, różne visibilities,
atrybuty użytkownika i błędne wejście.

## Koszt i bezpieczeństwo

Makro wykonuje kod podczas kompilacji z uprawnieniami procesu budowania.
Jest częścią łańcucha dostaw. Złożone makra zwiększają czas kompilacji, a ich
wygenerowane API podlega SemVer jak kod ręczny.

## Powiązane tematy

- [`macro_rules!`](01_macro_rules.md)
- [Zaawansowane makra proceduralne](../12_makra/04_zaawansowane_makra_proceduralne.md)
- [Build scripts](../08_moduly_cargo_i_workspaces/04_profile_build_scripts_i_publikowanie.md)
