[← Spis treści](../README.md)

# 21. `unsafe`, soundness i model pamięci

## Dla kogo i po co

Dla autorów bezpiecznych abstrakcji nad wskaźnikami, FFI, allocatorami i kodem systemowym. Ten dział nie jest wymagany do większości aplikacji.

> `unsafe` nie wyłącza borrow checkera. Udostępnia dodatkowe operacje i przenosi obowiązek utrzymania ich invariants na autora.

## Wymagania wstępne

Bardzo dobra znajomość ownership, lifetimes, layoutu typów i API biblioteki standardowej.

## Kolejność materiałów

1. [`unsafe` i soundness](01_unsafe_i_soundness.md)
2. [Raw pointers, aliasing i provenance](02_raw_pointers_aliasing_i_provenance.md)
3. [Layout, alignment i niezainicjalizowana pamięć](03_layout_alignment_i_uninitialized_memory.md)

## Po tym dziale

Potrafisz spisać invariants, ograniczyć powierzchnię `unsafe` i wystawić bezpieczne API, którego kontrakt można testować.

## Co dalej

Przejdź do FFI lub `no_std`. Fragmenty pokazujące potencjalne UB traktuj jako opis, nie kod do uruchomienia; w prawdziwym kodzie każdy blok wymaga precyzyjnego komentarza `SAFETY`.
