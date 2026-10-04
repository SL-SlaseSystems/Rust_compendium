[← Spis treści](../README.md)

# 22. FFI i interoperacyjność

## Dla kogo i po co

Dla osób łączących Rust z C lub innym ABI i budujących bezpieczne granice między różnymi modelami pamięci oraz obsługi błędów.

## Wymagania wstępne

`unsafe`, raw pointers, layout, ownership zasobów i podstawy procesu budowania Cargo.

## Kolejność materiałów

1. [FFI, ABI i `repr`](01_ffi_abi_i_repr.md)
2. [FFI, bezpieczne otoczki i undefined behavior](02_ffi_safe_wrappers_i_ub.md)

## Po tym dziale

Umiesz zdefiniować stabilną granicę ABI, ustalić ownership danych i opakować ryzykowny interfejs w małe, testowalne API.

## Co dalej

Rozważ `bindgen` lub `cbindgen` dopiero po ustaleniu kontraktu. Dokumentacja funkcji zagranicznej i jej preconditions są ważniejsze niż uproszczony model mentalny.
