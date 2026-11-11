[← Spis treści](../README.md)
<!-- status: expanded -->

# Operatory, komentarze i atrybuty

> Przykłady: **stable**, Rust 1.90.0, Edition 2024. Źródła sprawdzono 11 listopada 2026 r.

## Cele

Po tym rozdziale potrafisz:

- przewidzieć krótki obieg operatorów logicznych oraz skutki przeciążania operatora;
- odróżnić dokumentację publicznego kontraktu od komentarza implementacji;
- ograniczyć lint lokalnie i wyjaśnić różnicę między `cfg` a `cfg!`;

## Model — składnia, kontrakt i etap sprawdzania


## Operatory

Rust ma operatory arytmetyczne `+ - * / %`, porównania `== != < <= > >=`,
logiczne `&& || !`, bitowe `& | ^ << >>` oraz przypisania złożone, np.
`+=`. Operatory logiczne są leniwe.

~~~rust
fn main() {
    let x = 0b1010_u8;
    let y = 0b1100_u8;
    assert_eq!(x & y, 0b1000);
    assert_eq!(x | y, 0b1110);

    let mut n = 2;
    n <<= 3;
    assert_eq!(n, 16);
}
~~~

Własne typy mogą implementować wiele operatorów przez traits z `std::ops`,
np. `Add`. Nie można zmienić precedencji ani tworzyć nowych symboli.

Ważne operatory i formy języka:

- `&x` i `&mut x` — pożyczanie;
- `*p` — dereferencja;
- `a..b`, `a..=b` — zakresy;
- `?` — propagacja braku lub błędu;
- `as` — jawne rzutowanie;
- `.await` — zawieszenie future w kontekście async.

## Komentarze

`//` komentuje do końca wiersza, a komentarz blokowy obejmuje wiele wierszy.
Komentarze dokumentacyjne są przetwarzane przez rustdoc:

~~~rust
/// Zwraca kwadrat liczby.
///
/// # Examples
///
/// ```
/// assert_eq!(kwadrat(4), 16);
/// ```
pub fn kwadrat(x: i32) -> i32 {
    x * x
}

fn main() {
    assert_eq!(kwadrat(3), 9);
}
~~~

`//!` dokumentuje element nadrzędny, zwykle moduł lub crate. Dokumentacja
publicznego API powinna wyjaśniać błędy (`# Errors`), panic (`# Panics`) i
wymagania safety (`# Safety`).

## Atrybuty

Atrybut zewnętrzny `#[...]` dotyczy następnego elementu, a wewnętrzny
`#![...]` — elementu, w którym się znajduje.

~~~rust
#[derive(Debug, Clone, PartialEq, Eq)]
struct Uzytkownik {
    id: u64,
}

#[must_use = "wynik walidacji trzeba obsłużyć"]
fn poprawny_id(id: u64) -> bool {
    id > 0
}

fn main() {
    let a = Uzytkownik { id: 1 };
    assert_eq!(a.clone(), a);
    assert!(poprawny_id(a.id));
}
~~~

Popularne atrybuty to `derive`, `test`, `cfg`, `allow`/`warn`/`deny`,
`inline`, `repr` i `must_use`. Nie dodawaj `#[allow(...)]` bez komentarza,
dlaczego ostrzeżenie jest świadomie akceptowane.

## Precedencja i czytelność

Precedencja jest opisana w Reference, ale kod nie powinien zmuszać czytelnika
do jej pamiętania. Nawiasy są tanie. `rustfmt` ujednolica układ, lecz nie
naprawia niejasnego znaczenia wyrażenia.

## Reguły — ewaluacja i intencja operatora

`&&` oraz `||` wykonują prawy operand tylko wtedy, gdy wynik zależy od jego wartości. Warunek `indeks < dane.len() && dane[indeks] == 0` chroni dostęp przez kolejność sprawdzeń. Operator bitowy `&` takiej ochrony nie daje, nawet gdy oba operandy mają typ `bool`. Unikaj skutków ubocznych po prawej stronie warunku, jeśli dalsza logika zakłada, że wykonały się zawsze.

