[← Spis treści](../README.md)
<!-- status: expanded -->

# Layout, alignment i niezainicjalizowana pamięć

## Cele

Po tym rozdziale potrafisz:

- odróżnić layout i poprawność bitową od semantycznych niezmienników typu;
- prześledzić ownership przy write, assume_init_read i assume_init_drop;
- obsłużyć częściową inicjalizację i panic bez odczytu pustych miejsc;

## Model — mechanizm i kontrakt

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
        [const { MaybeUninit::uninit() }; 2];
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

## `Vec::spare_capacity_mut` — rezerwacja i inicjalizacja

**Stable:** `spare_capacity_mut()` udostępnia wolną część alokacji jako `&mut [MaybeUninit<T>]`, bez zmiany `len`. Nie jest to `&mut [T]`: miejsca za końcem żywego prefixu nie muszą zawierać wartości `T`. Odczyt przez `assume_init_ref` przed inicjalizacją byłby niepoprawny. `reserve(n)` zapewnia miejsce na co najmniej `n` dodatkowych elementów względem bieżącego `len`; wykonaj rezerwację przed pożyczeniem wolnego zakresu. Może ona realokować bufor, więc nie zachowuj przez nią surowych wskaźników do poprzedniej alokacji.

Inicjalizacja przez `MaybeUninit::write` jest bezpieczna, natomiast publikacja nowego prefixu przez `set_len` wymaga dowodu: nowa długość nie przekracza pojemności, a wszystkie dołączane elementy już istnieją. Kontrakty sprawdzono 2026-11-11 w [spare_capacity_mut](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.spare_capacity_mut), [reserve](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.reserve) i [set_len](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.set_len). Poniższy przykład działa także dla zasobowego `String`; w zwykłym kodzie preferuj gotowe `push` lub `extend_from_slice`.

~~~rust
fn dopisz<T: Clone>(wynik: &mut Vec<T>, nowe: &[T]) {
    wynik.reserve(nowe.len());
    for wartosc in nowe {
        let nowa_dlugosc = wynik.len().checked_add(1).expect("długość");
        let kopia = wartosc.clone(); // może panikować przed zapisem
        {
            let wolne = wynik.spare_capacity_mut();
            wolne[0].write(kopia);
        } // koniec pożyczki wolnego zakresu
        // SAFETY: reserve zapewniło pojemność dla wszystkich nowych
        // elementów. Stary prefix pozostał poprawny, a write właśnie
        // zainicjalizowało następne T. Od write nie było punktu paniki.
        unsafe { wynik.set_len(nowa_dlugosc) };
    }
}
fn main() {
    let mut pusty = Vec::<String>::new();
    dopisz(&mut pusty, &[]);
    assert!(pusty.is_empty());

    let nowe = [String::from("a"), String::from("b"), String::from("c")];
    let mut wynik = vec![String::from("prefix")];
    dopisz(&mut wynik, &nowe);
    assert_eq!(wynik, ["prefix", "a", "b", "c"]);
    assert_eq!(nowe, ["a", "b", "c"]);
}
~~~

Przy panice w kolejnym `Clone` poprzednie kopie należą już do `Vec`: długość publikujemy po każdym zapisie. Wektor pozostaje poprawny i zniszczy te `String` przy swoim `Drop`; funkcja dopuszcza częściowe dopisanie, nie obiecuje rollbacku całej operacji. Klon, którego nie udało się jeszcze zapisać, nie jest oznaczany jako element wektora. Obliczenie długości i potencjalnie panikujące tworzenie wartości następują przed `write`, a do `set_len` nie ma kodu użytkownika.

Alternatywa wypełniająca wiele slotów i zmieniająca `len` dopiero raz na końcu wymaga pilnowania liczby zainicjalizowanych elementów. Przy panice `Vec::drop` widzi wyłącznie stare `len`: zasoby zapisane poza nim wyciekłyby bez guarda niszczącego poprawnie utworzony prefix lub publikującego jego długość. Sama referencja `&mut [MaybeUninit<T>]` nie wykona takiego sprzątania. Przedwczesne zwiększenie `len` jest groźniejsze: udostępnia niezainicjalizowane `T` i może prowadzić do UB podczas odczytu lub destrukcji. Rezerwacja, inicjalizacja i przejęcie odpowiedzialności za drop to trzy osobne kroki.

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

## Stan inicjalizacji jest częścią typu abstrakcyjnego

