[← Spis treści](../README.md)
<!-- status: expanded -->

# Wątki i scoped threads

## Cele

Po tym rozdziale potrafisz:

- wyjaśnić bounds `spawn` i różnicę wobec scoped threads;
- zaprojektować zakończenie workera oraz moment synchronizacji;


`std::thread` udostępnia wątki systemowe. Closure przekazane do
`thread::spawn` musi być `'static` i `Send`, ponieważ wątek może przeżyć
wywołujący zakres.

## Spawn i join

~~~rust
use std::thread;

fn main() {
    let dane = vec![1, 2, 3, 4];
    let uchwyt = thread::spawn(move || dane.into_iter().sum::<i32>());
    let suma = uchwyt.join().expect("wątek nie powinien panikować");
    assert_eq!(suma, 10);
}
~~~

`move` przenosi wektor do closure. `JoinHandle::join` zwraca `Result`, bo
wątek może zakończyć się panic. Upuszczenie handle’a odłącza wątek; nie
zatrzymuje go automatycznie.

## Scoped threads

`thread::scope` gwarantuje join przed końcem zakresu, dlatego wątki mogą
pożyczać dane lokalne:

~~~rust
use std::thread;

fn main() {
    let dane = [1, 2, 3, 4, 5, 6];
    let (lewa, prawa) = dane.split_at(3);

    let (a, b) = thread::scope(|s| {
        let a = s.spawn(|| lewa.iter().sum::<i32>());
        let b = s.spawn(|| prawa.iter().sum::<i32>());
        (a.join().unwrap(), b.join().unwrap())
    });

    assert_eq!(a + b, 21);
}
~~~

Scoped threads nie eliminują kosztu tworzenia wątku. Dla wielu małych zadań
używa się puli wątków, np. crate’a **third-party** Rayon dla data parallelism.

## Builder i rozmiar stosu

`thread::Builder` nadaje nazwę oraz rozmiar stosu i zwraca błąd przy tworzeniu.
Nazwa pomaga w diagnostyce. Zbyt mały stos prowadzi do overflow, zbyt duży
rezerwuje przestrzeń adresową; nie dobieraj go bez pomiaru.

## Kooperacyjne zatrzymanie

Rust nie ma bezpiecznego „kill thread”. Przekaż token anulowania, kanał albo
`AtomicBool` i zaprojektuj punkty sprawdzania:

~~~rust
use std::sync::{
    Arc,
    atomic::{AtomicBool, Ordering},
};
use std::thread;

fn main() {
    let stop = Arc::new(AtomicBool::new(false));
    let worker_stop = Arc::clone(&stop);
    let h = thread::spawn(move || {
        while !worker_stop.load(Ordering::Relaxed) {
            thread::yield_now();
        }
        "zatrzymano"
    });
    stop.store(true, Ordering::Relaxed);
    assert_eq!(h.join().unwrap(), "zatrzymano");
}
~~~

Relaxed wystarcza tutaj tylko dla samej flagi; nie publikuje dodatkowych
danych. Zaawansowane porządki pamięci opisuje osobny rozdział.


## Model — właściciel pracy odpowiada za jej koniec

`'static` w wymaganiu closure oznacza, że nie przechowuje ona pożyczek o krótszym czasie życia. Posiadany `String` spełnia ten warunek i może zostać zniszczony zaraz po zakończeniu pracy. Samo `move` przenosi referencję, jeżeli to referencja jest przechwytywanym bindingiem; nie zamienia jej w posiadane dane ani nie przedłuża życia obiektu.

`thread::scope` ma silniejszą wiedzę o czasie zakończenia. Zanim zwróci sterowanie, dołącza wątki zakresu, dlatego może dopuścić pożyczki lokalnych danych. To nie jest specjalne wyłączenie borrow checkera. Jeżeli wątki mają mutować rozłączne obszary, nadal trzeba udowodnić rozłączność, na przykład przez `split_at_mut`.

~~~rust
fn main() {
    let mut dane = [1_u32, 2, 3, 4];
    let (a, b) = dane.split_at_mut(2);
    std::thread::scope(|s| {
        s.spawn(|| a.iter_mut().for_each(|n| *n *= 2));
        s.spawn(|| b.iter_mut().for_each(|n| *n += 10));
    });
    assert_eq!(dane, [2, 4, 13, 14]);
}
~~~

Dwie pożyczki mutowalne obejmują różne elementy. Nie ma wspólnego licznika ani mutexa, bo własność zakresów usuwa konflikt. Zewnętrzne użycie `dane` następuje po scope, gdy wszystkie wątki zakończyły pracę. To często prostszy model niż `Arc<Mutex<Vec<_>>>`, jeżeli zadanie naturalnie dzieli dane na niezależne fragmenty.

`join` to również moment synchronizacji: operacje wykonane przez dołączony wątek przed jego zakończeniem zachodzą przed operacjami po powrocie `join`. Nie trzeba dodatkowej flagi „wynik gotowy”, gdy jedynym konsumentem jest kod czekający na wynik uchwytu. `is_finished` może być wskazówką do planowania, lecz do odebrania wyniku i obsługi panic nadal służy `join`.

Nieobsłużony panic w scoped thread może spowodować panic scope podczas automatycznego dołączania. Jeżeli chcesz nadać awarii workera własną politykę, dołącz go jawnie i obsłuż wynik. Dla zwykłego `JoinHandle` upuszczenie uchwytu odłącza wątek, a zakończenie procesu nie czeka na odłączone wątki. Dlatego kod zapisujący ważne dane powinien mieć kontrolowany moment zamknięcia.

