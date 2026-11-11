[← Spis treści](../README.md)
<!-- status: expanded -->

# Closures i rodzina `Fn`

> Przykłady: **stable**, Rust 1.90.0, Edition 2024. Źródła sprawdzono 11 listopada 2026 r.

## Cele

Po tym rozdziale potrafisz:

- przewidzieć sposób przechwycenia danych na podstawie ciała closure;
- odróżnić przejęcie środowiska przez `move` od konsumpcji podczas wywołania;
- wybrać minimalny bound `FnOnce`, `FnMut` lub `Fn` dla callbacku;

## Model — środowisko jest wartością z prawami dostępu


Closure to anonimowa funkcja, która może przechwycić otoczenie. Kompilator
tworzy dla niej anonimową strukturę przechowującą przechwycone wartości.

## Inferencja i capture

~~~rust
fn main() {
    let prog = 10;
    let wieksze = |x: &i32| *x > prog;
    let wynik: Vec<_> = [5, 12, 20].iter().filter(|x| wieksze(x)).collect();
    assert_eq!(wynik, [&12, &20]);
}
~~~

Closure przechwytuje minimalnym wymaganym sposobem: przez `&T`, `&mut T` albo
wartość. Słowo `move` wymusza przejęcie bindingów do środka, lecz typy `Copy`
mogą zostać skopiowane.

~~~rust
fn main() {
    let tekst = String::from("dane");
    let dlugosc = move || tekst.len();
    assert_eq!(dlugosc(), 4);
}
~~~

`move` jest często konieczne dla wątku lub tasku, który może przeżyć bieżący
stos.

## `Fn`, `FnMut` i `FnOnce`

- `FnOnce` — wywołanie przez ten trait konsumuje obiekt closure; może oddać capture;
- `FnMut` — można wywoływać przez wyłączny dostęp do środowiska;
- `Fn` — można wywoływać przez współdzielony dostęp do środowiska.

Hierarchia zdolności jest odwrotna intuicyjnie: każde `Fn` spełnia też
`FnMut` i `FnOnce`, lecz nie odwrotnie.

~~~rust
fn powtorz<F>(ile: usize, mut akcja: F)
where
    F: FnMut(usize),
{
    for i in 0..ile {
        akcja(i);
    }
}

fn main() {
    let mut suma = 0;
    powtorz(4, |i| suma += i);
    assert_eq!(suma, 6);
}
~~~

~~~rust
fn wykonaj<F, T>(f: F) -> T
where
    F: FnOnce() -> T,
{
    f()
}

fn main() {
    let tekst = String::from("oddaj");
    let odzyskany = wykonaj(|| tekst);
    assert_eq!(odzyskany, "oddaj");
}
~~~

## Zwracanie i przechowywanie closures

`impl Fn(i32) -> i32` ukrywa jeden konkretny typ closure. `Box<dyn Fn(...)>`
pozwala przechowywać heterogeniczne closures kosztem alokacji i dynamic
dispatch.

~~~rust
fn dodaj(n: i32) -> impl Fn(i32) -> i32 {
    move |x| x + n
}

fn main() {
    let plus_dwa = dodaj(2);
    assert_eq!(plus_dwa(5), 7);
}
~~~

Async closure zwraca future i może mieć bardziej złożone relacje capture.
Przy API callbacków wybieraj najsłabszy wystarczający bound: `FnOnce` daje
wywołującemu największą swobodę.

## Reguły — capture i wywołanie to różne osie

`move` określa, jak closure pozyskuje dane, a rodzina `Fn` opisuje, co dzieje się przy wywołaniu. Closure `move || tekst.len()` posiada `String`, ale tylko go odczytuje, więc może implementować `Fn`. Closure `move || tekst` oddaje posiadany bufor i dlatego wywołanie konsumuje środowisko. Nie można powtórzyć takiego odczytu przez tę samą wartość closure.

