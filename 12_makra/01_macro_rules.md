[← Spis treści](../README.md)
<!-- status: expanded -->

# `macro_rules!`

## Cele

Po tym rozdziale potrafisz:

- przewidzieć dopasowanie ramion i ewaluację argumentów;
- wybrać funkcję albo makro według rzeczywistej potrzeby składniowej;


Makro deklaratywne dopasowuje tokeny wejściowe do wzorców i rozwija je do
nowego kodu. Działa przed pełną analizą typów, dlatego nie zna wyników
inferencji.

## Pierwsze makro

~~~rust
macro_rules! maksimum {
    ($jedna:expr) => { $jedna };
    ($pierwsza:expr, $($reszta:expr),+ $(,)?) => {{
        let mut wynik = $pierwsza;
        $(
            let kandydat = $reszta;
            if kandydat > wynik {
                wynik = kandydat;
            }
        )+
        wynik
    }};
}

fn main() {
    assert_eq!(maksimum!(3, 9, 2,), 9);
    assert_eq!(maksimum!(7), 7);
}
~~~

Każde ramię ma matcher i transcriber. `expr` dopasowuje wyrażenie.
`$(...),+` oznacza co najmniej jedno powtórzenie rozdzielone przecinkiem, a
`$(,)?` opcjonalny końcowy przecinek.

Podwójny blok `{{ ... }}` ogranicza zakres nazw pomocniczych i sam jest
wyrażeniem.

## Wielokrotna ewaluacja

Makro tekstowo generujące `$x + $x` może wykonać argument z efektem ubocznym
dwa razy. Zwiąż wyrażenie lokalnie:

~~~rust
macro_rules! podwoj_raz {
    ($x:expr) => {{
        let wartosc = $x;
        wartosc + wartosc
    }};
}

fn main() {
    let mut n = 1;
    let wynik = podwoj_raz!({
        n += 1;
        n
    });
    assert_eq!((wynik, n), (4, 2));
}
~~~

To nadal przenosi wartość do bindingu i wymaga, aby dodanie było poprawne.
Makro nie ma własnej ogólnej sygnatury typów jak funkcja.

## Formy delimitera

Wywołania `m!()`, `m![]` i `m!{}` przekazują token tree. Semicolon zależy od
kontekstu oraz rodzaju rozwinięcia. Makro może generować wyrażenia, items,
patterns, statements lub types, ale wynik musi pasować do miejsca wywołania.

## Eksport i zakres

`macro_rules!` ma reguły zakresu tekstowego oraz ścieżkowego. Atrybut
`#[macro_export]` umieszcza makro w korzeniu crate’a publicznego. W kodzie
2018+ zwykle importuje się makro przez `use crate_name::macro_name`.
`#[macro_use]` jest starszym mechanizmem i powinien mieć uzasadnienie.

## Kiedy makro

Użyj funkcji lub traitu, jeśli wystarczą. Makro ma sens, gdy potrzebujesz
zmiennej liczby elementów składni, generowania items, dopasowania tokenów lub
API typu DSL. Koszt to gorsze komunikaty, dłuższa kompilacja i trudniejsze
narzędzia.


## Model — składnia wybierana przed typami

Kompilator próbuje ramiona w kolejności zapisu i wybiera pierwsze poprawne dopasowanie. Jeżeli wygenerowany kod potem nie przechodzi analizy typów, nie wraca do kolejnego ramienia jako alternatywnego overloadu. Makro nie wybierze więc wersji dla `String` i liczby na podstawie ich typów, jeśli obie pasują do `expr`. Taką decyzję koduj przez trait lub jawny znacznik składni.

Makro ma kontrakt własności taki jak wygenerowany kod. Lokalny binding może zapobiec wielokrotnej ewaluacji, ale nie sprawia, że wartość staje się `Copy`. Makro `podwoj_raz!` z poprzedniego przykładu nadaje się do wartości, dla których `wartosc + wartosc` jest poprawne; nie jest uniwersalną metodą klonowania. Przy niekopiowalnych danych trzeba świadomie wybrać pożyczanie albo klonowanie.

~~~rust
macro_rules! para {
    ($a:expr, $b:expr $(,)?) => {{
        let lewy = $a;
        let prawy = $b;
        (lewy, prawy)
    }};
}
fn main() {
    let mut kroki = Vec::new();
    let p = para!({ kroki.push(1); String::from("a") }, { kroki.push(2); 7 });
    assert_eq!(kroki, [1, 2]);
    assert_eq!(p, (String::from("a"), 7));
}
~~~

