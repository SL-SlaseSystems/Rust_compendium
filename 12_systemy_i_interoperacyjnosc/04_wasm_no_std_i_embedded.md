[← Spis treści](../README.md)

# WebAssembly, `no_std` i embedded

Te trzy obszary rezygnują z części założeń zwykłej aplikacji systemowej, ale
nie są tym samym targetem ani modelem wykonania.

## WebAssembly

Popularne targety:

- `wasm32-unknown-unknown` — minimalne środowisko, np. przeglądarka przez
  JavaScript glue;
- targety WASI — system interface dla runtime’u WASI, zależny od wspieranej
  wersji i komponentów toolchainu.

~~~text
rustup target add wasm32-unknown-unknown
cargo build --release --target wasm32-unknown-unknown
~~~

`wasm-bindgen` i `wasm-pack` są **third-party**. Ułatwiają integrację z JS,
ale generują warstwę ABI i glue. Minimalizuj przekazywanie wielu małych
wartości przez granicę; kopiowanie pamięci może dominować koszt.

WebAssembly nie oznacza automatycznie sandboxu o dowolnych gwarancjach.
Możliwości modułu zależą od host imports, runtime’u i konfiguracji.

## `#![no_std]`

~~~text
#![no_std]

pub fn suma(dane: &[u32]) -> u32 {
    dane.iter().copied().sum()
}
~~~

Ten fragment jest biblioteką, więc nie potrzebuje `main` ani panic handlera.
`no_std` usuwa automatyczne linkowanie `std`, ale udostępnia `core`.
Jeżeli środowisko ma allocator, crate `alloc` daje `Vec`, `String` i `Box`.

## Co zapewniają warstwy

- `core` — typy i traits bez OS ani alokatora;
- `alloc` — kolekcje wymagające globalnego alokatora;
- `std` — I/O, wątki, sieć, filesystem i integracja platformy.

Feature `std` biblioteki powinien być addytywny:

~~~text
#![cfg_attr(not(feature = "std"), no_std)]

#[cfg(feature = "std")]
impl std::error::Error for MojBlad {}
~~~

## Bare metal

Binarium bez runtime’u może wymagać `#![no_main]`, własnego punktu wejścia,
linker scriptu, panic handlera, target specification i obsługi przerwań.
Szczegóły są zależne od architektury i crate’ów embedded.

Volatile nie oznacza atomic ani synchronizacji. Dostęp do memory-mapped I/O
powinien używać właściwych volatile operations i typów HAL. `static mut`
łatwo łamie aliasing; preferuj bezpieczne singletony i critical sections.

## Embedded ecosystem

Traits embedded-hal i implementacje PAC/HAL są **third-party**, choć
utrzymywane w szerokim ekosystemie Rust Embedded. Oddziel kod sterownika
oparty na traits od konkretnego mikrokontrolera. Testuj logikę na hoście,
a warstwę sprzętową na urządzeniu lub emulatorze.

## Rozmiar i panic

W embedded ważne są `opt-level = "s"`/`"z"`, LTO, `panic = "abort"` i analiza
sekcji linkera. Każda zmiana ma trade-off z czasem, debugowalnością i
wydajnością. Mierz wynik binarny.

## Powiązane tematy

- [`no_std`, allocatory i embedded — zaawansowane](../zaawansowane/12_no_std_allocatory_i_embedded.md)
- [Profile i build scripts](../07_moduly_i_cargo/04_profile_build_scripts_i_publikowanie.md)
- [FFI i ABI](03_ffi_abi_i_repr.md)
