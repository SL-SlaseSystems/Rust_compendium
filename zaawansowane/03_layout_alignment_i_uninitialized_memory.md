[← Spis treści](../README.md)

# Layout, alignment i niezainicjalizowana pamięć

Low-level kod musi rozróżniać rozmiar, alignment, padding, bit pattern i
inicjalizację. „Tyle samo bajtów” nie znaczy „ten sam typ”.

## Layout

`size_of::<T>()` zawiera padding potrzebny tablicom `T`.
`align_of::<T>()` podaje wymagane wyrównanie.

~~~rust
use std::mem::{align_of, size_of};

#[repr(C)]
struct Rekord {
    a: u8,
    b: u32,
}

fn main() {
    assert!(size_of::<Rekord>() >= 5);
    assert!(align_of::<Rekord>() >= align_of::<u32>());
}
~~~

Nie asertujemy konkretnego layoutu przenośnie, poza gwarancjami `repr`.
Domyślny `repr(Rust)` gwarantuje poprawne alignment, brak nakładania pól i
alignment typu co najmniej maksymalny z pól, ale kolejność oraz padding nie
są publicznym ABI.

`repr(C)` daje layout według reguł C dla wspieranych pól.
`repr(transparent)` służy wrapperowi ABI. `repr(packed)` może tworzyć
niewyrównane pola; samo utworzenie referencji do takiego pola może być UB.

## Odczyt niewyrównany

~~~rust
fn odczytaj_u32_le(buf: &[u8]) -> Option<u32> {
    let bytes: [u8; 4] = buf.get(..4)?.try_into().ok()?;
    Some(u32::from_le_bytes(bytes))
}

fn main() {
    assert_eq!(odczytaj_u32_le(&[1, 0, 0, 0]), Some(1));
}
~~~

To bezpieczniejsze od castu `*const u32`. Gdy naprawdę trzeba, raw pointer
można odczytać `read_unaligned`, ale nadal wymaga ważnych bajtów i poprawnego
bit pattern dla `T`.

## `MaybeUninit<T>`

Niezainicjalizowane bajty nie są wartością `T`. `MaybeUninit<T>` pozwala je
przechować bez natychmiastowego złamania invariants.

~~~rust
use std::mem::MaybeUninit;

fn para<T>(a: T, b: T) -> [T; 2] {
    let mut dane: [MaybeUninit<T>; 2] =
        unsafe { MaybeUninit::uninit().assume_init() };
    dane[0].write(a);
    dane[1].write(b);

    // SAFETY: oba elementy zostały zainicjalizowane dokładnie raz.
    unsafe { (&dane as *const _ as *const [T; 2]).read() }
}

fn main() {
    assert_eq!(para(String::from("a"), String::from("b")), ["a", "b"]);
}
~~~

Dla pętli, która może panikować w połowie, potrzebny jest guard niszczący
tylko zainicjalizowany prefix. Alternatywnie użyj stabilnych helperów
standard library, jeśli pokrywają przypadek. Ręczne `MaybeUninit` bez planu
panic jest częstym źródłem wycieku lub podwójnego drop.

## Niepoprawne wartości

Zera nie są uniwersalną wartością. `mem::zeroed` dla referencji lub
`NonZeroUsize` daje niepoprawną wartość. `bool` dopuszcza tylko poprawne
reprezentacje logiczne, a enum tylko prawidłowe discriminants.

`assume_init` nie „inicjalizuje”; jest unsafe obietnicą, że inicjalizacja już
nastąpiła. Samo utworzenie niepoprawnej wartości może być UB, zanim pole
zostanie odczytane.

## `transmute`

`transmute` wymaga zgodnego rozmiaru i natychmiast przenosi wszystkie
invariants typu docelowego. Padding może być niezainicjalizowany i nie jest
danymi do dowolnego kopiowania. Preferuj `from_ne_bytes`, jawne konwersje,
`cast` raw pointers albo wyspecjalizowane API.

## Zero-sized types

ZST ma rozmiar zero, ale może wymagać niezerowego alignment. Wektory i
allocatory muszą obsłużyć je bez zakładania, że różne elementy mają różne
adresy. `NonNull::dangling` jest aligned sentinelem, nie wskaźnikiem do
ważnego obiektu.

## Powiązane tematy

- [Raw pointers i provenance](02_raw_pointers_aliasing_i_provenance.md)
- [FFI i `repr`](../12_systemy_i_interoperacyjnosc/03_ffi_abi_i_repr.md)
- [`unsafe` i soundness](01_unsafe_i_soundness.md)
