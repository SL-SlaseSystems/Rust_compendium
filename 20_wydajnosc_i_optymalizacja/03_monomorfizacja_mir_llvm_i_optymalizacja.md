[← Spis treści](../README.md)
<!-- status: expanded -->

# Monomorfizacja, MIR, LLVM i optymalizacja

## Cele

Po tym rozdziale potrafisz:

- powiązać generics z liczbą instancji i kosztem codegen;
- wyjaśnić częściową inicjalizację przez semantykę drop, nie przez przypuszczenia o assembly;
- dobrać analizę MIR lub assembly bez traktowania jej jako stabilnego formatu API;

## Model — mechanizm i kontrakt

Model potoku pomaga wyjaśnić komunikaty, czas kompilacji i wynikowy kod, ale
szczegóły rustc nie są stabilnym API.

## Uproszczony potok

1. lexing i parsing tworzą AST;
2. expansion rozwija makra i część atrybutów;
3. name resolution wiąże ścieżki;
4. lowering tworzy HIR;
5. type checking i trait solving ustalają typy;
6. THIR/MIR przedstawiają sterowanie oraz miejsca;
7. borrow checking działa głównie na MIR;
8. monomorfizacja wybiera konkretne instancje generics;
9. codegen przekazuje IR do LLVM lub innego backendu;
10. linker tworzy artefakt.

Kolejność jest uproszczeniem i ewoluuje. Nie opieraj build scriptu na
wewnętrznym formacie HIR/MIR.

## Monomorfizacja

~~~rust
#[inline(never)]
fn podwoj<T>(x: T) -> T
where
    T: std::ops::Add<Output = T> + Copy,
{
    x + x
}

fn main() {
    assert_eq!(podwoj(2_u32), 4_u32);
    assert_eq!(podwoj(3_u64), 6_u64);
}
~~~

Kompilator może wygenerować osobne instancje dla `u32` i `u64`. Daje to
static dispatch i optymalizację, ale zwiększa codegen. Linker i LLVM mogą
scalać identyczne funkcje; wynik zależy od profilu i targetu.

Techniki kontroli bloat:

- przenieś niegeneryczny rdzeń za cienki wrapper;
- użyj trait object na zimnej granicy;
- ogranicz liczbę kombinacji const generics;
- analizuj `cargo llvm-lines` i `cargo bloat` (**third-party**);
- nie wymieniaj static dispatch bez pomiaru.

## MIR

MIR jest control-flow graph z locals, places, rvalues, statements i
terminators. Upraszcza wiele konstrukcji wysokiego poziomu. Na MIR działają
m.in. borrow checking, drop elaboration, const evaluation i optymalizacje.

Przydatne polecenia diagnostyczne:

~~~text
rustc --emit=mir plik.rs
rustc --emit=llvm-ir -O plik.rs
rustc --emit=asm -O plik.rs
~~~

Flagi `-Z dump-mir` i `-Z unpretty` są nightly oraz wewnętrzne. Format może
zmienić się bez kompatybilności.

## Drop elaboration

Kompilator dodaje drop flags i ścieżki cleanup, aby zniszczyć tylko
zainicjalizowane pola po move, early return lub unwind. To tłumaczy, dlaczego
częściowe przeniesienie i `MaybeUninit` są skomplikowane. Optymalizator może
usunąć niewidoczne operacje, ale obserwowalne `Drop` musi zachować semantykę.

## LLVM i optymalizacje

LLVM wykonuje inline, vectorization, dead-code elimination, scalar replacement
i wiele transformacji. Wynik zależy od:

- `opt-level`, LTO i codegen units;
- target triple oraz `target-cpu`/`target-feature`;
- widoczności ciał zależności;
- informacji aliasing wynikającej z referencji;
- panic/unwind i overflow checks;
- profilu PGO.

UB pozwala optymalizatorowi zakładać, że niedozwolona ścieżka nigdy nie
występuje. Kod z UB może „działać” w debug i zmienić zachowanie w release.

## Inline

`#[inline]` jest sugestią i częścią metadanych dla zależnych crate’ów.
`#[inline(always)]` nadal nie jest absolutną gwarancją i może zwiększyć
rozmiar. `#[inline(never)]` jest pomocne w benchmarku/analizie, ale nie jest
semantyczną barierą przed wszystkimi transformacjami.

## Analiza assembly

Porównuj funkcję w realnym profilu, zapobiegaj usunięciu wyniku przez
`black_box` i patrz na cały hot path. Liczba instrukcji sama nie opisuje
wydajności: ważne są latency, throughput, cache, branch prediction i calls.

## Cienki wrapper i wspólny rdzeń

Funkcja generyczna wykonująca dużo formatowania może powielić rozległe ciało dla wielu typów wejścia, mimo że po konwersji wszystkie przypadki pracują na `&str`. Ogranicz generyczność do granicy. To kompromis: zyskujesz mniej instancji dużego rdzenia, ale dodatkowe wywołanie lub mniej informacji o konkretnym typie może ograniczyć inline.

~~~rust
#[inline(never)]
fn rdzen(tekst: &str) -> usize {
    tekst.bytes().filter(|b| !b.is_ascii_whitespace()).count()
}
fn policz<T: AsRef<str>>(dane: T) -> usize { rdzen(dane.as_ref()) }
fn main() {
    assert_eq!(policz("a b"), 2);
    assert_eq!(policz(String::from("c d e")), 3);
}
~~~