Przeniesienie referencji nie przenosi referenta. Jeśli `r: &String` wskazuje lokalny tekst, `move || r.len()` nadal pożycza ten tekst. Nie staje się przez to `'static` i nie może swobodnie przeżyć właściciela. Przy zadaniu wymagającym `'static` przejmij posiadane dane albo uchwyt współwłasności, gdy właśnie taka semantyka jest potrzebna.

~~~rust
fn uruchom<F: FnOnce() -> String>(f: F) -> String { f() }
fn main() {
    let tekst = String::from("odpowiedź");
    let czytaj = move || tekst.len();
    assert_eq!(czytaj(), czytaj());

    let drugi = String::from("wynik");
    let oddaj = move || drugi;
    assert_eq!(uruchom(oddaj), "wynik");
}
~~~

Pierwsze środowisko posiada bufor i pozwala wielokrotnie go czytać. Drugie przejmuje inny bufor i przekazuje go do wyniku. Generyczna funkcja `uruchom` wymaga tylko jednego wywołania, więc bound `FnOnce` daje klientowi możliwość przekazania każdego z tych rodzajów zachowania, o ile zgadza się typ wyniku.

## Mutacja i inferencja

`FnMut` wymaga wyłącznego dostępu do środowiska wywołania, ale nie oznacza automatycznie, że callback mutuje dane przy każdym przebiegu. `Fn` pozwala wywoływać przez współdzieloną referencję; mutowalność wnętrza nadal może zmieniać stan przez `Cell`, `RefCell` lub blokadę. Wymaganie `Fn` nie jest dowodem czystości funkcji ani braku skutków ubocznych.

Typ parametrów closure jest wnioskowany z użyć i nie staje się generyczny dla kolejnych wywołań. Po ustaleniu `|x| x` jako funkcji dla `u32` nie można tym samym obiektem przyjąć potem `String`. Nazwana funkcja generyczna może być właściwym narzędziem, jeżeli potrzebujesz polimorfizmu typów.

Każde wyrażenie closure ma własny anonimowy typ, nawet gdy dwa ciała wyglądają identycznie. `impl Fn` w wyniku ukrywa jeden taki typ. Dwie gałęzie zwracające różne closures wymagają ujednolicenia reprezentacji albo przechwycenia parametru wyboru przez jedno wspólne ciało. `Box<dyn Fn>` umożliwia heterogeniczność, lecz nie jest obowiązkowy dla zwykłego przekazania callbacku.

## Async closures i rodzina `AsyncFn`

**stable** od Rust 1.85: `async || ...` tworzy asynchroniczne closure. Bound `F: AsyncFn() -> usize` opisuje callback, którego wywołanie daje future kończący się wartością `usize`. Future może pożyczać środowisko closure na czas wykonania; nie musi posiadać osobnej kopii wszystkich capture. To istotna różnica wobec prostego opisu `Fn() -> Fut` z jednym typem `Fut`, który często nie wyraża takiej zależności od pożyczki wywołania.

`AsyncFnMut` pozwala wywołać callback przez wyłączną pożyczkę, więc przyszłości pożyczającej mutowalne środowisko nie można swobodnie uruchomić ponownie równolegle. `AsyncFnOnce` konsumuje środowisko. Samo `move` nadal określa capture, a nie jednorazowość wywołania. Zwykłe wywołanie closure tylko tworzy future; wykonanie wymaga pollingu.

~~~rust
use std::{future::Future, ops::AsyncFn, pin::pin, task::{Context, Poll, Waker}};
async fn dwa<F: AsyncFn() -> usize>(f: F) -> usize {
    f().await + f().await
}
fn main() {
    let tekst = String::from("Rust");
    let odczyt = async move || tekst.len();
    let mut wynik = pin!(dwa(odczyt));
    let mut kontekst = Context::from_waker(Waker::noop());
    assert!(matches!(wynik.as_mut().poll(&mut kontekst), Poll::Ready(8)));
}
~~~

