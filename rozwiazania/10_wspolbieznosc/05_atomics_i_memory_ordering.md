[← Spis treści](../../README.md)

# Rozwiązania: Atomiki i memory ordering

[Rozdział źródłowy](../../10_wspolbieznosc/05_atomics_i_memory_ordering.md).

## B17-1

~~~rust
use std::sync::atomic::{AtomicUsize,Ordering};
fn main(){let n=AtomicUsize::new(0);std::thread::scope(|s|{for _ in 0..4{s.spawn(||{n.fetch_add(1,Ordering::Relaxed);});}});assert_eq!(n.load(Ordering::Relaxed),4);}
~~~
Powrót ze scope następuje po dołączeniu wątków. Licznik nie publikuje innych danych.

## B17-2

Producent: zapis payloadu sequenced-before zapis flagi Release. Konsument: odczyt Acquire pobiera `true` z tego Release, więc zapis flagi synchronizes-with odczyt flagi. Odczyt flagi sequenced-before odczyt payloadu. Przez złożenie zapis payloadu happens-before jego odczyt. Warunki: jedna publikacja, brak późniejszego niesynchronizowanego nadpisania, żywe dane oraz poprawna własność. Odczyt `false` nie daje tej samej krawędzi, a flaga Relaxed nie tworzy wymaganej synchronizacji.

## B17-3

Udany CAS Acquire odczytuje stan oddany przez Release poprzedniego właściciela. Porażka tylko dowiaduje się, że zasób jest zajęty; jeżeli kod nie czyta wtedy chronionego payloadu, wystarcza Relaxed. Nie wynika z tego bezpieczeństwo dostępu do `T`: nadal trzeba udowodnić wyłączność, czas życia, sposób zwracania guardu i zwolnienie po panic. Przykład operujący samą atomiką nie implementuje tych warstw i nie jest produkcyjną blokadą.