Wrapper może mieć odrębne instancje dla `&str` i `String`, lecz cięższa logika ma jeden niegeneryczny punkt wejścia. `inline(never)` ułatwia oglądanie tego przykładu, ale nie stanowi trwałej obietnicy liczby symboli. Zmierz rozmiar sekcji kodu i czas rzeczywistej ścieżki; nie porównuj samej liczby nazw w tabeli symboli. Mechanizm zbierania instancji opisuje [rustc-dev-guide: monomorphization](https://rustc-dev-guide.rust-lang.org/backend/monomorph.html), sprawdzony 2026-11-11.

## Diagnostyka kompilatora

Komunikat moved value powstaje z reguł języka przed końcową optymalizacją; optymalizator nie może „oddać” przeniesionej `String`, nawet jeśli jej bajty fizycznie pozostały w pamięci. Podobnie brak wywołania konstruktora w assembly nie dowodzi, że konstruktor logicznie się nie wykonał: jego skutek mógł zostać włączony do innej operacji.

Przy częściowym move kompilator śledzi inicjalizację pól. Zwykła struktura pozwala przenieść jedno pole i korzystać z pozostałego, lecz użycie całej struktury może zostać odrzucone. Typ z własnym `Drop` ma dodatkowe ograniczenia, ponieważ destructor powinien dostać poprawny obiekt. `ManuallyDrop` i `MaybeUninit` przekazują część odpowiedzialności autorowi; nie są ogólną naprawą błędu move.

Polecenia `--emit` oglądają reprezentację dla konkretnego wejścia, wersji i opcji. Rozróżniaj stabilną dostępność flagi od stabilności formatu wyjścia. Analizator parsujący prywatne szczegóły MIR powinien przypiąć toolchain i być gotowy na zmiany. Potok opisany w [overview rustc](https://rustc-dev-guide.rust-lang.org/overview.html), zweryfikowanym 2026-11-11, jest modelem implementacji, a nie rozszerzeniem gwarancji języka.

## Praktyka produkcyjna

Zbadaj trzy oddzielne problemy: długi build, duże binarium i powolne wykonanie. Ten sam generyczny helper może wpływać na każdy inaczej. `dyn Trait` na rzadko wywoływanej granicy może ograniczyć kombinacje instancji, ale dodaje pośrednie wywołanie i zwykle utrudnia inline. Dla małego zbioru wariantów enum może zachować jawny dispatch, za cenę wspólnego typu i dopasowania. Rozdziel decyzję architektoniczną od mikrooptymalizacji.

Porównuj czysty build i incremental osobno, z tym samym target directory oraz kontrolą cache zależności. Zmiana `codegen-units` może pomagać runtime’owi, a szkodzić iteracji deweloperskiej. LTO zwiększa dostępność kodu do optymalizacji między jednostkami, lecz koszt linkowania i zużycie pamięci rosną. Zapisz osobne budżety CI oraz programu, zamiast przyjmować wszystkie najagresywniejsze flagi.

Kod z UB pozwala kompilatorowi zakładać brak niedozwolonych zdarzeń. Nie oznacza to, że można przewidzieć konkretną optymalizację na podstawie jednego przebiegu debug. Jeśli wariant unsafe przyspiesza dlatego, że przypadki niepoprawne zostały wyłączone z kontraktu, porównaj go z bezpieczną wersją przy tych samych dozwolonych danych. Zmniejszenie zestawu gwarancji użytkownika nie jest darmowym przyspieszeniem tej samej funkcji.

Przechowuj benchmark i mały przykład wykazujący powód przyjęcia nietypowego rozwiązania. Po aktualizacji kompilatora wynik może się zmienić. `inline(always)` dodawane wszędzie zwiększa presję na cache instrukcji i koszt kompilacji; każdy atrybut powinien odpowiadać na obserwowaną sytuację. Liczba instrukcji jest wskazówką, ale kolejka pamięci, zależności między instrukcjami i przewidywanie gałęzi decydują o rzeczywistym czasie.

## Sprawdź, czy rozumiesz

- Dlaczego liczba instancji generycznych nie musi być liczbą końcowych symboli?
- Co zachowuje semantyka drop, gdy LLVM usuwa lokalną alokację?
- Jakie oddzielne miary zbierzesz przed zastąpieniem generycznej granicy przez `dyn`?

## Ćwiczenia

- `C12-1` — podstawowe: Wskaż instancje wrappera policz w przykładzie oraz część wspólną. Wyjaśnij, dlaczego nie obiecujemy dokładnie trzech symboli w binarium. [Rozwiązanie](../rozwiazania/20_wydajnosc_i_optymalizacja/03_monomorfizacja_mir_llvm_i_optymalizacja.md#c12-1).
- `C12-2` — praktyczne: Przepisz funkcję generyczną przyjmującą AsRef<[u8]> tak, aby walidację nagłówka wykonywał rdzeń na &[u8]. Dodaj dwa rodzaje wejścia. [Rozwiązanie](../rozwiazania/20_wydajnosc_i_optymalizacja/03_monomorfizacja_mir_llvm_i_optymalizacja.md#c12-2).
- `C12-3` — pogłębione: Zaplanuj eksperyment zastąpienia generics przez dyn na zimnej granicy pluginów. Uwzględnij czas builda, rozmiar, p99 i rollback decyzji. [Rozwiązanie](../rozwiazania/20_wydajnosc_i_optymalizacja/03_monomorfizacja_mir_llvm_i_optymalizacja.md#c12-3).

## Powiązane tematy

- [Wydajność i zero-cost abstractions](../20_wydajnosc_i_optymalizacja/01_wydajnosc_i_zero_cost.md)
- [Benchmarki i profilowanie](../20_wydajnosc_i_optymalizacja/02_benchmarki_profilowanie_i_miri.md)
- [Borrow checker i model pamięci](../19_runtime_pamiec_i_kompilator/01_borrow_checker_polonius_i_model_pamieci.md)
