[← Spis treści](../README.md)
<!-- status: expanded -->

# Benchmarki, profilowanie i Miri

## Cele

Po tym rozdziale potrafisz:

- oddzielić pomiar czasu od dowodzenia poprawności;
- wyeliminować koszt setupu i usunięcie pracy przez optymalizator z prostego benchmarku;
- dobrać profiler, Miri albo sanitizer do konkretnego podejrzenia;

## Model — mechanizm i kontrakt

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

## Porównanie dwóch wariantów

Benchmark jest eksperymentem, więc potrzebuje pytania. „Wariant B zmniejsza czas parsowania typowego rekordu o co najmniej 10% bez zwiększenia alokacji” jest sprawdzalne. „B ma mniej linii” nie jest hipotezą wydajności. Rozdziel dane gorące i zimne, krótkie i długie, poprawne i błędne. Parser odrzucający wejście wcześnie może wygrać wyłącznie dlatego, że workload nie obejmuje normalnej ścieżki.

~~~rust
use std::hint::black_box;
use std::time::Instant;
fn zlicz(dane: &[u8]) -> usize {
    dane.iter().filter(|&&b| b == b'a').count()
}
fn main() {
    let dane = vec![b'a'; 4096];
    let start = Instant::now();
    let mut kontrola = 0_usize;
    for _ in 0..100 {
        kontrola += black_box(zlicz(black_box(&dane)));
    }
    let czas = start.elapsed();
    assert_eq!(kontrola, 409_600);
    let _obserwacja = (czas, black_box(kontrola));
}
~~~

To wykonywalny przykład konstrukcji pomiaru, nie wiarygodny wynik naukowy ani zastępstwo harnessu. Bufor powstaje przed timerem, wejście i wynik przechodzą przez `black_box`, a suma kontrolna potwierdza wykonanie oczekiwanej pracy. Pojedynczy przebieg nie szacuje wariancji. Właściwy benchmark musi powtarzać pomiar i dobrać czas próbkowania do rozdzielczości zegara. `black_box` działa best-effort i nie gwarantuje zachowania każdej instrukcji; potwierdza to [jego dokumentacja](https://doc.rust-lang.org/std/hint/fn.black_box.html), sprawdzona 2026-11-11.

Dla dwóch wariantów utrzymuj tę samą politykę overflow i błędów. Generowanie losowych danych w mierzonym fragmencie może ukryć zysk parsera. Z kolei stały mały bufor wielokrotnie czytany z cache może nie reprezentować plików produkcyjnych. Zmierz zarówno koszt funkcji, jak i całego scenariusza, gdzie alokacja lub I/O rzeczywiście należą do zadania.

## Diagnostyka kompilatora

`#[bench]` oraz `extern crate test` wymagają nightly; błąd na stable nie oznacza uszkodzenia instalacji. Dla stable wybierz własny binarny harness lub bibliotekę **third-party**, z osobną konfiguracją benchmarku. Flagi `-Z` także nie są stabilnym interfejsem. Nie kopiuj ich do obowiązkowego polecenia budowania biblioteki bez oznaczenia wymaganego kanału.

Kompilator może ostrzec o nieużywanym wyniku, ale brak ostrzeżenia nie dowodzi, że optymalizator zachował pracę. Przypisanie do `_` może wystarczyć do usunięcia całego obliczenia. Wątpliwy wynik bliski zeru sprawdź w wygenerowanym kodzie i przez obserwowalną sumę kontrolną, a nie zwiększaj arbitralnie liczby miejsc po przecinku.

## Praktyka produkcyjna

Profilowanie próbkowe odpowiada, które stosy były aktywne w próbkach. Szeroki fragment wykresu może oznaczać koszt funkcji lub sumę jej wywołań; rozróżniaj czas własny i łączny. Wysoki wall-clock przy niskim CPU sugeruje oczekiwanie, lecz przyczyną może być I/O, lock, scheduler lub zewnętrzna usługa. Połącz profil CPU z pomiarem blokad, alokacji i trace żądania.

Nie porównuj Miri z natywnym release jako dwóch implementacji wydajnościowych. Miri interpretuje wykonanie i kontroluje wiele wymagań bezpieczeństwa, co zmienia koszt o rzędy wielkości. Uruchamiaj małe, celowane testy pustych zakresów, ZST, panic przy częściowej inicjalizacji i destrukcji. Bieżące możliwości oraz ograniczenia są w [repozytorium Miri](https://github.com/rust-lang/miri), zweryfikowanym 2026-11-11. Wybrany model aliasingu i wykonane ścieżki nadal ograniczają wniosek.

Sanitizer dobierz do podejrzenia: ASan szuka problemów pamięci, TSan wyścigów danych, a MSan niezainicjalizowanych odczytów. Wsparcie platform, runtime’ów i instrumentacji obcego kodu sprawdź w [Unstable Book](https://doc.rust-lang.org/unstable-book/compiler-flags/sanitizer.html), zweryfikowanym 2026-11-11. Nie uruchamiano tu tych narzędzi. Dla FFI brak instrumentacji biblioteki C może pozostawić część błędów niewidocznych.

Raport wyniku powinien zawierać wersję kompilatora, CPU, system, target, profil, próbki danych, liczbę powtórzeń i rozrzut. W CI rozważ próg praktycznie istotnej regresji i kontrolowany runner; współdzielona maszyna potrafi generować fałszywe alarmy. Poprawę wynoszącą 1% przy rozrzucie 8% oznacz jako nierozstrzygniętą, a nie sukces.

## Sprawdź, czy rozumiesz

- Co zmieni wniosek, gdy setup zajmuje 90% mierzonego czasu?
- Dlaczego profiler CPU może nie pokazać przyczyny powolnego zapytania sieciowego?
- Czy brak błędu ASan lub Miri uprawnia do usunięcia komentarzy SAFETY?

## Ćwiczenia

- `C11-1` — podstawowe: Wyjaśnij błąd benchmarku wywołującego czystą funkcję na stałych danych i odrzucającego wynik. Podaj poprawkę obu stron pomiaru. [Rozwiązanie](../rozwiazania/20_wydajnosc_i_optymalizacja/02_benchmarki_profilowanie_i_miri.md#c11-1).
- `C11-2` — praktyczne: Zaprojektuj porównanie parserów dla rekordów 32 B i 32 KiB, poprawnych i błędnych. Oddziel setup i podaj metryki. [Rozwiązanie](../rozwiazania/20_wydajnosc_i_optymalizacja/02_benchmarki_profilowanie_i_miri.md#c11-2).
- `C11-3` — pogłębione: Usługa ma wysoki p99, mały czas CPU i dużo czekających tasków. Ułóż plan obserwacji oraz powiedz, jaką rolę mają profiler, benchmark, TSan i Miri. [Rozwiązanie](../rozwiazania/20_wydajnosc_i_optymalizacja/02_benchmarki_profilowanie_i_miri.md#c11-3).

## Powiązane tematy

- [Wydajność i zero-cost abstractions](../20_wydajnosc_i_optymalizacja/01_wydajnosc_i_zero_cost.md)
- [Monomorfizacja, MIR i LLVM](../20_wydajnosc_i_optymalizacja/03_monomorfizacja_mir_llvm_i_optymalizacja.md)
- [`unsafe` i soundness](../21_unsafe_soundness_i_model_pamieci/01_unsafe_i_soundness.md)
