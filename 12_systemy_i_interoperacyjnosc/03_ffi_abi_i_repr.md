[← Spis treści](../README.md)

# FFI, ABI i `repr`

Foreign Function Interface łączy Rust z kodem o innym ABI. Kompilator nie
może sprawdzić kontraktu obcej funkcji, więc granica zwykle zawiera `unsafe`.

## Import funkcji C

W Edition 2024 blok obcych deklaracji jest `unsafe extern`:

~~~text
unsafe extern "C" {
    safe fn abs(input: std::ffi::c_int) -> std::ffi::c_int;
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
    a + b
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

Nie każdy typ Rust jest FFI-safe. Referencje, `String`, `Vec`, trait objects,
`bool` i niektóre enumy wymagają jawnego kontraktu lub wrappera.

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

## Powiązane tematy

- [FFI, bezpieczne otoczki i UB](../zaawansowane/11_ffi_safe_wrappers_i_ub.md)
- [Raw pointers i provenance](../zaawansowane/02_raw_pointers_aliasing_i_provenance.md)
- [Layout i niezainicjalizowana pamięć](../zaawansowane/03_layout_alignment_i_uninitialized_memory.md)
