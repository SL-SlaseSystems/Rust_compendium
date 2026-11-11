[← Spis treści](../README.md)
<!-- status: expanded -->

# Taski, join, select i stream

## Cele

Po tym rozdziale potrafisz:

- rozróżnić współbieżne pollowanie od niezależnego taska;
- zaprojektować posiadanie tasków, limity oraz bezpieczną selekcję;


Future jest wartością opisującą obliczenie. Task jest future zaplanowaną przez
executor, zwykle z własnym stanem i uchwytem do wyniku.

## Sekwencja kontra współbieżność

~~~rust
async fn krok(n: u32) -> u32 { n + 1 }

async fn sekwencyjnie() -> u32 {
    let a = krok(1).await;
    let b = krok(10).await;
    a + b
}

fn main() {
    let _ = sekwencyjnie();
}
~~~

Dwa kolejne `await` są sekwencyjne. Współbieżne join polluje kilka futures,
aż wszystkie się zakończą. Standard library nie ma ogólnego makra join;
runtime lub crate `futures` dostarcza implementację.

Przykład Tokio — **third-party**, nietestowany w tym kompendium:

~~~text
let (uzytkownik, zamowienia) = tokio::join!(
    pobierz_uzytkownika(id),
    pobierz_zamowienia(id),
);
~~~

Tokio `join!` czeka także na drugą gałąź, gdy pierwsza zwróci własny `Err`: wynikiem jest krotka wyników. `try_join!` kończy się przy pierwszym `Err` i porzuca pozostałe posiadane futures. Przy `JoinHandle<Result<T, E>>` istnieją jednak dwa poziomy błędu: zewnętrzny `JoinError` i wewnętrzny `E`. Bez jawnego spłaszczenia `try_join!` reaguje na błąd uchwytu, a nie automatycznie na błąd operacji. Upuszczone uchwyty Tokio mogą ponadto odłączyć pozostałe zadania, więc szybki powrót agregatora nie jest dowodem ich zatrzymania.

## Spawn

Spawn zwykle wymaga `Send + 'static` w wielowątkowym runtime. `'static` nie
znaczy „żyje wiecznie”; task posiada wszystkie dane lub tylko referencje
`'static`. Lokalne executory mogą uruchamiać futures niebędące `Send`.

Nie porzucaj uchwytu bez decyzji o lifecycle. Ustal, czy błąd child tasku,
panic i shutdown mają być propagowane, logowane czy ignorowane.

## Select

Select czeka na pierwszą gotową gałąź. Przegrane futures mogą pozostać do
następnej iteracji albo zostać upuszczone — zależy od konstrukcji. Tokio
przykładowo udostępnia makro **third-party**:

~~~text
tokio::select! {
    wynik = operacja() => obsluz(wynik),
    _ = token.cancelled() => zakoncz(),
}
~~~

Sprawdź fairness i cancellation safety każdej gałęzi. Tworzenie future od
nowa w pętli może utracić częściowy postęp.

## Stream

Stream jest asynchronicznym odpowiednikiem iteratora: produkuje wiele
elementów w czasie. Trait `Stream` nie należy do standard library; popularną
definicję dostarcza crate **third-party** `futures-core`. Typowe adaptery to
`map`, `filter`, `buffered` i `for_each_concurrent`.

Backpressure oznacza, że konsument ogranicza tempo producenta. Bufor poprawia
przepustowość, lecz zużywa pamięć i zwiększa opóźnienie. Strumień powinien
jawnie opisywać koniec, błąd i anulowanie.

## Structured concurrency

Taski potomne powinny pozostawać w kontrolowanym zakresie: rodzic czeka na nie
lub anuluje je podczas wyjścia. Nie każdy runtime wymusza structured
concurrency typami, więc warstwę lifecycle trzeba zaprojektować.


## Model — join i spawn mają różnych właścicieli

Join lokalnych futures zwykle przechowuje je wewnątrz jednej nadrzędnej future. Mogą pożyczać dane rodzica, jeśli cały zakres życia na to pozwala. Spawn tworzy niezależne zadanie kontrolowane przez runtime i osobny uchwyt. W Tokio kontrakt `spawn` wymaga `Send + 'static` zarówno dla future, jak i wyniku. Ta reguła obowiązuje również wtedy, gdy wybrany runtime aktualnie wykonuje pracę na jednym wątku; alternatywą dla lokalnego zadania jest osobne API.

Drop zwykłej future oraz Drop uchwytu taska nie muszą znaczyć tego samego. Tokio `JoinHandle` po upuszczeniu odłącza zadanie. Task może dalej wykonywać efekty, chociaż rodzic już nie czeka na wynik. Wymuszone przerwanie zleca się osobnym mechanizmem, a po nim warto doczekać zakończenia i sprzątania. To konkretne zachowanie **third-party**, nie reguła całego języka.