~~~rust
fn pierwszy_zero(dane: &[u8]) -> bool {
    !dane.is_empty() && dane[0] == 0
}
fn main() {
    assert!(!pierwszy_zero(&[]));
    assert!(pierwszy_zero(&[0, 7]));
    let bity = 0b1010_u8;
    assert_eq!(bity & (1 << 1), 2);
}
~~~

Maska `1 << 1` wybiera drugi bit licząc od zera. Nawiasy ujawniają intencję nawet wtedy, gdy precedencja już daje poprawny wynik. Przesunięcie wymaga sprawdzenia liczby pozycji względem szerokości typu; dla danych wejściowych wybierz `checked_shl`. Nie zakładaj, że każdy niepoprawny operand przesunięcia da ten sam efekt w profilach debug i release.

Przeciążanie operatora jest wywołaniem metody traitu, nie obietnicą taniej arytmetyki. `a + b` dla `String` konsumuje lewy `String` i dopisuje prawy `&str`; dla macierzy może wykonać alokację. Operator porównania powinien mieć semantykę spójną z kontraktem `PartialEq` lub `PartialOrd`. Własny typ powinien dokumentować również przepełnienie, jednostki oraz własność operandów.

## Dokumentacja oraz konfiguracja kodu

Komentarz `///` jest częścią dokumentacji elementu. Przykład powinien pokazywać realny import publicznego API; fragment osadzony przy funkcji `kwadrat` zakłada w prawdziwym crate'cie import tej funkcji. Sam blok demonstracyjny tego rozdziału sprawdza funkcję bez budowania odrębnej opublikowanej biblioteki. Komentarz `//` lepiej przeznaczyć na powód decyzji, którego nie widać w kodzie.

`#[cfg(...)]` usuwa element lub gałąź na etapie konfiguracji kompilacji. `cfg!(...)` zwraca stałe `bool`, ale zwykły `if cfg!(...)` nadal wymaga poprawnego typowania obu gałęzi. Dlatego kod używający API tylko unixowego ukrywaj atrybutem `cfg`, a nie samym warunkiem. `#[must_use]` uruchamia lint i może zostać jawnie zignorowane; nie jest mechanizmem wymuszającym transakcję ani obsługę błędu.

Atrybuty takie jak `repr` zmieniają kontrakt reprezentacji, a `inline` jest wskazówką optymalizacji. `derive` generuje implementacje zgodne z polami typu i może dodać wymagania wobec parametrów generycznych. Dobieraj je na podstawie semantyki API; lista atrybutów nie jest dekoracją każdego typu.

## `track_caller` i miejsce wywołania

`#[track_caller]` pozwala funkcji pomocniczej przekazać położenie wywołania do `std::panic::Location::caller()`. Bez atrybutu odczyt wewnątrz pomocnika wskazuje jego własne miejsce obserwacji. Z atrybutem diagnostyka może wskazać kod klienta, który podał błędny argument. To przydatne dla funkcji sprawdzających niezmienniki i konstruktorów pomocniczych, w których sama linia wewnętrznego `panic!` byłaby mało informacyjna.

~~~rust
use std::panic::Location;
#[track_caller]
fn skad() -> &'static Location<'static> { Location::caller() }
fn main() {
    let oczekiwana = line!() + 1;
    let miejsce = skad();
    assert_eq!(miejsce.line(), oczekiwana);
    assert_eq!(miejsce.file(), file!());
}
~~~

