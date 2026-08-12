[← Spis treści](../README.md)

# Anulowanie, timeouty i kod blokujący

Najczęstszy model anulowania future to jej upuszczenie. Destruktor usuwa stan,
ale efekty wykonane przed ostatnim `await` pozostają.

## Cancellation safety

Operacja jest cancellation-safe w danym miejscu, jeżeli jej przerwanie i
ponowienie nie gubi danych ani nie łamie invariants. Odczyt „jednej wiadomości”
z kolejki może być bezpieczny; `read_exact` przerwany po częściowym odczycie
może utracić informację o liczbie odebranych bajtów, jeśli bufor znika.

Projektuj operację jako:

1. przygotowanie stanu;
2. kroki zachowujące możliwość wznowienia;
3. krótki commit bez `await` albo z transakcją zewnętrzną;
4. cleanup przez RAII.

## Timeout nie zatrzymuje świata

Runtime’owy timeout zwykle ściga future z timerem i upuszcza ją po czasie.
Nie cofa już wysłanego requestu ani transakcji po stronie serwera. Protokół
potrzebuje idempotency key, deadline lub jawnego cancel.

Tokio — **third-party**:

~~~text
let wynik = tokio::time::timeout(
    Duration::from_secs(2),
    pobierz_dane(),
).await;
~~~

Rozróżnij:

- timeout kolejki;
- timeout połączenia;
- timeout pojedynczej operacji;
- deadline całego żądania;
- budżet retry.

Dodawanie pełnego timeoutu na każdą próbę może przekroczyć deadline rodzica.

## Kod blokujący

Wywołanie blokującego I/O, długie obliczenie lub standardowy mutex trzymany
przez `await` może zatrzymać wątek executora. Rozwiązania:

- użyj asynchronicznego API runtime’u;
- przenieś krótki blokujący fragment do `spawn_blocking` (**third-party**);
- użyj osobnej, ograniczonej puli dla CPU-bound;
- dziel obliczenie i kooperacyjnie oddawaj sterowanie.

Nie twórz nieograniczonej liczby blocking tasków — przeciążenie tylko zmieni
miejsce kolejki.

## Blokada przez `await`

~~~compile_fail
use std::sync::Mutex;

async fn bledne(m: &Mutex<Vec<u8>>) {
    let guard = m.lock().unwrap();
    async {}.await;
    drop(guard);
}

fn wymaga_send<T: Send>(_: T) {}

fn main() {
    let m = Mutex::new(Vec::new());
    wymaga_send(bledne(&m));
}
~~~

Na typowym wielowątkowym executorze taki guard sprawia, że future nie jest
`Send`. Nawet gdy kompiluje się na lokalnym executorze, trzymanie blokady przez
`await` grozi deadlockiem i opóźnieniami. Zbierz dane, upuść guard, dopiero
potem czekaj.

## Shutdown

Graceful shutdown zwykle ma fazy: przestań przyjmować pracę, rozgłoś token
anulowania, poczekaj na aktywne taski z deadline, zapisz trwały stan, a na
końcu wymuś zakończenie. Ustal, które operacje muszą być dokończone.

## Powiązane tematy

- [Taski, join, select i stream](03_taski_join_select_i_stream.md)
- [RAII i destruktory](../03_pamiec_i_wlasnosc/01_stos_sterta_i_raii.md)
- [Panic, unwind i abort](../06_bledy/03_panic_unwind_i_abort.md)
