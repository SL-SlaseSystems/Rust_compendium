[← Spis treści](../README.md)

# Borrow checker, Polonius i model pamięci

Borrow checker jest analizą konserwatywną: akceptacja ma gwarantować reguły,
ale odrzucenie nie dowodzi, że pomysł byłby niebezpieczny w każdym wykonaniu.

## Places, moves i loans

Analiza śledzi places, np. lokalną zmienną, pole i projekcję, ich inicjalizację
oraz move paths. Borrow tworzy loan. Dostęp jest odrzucany, gdy koliduje z
żywym loanem:

- zapis koliduje ze współdzielonym borrow;
- odczyt lub inny niezależny dostęp koliduje z wyłącznym borrow;
- move koliduje z borrow;
- referencja mogłaby przeżyć referent.

~~~rust
fn main() {
    let mut dane = vec![1, 2];
    let pierwsza = &dane[0];
    assert_eq!(*pierwsza, 1); // ostatnie użycie: loan może się skończyć
    dane.push(3);
    assert_eq!(dane, [1, 2, 3]);
}
~~~

Non-lexical lifetimes (NLL) kończą loan według przepływu i ostatniego użycia,
a nie zawsze na końcu bloku składniowego.

## Two-phase borrows

Wybrane niejawne mutowalne autoref w wywołaniach metod mogą mieć fazę
rezerwacji i aktywacji. Dzięki temu działa:

~~~rust
fn main() {
    let mut v = vec![10, 20];
    v.push(v.len());
    assert_eq!(v, [10, 20, 2]);
}
~~~

Receiver rezerwuje `&mut v`, potem `v.len()` wykonuje współdzielony odczyt,
a po obliczeniu argumentów mutowalna pożyczka jest aktywowana. Nie każda jawna
`&mut` korzysta z two-phase borrowing.

## Borrow checking nie jest modelem aliasingu

Borrow checker działa statycznie i może skracać lifetimes dla ergonomii.
Model pamięci określa runtime validity oraz UB także w `unsafe`. Kod może
przejść borrow checker i być UB przez:

- raw pointer do zwolnionej alokacji;
- utworzenie nieważnej referencji;
- złamanie aliasingu przez `UnsafeCell`/FFI;
- data race;
- zły discriminant, alignment lub ABI.

Z drugiej strony kod odrzucony przez borrow checker można czasem wyrazić
bezpiecznie przez zmianę modelu danych, indeksy, `split_at_mut`, enum lub
interior mutability.

## Polonius

Polonius to następna formulacja analizy borrow, modelująca origins jako zbiory
loans i ich przepływ przez punkty control-flow graph. Celem jest większa
precyzja, m.in. dla pożyczek zależnych od gałęzi.

Według oficjalnego opisu projektu, zweryfikowanego 2026-08-12, Polonius jest
prowizorycznie zintegrowany i można go eksperymentalnie uruchomić na nightly
flagą `-Zpolonius`, ale nie jest gotowy do powszechnego użycia ani podstawą,
na której należy opierać stable API.

~~~text
rustup toolchain install nightly
rustc +nightly -Zpolonius plik.rs
~~~

Nie traktuj „Polonius kiedyś zaakceptuje ten kod” jako gwarancji. Algorytm,
diagnostyka i harmonogram mogą się zmienić.

## Stacked Borrows, Tree Borrows i Miri

To modele operacyjne pomagające wykrywać błędy aliasingu. Miri może działać w
konkretnym modelu i znajdować UB na wykonanych ścieżkach. Modele badawcze mogą
się różnić i nie są pełną normatywną specyfikacją języka.

Konserwatywne zasady:

- twórz referencję dopiero, gdy możesz spełnić wszystkie jej gwarancje;
- trzymaj raw pointer z właściwym provenance;
- nie pisz przez raw pointer, gdy żywa shared reference zabrania mutacji;
- nie wyprowadzaj szerokiej provenance z pointera do pola;
- używaj `UnsafeCell` jako jedynej legalnej podstawy interior mutability.

## Stan specyfikacji

Rust Reference jawnie ostrzega, że lista UB nie jest wyczerpująca, dokładne
reguły aliasingu nie są ustalone, a formalny model całego języka nie istnieje.
Dokumentacja konkretnego API definiuje dodatkowe wymagania, których trzeba
przestrzegać.

## Powiązane tematy

- [Lifetimes](../03_ownership_i_pamiec/05_lifetimes.md)
- [Raw pointers, aliasing i provenance](02_raw_pointers_aliasing_i_provenance.md)
- [`unsafe` i soundness](01_unsafe_i_soundness.md)
