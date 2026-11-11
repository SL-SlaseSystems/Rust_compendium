[← Spis treści](../../README.md)

# Rozwiązania: Anulowanie, timeouty i kod blokujący

[Rozdział źródłowy](../../11_async_rust/04_anulowanie_timeouty_i_blocking.md).

## B22-1

~~~rust
fn main(){let mut bufor=Vec::new();bufor.extend_from_slice(b"ab");assert_eq!(bufor.len(),2);bufor.extend_from_slice(b"cd");assert_eq!(bufor,b"abcd");}
~~~
Istotna własność: bufor należy do stanu połączenia, a nie tymczasowej future próby.

## B22-2

~~~rust
use std::time::{Duration,Instant};
fn pozostalo(deadline:Instant,teraz:Instant)->Duration{deadline.saturating_duration_since(teraz)}
fn main(){let start=Instant::now();let koniec=start+Duration::from_secs(5);assert_eq!(pozostalo(koniec,start+Duration::from_secs(3)),Duration::from_secs(2));assert_eq!(pozostalo(koniec,start+Duration::from_secs(8)),Duration::ZERO);}
~~~
Saturacja eliminuje ujemny budżet; kolejna próba nie odnawia pierwotnych pięciu sekund.

## B22-3

Przestań przyjmować żądania, a zadaniu blokującemu przekaż token sprawdzany między ograniczonymi porcjami pracy. Jeśli zewnętrzne API nie ma limitu oczekiwania ani anulowania, proces nie może obiecać szybkiego graceful shutdown tej pracy; izoluj ją w osobnym procesie lub zaakceptuj jawny limit kończenia procesu. Dla płatności zapisz identyfikator idempotencji przed wysłaniem. Timeout oznacza stan „wynik nieznany”; uzgodnij go z serwerem tym samym identyfikatorem, zamiast tworzyć nową płatność. Abort taska nie jest rollbackiem płatności.

