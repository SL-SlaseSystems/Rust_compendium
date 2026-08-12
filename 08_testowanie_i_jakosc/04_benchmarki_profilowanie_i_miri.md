[← Spis treści](../README.md)

# Benchmarki, profilowanie i Miri

Optymalizacja zaczyna się od hipotezy i pomiaru. Benchmark odpowiada „jak
szybko?”, profiler — „gdzie znika czas?”, a narzędzia poprawności szukają
innych klas błędów.

## Benchmarki

Wbudowany harness `#[bench]` jest nightly. Na stable często używa się crate’a
**third-party** Criterion lub własnego binarium mierzącego cały scenariusz.
Dobry benchmark:

- ma realistyczne dane i rozgrzewkę;
- uniemożliwia optymalizatorowi usunięcie wyniku, np. przez `black_box`;
- mierzy osobno setup i właściwą operację;
- raportuje wariancję, nie pojedynczy czas;
- działa w kontrolowanym środowisku i profilu release.

`std::hint::black_box` jest dostępne na stable, ale stanowi barierę dla
optymalizatora w dobrej wierze, nie gwarancję kryptograficzną.

~~~rust
use std::hint::black_box;

fn suma(dane: &[u64]) -> u64 {
    dane.iter().sum()
}

fn main() {
    let dane = vec![1_u64; 100];
    assert_eq!(black_box(suma(black_box(&dane))), 100);
}
~~~

## Profilowanie

Narzędzie zależy od systemu: `perf` na Linuksie, Instruments na macOS,
Windows Performance Analyzer na Windows. Flame graph pokazuje stosy próbek,
nie przyczynę samą w sobie. Zachowaj symbole debug w zoptymalizowanym buildzie.

Sprawdzaj czas CPU i wall-clock, alokacje i kopie, cache misses, blokady,
I/O, rozmiar kodu oraz czas kompilacji.

## Sanitizery

AddressSanitizer, ThreadSanitizer, LeakSanitizer i inne integracje rustc
mogą wymagać nightly lub szczególnego targetu. Są uzupełnieniem, ponieważ
analizują wykonane ścieżki. Status oraz flagi sprawdzaj w aktualnym rustc Book.

## Miri

Miri interpretuje MIR i wykrywa wiele przypadków undefined behavior:
niepoprawne aliasing, out-of-bounds, use-after-free, część wycieków i
naruszeń alignment. Jest narzędziem nightly:

~~~text
rustup +nightly component add miri
cargo +nightly miri test
~~~

Miri jest wolniejsze, nie obsługuje całego FFI/systemu i nie dowodzi braku UB.
Jest szczególnie wartościowe dla małych testów bezpiecznych abstrakcji nad
`unsafe`.

## Analiza kodu

`cargo asm`, `cargo llvm-lines` i `cargo bloat` są narzędziami
**third-party** do oglądania assembly, udziału monomorfizacji i rozmiaru.
Wbudowane flagi `-Z` są nightly i mogą się zmieniać. Zanim zoptymalizujesz
assembly, potwierdź profil, target CPU i reprezentatywność benchmarku.

## Powiązane tematy

- [Wydajność i zero-cost abstractions](../13_wzorce_i_architektura/05_wydajnosc_i_zero_cost.md)
- [Monomorfizacja, MIR i LLVM](../zaawansowane/13_monomorfizacja_mir_llvm_i_optymalizacja.md)
- [`unsafe` i soundness](../zaawansowane/01_unsafe_i_soundness.md)