Każdy argument obliczany jest raz, w jawnej kolejności kolejnych instrukcji `let`. Makro akceptuje różne typy, bo wynik jest krotką, a nie wspólnym operatorem wymagającym jednego typu. Test sprawdza zarówno wynik, jak i efekty. Publiczne makro powinno dokumentować taką kolejność, jeżeli użytkownicy mogą polegać na niej przy efektach ubocznych.

Podwójne klamry tworzą blok będący wyrażeniem i izolują pomocnicze bindingi. Nie rozwiązują jednak wszystkich problemów higieny. Nazwy typów i funkcji mogą zależeć od miejsca wywołania; do helperów własnego crate’a używaj `$crate`, a do standardowych typów pełnych ścieżek tam, gdzie to uzasadnione. Publiczne makro nie może liczyć na import `Vec` lub `Result` o oczekiwanym znaczeniu u klienta.

Dobrze zaprojektowana składnia ma jednoznaczne separatory. Dopasowanie nie prowadzi dowolnego wyszukiwania w przód, więc zachłanne listy identyfikatorów bez separatora mogą być lokalnie dwuznaczne. Ramię błędu umieść po poprawnych formach, aby nie przechwytywało legalnego wejścia. Komunikat powinien wskazywać oczekiwany zapis, nie ogólne „błąd makra”.

Makro eksportowane jest publicznym API. Zmiana przyjmowanej składni, liczby ewaluacji albo generowanych nazw może łamać konsumentów mimo niezmienionej nazwy makra. Objętość rozwinięcia wpływa na czas kompilacji i komunikaty. Jeśli funkcja generyczna wyraża ten sam kontrakt, zwykle ma prostszą dokumentację i lepszą diagnostykę.

## Diagnostyka kompilatora

`no rules expected this token` wskazuje niedopasowaną składnię, nie brak implementacji traitu. Błąd operatora po ekspansji dotyczy typów wygenerowanego wyrażenia i nie uruchomi kolejnego ramienia. `local ambiguity` wymaga przeprojektowania separatorów lub fragmentów. Przy dużej ekspansji ogranicz przykład do jednego wywołania, a wynik obejrzyj narzędziem **third-party** lub ręcznie rozpisz prostą transkrypcję.

## Praktyka produkcyjna

Testuj pustą listę, jeden element, końcowy przecinek, efekty uboczne i argumenty przenoszone. Dla makra eksportowanego dodaj test z osobnego crate’a i z inną nazwą zależności. Nie otwieraj helperów jako przypadkowego API bez decyzji o zgodności. Generuj możliwie mało kodu, delegując powtarzalną logikę do zwykłych funkcji. Wtedy zmiany algorytmu nie mnożą się w każdym miejscu ekspansji, a użytkownik otrzymuje prostsze komunikaty.

## Sprawdź, czy rozumiesz

- Czy błąd typów w pierwszym dopasowanym ramieniu powoduje próbę następnego?
- Dlaczego jeden binding nie czyni argumentu `Copy`?
- Jak przetestować kolejność ewaluacji?

## Ćwiczenia

- `B24-1` — podstawowe: Napisz makro tworzące parę z opcjonalnym końcowym przecinkiem. [Rozwiązanie](../rozwiazania/12_makra/01_macro_rules.md#b24-1).
- `B24-2` — praktyczne: Sprawdź, że dwa argumenty z efektami wykonują się raz i w kolejności. [Rozwiązanie](../rozwiazania/12_makra/01_macro_rules.md#b24-2).
- `B24-3` — pogłębione: Dodaj celowy komunikat dla błędnej liczby argumentów i wyjaśnij wybór funkcji zamiast makra. [Rozwiązanie](../rozwiazania/12_makra/01_macro_rules.md#b24-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [Reference: macros by example](https://doc.rust-lang.org/reference/macros-by-example.html)

## Powiązane tematy

- [Higiena, fragmenty i repetition](02_higiena_fragmenty_i_repetition.md)
- [Makra proceduralne](03_makra_proceduralne.md)
- [Zaawansowane makra proceduralne](../12_makra/04_zaawansowane_makra_proceduralne.md)
