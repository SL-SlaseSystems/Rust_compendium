[← Spis treści](../../README.md)

# Rozwiązania: Taski, join, select i stream

[Rozdział źródłowy](../../11_async_rust/03_taski_join_select_i_stream.md).

## B21-1

~~~rust
use std::future::Future;
fn sprawdz<F:Future+Send+'static>(_:F)where F::Output:Send+'static{}
fn main(){let s=String::from("tekst");sprawdz(async move{s.len()});}
~~~

## B21-2

Rodzic posiada wszystkie trzy uchwyty. Po błędzie pierwszego oznacza żądanie jako kończące się, przestaje dodawać pracę, wysyła anulowanie dwóm pozostałym i czeka na ich zakończenie w ramach wspólnego deadline. Raportuje pierwotny błąd oraz ewentualne błędy cleanup według polityki. Samo upuszczenie uchwytów Tokio nie realizuje anulowania. Operację nieodwracalną, która mogła już zostać zatwierdzona, trzeba uzgodnić przez protokół biznesowy, a nie jedynie przez abort taska.

## B21-3

Dopuść maksymalnie 16 aktywnych operacji i maksymalnie 64 KiB na element; pozwolenie pobierz przed alokacją. Jeżeli odpowiedzi mogą wracać dowolnie, odbieraj zakończone zadania bez oczekiwania na wcześniejsze. Jeżeli kolejność jest wymagana, nadaj numery sekwencyjne i utrzymuj ograniczony bufor wyników; uwzględnij wolną pierwszą operację w deadline. Limit tasków, bufora i wejściowej kolejki musi być wspólną częścią budżetu pamięci. Przy rezygnacji rodzica anuluj oraz dołącz aktywne dzieci zgodnie z kontraktem runtime’u.

