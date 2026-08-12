[← Spis treści](../README.md)

# `unsafe` i soundness

Bezpieczny Rust zakłada, że wszystkie użyte unsafe abstractions są poprawne.
**Soundness** oznacza, że żaden program korzystający wyłącznie z bezpiecznego
API nie może przez to API wywołać undefined behavior (UB).

## Pięć możliwości

W bloku `unsafe` można:

1. dereferencjonować raw pointer;
2. wywołać `unsafe fn`;
3. uzyskać dostęp do mutowalnej wartości statycznej;
4. implementować unsafe trait;
5. odczytać pole `union`.

`unsafe` nie pozwala omijać typów, lifetimes ani borrow checkera dla zwykłych
referencji.

## Bezpieczna otoczka

~~~rust
fn rozdziel_mut<T>(slice: &mut [T], srodek: usize) -> (&mut [T], &mut [T]) {
    assert!(srodek <= slice.len());
    let len = slice.len();
    let ptr = slice.as_mut_ptr();

    // SAFETY:
    // - ptr pochodzi z ważnego &mut [T] o długości len;
    // - srodek <= len;
    // - zakresy są rozłączne;
    // - oba slices żyją najwyżej tak długo jak wejściowa pożyczka.
    unsafe {
        (
            std::slice::from_raw_parts_mut(ptr, srodek),
            std::slice::from_raw_parts_mut(ptr.add(srodek), len - srodek),
        )
    }
}

fn main() {
    let mut dane = [1, 2, 3, 4];
    let (a, b) = rozdziel_mut(&mut dane, 2);
    a[0] = 10;
    b[0] = 30;
    assert_eq!(dane, [10, 2, 30, 4]);
}
~~~

Bezpieczna sygnatura jest sound tylko dlatego, że implementacja tworzy
rozłączne mutowalne slices. Błąd w obliczeniu granicy mógłby utworzyć
nakładające się `&mut` i byłby UB, nawet bez widocznego crasha.

## Unsafe function

~~~rust
/// Czyta wartość spod wskaźnika.
///
/// # Safety
///
/// Wskaźnik musi być nie-null, prawidłowo wyrównany, dereferencjonowalny,
/// wskazywać zainicjalizowane T i zezwalać na odczyt.
unsafe fn kopiuj<T: Copy>(ptr: *const T) -> T {
    // SAFETY: wywołujący zobowiązuje się spełnić kontrakt funkcji.
    unsafe { ptr.read() }
}

fn main() {
    let x = 42_u32;
    // SAFETY: wskaźnik powstał z żywej, wyrównanej wartości x.
    assert_eq!(unsafe { kopiuj(&x) }, 42);
}
~~~

W Edition 2024 ciało `unsafe fn` nie jest automatycznie „jednym wielkim
unsafe”; operacje powinny być w jawnych blokach. Zmniejsza to zakres audytu.

## Invariants

Invariant może dotyczyć ważności i alignment wskaźnika, inicjalizacji,
aliasingu, ownership, dokładnie jednego `Drop`, granic alokacji, synchronizacji
między wątkami, panic safety i provenance.

Komentarz `SAFETY` ma dowodzić wszystkich preconditions używanej operacji.
Dokumentacja `# Safety` opisuje obowiązki wywołującego publiczne unsafe API.

## Unsound bez `unsafe` w wywołaniu

Bezpieczna funkcja może być unsound, jeśli wewnętrzny `unsafe` ufa
niezwalidowanemu indeksowi lub pozwala utworzyć dwa `&mut`. Odbiorca nie ma
obowiązku „używać jej ostrożnie”. Jeżeli wymaganie nie jest wyrażone w typie
i nie można go sprawdzić, funkcja powinna być `unsafe`.

## Audyt

1. znajdź wszystkie `unsafe`, unsafe impl i FFI;
2. zapisz invariants typu;
3. dla każdego bloku wypisz preconditions;
4. prześledź panic, early return i `Drop`;
5. testuj Miri oraz sanitizers, ale wykonaj też ręczny dowód;
6. utrzymuj blok minimalny i prywatny.

## Powiązane tematy

- [Raw pointers, aliasing i provenance](02_raw_pointers_aliasing_i_provenance.md)
- [Layout i niezainicjalizowana pamięć](03_layout_alignment_i_uninitialized_memory.md)
- [FFI, bezpieczne otoczki i UB](11_ffi_safe_wrappers_i_ub.md)
