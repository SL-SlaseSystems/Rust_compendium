[← Spis treści](../README.md)
<!-- status: expanded -->

# `Arc`, `Mutex`, `RwLock` i `Condvar`

## Cele

Po tym rozdziale potrafisz:

- oddzielić współdzielenie własności od ochrony niezmiennika;
- uzasadnić predykat Condvar i politykę po panic;


Współdzielony stan między wątkami zwykle łączy współdzielone ownership
`Arc<T>` z synchronizacją dostępu.

## `Arc<Mutex<T>>`

~~~rust
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let licznik = Arc::new(Mutex::new(0_u32));
    let mut watki = Vec::new();

    for _ in 0..4 {
        let licznik = Arc::clone(&licznik);
        watki.push(thread::spawn(move || {
            let mut guard = licznik.lock().unwrap();
            *guard += 1;
        }));
    }
    for h in watki { h.join().unwrap(); }
    assert_eq!(*licznik.lock().unwrap(), 4);
}
~~~

Guard odblokowuje mutex przez RAII. Skracaj jego zakres i nie wykonuj pod
blokadą wolnego I/O ani obcego callbacku.

## Poisoning

Jeżeli wątek panikuje z guardem mutexa, standardowy mutex staje się poisoned.
`lock` zwraca wtedy `PoisonError`, ale dane nadal można odzyskać przez
`into_inner` po świadomej ocenie invariants. `unwrap` nie jest jedyną
strategią — może propagować panic do kolejnych wątków.

## `RwLock<T>`

RwLock pozwala wielu czytelnikom albo jednemu piszącemu. Nie gwarantuje
konkretnej polityki fairness; zależy od systemu. Przy krótkim stanie i częstym
zapisie mutex może być szybszy. Zawsze mierz.

~~~rust
use std::sync::RwLock;

fn main() {
    let dane = RwLock::new(vec![1, 2]);
    {
        let odczyt = dane.read().unwrap();
        assert_eq!(odczyt.len(), 2);
    }
    dane.write().unwrap().push(3);
    assert_eq!(&*dane.read().unwrap(), &[1, 2, 3]);
}
~~~

## `Condvar`

Condition variable czeka na zmianę predykatu chronionego tym samym mutexem.
Zawsze sprawdzaj warunek w pętli, bo występują spurious wakeups:

~~~rust
use std::sync::{Arc, Condvar, Mutex};
use std::thread;

fn main() {
    let para = Arc::new((Mutex::new(false), Condvar::new()));
    let worker = Arc::clone(&para);
    let h = thread::spawn(move || {
        let (lock, cv) = &*worker;
        *lock.lock().unwrap() = true;
        cv.notify_one();
    });

    let (lock, cv) = &*para;
    let mut gotowe = lock.lock().unwrap();
    while !*gotowe {
        gotowe = cv.wait(gotowe).unwrap();
    }
    h.join().unwrap();
}
~~~

## Deadlock

Rust zapobiega data races, ale nie deadlockom. Ustal globalną kolejność
blokad, unikaj trzymania kilku naraz i rozważ message passing. `try_lock`
może pomóc, lecz retry bez backoff potrafi stworzyć livelock.


## Model — blokada chroni relację między polami

`Arc` zapewnia współdzieloną własność alokacji i atomowe zarządzanie licznikami referencji. Nie synchronizuje dowolnej mutacji pól `T`. `Mutex` daje wyłączny dostęp przez guard, więc typowym kontraktem jest „wszystkie pola niezmiennika są odczytywane i zmieniane pod tą samą blokadą”. Oddzielne mutexy dla pól powiązanych relacją mogą stworzyć chwilowo niepoprawny stan i ryzyko zakleszczeń.

~~~rust
use std::sync::Mutex;
#[derive(Debug, PartialEq)]
struct Stan { wolne: u32, zajete: u32 }
fn rezerwuj(m: &Mutex<Stan>) -> bool {
    let mut s = m.lock().unwrap();
    if s.wolne == 0 { return false; }
    s.wolne -= 1;
    s.zajete += 1;
    true
}
fn main() {
    let stan = Mutex::new(Stan { wolne: 1, zajete: 0 });
    assert!(rezerwuj(&stan));
    assert!(!rezerwuj(&stan));
    assert_eq!(*stan.lock().unwrap(), Stan { wolne: 0, zajete: 1 });
}
~~~

Sprawdzenie dostępności i aktualizacja tworzą jedną sekcję krytyczną. Gdyby odblokować mutex między `if` a dekrementacją, drugi wątek mógłby wykorzystać ostatnie miejsce. To race condition możliwe nawet bez data race. Bezpieczny Rust nie dowodzi atomowości wieloetapowej operacji biznesowej.

Poisoning standardowego mutexa jest sygnałem ostrzegawczym po części zdarzeń panic, a nie mechanizmem dowodzącym spójności. Dokumentacja opisuje sytuacje, w których panic nie zostanie wykryty w oczekiwany sposób. Kod `unsafe` nie może opierać soundness wyłącznie na fakcie, że mutex „na pewno zostanie poisoned”. `into_inner` odzyskuje dostęp, ale nie naprawia danych; najpierw sprawdź lub odtwórz niezmiennik.

`Condvar::wait` atomowo zwalnia mutex i rozpoczyna oczekiwanie, a przed powrotem odzyskuje blokadę. Powiadomienie nie przechowuje trwałego stanu „gotowe”; stanem jest predykat pod mutexem. Pętla jest potrzebna zarówno dla pozornych wybudzeń, jak i dla konkurenta, który wykorzystał zasób wcześniej. `notify_one` bez zmiany predykatu nie gwarantuje żadnego postępu. Jedna condition variable powinna być używana zgodnie z kontraktem powiązania z mutexem; mieszanie mutexów może panikować.

