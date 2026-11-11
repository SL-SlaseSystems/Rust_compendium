[← Spis treści](../README.md)
<!-- status: expanded -->

# Anulowanie, timeouty i kod blokujący

## Cele

Po tym rozdziale potrafisz:

- zachować postęp częściowej operacji po anulowaniu;
- rozróżnić timeout, deadline, abort taska i zatrzymanie blokującego kodu;


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


## Model — anulowanie ujawnia stan pośredni

Każdy punkt zawieszenia jest miejscem, w którym future może zostać porzucona. Sprawdź, jakie zasoby i efekty już istnieją, które dane żyją w jej stanie, a które w obiekcie o dłuższym życiu. Cancellation safety jest własnością konkretnej operacji w konkretnym sposobie użycia. Nie wynika z tego, że funkcja zwraca `Result` albo korzysta z RAII.

Jeżeli parser ramki przechowuje częściowy nagłówek wyłącznie w lokalnej future odczytu, przegrany select może go zniszczyć. Przechowywanie bufora i offsetu w obiekcie połączenia pozwala następnej próbie kontynuować. Nadal trzeba ustalić, czy metoda gwarantuje liczbę zużytych bajtów przy błędzie. Tokio wprost rozróżnia metody cancellation-safe oraz takie jak `read_exact`, których przerwanie w selekcji może zgubić wiedzę o postępie.

~~~rust
#[derive(Default)]
struct Odbior { bufor: Vec<u8>, wymagane: usize }
impl Odbior {
    fn dopisz(&mut self, dane: &[u8]) { self.bufor.extend_from_slice(dane); }
    fn gotowe(&self) -> bool { self.bufor.len() >= self.wymagane }
}
fn main() {
    let mut stan = Odbior { wymagane: 4, ..Odbior::default() };
    stan.dopisz(b"ru");
    assert!(!stan.gotowe());
    // Zmiana próby nie niszczy stanu należącego do połączenia.
    stan.dopisz(b"st");
    assert!(stan.gotowe());
    assert_eq!(stan.bufor, b"rust");
}
~~~

To model przechowywania postępu, nie implementacja asynchronicznego odczytu. Produkcyjny parser dodatkowo ogranicza długość, przechowuje nadmiar kolejnej ramki i rozróżnia EOF od anulowania. Nie ogłaszaj cancellation safety dla całego protokołu wyłącznie na podstawie obecności bufora.

Deadline oznacza wspólny moment końca budżetu, a timeout lokalny odcinek czasu. Próby połączenia, oczekiwanie w kolejce i retry powinny zużywać ten sam budżet rodzica. Jeżeli każda warstwa dostaje nowe dwie sekundy, całość może trwać wielokrotnie dłużej. Sprawdzenie czasu jest kooperacyjne: future wykonująca długą pracę bez oddawania sterowania może przekroczyć limit, zanim runtime odzyska kontrolę.

W Tokio `spawn_blocking` przenosi closure na pulę dopuszczającą blokowanie. Rozpoczętego zadania blokującego nie można zwyczajnie przerwać przez `abort`; trzeba zaprojektować własne punkty zatrzymania albo poczekać. Jeśli zadanie jeszcze nie wystartowało, anulowanie może zapobiec startowi. To rozróżnienie ma znaczenie dla shutdown, który inaczej czekałby na dowolnie długi syscall lub obliczenie.

Permit kolejki, połączenie i uchwyt taska również mają właścicieli. Upuszczenie permitu może zwolnić miejsce, ale nie cofa wysłanej operacji. Stan trwały zapisuj przez transakcję lub idempotentny protokół, a zewnętrzny async cleanup zlecaj kontrolowanemu właścicielowi. `Drop` nie daje zwykłego miejsca na oczekiwanie `.await`.

## Diagnostyka kompilatora

Błąd `Send` z guardem trzymanym przez `await` najlepiej naprawić zakresem leksykalnym: pobierz snapshot w bloku, zakończ blok i dopiero czekaj. Sam kompilator nie wykryje utraty częściowych danych po anulowaniu ani zbyt długiego shutdown. Rozróżniaj błąd timeoutu otoczki od błędu samej operacji. Zagnieżdżone `Result` przy timeoutach jest informacją o dwóch niezależnych kontraktach, a nie niepotrzebnym utrudnieniem typów.

## Praktyka produkcyjna

Testuj anulowanie przed startem, po częściowym postępie i po zewnętrznym commit. Limituj pulę blokującą oraz liczbę oczekujących zadań, szczególnie dla CPU-bound pracy. Ustal, które efekty wymagają uzgodnienia po timeout. Przy shutdown zatrzymaj wejście, rozgłoś anulowanie, dołącz dzieci i dopiero zwalniaj współdzielone zasoby. Kontrakty Tokio weryfikowano 11 listopada 2026; szkice z runtime’em są **third-party** i nie są tutaj przedstawiane jako wykonane testy integracyjne.

## Sprawdź, czy rozumiesz

- Gdzie powinien żyć częściowy bufor, jeśli próba może zostać anulowana?
- Dlaczego timeout nie dowodzi, że serwer nie wykonał operacji?
- Czy abort zatrzyma już rozpoczęte spawn_blocking?

## Ćwiczenia

- `B22-1` — podstawowe: Przechowaj dwa fragmenty ramki w stanie niezależnym od pojedynczej próby. [Rozwiązanie](../rozwiazania/11_async_rust/04_anulowanie_timeouty_i_blocking.md#b22-1).
- `B22-2` — praktyczne: Oblicz pozostały budżet ze wspólnego deadline zamiast odnawiać timeout. [Rozwiązanie](../rozwiazania/11_async_rust/04_anulowanie_timeouty_i_blocking.md#b22-2).
- `B22-3` — pogłębione: Zaprojektuj shutdown dla nieprzerywalnego zadania blokującego i operacji płatności. [Rozwiązanie](../rozwiazania/11_async_rust/04_anulowanie_timeouty_i_blocking.md#b22-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [Tokio select: cancellation safety](https://docs.rs/tokio/latest/tokio/macro.select.html#cancellation-safety)
- [Tokio spawn_blocking: zatrzymywanie](https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html)
- [Tokio timeout](https://docs.rs/tokio/latest/tokio/time/fn.timeout.html)

## Powiązane tematy

- [Taski, join, select i stream](03_taski_join_select_i_stream.md)
- [RAII i destruktory](../03_ownership_i_pamiec/01_stos_sterta_i_raii.md)
- [Panic, unwind i abort](../07_obsluga_bledow/03_panic_unwind_i_abort.md)
