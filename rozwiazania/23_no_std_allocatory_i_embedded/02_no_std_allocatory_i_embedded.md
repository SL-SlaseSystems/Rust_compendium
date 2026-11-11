[← Spis treści](../../README.md)

# Rozwiązania: Allocatory i sprzęt

## C19-1

Allocator respektuje rozmiar i alignment, zwraca rozłączne żywe bloki, poprawnie raportuje błąd alokacji, otrzymuje przy dealloc wyłącznie swój nadal żywy pointer i zgodny Layout, a zwolnienie następuje dokładnie raz po zakończeniu dostępu. Trzeba też zapewnić synchronizację, brak unwind i brak rekurencyjnej alokacji w implementacji. `Layout` może opisywać zero bajtów, ale `GlobalAlloc::alloc` wymaga niezerowego rozmiaru; obsługa ZST zwykle używa poprawnego sentinela bez rzeczywistej alokacji. Przekazanie zerowego żądania do niezgodnego API jest naruszeniem jego precondition.

## C19-2

Dla `#[cfg(target_has_atomic = "ptr")]` użyj `AtomicUsize` i `fetch_add`; `Relaxed` wystarcza tylko wtedy, gdy licznik jest samą statystyką i nie publikuje innych danych. Odczyt i zerowanie przez `swap(0, Relaxed)` tworzą jedną operację zamiast podatnej sekwencji load+store. Przepełnienie i utratę zdarzeń określ w kontrakcie licznika.

W drugim wariancie chroniony `Cell<usize>` lub inny zgodny magazyn jest dostępny wyłącznie w sekcji krytycznej biblioteki platformowej. Sekcja musi blokować wszystkie ISR używające licznika i uwzględniać rdzenie systemu. Nie trzymaj jej podczas I/O. Wyłączenie IRQ na jednym rdzeniu nie chroni przed drugim CPU ani DMA. Kod wariantów usuwaj przez atrybuty cfg; zwykły `if cfg!(...)` nie ukryje brakującego typu atomowego.

## C19-3

Stany to `Gotowy(bufor)`, `WTrakcie(transfer)` i `Zakonczony(bufor, wynik)`. Przejście do transferu przenosi własność pamięci do obiektu gwarantującego stabilny, dostępny dla DMA region; użytkownik nie otrzymuje slice do odczytu ani zapisu. Start wykonuje wymagane przygotowanie cache i bariery według platformy. IRQ zapisuje zakończenie dopiero po potwierdzeniu urządzenia.

`cancel` zleca stop, czeka na potwierdzenie końca wszystkich dostępów, wykonuje odpowiednią obsługę cache i dopiero zwraca bufor z liczbą poprawnie zapisanych bajtów. Timeout cancel nie oddaje bufora jako bezpiecznie wolnego, jeśli sprzęt nadal może pisać. Zapomnienie obiektu nie może uwolnić pamięci pod aktywnym transferem; posiadany magazyn można w takiej sytuacji wyciec, lecz pożyczony stos nie może wygasnąć. Sam Pin ani destructor bez protokołu zatrzymania nie realizują tej gwarancji.
