[← Spis treści](../README.md)
<!-- status: expanded -->

# FFI, bezpieczne otoczki i UB

## Cele

Po tym rozdziale potrafisz:

- udowodnić własność opaque handle od utworzenia do jednego zwolnienia;
- zweryfikować inicjalizację bufora wyjściowego przed udostępnieniem go jako slice;
- zaprojektować protokół callbacków z uwzględnieniem równoległości i wyrejestrowania;

## Model — mechanizm i kontrakt

Granica FFI łączy dwa zestawy invariants. Typy Rust nie naprawią błędu ABI,
złego ownership ani UB wykonanego po stronie C; UB w obcym kodzie wpływa na
cały program.

## Wzorzec opaque handle

Poniższy przykład symuluje C API w jednym pliku, aby pokazać wrapper:

~~~rust
use std::ptr::NonNull;

#[repr(C)]
struct Raw {
    wartosc: i32,
}

unsafe extern "C" fn raw_new(x: i32) -> *mut Raw {
    Box::into_raw(Box::new(Raw { wartosc: x }))
}

unsafe extern "C" fn raw_get(ptr: *const Raw) -> i32 {
    // SAFETY: kontrakt funkcji wymaga ważnego pointera do Raw.
    unsafe { (*ptr).wartosc }
}

unsafe extern "C" fn raw_free(ptr: *mut Raw) {
    if !ptr.is_null() {
        // SAFETY: kontrakt wymaga pointera zwróconego przez raw_new,
        // niezwolnionego wcześniej.
        unsafe { drop(Box::from_raw(ptr)) };
    }
}

struct Handle(NonNull<Raw>);

impl Handle {
    fn new(x: i32) -> Option<Self> {
        // SAFETY: raw_new akceptuje każde i32.
        NonNull::new(unsafe { raw_new(x) }).map(Self)
    }

    fn get(&self) -> i32 {
        // SAFETY: self posiada żywy handle do czasu Drop.
        unsafe { raw_get(self.0.as_ptr()) }
    }
}

impl Drop for Handle {
    fn drop(&mut self) {
        // SAFETY: ownership jest wyłączne, a Drop uruchamia free raz.
        unsafe { raw_free(self.0.as_ptr()) };
    }
}

fn main() {
    let h = Handle::new(42).expect("alokacja");
    assert_eq!(h.get(), 42);
}
~~~

Prawdziwa obca funkcja może zwrócić null, ustawić errno, wymagać inicjalizacji
globalnej lub mieć inny allocator. Wrapper musi udokumentować każdy przypadek.

## `Send` i `Sync`

`NonNull<T>` nie jest automatycznym dowodem bezpieczeństwa wątkowego.
Implementuj `unsafe impl Send/Sync for Handle` tylko, gdy dokumentacja obcej
biblioteki gwarantuje transfer/współdzielenie, a callbacki i globalny stan
również są bezpieczne. Czasem właściwą abstrakcją jest jeden worker thread i
kanał.

## Bufory

Kontrakt bufora musi podać:

- pointer i długość w bajtach lub elementach;
- pojemność, jeśli obcy kod zapisuje;
- alignment i typ elementu;
- inicjalizowany zakres po powrocie;
- czy pointer może być null dla długości zero;
- kto i jak realokuje oraz zwalnia.

Nie twórz `slice::from_raw_parts(null, 0)`: funkcja wymaga non-null i aligned
pointera także dla pustego slice. Użyj `NonNull::dangling().as_ptr()` jako
odpowiednio wyrównanego sentinela, jeśli ABI pozwala.

## Callback

Zwykle przekazuje się function pointer plus `*mut c_void` jako context.
Trampoline:

- rekonstruuje poprawny typ contextu;
- przechwytuje panic przed ABI `"C"`;
- nie używa contextu po unregister/free;
- synchronizuje równoległe callbacki;
- respektuje reentrancy.

`Box::into_raw` przekazuje ownership, `Box::from_raw` odzyskuje je dokładnie
raz. Sama kopia pointera nie jest nowym ownerem.

## Unwinding