`RwLock` nie jest automatycznie lepszy dla przewagi odczytów. Znaczenie ma długość sekcji, koszt synchronizacji, polityka systemu i opóźnienie pisarza. Próba uzyskania zapisu z trzymanym odczytem może zakleszczyć kod; standardowe API nie daje uniwersalnej atomowej promocji. Kopiowanie małego snapshotu i szybkie zwolnienie blokady bywa prostsze od trzymania guardu przez dalszą logikę.

## Jednorazowa inicjalizacja: `OnceLock` i `LazyLock`

`OnceLock<T>` pozwala dostarczyć wartość przez `set` albo inicjalizator przez `get_or_init`. Udana inicjalizacja publikuje wartość wszystkim czytelnikom zgodnie z kontraktem synchronizacji typu. Panic inicjalizatora pozostawia komórkę niezainicjalizowaną i pozwala na następną próbę. `get` nie blokuje do zakończenia inicjalizacji; może zwrócić `None`.

`LazyLock<T>` przechowuje inicjalizator podany przy tworzeniu i uruchamia go przy pierwszym wymuszeniu. Inne wątki mogą wtedy czekać na jego koniec. Panic zatruwa LazyLock nieodwracalnie: późniejsze wymuszenie również panikuje. Nie jest to ta sama polityka co ponawianie `OnceLock`. Wybór powinien uwzględniać, czy konfiguracja jest znana dopiero w runtime i czy inicjalizacja może zostać ponowiona.

~~~rust
use std::sync::{LazyLock, OnceLock};
static DOMYSLNA: LazyLock<String> = LazyLock::new(|| String::from("localhost"));
fn main() {
    let port = OnceLock::new();
    assert_eq!(*port.get_or_init(|| 8080_u16), 8080);
    assert_eq!(*port.get_or_init(|| 9090_u16), 8080);
    assert_eq!(DOMYSLNA.as_str(), "localhost");
}
~~~

Powtórny inicjalizator nie zastępuje już utworzonej wartości. Reentrant inicjalizacja tej samej komórki jest błędem projektu i może zakleszczyć wykonanie; nie traktuj jej jako mechanizmu rozwiązywania cykli zależności. Zwykły oczekiwany błąd można przechować jako `Result<T, E>`, ale wtedy zapisany błąd też staje się trwałym wynikiem inicjalizacji. Statyczne wartości nie dają zwykłej fazy Drop przy końcu procesu; shutdown zasobów wymagających zakończenia prowadź jawnie.

## Diagnostyka kompilatora

Błąd pożyczania po próbie zwrócenia `&T` z wnętrza lokalnego guardu wynika z tego, że referencja straciłaby ochronę blokady. Zwróć kopię, posiadany snapshot albo guard z odpowiednim kontraktem. Problemy `Send` związane z guardem wskazują ograniczenie jego przenoszenia między wątkami. Deadlock, nadmierna długość sekcji i zła kolejność blokad nie muszą dać błędu kompilacji; wymagają analizy przepływu i testów kontrolujących synchronizację.

## Praktyka produkcyjna

Zapisz chroniony niezmiennik i globalną kolejność uzyskiwania blokad. Nie wywołuj obcego callbacku pod blokadą, jeśli może wejść ponownie do struktury. W razie poison ustal jawnie: przerwanie, odtworzenie danych albo restart komponentu. Mierz czas oczekiwania i czas trzymania blokady oddzielnie. Dla pracy async zwykły mutex bywa właściwy dla bardzo krótkiej operacji bez `await`, lecz nie może osłaniać oczekiwania na sieć ani wielowątkowej zależności wymagającej tego samego executora.

## Sprawdź, czy rozumiesz

- Dlaczego dwie poprawne operacje na dwóch mutexach mogą złamać niezmiennik?
- Co przechowuje informację o gotowości: predykat czy `notify_one`?
- Dlaczego poisoning nie wystarcza do dowodu soundness?

## Ćwiczenia

- `B15-1` — podstawowe: Zmień dwa powiązane liczniki pod jednym mutexem. [Rozwiązanie](../rozwiazania/10_wspolbieznosc/03_arc_mutex_rwlock_i_condvar.md#b15-1).
- `B15-2` — praktyczne: Poczekaj na niepustą kolejkę przez `Condvar::wait_while`. [Rozwiązanie](../rozwiazania/10_wspolbieznosc/03_arc_mutex_rwlock_i_condvar.md#b15-2).
- `B15-3` — pogłębione: Opisz konkretną politykę naprawy stanu po poisoned mutex bez bezwarunkowego `unwrap`. [Rozwiązanie](../rozwiazania/10_wspolbieznosc/03_arc_mutex_rwlock_i_condvar.md#b15-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [Mutex i advisory poisoning](https://doc.rust-lang.org/std/sync/struct.Mutex.html)
- [Condvar: wait i spurious wakeups](https://doc.rust-lang.org/std/sync/struct.Condvar.html)

- [OnceLock](https://doc.rust-lang.org/std/sync/struct.OnceLock.html)
- [LazyLock i poisoning](https://doc.rust-lang.org/std/sync/struct.LazyLock.html)

## Powiązane tematy

- [Kanały](02_kanaly_i_message_passing.md)
- [`Send` i `Sync`](04_send_sync_i_atomiki.md)
- [Panic safety](../07_obsluga_bledow/03_panic_unwind_i_abort.md)
