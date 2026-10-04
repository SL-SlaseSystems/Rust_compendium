[← Spis treści](../README.md)

# 20. Wydajność i optymalizacja

## Dla kogo i po co

Dla osób, które chcą optymalizować na podstawie pomiarów i rozumieć koszt abstrakcji od kodu źródłowego po LLVM.

## Wymagania wstępne

Generics, traits, iteratory, profile Cargo i podstawy testowania.

## Kolejność materiałów

1. [Wydajność i zero-cost abstractions](01_wydajnosc_i_zero_cost.md)
2. [Benchmarki, profilowanie i Miri](02_benchmarki_profilowanie_i_miri.md)
3. [Monomorfizacja, MIR, LLVM i optymalizacja](03_monomorfizacja_mir_llvm_i_optymalizacja.md)

Obecny materiał o benchmarkach łączy również podstawy profilowania i Miri. Traktuj Miri jako narzędzie do wykrywania części błędów pamięci, a nie benchmark ani dowód braku undefined behavior.

## Po tym dziale

Potrafisz zbudować hipotezę wydajnościową, zmierzyć ją i powiązać wynik z alokacjami, monomorfizacją oraz wygenerowanym kodem.

## Co dalej

Przejdź do testów zaawansowanych i obserwowalności. Nie optymalizuj bez reprezentatywnego benchmarku i profilu.
