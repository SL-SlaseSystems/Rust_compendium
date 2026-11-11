[← Spis treści](../../README.md)

# Rozwiązania: Clippy, rustfmt i linty

[Rozdział źródłowy](../../09_dokumentacja_testowanie_i_jakosc/03_clippy_rustfmt_i_linty.md).

## B12-1

~~~rust
#[must_use] fn poprawne(n:u32)->bool{n>0}
fn main(){assert!(poprawne(1));assert!(!poprawne(0));}
~~~

## B12-2

~~~rust
#[allow(clippy::upper_case_acronyms)] // publiczna nazwa pochodzi ze stabilnego formatu domeny
struct HTTP { kod: u16 }
fn main(){let odpowiedz=HTTP{kod:200};assert_eq!(odpowiedz.kod,200);}
~~~
Wyjątek ma wąski zakres. W nowym API lepiej dobrać nazwę zgodną z konwencją niż dodawać taki wyjątek.

## B12-3

Najpierw formatowanie wykrywa różnice stylu, następnie check/lint sprawdza aktywne typy i znane wzorce. Testy jednostkowe/integracyjne sprawdzają zachowanie, rustdoc przykłady i linki, a build wybranych targetów rzeczywiste linkowanie. Formatowanie nie sprawdza semantyki; check nie testuje uruchomienia i zwykle nie weryfikuje finalnego linkowania; lint nie jest dowodem braku UB; testy obejmują wybrane przypadki. Macierz MSRV/features/platform dobieraj do deklarowanego wsparcia, zamiast uznawać jeden build maksymalnej konfiguracji za całość.