Panic nie może przekroczyć ramki ABI, które nie zezwala na unwinding.
Na granicy eksportu można użyć `catch_unwind` i zamienić wynik na kod błędu.
Nie wszystkie panic da się przechwycić, np. przy strategii abort.
ABI `"C-unwind"` ma osobne reguły; używaj tylko przy kontrakcie obu stron.

## Błędy i stringi

Nie zwracaj pointera do tymczasowego `CString`. Wybierz:

- caller-provided buffer;
- owned pointer plus osobna funkcja free;
- kod błędu i funkcja kopiująca ostatni błąd;
- struct `repr(C)` z pointerem oraz długością.

Zapisz encoding. `char*` nie gwarantuje UTF-8.

## Dowód otoczki uchwytu

W przykładzie `Handle` posiada nie-null pointer uzyskany wyłącznie z `raw_new`. Pole jest prywatne, typ nie implementuje `Clone` ani kopiowania, a konstruktor nie przyjmuje dowolnego obcego adresu. `get(&self)` może czytać, ponieważ uchwyt żyje do `Drop`, a symulowane API nie mutuje wartości przez współdzielone wywołanie. `Drop` oddaje dokładnie pierwotny pointer do właściwego destruktora, który odtwarza `Box` raz. Panika alokacji w tym przykładzie nie jest symulacją null zwracanego przez prawdziwe C API.

Wycieczka pointera przez metodę `as_raw` wymaga dodatkowego kontraktu: użytkownik nie może zwolnić go ani zachować poza życiem właściciela. Bezpieczna metoda `from_raw` przyjmująca dowolny pointer zniszczyłaby dowód. Oznacz ją `unsafe` z sekcją `# Safety` albo ukryj całkowicie. Bezpieczny `mem::forget(handle)` może wyciec zasobem, ale nie może spowodować użycia zwolnionej pamięci przez pozostałe bezpieczne API.

## Bufor wyjściowy i liczba zapisanych elementów

Poniższe API jest lokalną symulacją, bez linkowania biblioteki C. Jego kontrakt mówi, że zapisuje najwyżej `cap` bajtów i zwraca liczbę rzeczywiście zainicjalizowanych miejsc.

~~~rust
/// # Safety
/// Dla cap > 0 dst musi wskazywać cap bajtów jednej żywej alokacji,
/// dostępnej do wyłącznego zapisu. Funkcja nie zachowuje wskaźnika.
unsafe extern "C" fn wypelnij(dst: *mut u8, cap: usize) -> usize {
    let n = cap.min(3);
    for i in 0..n {
        // SAFETY: i < n <= cap; kontrakt daje wyłączny zakres zapisu.
        unsafe { dst.add(i).write(7) };
    }
    n
}
fn pobierz() -> Vec<u8> {
    let mut wynik = Vec::<u8>::with_capacity(8);
    // SAFETY: Vec udostępnia cap bajtów wyłącznej pamięci, które obca
    // funkcja wyłącznie inicjalizuje. Bufor nie jest realokowany.
    let n = unsafe { wypelnij(wynik.as_mut_ptr(), wynik.capacity()) };
    assert!(n <= wynik.capacity());
    // SAFETY: kontrakt wypelnij zapewnia inicjalizację prefixu 0..n.
    // Te bajty od tej chwili należą do Vec i mogą być bezpiecznie czytane.
    unsafe { wynik.set_len(n) };
    wynik
}
fn main() { assert_eq!(pobierz(), [7, 7, 7]); }
~~~

`with_capacity` rezerwuje miejsce, ale nie tworzy ośmiu zainicjalizowanych elementów. Długość zmienia się dopiero po udanym wypełnieniu. Sprawdzenie `n <= capacity` nie naprawi obcej funkcji, która już zapisała poza bufor: przestrzeganie limitu przez producenta pozostaje wymaganiem bezpieczeństwa. Dla typów z `Drop` trzeba także posprzątać częściowo utworzony prefix przy błędzie. Przykład bajtowy nie przenosi automatycznie tego dowodu na dowolne `T`.

## Diagnostyka kompilatora

