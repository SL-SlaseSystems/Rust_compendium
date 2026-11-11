[← Spis treści](../README.md)
<!-- status: expanded -->

# Const evaluation, SIMD, asm i kontrakt numeryczny

## Cele

Po tym rozdziale potrafisz:

- wymusić obliczenie oraz asercję w czasie kompilacji bez mylenia ich z optymalizacją runtime;
- porównać autowektoryzację, portable SIMD i targetowe intrinsics;
- spisać zobowiązania asm oraz rozpoznać zmianę kontraktu liczb zmiennoprzecinkowych;
- ocenić wymagania wersji i własności bufora formatowania liczb.

## Model — Najpierw semantyka, potem miejsce wykonania

Ewaluacja stałych (constant evaluation, CTFE) oblicza wyrażenie w trakcie kompilacji. `const fn` pozwala użyć funkcji w takim kontekście, lecz wywołanie tej funkcji ze zwykłej funkcji nadal może wykonać się podczas działania programu. Optymalizator może policzyć prosty wynik wcześniej bez `const fn`; to możliwość optymalizacji, a nie semantyczne wymuszenie. Reguły i ograniczenia opisuje [Reference: const evaluation](https://doc.rust-lang.org/reference/const_eval.html), sprawdzone 2026-11-11.

**Stable, zgodne z Rust 1.90:** tabela generowana przez `const fn`, asercja stała i inline const nie wymagają nightly.

~~~rust
const fn kwadraty() -> [u16; 16] {
    let mut wynik = [0; 16];
    let mut i = 0;
    while i < wynik.len() {
        wynik[i] = (i * i) as u16;
        i += 1;
    }
    wynik
}
const TABELA: [u16; 16] = kwadraty();
const _: () = assert!(TABELA[15] == 225);
fn main() {
    let puste: [Option<String>; 4] = [const { None }; 4];
    assert!(puste.iter().all(Option::is_none));
    assert_eq!(TABELA[3], 9);
}
~~~

Pętla wykonuje się w stałym, znanym zakresie. Tabela nie jest budowana z pliku konfiguracyjnego i nie wymaga inicjalizacji przez pierwszy request. Inline `const { None }` ocenia osobny element powtórzenia, dzięki czemu tablica może zawierać typ niebędący `Copy`. Blok const może korzystać z odpowiednio dostępnych parametrów generycznych, lecz nie przechwytuje dowolnej lokalnej zmiennej runtime. Zobacz [const blocks](https://doc.rust-lang.org/reference/expressions/block-expr.html#const-blocks), sprawdzone 2026-11-11.

Asercja stała sprawdza konfigurację i typy znane przy kompilacji. Nie zastępuje walidacji długości payloadu przychodzącego z sieci. Duża wygenerowana tabela zwiększa czas budowania i rozmiar artefaktu; dynamiczne wyliczenie może zużyć mniej miejsca i szybciej mieścić się w cache. Nie przenoś pracy do CTFE bez określenia tych kosztów.

## Diagnostyka kompilatora

~~~compile_fail
const POJEMNOSC: usize = 7;
const _: () = assert!(POJEMNOSC.is_power_of_two());
fn main() {}
~~~

Kompilacja ma zakończyć się błędem ewaluacji stałej, bo konfiguracja nie spełnia kontraktu. Naprawa polega na zmianie wartości albo kontraktu, nie na przeniesieniu asercji do nieużywanej funkcji. Błąd wywołania funkcji nie-const w CTFE oznacza z kolei, że wybrana operacja nie jest dostępna w tym kontekście na minimalnej wspieranej wersji. Fakt, że metoda jest stable podczas wykonania, nie dowodzi stabilnego wywołania const.

## SIMD i obsługa ogona

SIMD wykonuje podobną operację na wielu torach danych. Najpierw spróbuj prostej pętli lub iteratora w release i sprawdź wygenerowany kod. Autowektoryzacja nie jest gwarancją języka. Ręczna wektoryzacja wymaga obsługi liczby elementów niepodzielnej przez szerokość wektora, właściwych odczytów i identycznej semantyki przepełnienia. Dla sumy `u32` wybierz jawnie wrapping albo sprawdzanie błędu; domyślna suma debug nie jest automatycznie równoważna wektorowemu dodawaniu modularnemu.

**Nightly:** portable SIMD w `std::simd` wymaga `#![feature(portable_simd)]`. Poniższy szkic nie jest testowany na stable 1.90. API i ograniczenia sprawdzono w [dokumentacji std::simd](https://doc.rust-lang.org/std/simd/index.html), 2026-11-11.

~~~text
#![feature(portable_simd)]
use std::simd::u32x4;
let a = u32x4::from_array([1, 2, 3, 4]);
let b = a + u32x4::splat(10);
assert_eq!(b.to_array(), [11, 12, 13, 14]);
~~~

Portable oznacza przenośną abstrakcję, nie obietnicę jednej instrukcji dla każdej operacji. Target bez odpowiednich instrukcji może użyć kodu skalarnego. Intrinsics `std::arch` pozwalają wykorzystać konkretne cechy CPU; wymagają sprawdzenia wsparcia albo gwarancji targetu i ścieżki fallback. `target-cpu=native` utrwala założenia maszyny budującej, więc nie jest właściwą flagą dla każdego dystrybuowanego binarium.

## Inline assembly jako zaufany kontrakt

**Stable na obsługiwanych architekturach:** `asm!` jest zależne od targetu. Szkic x86-64 nie jest tutaj wykonywany; zastępuje zwykłe `wrapping_add` wyłącznie dydaktycznie. Reguły operandów i opcji sprawdzono w [Reference: inline assembly](https://doc.rust-lang.org/reference/inline-assembly.html), 2026-11-11.

~~~text
#[cfg(target_arch = "x86_64")]
fn dodaj(mut x: u64, y: u64) -> u64 {
    // SAFETY: tylko zadeklarowane rejestry wejścia/wyjścia; brak pamięci,
    // stosu, wywołań i wymagań dodatkowych instrukcji CPU. ADD zmienia
    // flagi, dlatego nie deklarujemy preserves_flags.
    unsafe {
        core::arch::asm!("add {x}, {y}",
            x = inout(reg) x, y = in(reg) y,
            options(pure, nomem, nostack));
    }
    x
}
~~~

Opcje są zapewnieniami dla kompilatora. Błędne `nomem`, pominięty clobber albo zmiana stosu przy `nostack` mogą unieważnić program. Kompilator nie odtwarza wszystkich efektów z tekstu instrukcji. Minimalizuj powierzchnię, zachowaj implementację referencyjną i nie używaj assembly tylko dlatego, że wydaje się bliżej procesora.

## Praktyka produkcyjna

**Stable od 1.98, bez lokalnego testu tym toolchainem:** `f32`/`f64::algebraic_*` dopuszczają przekształcenia według własności liczb rzeczywistych. Wynik może być niedeterministyczny nawet dla powtórzonych wejść; szczegóły NaN, nieskończoności, zera i dokładności nie mają zwykłego kontraktu operatorów. Operacje same nie powodują UB, ale kod unsafe nie może opierać soundness na przewidywaniu ich wyniku. Zweryfikowano 2026-11-11 w [dokumentacji f32](https://doc.rust-lang.org/std/primitive.f32.html#algebraic-operators). To świadoma zmiana kontraktu numerycznego, wymagająca walidacji jakości wyników, nie automatyczna flaga przyspieszająca każdy algorytm.

**Stable od 1.98, opis dokumentacyjny:** `NumBuffer<T>` przechowuje miejsce na dziesiętny zapis właściwego typu całkowitego. `format_into` zwraca `&str` pożyczony z bufora; wykorzystaj tekst przed ponownym formatowaniem albo skopiuj go do posiadanego wyniku. Nie zakładaj, że ogólne formatowanie floatów lub podstawy szesnastkowej jest objęte tą samą metodą. API sprawdzono 2026-11-11 w [NumBuffer](https://doc.rust-lang.org/std/fmt/struct.NumBuffer.html) i [u64::format_into](https://doc.rust-lang.org/std/primitive.u64.html#method.format_into).

Poniższy szkic wymaga Rust co najmniej 1.98 i dlatego jest `text`, poza lokalnymi doctestami 1.90.

~~~text
let mut buf = core::fmt::NumBuffer::<u64>::new();
let tekst = 123_u64.format_into(&mut buf);
assert_eq!(tekst, "123");
~~~

Porównuj pełny workload: rozmiar tabel, kodu, czas kompilacji, przepustowość i dopuszczalny błąd numeryczny. Szybsza operacja o innym dopuszczalnym wyniku nie jest bezwarunkowym zamiennikiem dokładnego protokołu lub obliczeń wymagających powtarzalności bitowej.

## Sprawdź, czy rozumiesz

- Kiedy `const fn` wykona się podczas działania programu?
- Dlaczego ogon krótszy niż szerokość wektora jest częścią poprawności?
- Czemu `pure` i `nomem` są zobowiązaniami, a nie tylko wskazówkami optymalizacyjnymi?
- Jak pożyczka `NumBuffer` wpływa na kolejne formatowanie?

## Ćwiczenia

- `C20-1` — podstawowe: Napisz const fn obliczającą sumę 0..n dla n <= 100 i asercję stałą dla n=10. Odróżnij błąd konfiguracji od niepoprawnego wejścia runtime. [Rozwiązanie](../rozwiazania/20_wydajnosc_i_optymalizacja/04_const_eval_simd_i_asm.md#c20-1).
- `C20-2` — praktyczne: Zaprojektuj sumowanie u32 w partiach czterech z bezpiecznym ogonem i semantyką wrapping. Przetestuj długości 0, 1, 4 i 5. [Rozwiązanie](../rozwiazania/20_wydajnosc_i_optymalizacja/04_const_eval_simd_i_asm.md#c20-2).
- `C20-3` — pogłębione: Oceń plan włączenia algebraic_add w algorytmie z wymaganiem powtarzalności bitowej oraz zastąpienia dodawania asm!. Podaj warunki odmowy i eksperymentu. [Rozwiązanie](../rozwiazania/20_wydajnosc_i_optymalizacja/04_const_eval_simd_i_asm.md#c20-3).

## Powiązane tematy

- [MIR i codegen](03_monomorfizacja_mir_llvm_i_optymalizacja.md)
- [Benchmarki](02_benchmarki_profilowanie_i_miri.md)
- [Unsafe i soundness](../21_unsafe_soundness_i_model_pamieci/01_unsafe_i_soundness.md)
