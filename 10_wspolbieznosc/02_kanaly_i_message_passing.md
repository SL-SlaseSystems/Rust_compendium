[← Spis treści](../README.md)
<!-- status: expanded -->

# Kanały i message passing

## Cele

Po tym rozdziale potrafisz:

- opisać własność wiadomości i protokół zamknięcia;
- policzyć ograniczenie pamięci oraz rozróżnić wysłanie od potwierdzenia;


Kanał przekazuje ownership wiadomości między wykonawcami. Standardowy
`std::sync::mpsc` ma wielu producentów i jednego konsumenta.

## Kanał nieograniczony

~~~rust
use std::sync::mpsc;
use std::thread;

fn main() {
    let (tx, rx) = mpsc::channel();
    let mut watki = Vec::new();

    for id in 0..3 {
        let tx = tx.clone();
        watki.push(thread::spawn(move || tx.send(id * id).unwrap()));
    }
    drop(tx); // bez tego iterator czekałby na możliwe nowe wiadomości

    let mut wyniki: Vec<_> = rx.iter().collect();
    for h in watki { h.join().unwrap(); }
    wyniki.sort();
    assert_eq!(wyniki, [0, 1, 4]);
}
~~~

Kolejność między różnymi producentami nie jest gwarantowana. `send` zwraca
wiadomość w błędzie, jeśli odbiorca został zamknięty.

## Backpressure

`sync_channel(n)` ma ograniczoną pojemność. `send` blokuje, gdy bufor jest
pełny; pojemność zero tworzy rendezvous:

~~~rust
use std::sync::mpsc;
use std::thread;

fn main() {
    let (tx, rx) = mpsc::sync_channel(1);
    let h = thread::spawn(move || {
        tx.send("a").unwrap();
        tx.send("b").unwrap();
    });
    assert_eq!(rx.recv().unwrap(), "a");
    assert_eq!(rx.recv().unwrap(), "b");
    h.join().unwrap();
}
~~~

Ograniczony kanał zapobiega niekontrolowanemu wzrostowi pamięci, ale może
tworzyć deadlock, jeżeli cykl komponentów czeka na wzajemne opróżnienie.

## Odbiór

- `recv` blokuje do wiadomości lub zamknięcia;
- `recv_timeout` ma limit czasu;
- `try_recv` nie blokuje;
- iteracja kończy się, gdy wszyscy nadawcy zostali upuszczeni.

Zamknięcie jest częścią protokołu. Nie ukrywaj klona `Sender` w globalnym
stanie, bo odbiorca nigdy nie zobaczy końca.

## Protokół jako enum

~~~rust
enum Polecenie {
    Dodaj(i32),
    Odczytaj(std::sync::mpsc::Sender<i32>),
    Zakoncz,
}

fn main() {
    let _ = Polecenie::Dodaj(1);
    let _ = Polecenie::Zakoncz;
    let (tx, _rx) = std::sync::mpsc::channel();
    let _ = Polecenie::Odczytaj(tx);
}
~~~

Enum dokumentuje dopuszczalne wiadomości. Kanał odpowiedzi może realizować
request-response bez współdzielonej mutacji.

## Ekosystem

Crossbeam channel, flume oraz kanały runtime’ów async są **third-party**.
Różnią się liczbą konsumentów, selekcją, fairness, cancellation safety i
zachowaniem backpressure. Nie używaj blokującego `recv` wewnątrz wątku
executora async.


## Model — kolejka nie jest potwierdzeniem wykonania

Sukces `send` oznacza przyjęcie wiadomości zgodnie z kontraktem kanału. Nie oznacza, że konsument zakończył żądaną operację ani zapisał dane trwale. Dla niebuforowanego `sync_channel(0)` wysłanie spotyka się z odbiorem, ale nadal nie potwierdza końca obsługi biznesowej. Jeżeli klient potrzebuje wyniku, dodaj kanał odpowiedzi lub osobną wiadomość potwierdzającą.

~~~rust
use std::{sync::mpsc, thread};
enum Polecenie { Dodaj(u32), Wynik(mpsc::Sender<u32>) }
fn main() {
    let (tx, rx) = mpsc::sync_channel(2);
    let worker = thread::spawn(move || {
        let mut suma = 0;
        for polecenie in rx {
            match polecenie {
                Polecenie::Dodaj(n) => suma += n,
                Polecenie::Wynik(odpowiedz) => { let _ = odpowiedz.send(suma); }
            }
        }
    });
    tx.send(Polecenie::Dodaj(7)).unwrap();
    let (odp_tx, odp_rx) = mpsc::channel();
    tx.send(Polecenie::Wynik(odp_tx)).unwrap();
    assert_eq!(odp_rx.recv().unwrap(), 7);
    drop(tx);
    worker.join().unwrap();
}
~~~