Brak automatycznego `Send` lub `Sync` dla uchwytu z `NonNull` jest powodem do odczytania kontraktu biblioteki. `unsafe impl` nie uruchamia ochrony wątku. Jeśli API wymaga wywołań z wątku utworzenia, przechowaj uchwyt w dedykowanym workerze i wymieniaj posiadane komunikaty. Nie przesyłaj surowego adresu przez integer tylko po to, aby ominąć kontrolę traitów.

Błąd użycia po move przy zamykaniu uchwytu jest często pożądany. `close(self)` może konsumować ownera, odebrać jego pointer i zapobiec ponownemu zwolnieniu przez `Drop`. Jeżeli metoda przyjmuje `&mut self`, potrzebny jest jawny stan zamknięty i zablokowanie późniejszego `get`. Prostszy model liniowej własności zmniejsza powierzchnię błędów.

## Praktyka produkcyjna

Rejestracja callbacku potrzebuje właściciela contextu, gwarancji stabilnego adresu i dokładnego momentu końca wywołań. `unregister` musi potwierdzić, że żaden callback nie jest już aktywny i żaden nowy nie wystartuje, zanim zwolnisz context. Sam powrót funkcji rejestracji niczego nie mówi o przyszłych wywołaniach. Równoległość i reentrancy wymagają osobnego protokołu, nawet w aplikacji z jednym głównym wątkiem. Wskazówki granicy opisuje [Rustonomicon: FFI](https://doc.rust-lang.org/nomicon/ffi.html), sprawdzone 2026-11-11.

Jeżeli bezpieczny guard pożycza dane ze stosu i dopiero w `Drop` wyrejestrowuje callback, `mem::forget` może zostawić obcy kod z adresem nieżywej zmiennej. Bezpieczeństwo nie może zakładać obowiązkowego dropu; wybierz posiadany context o życiu zgodnym z rejestracją albo bezpieczny protokół scoped, który nie pozwala pozostawić pracy po wyjściu zakresu. Po stronie callbacku zamień panikę na błąd zgodnie z ABI, nie wywołuj dowolnego kodu Rust z surowego handlera sygnału.

Dokumentuj ograniczenia testu: lokalna symulacja nie sprawdza nagłówka C, linkera, wersji biblioteki ani zachowania jej wątków. Potrzebne są testy integracyjne z rzeczywistą zależnością, kontrola sanitizerami według platformy i ręczny przegląd kontraktu. Żaden wrapper nie izoluje procesu od UB wykonanego w obcej bibliotece.

## Sprawdź, czy rozumiesz

- Dlaczego prywatność pola i brak `Clone` są częścią dowodu `Handle`?
- Czemu kontrola długości po FFI nie zabezpiecza przed wcześniejszym zapisem poza bufor?
- Jakie potwierdzenie musi dać unregister przed zwolnieniem contextu?

## Ćwiczenia

- `C17-1` — podstawowe: Wyjaśnij, co zepsułaby implementacja Clone tworząca drugi Handle z tym samym NonNull. Podaj poprawne alternatywy. [Rozwiązanie](../rozwiazania/22_ffi_i_interoperacyjnosc/02_ffi_safe_wrappers_i_ub.md#c17-1).
- `C17-2` — praktyczne: Przeanalizuj wypelnij dla cap 0, 2 i 8. Wskaż liczbę zainicjalizowanych bajtów i wymagany moment set_len. [Rozwiązanie](../rozwiazania/22_ffi_i_interoperacyjnosc/02_ffi_safe_wrappers_i_ub.md#c17-2).
- `C17-3` — pogłębione: Zaprojektuj protokół rejestracji callbacku, który może być wywołany równolegle. Uwzględnij zatrzymanie, aktywne wywołania, panic i własność contextu. [Rozwiązanie](../rozwiazania/22_ffi_i_interoperacyjnosc/02_ffi_safe_wrappers_i_ub.md#c17-3).

## Powiązane tematy

- [Podstawy FFI, ABI i `repr`](../22_ffi_i_interoperacyjnosc/01_ffi_abi_i_repr.md)
- [Raw pointers i provenance](../21_unsafe_soundness_i_model_pamieci/02_raw_pointers_aliasing_i_provenance.md)
- [`unsafe` i soundness](../21_unsafe_soundness_i_model_pamieci/01_unsafe_i_soundness.md)
