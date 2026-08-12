[← Spis treści](../README.md)

# Czym jest Rust

Rust jest kompilowanym, statycznie typowanym językiem ogólnego przeznaczenia,
zaprojektowanym z myślą o bezpieczeństwie pamięci, współbieżności i
przewidywalnej wydajności. Nie używa garbage collectora. Zamiast niego
kompilator kontroluje własność (ownership), pożyczanie (borrowing) oraz czas
życia referencji.

## Najważniejsza obietnica

Bezpieczny kod Rust ma nie dopuszczać między innymi do użycia wartości po
zwolnieniu pamięci, podwójnego zwolnienia, wiszących referencji, odczytu
niezainicjalizowanej pamięci i wyścigu danych między wątkami.

Nie oznacza to, że każdy program jest logicznie poprawny. Nadal można
zakleszczyć wątki, wywołać `panic!`, przepełnić stos albo napisać błędny
algorytm. Rust przesuwa dużą klasę błędów z wykonania do etapu kompilacji.

## Zero-cost abstractions

Abstrakcje wysokiego poziomu — iteratory, generics, closures czy RAII — mają
zwykle koszt porównywalny z ręcznie napisanym kodem niskopoziomowym.

~~~rust
fn suma_parzystych(liczby: &[i32]) -> i32 {
    liczby.iter().copied().filter(|n| n % 2 == 0).sum()
}

fn main() {
    assert_eq!(suma_parzystych(&[1, 2, 3, 4]), 6);
}
~~~

Łańcuch iteratorów nie tworzy tutaj kolekcji pośrednich. Jest leniwy i dopiero
`sum` konsumuje elementy. Kompilator może zmonomorfizować i zoptymalizować
całą operację.

## Gdzie Rust pasuje

Rust dobrze sprawdza się w narzędziach CLI, serwerach, bibliotekach
systemowych, silnikach, embedded, WebAssembly i komponentach, w których ważne
są opóźnienia oraz kontrola zasobów. Bywa mniej wygodny do bardzo szybkich
prototypów, gdy koszt modelowania ownership przewyższa korzyść, albo tam,
gdzie brakuje dojrzałych bibliotek domenowych.

## Kompilacja i filozofia pracy

W uproszczeniu kod przechodzi analizę składni i typów, borrow checking,
budowę reprezentacji pośredniej MIR, generowanie oraz optymalizację kodu
maszynowego. Cargo organizuje pakiet, zależności i wywołanie `rustc`.

- modeluj niepoprawne stany tak, aby nie dało się ich utworzyć;
- preferuj bezpieczne API, a `unsafe` zamykaj w małych granicach;
- pozwól typom opisać własność i możliwość błędu;
- najpierw mierz wydajność, potem optymalizuj.

## Powiązane tematy

- [Instalacja i toolchain](02_instalacja_i_toolchain.md)
- [Ownership, move i Copy](../03_pamiec_i_wlasnosc/02_ownership_move_i_copy.md)
- [Wydajność i zero-cost abstractions](../13_wzorce_i_architektura/05_wydajnosc_i_zero_cost.md)
- [`unsafe` i soundness](../zaawansowane/01_unsafe_i_soundness.md)
