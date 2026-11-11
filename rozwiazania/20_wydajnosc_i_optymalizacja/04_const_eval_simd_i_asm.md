[← Spis treści](../../README.md)

# Rozwiązania: Const, SIMD i asm

## C20-1

~~~rust
const fn suma(n: u32) -> u32 {
    assert!(n <= 100);
    let mut i = 0;
    let mut wynik = 0;
    while i < n { wynik += i; i += 1; }
    wynik
}
const _: () = assert!(suma(10) == 45);
fn main() { assert_eq!(suma(10), 45); }
~~~

W kontekście const `suma(101)` daje błąd ewaluacji. Zwykłe wywołanie z niepoprawnym argumentem może panikować podczas wykonania; publiczny parser powinien raczej zwracać Result i walidować wejście. Stała asercja nie analizuje przyszłych danych użytkownika.

## C20-2

~~~rust
fn suma(dane: &[u32]) -> u32 {
    let mut partie = dane.chunks_exact(4);
    let mut wynik = 0_u32;
    for p in &mut partie {
        let lokalna = p.iter().fold(0_u32, |a, &x| a.wrapping_add(x));
        wynik = wynik.wrapping_add(lokalna);
    }
    for &x in partie.remainder() { wynik = wynik.wrapping_add(x); }
    wynik
}
fn main() {
    assert_eq!(suma(&[]), 0);
    assert_eq!(suma(&[9]), 9);
    assert_eq!(suma(&[1, 2, 3, 4]), 10);
    assert_eq!(suma(&[1, 2, 3, 4, 5]), 15);
    assert_eq!(suma(&[u32::MAX, 1]), 0);
}
~~~

To bezpieczna implementacja referencyjna, bez gwarancji SIMD. Wariant wektorowy ma zachować te same przypadki i modularną arytmetykę; `remainder` nigdy nie jest pomijane ani odczytywane jako pełny wektor.

## C20-3

Przy wymaganiu powtarzalności bitowej odmów mechanicznego użycia `algebraic_add`, ponieważ dopuszczalna niedeterministyczność i zmiana kolejności obliczeń są sprzeczne z wymaganiem. Jeżeli produkt dopuszcza nowy kontrakt tolerancji, najpierw określ go oraz zbiór danych obejmujący anulowanie numeryczne, NaN, nieskończoności, bardzo małe i duże wartości. Następnie zmierz błąd i wydajność na targetach, nie twierdząc, że test zmienia słabszy kontrakt API w silniejszą gwarancję.

Zwykłe dodawanie u64 nie potrzebuje asm: `wrapping_add` ma jasny, przenośny kontrakt. Eksperyment assembly wymaga wskazanego problemu w codegen, profilu i różnicy zmierzonej w całym workloadzie. Audyt obejmuje rejestry, clobbery, pamięć, stos, flagi CPU i fallback. Jeżeli zysk jest niewidoczny albo utrzymanie targetów nie mieści się w budżecie, zachowaj implementację Rust.