Flaga zatrzymania nie wybudza automatycznie blokującego `recv` ani odczytu pliku. Projekt shutdown musi uwzględniać punkty, w których worker może zauważyć anulowanie. Kanał zamykający, timeout lub osobny mechanizm wybudzenia bywa potrzebny niezależnie od atomowej flagi. Gwarancja kooperacyjnego zatrzymania zależy też od tego, czy zewnętrzne API ma ograniczony czas oczekiwania.

## `Barrier`, stan lokalny wątku i rozmiar puli

`Barrier::new(n)` zatrzymuje uczestników w `wait`, aż dotrze ich `n`. Bariera jest wielokrotnego użytku, a dokładnie jeden uczestnik otrzymuje w danej rundzie wynik `is_leader() == true`; nie zakładaj, który. To narzędzie faz pracy, a nie blokada dostępu do wspólnego `Vec`. Jeśli jeden uczestnik panikuje przed dojściem do bariery, pozostali mogą czekać bez końca. Standardowe `Barrier::wait` nie ma mechanizmu automatycznego wycofania brakującego uczestnika.

~~~rust
use std::sync::{Barrier, atomic::{AtomicUsize, Ordering}};
fn main() {
    let b = Barrier::new(3);
    let liderzy = AtomicUsize::new(0);
    std::thread::scope(|s| {
        for _ in 0..3 {
            s.spawn(|| {
                if b.wait().is_leader() { liderzy.fetch_add(1, Ordering::Relaxed); }
            });
        }
    });
    assert_eq!(liderzy.load(Ordering::Relaxed), 1);
}
~~~

`thread_local!` daje osobną wartość dla każdego wątku systemowego. `Cell` lub `RefCell` w takim magazynie pozwala lokalnie mutować dane bez współdzielonej blokady. Referencja do wartości nie może dowolnie uciec z closure `with`. Nie jest to stan lokalny taska: future wielowątkowego runtime’u może wznowić się na innym workerze. Nie przechowuj tam identyfikatora żądania bez protokołu ustawiania i przywracania kontekstu.

~~~rust
use std::cell::Cell;
thread_local! { static LICZNIK: Cell<u32> = const { Cell::new(0) }; }
fn main() {
    LICZNIK.with(|n| n.set(7));
    let h = std::thread::spawn(|| LICZNIK.with(Cell::get));
    assert_eq!(h.join().unwrap(), 0);
    assert_eq!(LICZNIK.with(Cell::get), 7);
}
~~~

`available_parallelism` zwraca przybliżony sensowny poziom równoległości albo błąd. Nie jest pomiarem aktualnego obciążenia, pełną mapą NUMA ani gwarancją stałych limitów kontenera. Odczytaj go podczas konfiguracji, dopuść jawne nadpisanie i dobierz pulę pomiarem. Nie wywołuj go dla każdego elementu gorącej pętli. Zasoby lokalne wątków i ich destruktory nie powinny być jedynym mechanizmem obowiązkowego trwałego zapisu przy końcu procesu.

## Diagnostyka kompilatora

Błąd „closure may outlive the current function” wskazuje pożyczkę, której `spawn` nie może zaakceptować. `move` pomaga tylko dla posiadanych danych. Jeżeli zadanie musi pożyczyć lokalny bufor, użyj scope albo zmień własność. Błąd dwóch mutowalnych pożyczek nie znika po dodaniu wątków; podziel dane bezpiecznym API. Kompilator nie wykryje natomiast logicznego zakleszczenia, gdy główny wątek czeka na worker czekający na wiadomość, której nikt już nie wyśle.

## Praktyka produkcyjna

Ogranicz liczbę wątków i nie twórz jednego dla każdej drobnej operacji. Koszt obejmuje stos, przełączenia kontekstu i planowanie systemowe. Wyznacz właściciela uchwytów, politykę panic i kolejność shutdown. Nazwy wątków oraz identyfikatory zadań ułatwiają diagnozę. Przy CPU-bound pracy najpierw dobierz ziarnistość podziału i pulę; nadmiar wątków może spowolnić obliczenia. Nie nazywaj testu równoległości dowodem poprawności wszystkich przeplotów.

## Sprawdź, czy rozumiesz

- Dlaczego `move` nie przedłuża życia pożyczonego obiektu?
- Co uzasadnia użycie danych po powrocie scope?
- Dlaczego flaga anulowania nie wystarcza dla blokującego odczytu?

## Ćwiczenia

- `B13-1` — podstawowe: Przenieś wektor do wątku i odbierz jego sumę przez `join`. [Rozwiązanie](../rozwiazania/10_wspolbieznosc/01_watki_i_scoped_threads.md#b13-1).
- `B13-2` — praktyczne: Zmutuj dwie rozłączne połowy tablicy przez scoped threads. [Rozwiązanie](../rozwiazania/10_wspolbieznosc/01_watki_i_scoped_threads.md#b13-2).
- `B13-3` — pogłębione: Zatrzymaj worker zamknięciem kanału, obsługując zakończenie przez `join`. [Rozwiązanie](../rozwiazania/10_wspolbieznosc/01_watki_i_scoped_threads.md#b13-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [thread::scope](https://doc.rust-lang.org/std/thread/fn.scope.html)
- [JoinHandle::join i synchronizacja](https://doc.rust-lang.org/std/thread/struct.JoinHandle.html#method.join)

- [Barrier](https://doc.rust-lang.org/std/sync/struct.Barrier.html)
- [thread_local](https://doc.rust-lang.org/std/macro.thread_local.html)
- [available_parallelism](https://doc.rust-lang.org/std/thread/fn.available_parallelism.html)

## Powiązane tematy

- [Kanały](02_kanaly_i_message_passing.md)
- [`Send`, `Sync` i atomiki](04_send_sync_i_atomiki.md)
- [Atomiki i memory ordering](../10_wspolbieznosc/05_atomics_i_memory_ordering.md)
