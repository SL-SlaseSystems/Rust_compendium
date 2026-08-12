[← Spis treści](../README.md)

# Wydajność i zero-cost abstractions

„Zero-cost” znaczy: nie płacisz zasadniczo więcej niż za równoważną ręczną
implementację i nie płacisz za nieużywaną abstrakcję. Nie znaczy „każdy kod
jest darmowy”.

## Iteratory

~~~rust
fn suma_petla(dane: &[u64]) -> u64 {
    let mut wynik = 0;
    for &x in dane {
        wynik += x;
    }
    wynik
}

fn suma_iterator(dane: &[u64]) -> u64 {
    dane.iter().copied().sum()
}

fn main() {
    let dane = [1, 2, 3, 4];
    assert_eq!(suma_petla(&dane), suma_iterator(&dane));
}
~~~

Obie formy mogą wygenerować podobny kod. Potwierdza się to benchmarkiem i
profilem dla konkretnego targetu, nie samą stylistyką.

## Najczęstsze koszty

- alokacja i realokacja;
- kopiowanie dużych buforów;
- słaba lokalność cache i pointer chasing;
- dynamic dispatch i brak inliningu;
- synchronizacja oraz contention;
- syscall, sieć i dysk;
- nadmiarowa serializacja;
- rozmiar kodu po monomorfizacji.

`clone` nie zawsze jest drogi, a referencja nie zawsze szybsza. Klon `Arc`
jest inkrementacją atomową; klon `String` kopiuje bufor; klon małego `Copy`
to kilka bajtów.

## Layout i cache

`Vec<T>` przechowuje elementy ciągle, co sprzyja prefetch. Lista węzłów może
mieć teoretycznie tani insert, ale wiele alokacji i cache misses. Struct of
arrays bywa lepszy dla przetwarzania jednej kolumny; array of structs dla
przetwarzania pełnych rekordów. Pomiar rozstrzyga.

## Alokacje

Używaj `with_capacity`, jeśli rozmiar jest znany. Przyjmuj slices, aby nie
tworzyć kolekcji. Zwracaj iterator, gdy obliczenie może być leniwe. Nie
utrzymuj własnej puli obiektów bez profilu — może zwiększyć fragmentację i
złożoność.

## Profile kompilacji

`--release` zmienia optymalizację. LTO może poprawić inline między crate’ami
kosztem czasu linkowania. Mniej codegen units pomaga globalnej optymalizacji.
`target-cpu=native` może przyspieszyć lokalny program, lecz traci przenośność
binarną.

Profile-guided optimization i BOLT zależą od toolchainu/platformy i wymagają
reprezentatywnych profili. Sprawdzaj aktualny rustc Book.

## Bounds checks i `unsafe`

Optymalizator często usuwa bounds checks w prostych iteracjach. Nie przechodź
do `get_unchecked` bez dowodu z benchmarku i pełnego kontraktu bezpieczeństwa.
Jedna zła granica daje UB, a zysk może być zerowy.

## Metodyka

1. zdefiniuj metrykę i workload;
2. zmierz baseline w release;
3. użyj profilera;
4. postaw jedną hipotezę;
5. zmień jedną rzecz;
6. porównaj wynik i wariancję;
7. zachowaj regression benchmark.

Optymalizuj przepustowość, latency, pamięć, energię lub rozmiar świadomie —
cele mogą być sprzeczne.

## Powiązane tematy

- [Benchmarki i profilowanie](../08_testowanie_i_jakosc/04_benchmarki_profilowanie_i_miri.md)
- [Monomorfizacja, MIR i LLVM](../zaawansowane/13_monomorfizacja_mir_llvm_i_optymalizacja.md)
- [Layout i alignment](../zaawansowane/03_layout_alignment_i_uninitialized_memory.md)
