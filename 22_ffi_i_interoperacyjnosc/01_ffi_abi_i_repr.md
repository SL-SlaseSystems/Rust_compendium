[← Spis treści](../README.md)
<!-- status: expanded -->

# FFI, ABI i `repr`

## Cele

Po tym rozdziale potrafisz:

- porównać sygnaturę Rust z kontraktem obcego nagłówka i docelowym ABI;
- odróżnić pożyczony C string od przekazanego właściciela bufora;
- zdefiniować kanał błędu oraz zachowanie na granicy unwinding;

## Model — mechanizm i kontrakt

Foreign Function Interface łączy Rust z kodem o innym ABI. Kompilator nie
może sprawdzić kontraktu obcej funkcji, więc granica zwykle zawiera `unsafe`.

## Import funkcji C

W Edition 2024 blok obcych deklaracji jest `unsafe extern`:

~~~text
unsafe extern "C" {
    unsafe fn abs(input: std::ffi::c_int) -> std::ffi::c_int;
    unsafe fn funkcja_wymagajaca_kontraktu(ptr: *mut std::ffi::c_void);
}
~~~

Element można oznaczyć `safe` tylko wtedy, gdy każde wywołanie z argumentami
poprawnymi typowo jest bezpieczne. Samo ABI `"C"` nie weryfikuje sygnatury
z nagłówkiem.

## Eksport

Edition 2024 wymaga jawnego `unsafe(...)` dla atrybutów o globalnych
invariants, np.:

~~~text
#[unsafe(no_mangle)]
pub extern "C" fn suma(a: i32, b: i32) -> i32 {
    a.wrapping_add(b) // jawna, niepanikująca polityka przepełnienia
}
~~~

Autor musi zapewnić między innymi brak konfliktu symbolu. Eksportowana funkcja
nie powinna dopuścić, aby unwinding przekroczył ABI, które tego nie zezwala.

## Reprezentacja

- `repr(Rust)` — domyślna, z ograniczonymi gwarancjami;
- `repr(C)` — layout zgodny z regułami C dla wspieranych pól;
- `repr(transparent)` — reprezentacja pojedynczego pola niezerowego rozmiaru;
- `repr(u8)` i podobne — reprezentacja discriminantów enumu w dozwolonych
  formach;
- `repr(packed)` — usuwa część paddingu, ale tworzy niewyrównane pola.

~~~rust
#[repr(C)]
#[derive(Clone, Copy)]
struct Punkt {
    x: f64,
    y: f64,
}

fn main() {
    let p = Punkt { x: 1.0, y: 2.0 };
    assert_eq!(p.x + p.y, 3.0);
}
~~~

`String`, `Vec` i trait objects nie mają stabilnego układu odpowiednika C.
Referencje, `bool` oraz enumy wymagają zgodnej reprezentacji i kontraktu
ważności; nie wolno traktować dowolnych bajtów C jako poprawnych wartości Rust.

## C strings

`CString` posiada zakończony NUL-em bufor bez wewnętrznych NUL. `CStr` jest
pożyczonym widokiem. Wskaźnik z `CString::as_ptr` jest ważny tylko tak długo,
jak źródłowy `CString` nie został zniszczony lub zmieniony.

~~~rust
use std::ffi::CString;

fn main() {
    let s = CString::new("rust").unwrap();
    assert_eq!(s.as_bytes_with_nul(), b"rust\0");
}
~~~

## Ownership przez granicę

Dokumentuj, kto alokuje, kto zwalnia, długość bufora, nullability, aliasing,
threading, callback lifetime i error channel. Pamięć powinna zostać zwolniona
przez ten sam allocator/API, który ją utworzył, chyba że ABI gwarantuje inaczej.

## Sygnatura nie weryfikuje całej umowy