`MaybeUninit<T>` nie pamięta, czy wykonano `write`. Przechowuje miejsce, a metadane inicjalizacji prowadzi autor. `assume_init` jest zobowiązaniem, nie sprawdzeniem. Z kolei `ManuallyDrop<T>` tylko wyłącza automatyczny drop i nadal wymaga poprawnej wartości `T`. Nie zastępuje magazynu na niezainicjalizowane bajty. Rozróżnienie opisują [MaybeUninit](https://doc.rust-lang.org/std/mem/union.MaybeUninit.html) i [ManuallyDrop](https://doc.rust-lang.org/std/mem/struct.ManuallyDrop.html), zweryfikowane 2026-11-11.

Poniższy slot pokazuje stan „pusty albo posiada dokładnie jedno T”. W aplikacji użyj `Option<T>`; ręczna implementacja służy prześledzeniu obowiązków.

~~~rust
use std::mem::MaybeUninit;
struct Slot<T> { dane: MaybeUninit<T>, pelny: bool }
impl<T> Slot<T> {
    fn nowy() -> Self {
        Self { dane: MaybeUninit::uninit(), pelny: false }
    }
    fn wstaw(&mut self, x: T) {
        assert!(!self.pelny, "slot jest zajęty");
        self.dane.write(x);
        self.pelny = true;
    }
    fn wez(&mut self) -> Option<T> {
        if !std::mem::replace(&mut self.pelny, false) { return None; }
        // SAFETY: pelny było true: istnieje jedno żywe T. Oznaczenie
        // slotu jako pustego zapobiega kolejnemu odczytowi i dropowi.
        Some(unsafe { self.dane.assume_init_read() })
    }
}
impl<T> Drop for Slot<T> {
    fn drop(&mut self) {
        if self.pelny {
            self.pelny = false;
            // SAFETY: pełny slot posiada żywe T, nieodczytane przez wez.
            // Drop wywołujemy raz, a MaybeUninit nie zniszczy go ponownie.
            unsafe { self.dane.assume_init_drop() };
        }
    }
}
fn main() {
    let mut slot = Slot::nowy();
    slot.wstaw(String::from("a"));
    assert_eq!(slot.wez().as_deref(), Some("a"));
    assert!(slot.wez().is_none());
    slot.wstaw(String::from("b"));
}
~~~

`wstaw` sprawdza pustkę przed zapisem. Między `write` a ustawieniem flagi nie ma operacji mogącej wywołać panic. `wez` najpierw odbiera slotowi własność, potem przenosi wartość do wyniku. Gdy `T::drop` spanikuje, flaga jest już wyłączona i slot nie próbuje drugi raz niszczyć tego samego obiektu. Przeniesienie samego slotu jest dozwolone: nie przechowuje samowskazującej referencji i zachowuje razem flagę oraz magazyn.

## Diagnostyka kompilatora

~~~compile_fail
#[repr(C, packed)]
struct Pakiet { tag: u8, liczba: u32 }
fn main() {
    let p = Pakiet { tag: 1, liczba: 7 };
    let r = &p.liczba;
    println!("{r}");
}
~~~

E0793 odrzuca referencję o niedostatecznym wyrównaniu. Kopia `let liczba = p.liczba` nie tworzy takiej referencji. Jeśli naprawdę potrzebujesz pointer API, użyj `&raw const p.liczba` i `read_unaligned` z dowodem ważności pola. Cast z `&p.liczba` jest za późny: błędna referencja powstałaby przed nim. Wymagania opisuje [read_unaligned](https://doc.rust-lang.org/std/ptr/fn.read_unaligned.html), sprawdzone 2026-11-11.

Kompilator może ostrzec o utworzeniu oczywiście niepoprawnej wartości przez `zeroed`, ale nie sprawdza automatycznie całego protokołu flagi `pelny`. Bezpieczna metoda odczytująca pusty slot byłaby unsound mimo udanej kompilacji. Prywatność pól i brak bezmyślnego derive dla ręcznie zarządzanych wartości są częścią ochrony niezmiennika.

## Praktyka produkcyjna

Dla tablic inicjalizowanych w pętli pilnuj długości żywego prefixu. Guard niszczy prefix przy early return i unwind; po udanym przeniesieniu wszystkich wartości musi zostać rozbrojony. Bezpieczne `std::array::from_fn` albo `Vec` często usuwają potrzebę tego dowodu. Wycieku przy panic nie nazywaj automatycznie UB, lecz uwzględnij go jako błąd zarządzania zasobami.

Layout `repr(C)` zależy od targetu i reguł jego ABI. Domyślny layout Rust nie gwarantuje kolejności pól. Rozmiar zawiera padding, który nie stanowi gotowego formatu serializacji; odczytywanie całej reprezentacji jako zainicjalizowanych bajtów może naruszać wymagania. Kontrakty reprezentacji opisuje [Rust Reference: type layout](https://doc.rust-lang.org/reference/type-layout.html), sprawdzone 2026-11-11.

Przed własną alokacją oblicz layout przez sprawdzone API, nie przez mnożenie bez kontroli przepełnienia. Własny format binarny koduj jawnie: endianness, długość i dopuszczalne wartości enumów są osobnymi decyzjami. Test rozmiaru na jednej platformie jest przydatną kontrolą ABI tego targetu, ale nie dowodem przenośności.

## Sprawdź, czy rozumiesz

- Dlaczego flaga slotu zmienia się przed odczytem i przed destrukcją?
- Czy `MaybeUninit<String>` po `write` automatycznie zniszczy `String`?
- Czemu zero bajtów nie jest uniwersalnym konstruktorem `T`?

## Ćwiczenia

- `C15-1` — podstawowe: Wskaż, kto posiada String po wez oraz kto niszczy wartość pozostawioną w pełnym slocie. [Rozwiązanie](../rozwiazania/21_unsafe_soundness_i_model_pamieci/03_layout_alignment_i_uninitialized_memory.md#c15-1).
- `C15-2` — praktyczne: Zaprojektuj test slotu z licznikiem Drop dla ścieżek pełny-drop, wez-drop i ponowne wstawienie. Podaj oczekiwane liczniki. [Rozwiązanie](../rozwiazania/21_unsafe_soundness_i_model_pamieci/03_layout_alignment_i_uninitialized_memory.md#c15-2).
- `C15-3` — pogłębione: Opisz guard dla częściowo inicjalizowanej tablicy o długości N. Prześledź panic po utworzeniu k elementów i udane przeniesienie całości. [Rozwiązanie](../rozwiazania/21_unsafe_soundness_i_model_pamieci/03_layout_alignment_i_uninitialized_memory.md#c15-3).

## Powiązane tematy

- [Raw pointers i provenance](02_raw_pointers_aliasing_i_provenance.md)
- [FFI i `repr`](../22_ffi_i_interoperacyjnosc/01_ffi_abi_i_repr.md)
- [`unsafe` i soundness](01_unsafe_i_soundness.md)
