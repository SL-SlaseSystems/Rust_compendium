[← Spis treści](../README.md)

# Raw pointers, aliasing i provenance

`*const T` oraz `*mut T` mają mniej statycznych gwarancji niż referencje.
Mogą być null, dangling, niewyrównane albo wskazywać niepoprawny bit pattern.
Utworzenie wskaźnika jest zwykle bezpieczne; dostęp do pamięci wymaga dowodu.

## Wskaźnik nie jest liczbą

Semantycznie pointer niesie adres oraz provenance — pochodzenie i uprawnienie
do konkretnej alokacji. Taki sam adres liczbowy nie daje automatycznie prawa
do odczytu nowej alokacji. Pełna postać provenance i aliasingu nadal nie jest
ostatecznie określona, dlatego preferuj oficjalne Strict Provenance APIs.

~~~rust
fn main() {
    let x = 17_u32;
    let ptr = &x as *const u32;
    let adres = ptr.addr();
    let ten_sam = ptr.with_addr(adres);

    // SAFETY: ten_sam zachował provenance i adres żywego x, jest
    // wyrównany i używany tylko do odczytu.
    assert_eq!(unsafe { *ten_sam }, 17);
}
~~~

`addr` pobiera część adresową, a `with_addr` łączy nowy adres z provenance
istniejącego wskaźnika. `map_addr` pomaga w pointer tagging.
`without_provenance` tworzy wskaźnik bez uprawnienia do dostępu, użyteczny
np. jako sentinel.

Exposed Provenance (`expose_provenance` i `with_exposed_provenance`) modeluje
nieuniknione round-trip przez integer, ale ma słabszą podstawę semantyczną i
gorzej współpracuje z Miri oraz architekturami capabilities.

## Pointer arithmetic

`add` i `offset` wymagają pozostania w granicach tej samej alokacji według
swojego kontraktu. `wrapping_add` może utworzyć adres poza alokacją, lecz nie
legalizuje jego dereferencji.

~~~rust
fn suma(dane: &[u32]) -> u32 {
    let ptr = dane.as_ptr();
    let mut wynik = 0;
    for i in 0..dane.len() {
        // SAFETY: i < len; pointer pochodzi z dane, a odczyt jest
        // wyrównany, zainicjalizowany i tylko współdzielony.
        wynik += unsafe { *ptr.add(i) };
    }
    wynik
}

fn main() {
    assert_eq!(suma(&[1, 2, 3]), 6);
}
~~~

Bezpieczne `iter().sum()` jest preferowane i prawdopodobnie równie szybkie.

## Tworzenie referencji

Konwersja `&*ptr` ma silniejsze wymagania niż chwilowy odczyt przez
`ptr::read`: pointer musi być non-null, aligned, dereferenceable, wskazywać
ważne `T` i spełniać reguły aliasingu przez cały lifetime referencji.
Wymagania obowiązują nawet, jeśli utworzona referencja nie jest potem użyta.

## Aliasing

Przybliżony, konserwatywny model:

- żywa `&T` zezwala na odczyt, a mutacja wskazywanego miejsca jest zabroniona
  poza `UnsafeCell`;
- żywa `&mut T` ma wyłączność dostępu dla danego zakresu;
- raw pointers nie omijają zobowiązań wynikających z wcześniej utworzonych
  referencji;
- reborrow może tymczasowo ograniczyć użycie starszego pointera.

Dokładne reguły są aktywnym obszarem modelu pamięci. Stacked Borrows i Tree
Borrows w Miri są modelami diagnostycznymi, a nie normatywną specyfikacją.

## `NonNull<T>`

`NonNull<T>` jest covariant raw pointerem non-null, używanym w implementacji
kolekcji i smart pointerów. Nie udowadnia inicjalizacji, alignment dla
konkretnego dostępu ani ownership. Jego covariance może być niewłaściwa dla
abstrakcji mutowalnej; `PhantomData` koryguje variance i drop semantics.

## Powiązane tematy

- [`unsafe` i soundness](01_unsafe_i_soundness.md)
- [Layout i niezainicjalizowana pamięć](03_layout_alignment_i_uninitialized_memory.md)
- [Borrow checker i model pamięci](../19_runtime_pamiec_i_kompilator/01_borrow_checker_polonius_i_model_pamieci.md)
