[← Spis treści](../README.md)

# Monomorfizacja, MIR, LLVM i optymalizacja

Model potoku pomaga wyjaśnić komunikaty, czas kompilacji i wynikowy kod, ale
szczegóły rustc nie są stabilnym API.

## Uproszczony potok

1. lexing i parsing tworzą AST;
2. expansion rozwija makra i część atrybutów;
3. name resolution wiąże ścieżki;
4. lowering tworzy HIR;
5. type checking i trait solving ustalają typy;
6. THIR/MIR przedstawiają sterowanie oraz miejsca;
7. borrow checking działa głównie na MIR;
8. monomorfizacja wybiera konkretne instancje generics;
9. codegen przekazuje IR do LLVM lub innego backendu;
10. linker tworzy artefakt.

Kolejność jest uproszczeniem i ewoluuje. Nie opieraj build scriptu na
wewnętrznym formacie HIR/MIR.

## Monomorfizacja

~~~rust
#[inline(never)]
fn podwoj<T>(x: T) -> T
where
    T: std::ops::Add<Output = T> + Copy,
{
    x + x
}

fn main() {
    assert_eq!(podwoj(2_u32), 4_u32);
    assert_eq!(podwoj(3_u64), 6_u64);
}
~~~

Kompilator może wygenerować osobne instancje dla `u32` i `u64`. Daje to
static dispatch i optymalizację, ale zwiększa codegen. Linker i LLVM mogą
scalać identyczne funkcje; wynik zależy od profilu i targetu.

Techniki kontroli bloat:

- przenieś niegeneryczny rdzeń za cienki wrapper;
- użyj trait object na zimnej granicy;
- ogranicz liczbę kombinacji const generics;
- analizuj `cargo llvm-lines` i `cargo bloat` (**third-party**);
- nie wymieniaj static dispatch bez pomiaru.

## MIR

MIR jest control-flow graph z locals, places, rvalues, statements i
terminators. Upraszcza wiele konstrukcji wysokiego poziomu. Na MIR działają
m.in. borrow checking, drop elaboration, const evaluation i optymalizacje.

Przydatne polecenia diagnostyczne:

~~~text
rustc --emit=mir plik.rs
rustc --emit=llvm-ir -O plik.rs
rustc --emit=asm -O plik.rs
~~~

Flagi `-Z dump-mir` i `-Z unpretty` są nightly oraz wewnętrzne. Format może
zmienić się bez kompatybilności.

## Drop elaboration

Kompilator dodaje drop flags i ścieżki cleanup, aby zniszczyć tylko
zainicjalizowane pola po move, early return lub unwind. To tłumaczy, dlaczego
częściowe przeniesienie i `MaybeUninit` są skomplikowane. Optymalizator może
usunąć niewidoczne operacje, ale obserwowalne `Drop` musi zachować semantykę.

## LLVM i optymalizacje

LLVM wykonuje inline, vectorization, dead-code elimination, scalar replacement
i wiele transformacji. Wynik zależy od:

- `opt-level`, LTO i codegen units;
- target triple oraz `target-cpu`/`target-feature`;
- widoczności ciał zależności;
- informacji aliasing wynikającej z referencji;
- panic/unwind i overflow checks;
- profilu PGO.

UB pozwala optymalizatorowi zakładać, że niedozwolona ścieżka nigdy nie
występuje. Kod z UB może „działać” w debug i zmienić zachowanie w release.

## Inline

`#[inline]` jest sugestią i częścią metadanych dla zależnych crate’ów.
`#[inline(always)]` nadal nie jest absolutną gwarancją i może zwiększyć
rozmiar. `#[inline(never)]` jest pomocne w benchmarku/analizie, ale nie jest
semantyczną barierą przed wszystkimi transformacjami.

## Analiza assembly

Porównuj funkcję w realnym profilu, zapobiegaj usunięciu wyniku przez
`black_box` i patrz na cały hot path. Liczba instrukcji sama nie opisuje
wydajności: ważne są latency, throughput, cache, branch prediction i calls.

## Powiązane tematy

- [Wydajność i zero-cost abstractions](../20_wydajnosc_i_optymalizacja/01_wydajnosc_i_zero_cost.md)
- [Benchmarki i profilowanie](../20_wydajnosc_i_optymalizacja/02_benchmarki_profilowanie_i_miri.md)
- [Borrow checker i model pamięci](../19_runtime_pamiec_i_kompilator/01_borrow_checker_polonius_i_model_pamieci.md)