Jeden worker posiada stan i aktualizuje go bez mutexa. Wiadomości jednego nadawcy zachowują kolejność protokołu, więc odczyt następuje po dodaniu. Nie wyprowadzaj z tego globalnej kolejności dla wielu niezależnych producentów. Odpowiedź może się nie udać, jeżeli klient już zrezygnował; celowe odrzucenie tego błędu jest tutaj częścią polityki, a nie pominiętą obsługą.

Pojemność `n` ogranicza liczbę wiadomości w buforze, nie wszystkie bajty procesu. Jeżeli każdy producent alokuje duży payload przed blokującym `send`, pamięć jest zużywana także przez oczekujących producentów i już obsługiwane wiadomości. Limit rozmiaru payloadu i liczby producentów jest równie ważny jak limit kolejki. W serwisie warto nabyć pozwolenie przed kosztowną alokacją.

Przeciążenie wymaga wyboru: blokowanie, odrzucenie, timeout, agregacja lub zastąpienie starej wartości. `try_send` pozwala rozróżnić pełny bufor i rozłączenie, zwracając własność niewysłanej wiadomości. Nie ponawiaj bez końca w gorącej pętli, bo konsumujesz CPU i utrudniasz konsumentowi postęp.

Zamykanie kanału jest protokołem własności. Odbiorca kończy iterację po upuszczeniu wszystkich nadawców i wyczerpaniu bufora. Samo wysłanie `Zakoncz` może zostawić późniejsze wiadomości innych producentów bez obsługi. Wyznacz, kto zatrzymuje przyjmowanie pracy i kiedy wolno porzucić pozostały bufor. Odbiornik `std::sync::mpsc` jest pojedynczy; klonowanie `Sender` nie tworzy kolejki wielu konsumentów.

## Diagnostyka kompilatora

Próba sklonowania `Receiver` albo współdzielenia go tak jak typu `Sync` zostanie odrzucona. To kontrakt MPSC, nie brak importu. Po `send(payload)` payload zostaje przeniesiony; przy błędzie można odzyskać go z `SendError`. Błędna kolejność `join` przed odbieraniem z ograniczonego kanału może zakleszczyć program i nie zostanie wykryta przez kompilator. Analizuj cykl oczekiwań, nie tylko bounds typów.

## Praktyka produkcyjna

Mierz długość kolejki, czas oczekiwania oraz czas obsługi oddzielnie. Ustal maksymalny payload, liczbę aktywnych producentów i politykę przeciążenia. Zamknięcie powinno być testowane z pustym i niepustym buforem oraz ze zrezygnowanym klientem odpowiedzi. Kanały async **third-party** mają własne kontrakty anulowania, permitów i fairness; nie przenoś na nie automatycznie zachowania `std`. Blokującego kanału standardowego nie obsługuj na wątku, który ma jednocześnie pollować inne futures.

## Sprawdź, czy rozumiesz

- Co potwierdza sukces `send`, a czego nie?
- Dlaczego pojemność 10 nie oznacza limitu pamięci 10 payloadów?
- Jak ukryty klon nadawcy wpływa na shutdown?

## Ćwiczenia

- `B14-1` — podstawowe: Wyślij dwie wiadomości i zakończ odbiór upuszczeniem nadawcy. [Rozwiązanie](../rozwiazania/10_wspolbieznosc/02_kanaly_i_message_passing.md#b14-1).
- `B14-2` — praktyczne: Odzyskaj payload przy `try_send` do pełnej kolejki. [Rozwiązanie](../rozwiazania/10_wspolbieznosc/02_kanaly_i_message_passing.md#b14-2).
- `B14-3` — pogłębione: Zaprojektuj request-response z kanałem odpowiedzi oraz świadomą obsługą rezygnacji klienta. [Rozwiązanie](../rozwiazania/10_wspolbieznosc/02_kanaly_i_message_passing.md#b14-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [std::sync::mpsc](https://doc.rust-lang.org/std/sync/mpsc/index.html)
- [SyncSender::send](https://doc.rust-lang.org/std/sync/mpsc/struct.SyncSender.html#method.send)

## Powiązane tematy

- [Wątki](01_watki_i_scoped_threads.md)
- [`Arc` i blokady](03_arc_mutex_rwlock_i_condvar.md)
- [Taski, join, select i stream](../11_async_rust/03_taski_join_select_i_stream.md)
