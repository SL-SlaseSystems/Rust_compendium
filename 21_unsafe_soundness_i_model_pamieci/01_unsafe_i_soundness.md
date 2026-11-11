[← Spis treści](../README.md)
<!-- status: expanded -->

# `unsafe` i soundness

## Cele

Po tym rozdziale potrafisz:

- rozróżnić obowiązek wywołującego unsafe fn od dowodu wewnątrz bezpiecznej otoczki;
- prześledzić inicjalizację, aliasing i zniszczenie zasobu na każdej ścieżce;
- wykazać, dlaczego test nie zastępuje niezmiennika abstrakcji;

## Model — mechanizm i kontrakt

Bezpieczny Rust zakłada, że wszystkie użyte unsafe abstractions są poprawne.
**Soundness** oznacza, że żaden program korzystający wyłącznie z bezpiecznego
API nie może przez to API wywołać undefined behavior (UB).

## Pięć możliwości

Do operacji i deklaracji wymagających zaufanego kontraktu należą:

1. dereferencjonować raw pointer;
2. wywołać `unsafe fn`;
3. używać mutowalnych statyk i niebezpiecznych statyk obcych zgodnie z ich kontraktem;
4. implementować unsafe trait przez `unsafe impl` (to deklaracja, nie operacja wymagająca otaczającego bloku);
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

W Edition 2024 operacje w `unsafe fn` powinny mieć jawne bloki `unsafe`;
domyślny lint ostrzega przy ich braku. Oddziela to kontrakt wywołującego
od uzasadnienia konkretnej operacji w implementacji.

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

## Dowód na granicy bezpiecznej funkcji

Dla `rozdziel_mut` wypisz przesłanki w kolejności wykonania. Wejściowy `&mut [T]` zapewnia ważny zakres zainicjalizowanych elementów, alignment oraz wyłączność na czas pożyczki. `assert!` działa również w release i odrzuca `srodek > len` przed arytmetyką wskaźnika. Oba wyniki obejmują rozłączne zbiory elementów, a wyprowadzony lifetime ogranicza ich użycie do pożyczki wejściowej. Podział nie przenosi elementów i nie przejmuje własności alokacji, więc nie dodaje żadnego `Drop`.