Jednorazowy poll wystarcza wyłącznie dlatego, że pokazane operacje nie oczekują na zdarzenia. `Waker::noop` nie jest wykonawcą I/O. Bezpośrednie używanie metod traitu `async_call` pozostaje odrębnie niestabilne; przykład korzysta ze stabilnej składni wywołania. Źródło: [AsyncFn](https://doc.rust-lang.org/std/ops/trait.AsyncFn.html), sprawdzone 11 listopada 2026 r.

## Diagnostyka kompilatora

Closure konsumujące przechwycony `String` przenosi siebie przy pierwszym wywołaniu. Druga próba daje E0382.

~~~compile_fail
fn main() {
    let tekst = String::from("jednorazowy");
    let oddaj = move || tekst;
    let _pierwszy = oddaj();
    let _drugi = oddaj();
}
~~~

Jeśli operacja ma zwracać niezależny tekst wielokrotnie, trzeba świadomie klonować bufor wewnątrz callbacku. Jeśli wystarczy odczyt, zmień wynik na liczbę albo inny niepożyczający rezultat. Przy błędzie „cannot borrow as mutable” sprawdź, czy closure implementuje `FnMut` i czy binding lub parametr funkcji jest oznaczony `mut`.

## Praktyka produkcyjna

API jednorazowej inicjalizacji zwykle powinno przyjmować `FnOnce`, a pętla z aktualizacją callbacku — `FnMut`. `Fn` wybieraj, gdy rzeczywiście potrzebujesz wywołań przez współdzielony dostęp. Nadmiernie mocny bound wyklucza poprawne zastosowania bez zwiększenia bezpieczeństwa protokołu.

Przechwycenie dużego obiektu może przedłużyć jego życie do zniszczenia callbacku, nawet jeśli ten nigdy nie zostanie wywołany. W kolejce zadań kontroluj rozmiar środowisk i anulowanie: usunięcie closure z kolejki powinno zwolnić przejęte zasoby, ale wcześniejsze skutki uboczne pozostają. Dla callbacków wywoływanych pod blokadą dokumentuj reentrancję i czas wykonania.

## Sprawdź, czy rozumiesz

1. Dlaczego closure z `move` może nadal implementować `Fn`?
2. Czy `Fn` oznacza brak mutacji jakiegokolwiek stanu?
3. Czy przejęcie `&T` przez `move` daje własność `T`?

## Ćwiczenia

- `A27-1` — podstawowe: napisz closure przechwytujące próg przez pożyczkę i sprawdzające trzy liczby [Rozwiązanie](../rozwiazania/06_kolekcje_iteratory_i_closures/04_closures_i_fn_traits.md#a27-1).
- `A27-2` — praktyczne: napisz `powtorz` z boundem `FnMut` i zlicz wywołania bez globalnego stanu [Rozwiązanie](../rozwiazania/06_kolekcje_iteratory_i_closures/04_closures_i_fn_traits.md#a27-2).
- `A27-3` — pogłębione: napisz fabrykę `impl Fn(i32) -> i32` wybierającą dodawanie lub odejmowanie przez jeden ukryty typ; wyjaśnij, czemu dwie niezależne closures w gałęziach mogą nie pasować [Rozwiązanie](../rozwiazania/06_kolekcje_iteratory_i_closures/04_closures_i_fn_traits.md#a27-3).

## Źródła i zakres stabilności

Capture oraz traits wywołania: [Reference: closure types](https://doc.rust-lang.org/reference/types/closure.html). Ograniczenia jednorazowego wywołania: [FnOnce](https://doc.rust-lang.org/std/ops/trait.FnOnce.html).

## Powiązane tematy

- [Iteratory](05_iteratory.md)
- [Wątki i scoped threads](../10_wspolbieznosc/01_watki_i_scoped_threads.md)
- [HRTB i `impl Trait`](../05_generics_traits_i_system_typow/05_hrtb_gat_rpit_i_impl_trait.md)
