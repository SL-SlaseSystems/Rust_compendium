[← Spis treści](../README.md)

# Taski, join, select i stream

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

## Powiązane tematy

- [Anulowanie i timeouty](04_anulowanie_timeouty_i_blocking.md)
- [Kanały](../09_wspolbieznosc/02_kanaly_i_message_passing.md)
- [`Future` i executor](01_future_async_i_await.md)