Deklaracja `unsafe extern "C"` jest zapewnieniem autora, że nazwa, konwencja wywołania, parametry i wynik odpowiadają rzeczywistej funkcji dla wybranego targetu. Linker zwykle rozpoznaje nazwę symbolu, a nie pełny typ C. Zgodne rozmiary liczb też nie gwarantują identycznego sposobu przekazywania agregatu. Szczegóły deklaracji oraz wymogi Edition 2024 opisuje [Rust Reference: external blocks](https://doc.rust-lang.org/reference/items/external-blocks.html), sprawdzone 2026-11-11.

Funkcję wolno oznaczyć `safe` w obcym bloku tylko wtedy, gdy każdy argument dopuszczony przez bezpieczną sygnaturę jest legalny. Klasyczna funkcja C `abs` nie jest dobrym przykładem: dla minimalnej wartości typu ze znakiem wynik nie jest reprezentowalny, a kontrakt C wymaga wykluczenia takiego przypadku. Źródło: [projekt normy C11 N1570, §7.22.6.1](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf#page=374), sprawdzony 2026-11-11. Wrapper może sprawdzić granicę, ale nie wolno ukryć tego obowiązku w deklaracji `safe fn abs`. Wybór typów `c_int`, `c_long` i `usize` też wymaga porównania z właściwym nagłówkiem; nie zakładaj równości `long` i `i64` na wszystkich platformach.

`#[repr(C)]` na zewnętrznej strukturze nie zmienia automatycznie reprezentacji typów jej pól. Gdy pole ma domyślny layout Rust, zewnętrzny atrybut nie legalizuje jego przekazywania jako odpowiednika C. `repr(transparent)` zapewnia odpowiednią reprezentację i ABI według swoich ograniczeń; nie dodaje walidacji zawartości. `bool` wymaga poprawnych wartości i zgodnego typu po stronie C; dowolny bajt statusu lepiej odebrać jako integer i sprawdzić go przed konwersją.

## Ownership napisów w działającym przykładzie

~~~rust
use std::ffi::{CStr, CString};
fn main() {
    let nazwa = CString::new("raport").unwrap();
    let ptr = nazwa.as_ptr();
    // SAFETY: ptr wskazuje do żywego CString, zakończonego NUL-em;
    // brak mutacji i odczyt nie wychodzi poza bufor.
    let widok = unsafe { CStr::from_ptr(ptr) };
    assert_eq!(widok.to_str().unwrap(), "raport");
    assert!(CString::new("a\0b").is_err());

    let owned = CString::new("przekazano").unwrap().into_raw();
    // SAFETY: dokładnie ten wskaźnik pochodzi z into_raw; nic go nie
    // zwolniło, a długość i pozycja końcowego NUL nie zostały zmienione.
    let odzyskana = unsafe { CString::from_raw(owned) };
    assert_eq!(odzyskana.as_bytes(), b"przekazano");
}
~~~

Pierwszy wskaźnik jest pożyczony: `CStr` nie zwalnia pamięci, a właścicielem pozostaje `nazwa`. Drugi wskaźnik przekazuje odpowiedzialność za odzyskanie alokacji; dopiero `from_raw` rekonstruuje jej właściciela dokładnie raz. Nie wolno przekazać go do dowolnego `free` ani utworzyć dwóch właścicieli. Kontrakt `CString` i jego surowych konwersji sprawdzono 2026-11-11 w [dokumentacji API](https://doc.rust-lang.org/std/ffi/struct.CString.html).

## Diagnostyka kompilatora

~~~compile_fail
#[no_mangle]
pub extern "C" fn kompendium_bledny_eksport(a: u32) -> u32 { a }
fn main() {}
~~~

W Edition 2024 atrybut wymaga formy `#[unsafe(no_mangle)]`, ponieważ autor odpowiada za globalne invariants nazwy symbolu. Zmiana składni nie dowodzi braku kolizji z biblioteką ani poprawności ABI. Ostrzeżenia `improper_ctypes` traktuj jako sygnał kontroli granicy, lecz brak ostrzeżeń nie jest kompletnym dowodem bezpieczeństwa.

Próba zwrócenia referencji do lokalnego `CString` zostanie odrzucona. Zwrócenie jego raw pointera może przejść typowanie, lecz nie przedłuża życia bufora. Napraw własność, nie sam typ: caller-provided buffer albo owned pointer z dedykowaną funkcją zwalniającą.

## Praktyka produkcyjna

Przygotuj tabelę kontraktu: reprezentacja, jednostki długości, dopuszczalność null, ownership, lifetime, aliasing, synchronizacja, callbacki i błędy. Sprawdź ją dla każdego targetu. Nagłówek wygenerowany przez narzędzie **third-party**, takie jak `cbindgen`, ogranicza ręczne rozbieżności, ale nie opisuje automatycznie wszystkich wymagań semantycznych. Testuj obie strony po zmianie ABI.

Panic na granicy ABI, które nie pozwala na unwind, może zakończyć proces; obcy wyjątek przekraczający niewłaściwą granicę ma jeszcze inne ryzyka. `catch_unwind` działa tylko dla przechwytywalnego unwind i nie cofa efektów wykonanych przed panic. Dla eksportu zdefiniuj niepanikujące mapowanie błędów oraz niezmienniki pozostające po porażce. `"C-unwind"` wymaga uzgodnienia obu stron, nie jest mechanicznym wyłączeniem problemu. Zobacz [Rustonomicon: FFI](https://doc.rust-lang.org/nomicon/ffi.html), sprawdzone 2026-11-11.

Długotrwałe ABI powinno umożliwiać rozszerzanie kontraktu, np. przez wersję protokołu, rozmiar przekazywanej struktury lub osobną funkcję negocjacji. Zmiana kolejności pól struktury `repr(C)` jest zmianą ABI nawet wtedy, gdy Rust kompiluje oba warianty. Konwersja między wersjami na granicy jest często tańsza niż utrzymywanie wewnętrznych typów podporządkowanych obcemu layoutowi.

## Sprawdź, czy rozumiesz

- Dlaczego znaleziony symbol nie potwierdza zgodności sygnatury?
- Co musi pozostać niezmienione między `CString::into_raw` i `from_raw`?
- Czy `repr(C)` struktury ustala layout każdego zagnieżdżonego typu Rust?

## Ćwiczenia

- `C16-1` — podstawowe: Wypisz brakujące elementy kontraktu funkcji C otrzymującej char* i długość. Uwzględnij zapis, kodowanie i własność. [Rozwiązanie](../rozwiazania/22_ffi_i_interoperacyjnosc/01_ffi_abi_i_repr.md#c16-1).
- `C16-2` — praktyczne: Zaprojektuj bezpieczne API dla obcej funkcji czytającej C string tylko podczas wywołania. Określ właściciela i obsługę wewnętrznego NUL. [Rozwiązanie](../rozwiazania/22_ffi_i_interoperacyjnosc/01_ffi_abi_i_repr.md#c16-2).
- `C16-3` — pogłębione: Zaprojektuj eksport obliczenia sumy u64 do C z kontrolą przepełnienia i kodem błędu. Opisz ABI wyniku bez przenoszenia Result przez granicę. [Rozwiązanie](../rozwiazania/22_ffi_i_interoperacyjnosc/01_ffi_abi_i_repr.md#c16-3).

## Powiązane tematy

- [FFI, bezpieczne otoczki i UB](../22_ffi_i_interoperacyjnosc/02_ffi_safe_wrappers_i_ub.md)
- [Raw pointers i provenance](../21_unsafe_soundness_i_model_pamieci/02_raw_pointers_aliasing_i_provenance.md)
- [Layout i niezainicjalizowana pamięć](../21_unsafe_soundness_i_model_pamieci/03_layout_alignment_i_uninitialized_memory.md)