Poniższy samowystarczalny przykład pokazuje wymaganie typowe dla przenośnego taska, ale nie uruchamia executora ani prawdziwego `spawn`.

~~~rust
use std::future::Future;
fn przenosne<F>(_: &F)
where F: Future + Send + 'static, F::Output: Send + 'static {}
fn main() {
    let dane = String::from("Rust");
    let f = async move { dane.len() };
    przenosne(&f);
    drop(f);
}
~~~

Select polluje konkurujące gałęzie. Gdy własna future gałęzi zostaje upuszczona, traci jej stan lokalny. Jeżeli select dostał pożyczkę do przypiętej future trzymanej poza pętlą, właściciel może zachować postęp na kolejną iterację. To ważna różnica przy timerach i operacjach częściowych. Nie twórz od nowa długiej operacji przy każdym niezwiązanym komunikacie, jeżeli oznacza to resetowanie deadline lub gubienie postępu.

Tokio `select!` domyślnie losuje pierwszą sprawdzaną gałąź. Tryb `biased` zmienia tę politykę i przenosi odpowiedzialność za brak głodzenia na autora. Gdy jedna gałąź stale jest gotowa, gałąź shutdown musi nadal dostawać szansę. Select nie uruchamia równolegle CPU-bound kodu gałęzi; wszystkie polle należą do bieżącego taska.

Dla strumieni limit aktywnych operacji jest konieczny. Nieograniczone spawn dla każdego elementu omija backpressure źródła, nawet jeśli sam stream jest leniwy. Limituj pracę przed utworzeniem kosztownego payloadu. Adapter zachowujący kolejność wyników może zatrzymywać szybkie odpowiedzi za jedną wolną operacją; wariant nieuporządkowany zmniejsza ten efekt, ale zmienia kontrakt kolejności.

Structured concurrency to odpowiedzialność za całe drzewo zadań: po wyjściu rodzica dzieci mają być zakończone albo świadomie przekazane innemu właścicielowi. Zapisz politykę pierwszego błędu, anulowania rodzeństwa i odbierania pozostałych wyników. Bez tego poprawne typy nie zapobiegną osieroconej pracy.

## Własność grupy: `JoinSet` i wykonanie lokalne

Tokio `JoinSet<T>` posiada grupę tasków o wspólnym typie wyniku i oddaje je w kolejności ukończenia przez `join_next`. Drop zbioru zleca abort pozostałych tasków, inaczej niż Drop pojedynczego `JoinHandle`, który odłącza zadanie. `abort_all` nie odbiera wyników i nie czeka na sprzątanie: po nim opróżnij zbiór przez join. Dla rozpoczętej pracy `spawn_blocking` obowiązuje opisane osobno ograniczenie przerywania.

Tokio `LocalSet` pozwala wykonywać `!Send` futures na jednym wątku, a `spawn_local` nadal wymaga, by niezależny task nie pożyczał krótkotrwałych lokalnych danych rodzica. Samo wybranie runtime’u current-thread nie zmienia bounds zwykłego `tokio::spawn`. `run_until` napędza zestaw podczas oczekiwania na wskazaną future; powrót tej future nie jest dowodem zakończenia wszystkich lokalnych dzieci. Ich lifecycle trzeba nadal kontrolować.

Poniższy opisowy szkic wymaga Tokio (**third-party**), aktywnego runtime’u oraz funkcji aplikacji; nie jest wykonywany przez testy `std`.

~~~text
let mut grupa = tokio::task::JoinSet::new();
for dane in ograniczona_partia {
    grupa.spawn(async move { przetworz(dane).await });
}
while let Some(wynik_taska) = grupa.join_next().await {
    // Oddziel JoinError (panic/anulowanie) od błędu samego przetwarzania.
    obsluz(wynik_taska);
}
~~~

## Kontrola zasobów: `Semaphore` i `mpsc`

Tokio `Semaphore` daje określoną liczbę permitów. Permit trzymany przez zadanie wraca po Drop; owned permit można przenieść do niezależnego taska. Nabywaj go przed spawn i kosztowną alokacją, inaczej utworzysz nieograniczoną kolejkę futures czekających na pozwolenie. Semafor limituje współbieżność, nie automatycznie liczbę żądań na sekundę. Fairness kolejki oznacza też, że duże `acquire_many` na początku może opóźnić mniejszych odbiorców, a anulowanie oczekiwania traci miejsce w kolejce.

Ograniczony Tokio `mpsc` przenosi wiadomości do jednego odbiorcy i zapewnia backpressure przez oczekiwanie na miejsce. Rezygnacja z `send` w select może upuścić przeniesiony payload, mimo że wiadomość nie została wysłana. Gdy payload ma pozostać u producenta, najpierw rezerwuj miejsce przez `reserve`, potem wykonaj nieoczekujące wysłanie przez permit. Zamknięcie odbiorcy powinno zatrzymać nowych producentów i dopuścić opróżnienie już przyjętej pracy według polityki aplikacji.

