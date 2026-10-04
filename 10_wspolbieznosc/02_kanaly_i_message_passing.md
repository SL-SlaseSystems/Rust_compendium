[← Spis treści](../README.md)

# Kanały i message passing

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

## Powiązane tematy

- [Wątki](01_watki_i_scoped_threads.md)
- [`Arc` i blokady](03_arc_mutex_rwlock_i_condvar.md)
- [Taski, join, select i stream](../11_async_rust/03_taski_join_select_i_stream.md)
