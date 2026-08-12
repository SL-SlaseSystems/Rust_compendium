[← Spis treści](../README.md)

# Testy dokumentacyjne i rustdoc

Komentarz `///` dokumentuje następny element, `//!` — element zawierający.
`cargo doc --open` generuje HTML dla crate’a i zależności.

## Przykład jako test

~~~rust
/// Dodaje podatek w punktach bazowych.
///
/// # Examples
///
/// ```
/// let brutto = z_podatkiem(10_000, 2300);
/// assert_eq!(brutto, 12_300);
/// ```
///
/// # Panics
///
/// Może wywołać panic przy przepełnieniu u64.
pub fn z_podatkiem(netto: u64, punkty_bazowe: u64) -> u64 {
    netto + netto * punkty_bazowe / 10_000
}

fn main() {
    assert_eq!(z_podatkiem(100, 1000), 110);
}
~~~

Rustdoc ukrywa wiersze zaczynające się od `# ` w renderowaniu, ale dołącza je
do kompilacji. To pozwala skrócić setup:

~~~text
/// ```
/// # use moja_biblioteka::Klient;
/// # let klient = Klient::testowy();
/// assert!(klient.zdrowy());
/// ```
~~~

## Rodzaje bloków

- `rust` — kompiluje i uruchamia;
- `no_run` — kompiluje bez uruchamiania;
- `compile_fail` — sukces, gdy kompilacja zostanie odrzucona;
- `should_panic` — oczekuje panic;
- `ignore` — pomija; używaj oszczędnie;
- `text` — nie jest kodem Rust.

`compile_fail` jest dobry do dokumentowania gwarancji typów:

~~~compile_fail
fn main() {
    let s = String::from("move");
    let t = s;
    println!("{s} {t}");
}
~~~

## Linki wewnętrzne

Intra-doc links, np. `[Vec]` lub `[modul::Typ::metoda]`, są sprawdzane przez
rustdoc. Lint `rustdoc::broken_intra_doc_links` warto ustawić na deny.
Dokumentuj re-exportowaną ścieżkę, którą ma widzieć użytkownik.

## Typowe sekcje

- `# Examples`;
- `# Errors` dla `Result`;
- `# Panics`;
- `# Safety` dla publicznego `unsafe fn`;
- `# Cancellation safety` dla operacji async, jeśli ma znaczenie.

Opis „co” bez „dlaczego” jest niewystarczający. Dokumentacja publiczna
powinna wyjaśniać ownership parametrów, koszt, side effects, porządek i
platformowe różnice.

## Prywatne elementy i cfg

`cargo doc --document-private-items` pomaga przeglądać architekturę. Elementy
wyłączone przez `cfg` nie pojawią się bez właściwej konfiguracji. Docs.rs
często buduje zestaw features określony w metadanych, więc sprawdzaj dokumenty
lokalnie w tej samej kombinacji.

## Powiązane tematy

- [Testy jednostkowe i integracyjne](01_testy_jednostkowe_i_integracyjne.md)
- [Komentarze i atrybuty](../02_podstawy_jezyka/05_operatory_komentarze_i_atrybuty.md)
- [`unsafe` i soundness](../zaawansowane/01_unsafe_i_soundness.md)
