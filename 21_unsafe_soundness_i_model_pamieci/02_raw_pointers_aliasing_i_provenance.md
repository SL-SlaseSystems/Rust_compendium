[← Spis treści](../README.md)
<!-- status: expanded -->

# Raw pointers, aliasing i provenance

## Cele

Po tym rozdziale potrafisz:

- odróżnić adres, provenance, alignment i ważność dostępu;
- przeprowadzić arytmetykę wskaźnika w granicach jednej alokacji;
- ustalić moment powstania zobowiązań referencji oraz własności po odczycie;

## Model — mechanizm i kontrakt

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

## Granice uprawnienia do pamięci

Adres nie jest dowodem długości alokacji, życia obiektu ani prawa mutacji. `NonNull::new` sprawdza wyłącznie brak null. Wskaźnik do pierwszego pola nie jest automatycznie uprawnieniem do odczytu całego otaczającego obiektu; wyprowadzaj wskaźnik z miejsca obejmującego planowany dostęp. Po zwolnieniu i ponownym przydzieleniu pamięci nowy obiekt może otrzymać ten sam adres, co nie przywraca dawnej provenance.

Strict Provenance APIs pomagają oddzielić manipulację adresem od zachowania pochodzenia. `with_addr` nie tworzy alokacji i nie przedłuża jej życia: nowy adres nadal musi być legalny dla konkretnego dostępu. Znakowanie wskaźników (pointer tagging) wymaga znanej liczby dostępnych bitów, usunięcia tagu przed odczytem i zachowania oryginalnej provenance. To nie jest technika przenośna tylko dlatego, że działa na jednym 64-bitowym CPU. Wymagania i aktualny status semantyki opisuje [moduł ptr](https://doc.rust-lang.org/std/ptr/index.html), sprawdzony 2026-11-11.

## Przykład kontrolowanego odczytu

~~~rust
fn trzeci(dane: &[u32]) -> Option<u32> {
    if dane.len() < 3 { return None; }
    let ptr = dane.as_ptr();
    // SAFETY: wejście zapewnia jedną żywą alokację, co najmniej trzy
    // zainicjalizowane i wyrównane u32. Dostęp jest tylko do odczytu;
    // index 2 leży w slice, a wynik Copy nie przejmuje własności bufora.
    Some(unsafe { ptr.add(2).read() })
}
fn main() {
    assert_eq!(trzeci(&[4, 5, 6]), Some(6));
    assert_eq!(trzeci(&[]), None);
}
~~~

Warunek jest częścią bezpiecznej otoczki i nie wolno zamienić go na `debug_assert!`. Funkcja zwraca kopię, więc lifetime wskaźnika nie wydostaje się na zewnątrz. Produkcyjny odpowiednik to `dane.get(2).copied()`: krótszy dowód, ten sam kontrakt i brak założonego zysku unsafe. Ręczny kod ma wartość dydaktyczną, nie stanowi domyślnej optymalizacji.

`ptr.read()` dla typu posiadającego zasób kopiuje jego reprezentację. Autor musi wtedy rozliczyć własność; zmiana `u32` na `String` nie jest mechaniczną generalizacją. `read_unaligned` usuwa wymaganie wyrównania tej operacji, ale nie wymóg inicjalizacji, legalnego bit pattern i poprawnego ownership. Nie twórz po drodze niewyrównanej referencji tylko po to, by natychmiast zamienić ją na raw pointer.

## Diagnostyka kompilatora

Raw pointer nie ma zwykłego lifetime referencji. Kod zwracający wskaźnik do lokalnej zmiennej może przejść typowanie, a późniejsza dereferencja nadal będzie błędem. Kompilator może ostrzec o oczywistej sytuacji, lecz brak ostrzeżenia nie dowodzi ważności. Preferuj zwracanie wartości posiadanej lub referencji związanej z wejściem, gdy nie potrzebujesz FFI.

Przy `repr(packed)` kompilator odrzuca utworzenie referencji do potencjalnie niewyrównanego pola. Poprawka to kopiowanie pola przez dozwoloną operację wartościową albo `&raw const pole` z odczytem `read_unaligned`, jeśli spełniasz pozostałe wymagania. Nie maskuj błędu castem z już utworzonej złej referencji. Komunikat wskazuje, że kontrakt referencji jest silniejszy od samej dostępności bajtów.

## Praktyka produkcyjna

Twórz referencję możliwie blisko miejsca użycia, po walidacji. `slice::from_raw_parts` wymaga jednego ciągłego zakresu w jednej alokacji; sąsiedztwo liczbowe dwóch oddzielnych buforów nie pozwala połączyć ich w slice. Pusty zakres także ma własne preconditions. Przy obcym ABI opisuj, czy null z zerową długością jest dozwolony, i normalizuj go przed utworzeniem widoku Rust.

Rzutowanie wskaźnika współdzielonego na `*mut T` nie przyznaje prawa do zapisu. `UnsafeCell` wyłącza odpowiednią gwarancję niemutowalności wnętrza, ale nie wyłącza wyłączności `&mut` ani wymagań synchronizacji wątków. Własny typ interior mutability musi kontrolować, kto może tworzyć referencje; samo prywatne pole `UnsafeCell<T>` nie czyni API bezpiecznym.

Nie utożsamiaj modeli Stacked Borrows lub Tree Borrows z zamkniętą specyfikacją. W razie rozbieżności rozpocznij od kontraktu API i gwarancji języka, ogranicz niepotrzebne mieszanie raw pointers z referencjami i zachowaj mały test regresji Miri. Krytyczny kod audytuj także dla panic, ponownego użycia adresu i innych targetów. Podstawą poprawności jest protokół dostępu, a nie obserwacja, że wskaźnik miał oczekiwaną wartość szesnastkową.

## Sprawdź, czy rozumiesz

- Dlaczego `NonNull<T>` nie dowodzi prawa do utworzenia `&mut T`?
- Co pozostaje wymagane po zastąpieniu `read` przez `read_unaligned`?
- Dlaczego `wrapping_add` może być dozwolone, a dereferencja wyniku zabroniona?

## Ćwiczenia

- `C14-1` — podstawowe: Wypisz dowody wymagane dla trzeci i podaj jego całkowicie bezpieczny odpowiednik. [Rozwiązanie](../rozwiazania/21_unsafe_soundness_i_model_pamieci/02_raw_pointers_aliasing_i_provenance.md#c14-1).
- `C14-2` — praktyczne: Odczytaj drugie u32 little-endian z bufora bajtów bez raw pointers i bez wymagań alignment. Przetestuj za krótki input. [Rozwiązanie](../rozwiazania/21_unsafe_soundness_i_model_pamieci/02_raw_pointers_aliasing_i_provenance.md#c14-2).
- `C14-3` — pogłębione: Oceń konstrukcję slice obejmującego dwie osobne, przypadkiem sąsiadujące alokacje. Zaproponuj reprezentację bez kopiowania i reprezentację ciągłą. [Rozwiązanie](../rozwiazania/21_unsafe_soundness_i_model_pamieci/02_raw_pointers_aliasing_i_provenance.md#c14-3).

## Powiązane tematy

- [`unsafe` i soundness](01_unsafe_i_soundness.md)
- [Layout i niezainicjalizowana pamięć](03_layout_alignment_i_uninitialized_memory.md)
- [Borrow checker i model pamięci](../19_runtime_pamiec_i_kompilator/01_borrow_checker_polonius_i_model_pamieci.md)
