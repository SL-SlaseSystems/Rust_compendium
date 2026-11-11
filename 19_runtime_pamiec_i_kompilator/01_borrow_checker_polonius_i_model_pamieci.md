[← Spis treści](../README.md)
<!-- status: expanded -->

# Borrow checker, Polonius i model pamięci

## Cele

Po tym rozdziale potrafisz:

- wskazać konflikt pożyczek na podstawie miejsca, ostatniego użycia i rodzaju dostępu;
- odróżnić analizę statyczną od kontraktu bezpieczeństwa wykonywanej operacji;
- ocenić status eksperymentu kompilatora bez opierania publicznego API na prognozie;

## Model — mechanizm i kontrakt

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

Według oficjalnego opisu projektu, zweryfikowanego ponownie 2026-11-11, Polonius jest
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

## Diagnostyka kompilatora

Zacznij od zaznaczenia miejsc: `dane`, `dane[0]`, `dane.len()`. Następnie zapisz, który dostęp potrzebuje wyłączności i gdzie następuje ostatnie użycie pożyczonej wartości. Ważność obiektu nie oznacza braku konfliktu: wektor może nadal istnieć, lecz `push` może zmienić jego alokację i unieważnić referencję do elementu.

~~~compile_fail
fn main() {
    let mut dane = vec![1, 2];
    let pierwsza = &dane[0];
    dane.push(3);
    println!("{pierwsza}");
}
~~~

Błąd E0502 wiąże współdzieloną pożyczkę z późniejszym użyciem w `println!` i wyłącznym dostępem przy `push`. Przeniesienie `println!` przed `push` skraca potrzebny okres pożyczki. Jeżeli potrzebujesz tylko liczby, skopiuj `dane[0]` do `i32`; jeżeli potrzebujesz później znaleźć obiekt, przechowuj stabilny identyfikator zamiast referencji do miejsca w realokowalnej kolekcji. `clone` całego wektora nie jest domyślnym rozwiązaniem problemu jednego odczytu.

Kompilator rozumie rozłączność zwykłych pól struktury, lecz dwa indeksy slice nie są automatycznym dowodem rozłączności. `split_at_mut` wyraża ten dowód w kontrakcie biblioteki. Przestawienie danych tak, aby funkcja przyjmowała tylko potrzebne pole, ogranicza też przypadkowo szerokie pożyczki `&mut self`. Nie dodawaj `RefCell` jedynie po to, aby ukryć niezrozumiany konflikt: wtedy część naruszeń zostanie przeniesiona do panic podczas wykonania.

Two-phase borrow nie jest ogólną zasadą przestawiania kolejności obliczeń. Jawne `&mut v` w argumencie zwykłej funkcji może kolidować z późniejszym `v.len()`. Bezpieczną naprawą jest obliczenie długości wcześniej. Zakres mechanizmu to szczegół analizy rustc opisany w [Two-phase borrows](https://rustc-dev-guide.rust-lang.org/borrow-check/two-phase-borrows.html), sprawdzony 2026-11-11; reguł dla wybranych niejawnych pożyczek nie rozszerzaj na dowolny kod.

## Praktyka produkcyjna

Przy złożonym błędzie zbuduj minimalny przykład, zachowując istotny przepływ sterowania. Zamiana referencji na indeks może naprawić analizę, ale indeks musi pozostać poprawny po usunięciu lub przestawieniu elementów. Klucz generacyjny może wykrywać ponowne użycie slotu, za cenę dodatkowej pamięci i walidacji. Zmiana modelu danych ma więc konsekwencje funkcjonalne, nie tylko kompilacyjne.

Analiza NLL dotyczy użycia referencji; nie obiecuje wcześniejszego wykonania destructora właściciela. Jeżeli zasób taki jak guard mutexu ma być zwolniony przed kosztowną operacją, zakończ jego zakres albo jawnie go zniszcz. Nie wnioskuj z krótkiej pożyczki, że plik, alokacja lub blokada też już zostały zwolnione.

Raportując błąd kompilatora, zapisz wersję `rustc`, edycję, target, features i pełny komunikat. Wypróbowanie nightly jest eksperymentem porównawczym, a nie zobowiązaniem do zmiany minimalnej wspieranej wersji biblioteki. Aktualny opis [statusu Poloniusa](https://rust-lang.github.io/polonius/current_status.html), sprawdzony 2026-11-11, nadal oznacza funkcję jako eksperymentalną. Nie przypisuj całej różnicy diagnostyki jednemu projektowi bez sprawdzenia wydania i flag.

Przy `unsafe` sprawdzaj dokumentację konkretnego API: akceptacja programu przez borrow checker nie analizuje całego obcego kodu ani nie potwierdza ważności raw pointera. Stan niepełnej specyfikacji opisuje [Rust Reference](https://doc.rust-lang.org/reference/behavior-considered-undefined.html), sprawdzone 2026-11-11. Test Miri pomaga znaleźć kontrprzykład, ale nie zastępuje niezmiennika i dowodu dla wszystkich bezpiecznych wywołań.

## Sprawdź, czy rozumiesz

- Dlaczego ostatnie użycie referencji i koniec życia właściciela to różne zdarzenia?
- Kiedy `split_at_mut` wnosi informację, której nie daje porównanie dwóch indeksów?
- Co wolno wywnioskować z odrzucenia programu przez konserwatywną analizę?

## Ćwiczenia

- `C09-1` — podstawowe: Napraw przykład E0502 na dwa sposoby: zmień kolejność użycia i skopiuj wartość. Wyjaśnij, kiedy semantyka obu wersji się różni. [Rozwiązanie](../rozwiazania/19_runtime_pamiec_i_kompilator/01_borrow_checker_polonius_i_model_pamieci.md#c09-1).
- `C09-2` — praktyczne: Napisz funkcję zwiększającą pierwszy i ostatni element niepustego slice bez jednoczesnego indeksowania przez dwa &mut. Obsłuż długości 0 i 1. [Rozwiązanie](../rozwiazania/19_runtime_pamiec_i_kompilator/01_borrow_checker_polonius_i_model_pamieci.md#c09-2).
- `C09-3` — pogłębione: Oceń trzy twierdzenia: przechodzi borrow checker więc brak UB; Miri nie zgłosiło błędu więc API jest sound; nightly akceptuje przykład więc będzie akceptowany na stable. Uzasadnij każdy werdykt. [Rozwiązanie](../rozwiazania/19_runtime_pamiec_i_kompilator/01_borrow_checker_polonius_i_model_pamieci.md#c09-3).

## Powiązane tematy

- [Lifetimes](../03_ownership_i_pamiec/05_lifetimes.md)
- [Raw pointers, aliasing i provenance](../21_unsafe_soundness_i_model_pamieci/02_raw_pointers_aliasing_i_provenance.md)
- [`unsafe` i soundness](../21_unsafe_soundness_i_model_pamieci/01_unsafe_i_soundness.md)