Przypadki `srodek=0`, `srodek=len` oraz pusty slice nadal wymagają nie-null i wyrównanego wskaźnika. Pochodzi on z ważnego slice, więc warunek jest spełniony; wskaźnik za końcem wolno wykorzystać wyłącznie zgodnie z kontraktem pustego widoku. Dla ZST rozłączność dotyczy logicznych elementów, mimo że ich adresy mogą się pokrywać. Pełne wymagania opisuje [from_raw_parts_mut](https://doc.rust-lang.org/std/slice/fn.from_raw_parts_mut.html), sprawdzone 2026-11-11. Produkcyjnie wybierz gotowe `slice.split_at_mut`, chyba że inna implementacja ma uzasadnioną potrzebę.

Niezmiennik typu musi być zachowany przez wszystkie bezpieczne metody, nie tylko te zawierające `unsafe`. Jeżeli prywatny `len` określa liczbę zainicjalizowanych elementów, bezpieczny setter nie może go dowolnie zwiększać. Późniejszy `Drop` zaufa temu polu. Samo zredukowanie bloku unsafe do jednej linii nie ogranicza zakresu logicznego audytu do tej linii.

## Diagnostyka kompilatora

~~~compile_fail
fn odczytaj(ptr: *const u32) -> u32 {
    *ptr
}
fn main() {}
~~~

Błąd E0133 wskazuje operację wymagającą dodatkowego dowodu. Dodanie bloku `unsafe` pozwoli kompilować funkcję, ale uczyni ją unsound jako bezpieczne API przyjmujące dowolny wskaźnik. Poprawka to bezpieczna referencja `&u32` albo `unsafe fn` z pełną sekcją `# Safety`; sama nazwa „ważny_ptr” niczego nie gwarantuje. Testowanie wyłącznie `&x as *const _` nie obejmuje wszystkich wartości przyjmowanych przez publiczną sygnaturę.

Edition 2024 domyślnie ostrzega przez lint `unsafe_op_in_unsafe_fn` o operacjach bez jawnego bloku w `unsafe fn`. Można ustawić `deny`, aby błąd zatrzymywał build. Rozróżniaj tę politykę lintów od wymagań typów i bezpieczeństwa; szczegóły podaje [Edition Guide](https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-op-in-unsafe-fn.html), zweryfikowane 2026-11-11.

## Praktyka produkcyjna

`ptr::read` kopiuje reprezentację bez oznaczenia źródła jako przeniesionego. Dla `T: Copy` w pokazanej funkcji nie tworzy drugiego ownera zasobu. Gdy usuniesz to ograniczenie i odczytasz `String`, musisz zapewnić, że źródło nie zostanie później użyte ani zniszczone jako drugi właściciel. Wymagania [ptr::read](https://doc.rust-lang.org/std/ptr/fn.read.html), sprawdzone 2026-11-11, dotyczą także inicjalizacji i alignment. Zwykłe przypisanie na niezainicjalizowane miejsce może próbować zniszczyć starą wartość; inicjalizuj przez API do tego przeznaczone.

Przy panic safety rozdziel błąd pamięci od wycieku. Utrata już utworzonego `String` w `MaybeUninit` może być wyciekiem bez UB, natomiast podwójne zniszczenie jego bufora narusza bezpieczeństwo. Nie zakładaj, że użytkownik zawsze wykona destructor: `mem::forget` jest bezpieczne, a proces może zakończyć się bez drop. Takie ograniczenie opisuje [dokumentacja forget](https://doc.rust-lang.org/std/mem/fn.forget.html), sprawdzona 2026-11-11. Bezpieczeństwo pamięci nie może zależeć od obowiązkowego wyrejestrowania pożyczonego callbacku wyłącznie w zapomnianym guardzie.

Audyt łącz z testami granic, licznikiem destrukcji, kontrolowanym panic i Miri. Zachowaj pisemny dowód obejmujący pusty zakres, przepełnienie obliczeń rozmiaru, ZST i wejścia niepoprawne. Zmiana reprezentacji lub dodanie metody modyfikującej prywatny stan wymaga ponownego sprawdzenia dowodu, nawet jeśli żaden istniejący blok unsafe się nie zmienił.

## Sprawdź, czy rozumiesz

- Dlaczego `debug_assert!` nie wystarcza do sprawdzenia precondition bezpieczeństwa publicznego API?
- Jak bezpieczna metoda bez słowa `unsafe` może zepsuć niezmiennik destructora?
- Dlaczego dopuszczalność `mem::forget` ogranicza projekt callbacków?

## Ćwiczenia

- `C13-1` — podstawowe: Oceń zastąpienie assert! przez debug_assert! w rozdziel_mut. Podaj kontrprzykład bez uruchamiania UB. [Rozwiązanie](../rozwiazania/21_unsafe_soundness_i_model_pamieci/01_unsafe_i_soundness.md#c13-1).
- `C13-2` — praktyczne: Napisz bezpieczną wersję kopiuj przyjmującą &T dla T: Copy. Porównaj obowiązki wywołującego i implementacji. [Rozwiązanie](../rozwiazania/21_unsafe_soundness_i_model_pamieci/01_unsafe_i_soundness.md#c13-2).
- `C13-3` — pogłębione: Zaprojektuj audyt własnej kolekcji z polami ptr, len, cap. Wyjaśnij niezmienniki konstruktora, push, pop i Drop oraz wpływ panic. [Rozwiązanie](../rozwiazania/21_unsafe_soundness_i_model_pamieci/01_unsafe_i_soundness.md#c13-3).

## Powiązane tematy

- [Raw pointers, aliasing i provenance](02_raw_pointers_aliasing_i_provenance.md)
- [Layout i niezainicjalizowana pamięć](03_layout_alignment_i_uninitialized_memory.md)
- [FFI, bezpieczne otoczki i UB](../22_ffi_i_interoperacyjnosc/02_ffi_safe_wrappers_i_ub.md)
