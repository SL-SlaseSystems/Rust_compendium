[← Spis treści](../README.md)

# `no_std`, allocatory i embedded

`no_std` oznacza brak automatycznej zależności od `std`, nie brak języka ani
wszystkich bibliotek. `core` działa bez systemu operacyjnego; `alloc` wymaga
globalnego alokatora.

## Warstwowa biblioteka

Szkic źródła:

~~~text
#![cfg_attr(not(feature = "std"), no_std)]

#[cfg(feature = "alloc")]
extern crate alloc;

#[cfg(feature = "alloc")]
pub fn kopia(dane: &[u8]) -> alloc::vec::Vec<u8> {
    dane.to_vec()
}

#[cfg(feature = "std")]
impl std::error::Error for Blad {}
~~~

Feature `std` powinien implikować `alloc`, a oba być addytywne. Testuj:

~~~text
cargo check --no-default-features
cargo check --no-default-features --features alloc
cargo check --features std
~~~

## Globalny allocator

Program korzystający z `alloc` musi dostarczyć `#[global_allocator]` albo
otrzymać go z platformy. Trait `GlobalAlloc` jest unsafe: implementacja musi
respektować `Layout`, alignment, odpowiedni pointer, parę alloc/dealloc i
zachowanie przy błędzie.

Szkic deklaracji:

~~~text
#[global_allocator]
static ALOKATOR: MojAllocator = MojAllocator;
~~~

Nie pisz allocatora bez potrzeby. Błąd dotyczy całego programu. Stabilne
`Box`/`Vec` używają globalnego alokatora; rozbudowane per-container allocator
APIs nadal obejmują funkcjonalności nightly, które trzeba sprawdzić w
Unstable Book.

## `Layout`

`Layout::from_size_align` sprawdza potęgę dwójki alignmentu i granice rozmiaru.
Łączenie layoutów wymaga uwzględnienia paddingu. ZST może nie potrzebować
alokacji, ale pointer nadal musi spełniać wymagania API.

## Panic i punkt wejścia

Bare-metal binarium zwykle definiuje `#[panic_handler]` i niestandardowy entry
point. `panic = "abort"` nie tworzy automatycznie handlera. Testy hostowe mogą
używać `std` przez warunkowy build, podczas gdy target używa `no_std`.

## Przerwania

Interrupt może nastąpić między instrukcjami. Zwykłe `&mut static` nie jest
bezpieczne. Opcje:

- atomiki wspierane przez target;
- critical section wyłączająca odpowiednią klasę przerwań;
- lock-free SPSC queue o udowodnionym protokole;
- przeniesienie minimalnej pracy z ISR do głównej pętli.

Nie każda architektura ma atomiki wszystkich szerokości. `target_has_atomic`
pozwala warunkować kod. Volatile zapewnia wykonanie dostępu do MMIO, ale nie
atomowość ani happens-before.

## MMIO

Rejestry sprzętowe mają side effects i specjalne reguły. Używaj PAC/HAL
generowanego dla układu. `read_volatile`/`write_volatile` wymagają poprawnego
adresu oraz typu; nie legalizują aliasingu zwykłej pamięci i nie zastępują
barier sprzętowych.

## DMA

DMA współdzieli bufor ze sprzętem. Trzeba zapewnić:

- pinning/stabilny adres;
- właściwy lifetime i brak CPU access w czasie transferu;
- alignment oraz wymagany region pamięci;
- cache maintenance i bariery platformowe;
- obsługę anulowania i przerwania;
- odzyskanie ownership po zakończeniu.

Dobry HAL modeluje stan transferu typem i oddaje bufor dopiero po zakończeniu.

## Rozmiar

Analizuj map file i sekcje. LTO, `opt-level = "s"/"z"`, brak formatowania,
panic abort i ograniczenie generics mogą zmniejszyć binarium, ale wpływają na
debugowanie i szybkość. `cargo size`/`cargo bloat` są zależne od narzędzi
ekosystemu.

## Powiązane tematy

- [Podstawy WebAssembly, `no_std` i embedded](../12_systemy_i_interoperacyjnosc/04_wasm_no_std_i_embedded.md)
- [Layout i `MaybeUninit`](03_layout_alignment_i_uninitialized_memory.md)
- [Atomiki i memory ordering](08_atomics_i_memory_ordering.md)
