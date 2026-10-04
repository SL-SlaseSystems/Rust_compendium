[← Spis treści](../README.md)

# FFI, bezpieczne otoczki i UB

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

## Powiązane tematy

- [Podstawy FFI, ABI i `repr`](../22_ffi_i_interoperacyjnosc/01_ffi_abi_i_repr.md)
- [Raw pointers i provenance](../21_unsafe_soundness_i_model_pamieci/02_raw_pointers_aliasing_i_provenance.md)
- [`unsafe` i soundness](../21_unsafe_soundness_i_model_pamieci/01_unsafe_i_soundness.md)