## Aktualny stan, zdarzenia i aktor

`watch` przechowuje tylko ostatnią wartość. Nadaje się do konfiguracji lub stanu shutdown, ale nie do gwarantowanego odebrania każdej zmiany. Odbiorcy śledzą własne „widziane”; po `changed` użyj odpowiednio `borrow_and_update`, a guard pożyczki zwolnij przed długim oczekiwaniem. `broadcast` udostępnia zdarzenia wielu odbiorcom w ograniczonym buforze. Powolny odbiorca może dostać `Lagged` i musi odtworzyć stan albo zaakceptować utratę; nadawca nie czeka automatycznie na każdego klienta. To różne kontrakty od kolejki zadań.

Aktor jest właścicielem stanu i odbiera enum poleceń przez `mpsc`; odpowiedź można przekazać przez `oneshot`. Potwierdzenie wejścia do kolejki nie oznacza commit. Rezygnacja klienta odpowiedzi nie zatrzymuje automatycznie aktora ani jego operacji zewnętrznej. Ustal limit skrzynki, politykę błędów, idempotencję oraz zatrzymanie aktora po opróżnieniu skrzynki. Wszystkie opisane typy Tokio są **third-party**; nie są dodatkowymi elementami `std`.

## Diagnostyka kompilatora

Błąd `Send` może dotyczyć wyniku taska, choć sama future jest przenośna; sprawdź oba bounds. Błąd `'static` zwykle oznacza pożyczkę z rodzica w niezależnym zadaniu. Nie naprawiaj go przez wyciek pamięci. Dla select z przyszłością zakończoną sprawdź, czy pętla nie polluje jej ponownie. Brak typu `Stream` w `std` jest zgodny z podziałem API: potrzebny trait dostarcza wybrany crate **third-party**.

## Praktyka produkcyjna

Przechowuj uchwyty w kontrolowanej kolekcji, obserwuj błędy i ogranicz liczbę aktywnych tasków. Zapisz, czy kolejność odpowiedzi ma znaczenie. Przy shutdown zatrzymaj napływ, anuluj oczekiwania i odbierz końcowe statusy. Dokumentację cancellation safety czytaj dla dokładnych metod użytych w select, nie tylko dla makra. API Tokio sprawdzono 11 listopada 2026 w dokumentacji 1.54.1; szkice z tym runtime’em nie są częścią testów `std` kompendium.

## Sprawdź, czy rozumiesz

- Dlaczego upuszczenie Tokio JoinHandle może zostawić pracę w tle?
- Jak zachować jedną future między iteracjami select?
- Jak zachowanie kolejności wyników wpływa na pamięć i opóźnienia?

## Ćwiczenia

- `B21-1` — podstawowe: Sprawdź bounds `Send + 'static` future posiadającej tekst. [Rozwiązanie](../rozwiazania/11_async_rust/03_taski_join_select_i_stream.md#b21-1).
- `B21-2` — praktyczne: Rozpisz lifecycle trzech tasków po błędzie jednego z nich. [Rozwiązanie](../rozwiazania/11_async_rust/03_taski_join_select_i_stream.md#b21-2).
- `B21-3` — pogłębione: Zaprojektuj limit aktywnych operacji dla streamu i zachowanie kolejności wyników. [Rozwiązanie](../rozwiazania/11_async_rust/03_taski_join_select_i_stream.md#b21-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [Tokio spawn: bounds](https://docs.rs/tokio/latest/tokio/task/fn.spawn.html)
- [Tokio JoinHandle: detach](https://docs.rs/tokio/latest/tokio/task/struct.JoinHandle.html)
- [Tokio select: fairness i cancellation](https://docs.rs/tokio/latest/tokio/macro.select.html)

- [Tokio JoinSet](https://docs.rs/tokio/latest/tokio/task/struct.JoinSet.html)
- [Tokio LocalSet](https://docs.rs/tokio/latest/tokio/task/struct.LocalSet.html)
- [Tokio Semaphore](https://docs.rs/tokio/latest/tokio/sync/struct.Semaphore.html)
- [Tokio mpsc](https://docs.rs/tokio/latest/tokio/sync/mpsc/index.html)
- [Tokio watch](https://docs.rs/tokio/latest/tokio/sync/watch/index.html)
- [Tokio broadcast](https://docs.rs/tokio/latest/tokio/sync/broadcast/index.html)

- [Tokio try_join i zagnieżdżone wyniki](https://docs.rs/tokio/latest/tokio/macro.try_join.html)
- [Tokio mpsc: reserve i cancellation safety](https://docs.rs/tokio/latest/tokio/sync/mpsc/struct.Sender.html#method.reserve)

## Powiązane tematy

- [Anulowanie i timeouty](04_anulowanie_timeouty_i_blocking.md)
- [Kanały](../10_wspolbieznosc/02_kanaly_i_message_passing.md)
- [`Future` i executor](01_future_async_i_await.md)