Jeżeli opakowujesz pomocnika kolejną funkcją i chcesz przekazać lokalizację dalej, ta warstwa także potrzebuje atrybutu. Zwykła warstwa bez atrybutu zatrzymuje propagację na swoim wywołaniu. Informacja jest wskazówką diagnostyczną, nie mechanizmem ustalania tożsamości użytkownika ani pełnym stosem wywołań. Koercja śledzonej funkcji do wskaźnika `fn` traci rzeczywiste miejsce klienta przez wygenerowany adapter. Nie dodawaj atrybutu do `main` ani funkcji o obcym ABI. Źródła: [Reference: track_caller](https://doc.rust-lang.org/reference/attributes/codegen.html#the-track_caller-attribute) i [Location::caller](https://doc.rust-lang.org/std/panic/struct.Location.html#method.caller), sprawdzone 11 listopada 2026 r.

## Diagnostyka kompilatora

Lint może zostać podniesiony do błędu. Tutaj wynik świadomie zaprojektowanego API został odrzucony, a `deny` sprawia, że przykład musi nie przejść kompilacji.

~~~compile_fail
#![deny(unused_must_use)]
#[must_use]
fn zatwierdz() -> bool { true }
fn main() { zatwierdz(); }
~~~

Naprawą jest obsłużenie wyniku, na przykład warunkiem albo propagacją błędu. `let _ = zatwierdz();` uciszyłoby lint, lecz byłoby poprawne tylko wtedy, gdy odrzucenie wyniku jest rzeczywiście zgodne z protokołem. Przy błędzie operacji na różnych typach nie dodawaj odruchowo `as`; sprawdź jednostki i wymagany trait.

## Praktyka produkcyjna

Włącz ostrzeżenia wcześnie, a wyjątków używaj w najwęższym zakresie. `allow` na cały crate ukrywa także przyszłe problemy. Jeżeli ważny jest wykrywalny powrót ostrzeżenia po zmianie implementacji, rozważ `#[expect(lint)]` z uzasadnieniem i odpowiednią polityką lintów. Nie obiecuj, że `deny(warnings)` będzie przechodziło na każdym przyszłym kompilatorze: nowe linty mogą zmienić wynik CI.

Dokumentuj warunki paniki i znaczenie błędów przy publicznych funkcjach. Przykład z `assert_eq!` w dokumentacji daje klientowi sprawdzalny kontrakt, ale testuje tylko pokazany przypadek. Przenośne API powinno mieć sprawdzane warianty konfiguracji platform, bo kod usunięty przez `cfg` nie jest testowany na bieżącym hoście.

## Sprawdź, czy rozumiesz

1. Kiedy `a & b` dla `bool` różni się od `a && b`?
2. Dlaczego `if cfg!(unix)` może nie ukryć błędu na Windows?
3. Czy `must_use` gwarantuje, że wynik nie zostanie zignorowany?

## Ćwiczenia

- `A09-1` — podstawowe: napisz test, w którym prawa strona `false && ...` nie zmienia licznika [Rozwiązanie](../rozwiazania/02_podstawy_jezyka/05_operatory_komentarze_i_atrybuty.md#a09-1).
- `A09-2` — praktyczne: napisz udokumentowaną funkcję `bit(n: u32) -> Option<u8>` używającą `checked_shl` [Rozwiązanie](../rozwiazania/02_podstawy_jezyka/05_operatory_komentarze_i_atrybuty.md#a09-2).
- `A09-3` — pogłębione: zaprojektuj lokalną politykę `must_use` dla wyniku walidacji; pokaż obsługę wyniku i wyjaśnij, kiedy jawne zignorowanie byłoby zasadne [Rozwiązanie](../rozwiazania/02_podstawy_jezyka/05_operatory_komentarze_i_atrybuty.md#a09-3).

## Źródła i zakres stabilności

Krótkie obiegi: [Reference: operator expressions](https://doc.rust-lang.org/reference/expressions/operator-expr.html#lazy-boolean-operators). Konfiguracja: [Reference: conditional compilation](https://doc.rust-lang.org/reference/conditional-compilation.html). Kontrakty lintów: [Reference: diagnostics](https://doc.rust-lang.org/reference/attributes/diagnostics.html).

## Powiązane tematy

- [Propagacja i operator `?`](../07_obsluga_bledow/02_propagacja_i_operator_question_mark.md)
- [Zależności, features i `cfg`](../08_moduly_cargo_i_workspaces/03_zaleznosci_features_i_cfg.md)
- [Testy dokumentacyjne i rustdoc](../09_dokumentacja_testowanie_i_jakosc/02_testy_dokumentacyjne_i_rustdoc.md)
