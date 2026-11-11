[← Spis treści](../README.md)
<!-- status: expanded -->

# `no_std`, allocatory i embedded

## Cele

Po tym rozdziale potrafisz:

- wyznaczyć layout alokacji i poprawnie rozliczyć parę alokacja–zwolnienie;
- odróżnić volatile, atomiki i sekcję krytyczną na konkretnym targetcie;
- opisać własność bufora DMA podczas transferu, kończenia i anulowania;

## Model — mechanizm i kontrakt

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

- stabilny adres bufora i jawny kontrakt jego przenoszenia;
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

## Jawne obliczanie layoutu

Nie obliczaj rozmiaru przez `n * size_of::<T>()` bez sprawdzania przepełnienia. API `Layout` waliduje granice, alignment oraz padding. `Layout::array` nadaje się do tablic, a `extend` zwraca również offset dołączanego pola. Przed użyciem całego układu uwzględnij końcowy padding. Wymagania sprawdzono 2026-11-11 w [Layout](https://doc.rust-lang.org/core/alloc/struct.Layout.html).

~~~rust
use std::alloc::Layout;
fn main() {
    let naglowek = Layout::new::<u8>();
    let elementy = Layout::array::<u32>(3).unwrap();
    let (razem, offset) = naglowek.extend(elementy).unwrap();
    let razem = razem.pad_to_align();
    assert_eq!(offset % std::mem::align_of::<u32>(), 0);
    assert!(razem.size() >= offset + 3 * std::mem::size_of::<u32>());
    assert!(Layout::from_size_align(4, 3).is_err());
}
~~~

Przykład nie alokuje pamięci. Sam poprawny layout nie dowodzi inicjalizacji elementów ani zgodności późniejszego `dealloc`. Zwrócony pointer musi pochodzić z właściwego API, być nadal żywy i zostać zwolniony z pasującymi parametrami. Rozmiar zero jest dozwolonym opisem `Layout`, lecz `GlobalAlloc::alloc` ma osobny kontrakt wykluczający żądania zerowego rozmiaru. Nie myl tych dwóch warstw.

Własny allocator nie powinien logować przez `format!`, jeśli to ponownie wywołuje ten sam allocator. Może to prowadzić do rekurencji lub deadlocka. Metody `GlobalAlloc` nie mogą unwindować; uwzględnij błędy arytmetyki, atomiki i blokady. Odrębnie przeanalizuj wielowątkowość i przerwania. Dokładne wymagania zawiera [GlobalAlloc](https://doc.rust-lang.org/std/alloc/trait.GlobalAlloc.html), sprawdzone 2026-11-11. Licznik alokacji jest narzędziem obserwacji, a nie podstawą niezmiennika bezpieczeństwa, bo optymalizator może usuwać nieobserwowalne alokacje.

## Diagnostyka kompilatora

Brak `AtomicU64` albo metody CAS na wybranym targetcie jest ograniczeniem platformy, a nie sygnałem do użycia zwykłego `static mut`. Konfigurację szerokości atomików sprawdzaj przez `rustc --print cfg --target ...` i odpowiednie `#[cfg(target_has_atomic = "...")]`. Kontrakt opcji podaje [Reference: conditional compilation](https://doc.rust-lang.org/reference/conditional-compilation.html#target_has_atomic), zweryfikowane 2026-11-11. `cfg!` zwraca stałą logiczną, ale nie usuwa nieobsługiwanych nazw z typowania obu gałęzi jak atrybut `#[cfg]`.

Błędy linkera dotyczące allocatora i panic handlera rozwiązuj w składzie finalnego binarium. Biblioteka zależna nie powinna bezwarunkowo narzucać globalnego allocatora całej aplikacji. Ręczne dostarczenie symbolu o podobnej nazwie bez zgodnego ABI nie naprawia kontraktu runtime’u. Nie kompiluj embedded tylko dla hosta: inne szerokości wskaźników i dostępne atomiki ujawnią dodatkowe problemy.

## Praktyka produkcyjna

Sekcja krytyczna musi wykluczyć wszystkich uczestników chronionego dostępu. Wyłączenie lokalnych przerwań nie zatrzymuje drugiego rdzenia ani kontrolera DMA. Ma też koszt: zwiększa opóźnienie obsługi IRQ. Przetrzymanie locka w ISR, gdy przerwany kod posiada ten sam lock, może zablokować system. Wzorce oraz ograniczenia omawia [Embedded Rust Book: concurrency](https://docs.rust-embedded.org/book/concurrency/), sprawdzone 2026-11-11. Projektuj krótki ISR przekazujący pracę do pętli głównej.

Volatile zapewnia odpowiednią obserwowalność dostępu według kontraktu operacji, lecz nie jest synchronizacją między wątkami ani obietnicą jednej instrukcji dla dowolnego typu. Rejestr może mieć semantykę „odczyt kasuje flagę” lub „zapis jedynki kasuje bit”; ogólne read–modify–write może wtedy uszkodzić stan. Prawidłowy adres, szerokość i sekwencję określa dokumentacja układu. Rozróżnienie zwykłej alokacji i MMIO poza nią opisuje [read_volatile](https://doc.rust-lang.org/std/ptr/fn.read_volatile.html), zweryfikowane 2026-11-11.

DMA jest drugim wykonawcą dostępu do bufora. Sam `Pin` może stabilizować obiekt zgodnie z kontraktem typu, ale nie blokuje CPU ani nie gwarantuje adresu odpowiedniego dla DMA, regionu pamięci i spójności cache. Transfer powinien posiadać bufor przez cały okres pracy urządzenia. `wait` oddaje go po potwierdzonym zakończeniu, a anulowanie najpierw zatrzymuje sprzęt i potwierdza brak dalszych dostępów. Guard z samym dropem nie może pozwolić, aby `mem::forget` pozostawiło urządzenie zapisujące do później zwolnionego, pożyczonego bufora.

Budżet czasu wyznaczaj dla najgorszego przypadku: zapełnionej kolejki, błędu magistrali, restartu i braku miejsca. Dynamiczny allocator może mieć fragmentację i zmienny czas operacji; stałe pule upraszczają limit zasobów, ale wymagają polityki wyczerpania. Mapa linkera pokazuje statyczne sekcje, natomiast szczyt stosu, przerwania i dynamiczna pamięć wymagają osobnych pomiarów. Test hostowy layoutu nie potwierdza poprawnego cache maintenance na urządzeniu.

## Sprawdź, czy rozumiesz

- Dlaczego poprawny `Layout` rozmiaru zero nie uprawnia do dowolnego `GlobalAlloc::alloc`?
- Jakie źródła współbieżności pomija wyłączenie przerwań jednego rdzenia?
- Co musi się wydarzyć przed oddaniem bufora po anulowaniu DMA?

## Ćwiczenia

- `C19-1` — podstawowe: Wypisz pięć wymagań pary alloc/dealloc oraz odróżnij Layout o rozmiarze zero od żądania GlobalAlloc. [Rozwiązanie](../rozwiazania/23_no_std_allocatory_i_embedded/02_no_std_allocatory_i_embedded.md#c19-1).
- `C19-2` — praktyczne: Zaprojektuj dwie implementacje licznika zdarzeń: dla targetu z atomikami ptr i dla targetu wymagającego sekcji krytycznej. Podaj granice obu rozwiązań. [Rozwiązanie](../rozwiazania/23_no_std_allocatory_i_embedded/02_no_std_allocatory_i_embedded.md#c19-2).
- `C19-3` — pogłębione: Zaprojektuj stany transferu DMA i kontrakt cancel. Uwzględnij stabilny adres, cache, przerwanie zakończenia i zapomnienie guarda. [Rozwiązanie](../rozwiazania/23_no_std_allocatory_i_embedded/02_no_std_allocatory_i_embedded.md#c19-3).

## Powiązane tematy

- [Podstawy WebAssembly, `no_std` i embedded](../23_no_std_allocatory_i_embedded/01_wasm_no_std_i_embedded.md)
- [Layout i `MaybeUninit`](../21_unsafe_soundness_i_model_pamieci/03_layout_alignment_i_uninitialized_memory.md)
- [Atomiki i memory ordering](../10_wspolbieznosc/05_atomics_i_memory_ordering.md)
