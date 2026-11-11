[← Spis treści](../../README.md)

# Rozwiązania: Lock-free i problem ABA

[Rozdział źródłowy](../../10_wspolbieznosc/06_lock_free_i_aba.md).

## B18-1

~~~rust
use std::sync::atomic::{AtomicUsize,Ordering::SeqCst};
fn main(){let a=AtomicUsize::new(7);let stare=a.load(SeqCst);a.store(8,SeqCst);a.store(7,SeqCst);assert_eq!(a.compare_exchange(stare,9,SeqCst,SeqCst),Ok(7));}
~~~

## B18-2

Faza 1 odłącza węzeł poprawnie zsynchronizowanym CAS. Faza 2 oznacza go jako retired i zachowuje alokację. Faza 3 dowodzi, że żaden czytelnik nie może już używać wcześniejszego pointera, zgodnie z konkretnym protokołem hazard pointers lub epok. Dopiero faza 4 uruchamia destruktor i zwalnia alokację. Sam brak węzła w `head` nie jest warunkiem fazy 3. Jeśli czytelnik może zostać zawieszony z pointerem, natychmiastowe `Box::from_raw` jest nieuzasadnione.

## B18-3

Dla przeciążonej kolejki mutex może usypiać oczekujących i ograniczać zużycie CPU, lecz wstrzymany właściciel blokuje innych. Lock-free daje postęp systemu według kontraktu algorytmu, lecz pojedynczy uczestnik może głodować, a retry zwiększać ogony opóźnień. Reclamation może przechowywać wiele retired nodes. Porównanie obejmuje stabilną liczbę producentów/konsumentów, wielkość payloadu, p50/p99, pamięć szczytową i shutdown. Wyniku nie da się uczciwie przesądzić bez pomiaru na targetcie; brak mutexa nie jest wynikiem benchmarku.

