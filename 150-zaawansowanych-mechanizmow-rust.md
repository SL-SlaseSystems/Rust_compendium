# 150 zaawansowanych mechanizmów języka Rust

Praktyczny katalog zaawansowanych możliwości Rusta: od ownershipu i lifetime'ów, przez traity i typy generyczne, po `Future`, atomiki, makra proceduralne, projektowanie API, Cargo, testowanie, `unsafe`, `no_std`, optymalizację oraz FFI.

> Stan API: wrzesień 2026. Materiał zakłada **Rust 1.98.1** i **Edition 2024**. Wszystkie przykłady języka i biblioteki standardowej są oparte na stabilnym Ruście, z wyjątkiem punktu 100, który został wyraźnie oznaczony jako `nightly`. Przykłady wykorzystujące Tokio, `proptest`, Miri, Loom lub Criterion są oznaczone jako zależne od narzędzia albo biblioteki. Fragmenty `unsafe` wymagają samodzielnego udowodnienia opisanych inwariantów bezpieczeństwa.

## Spis treści

- [Ownership, lifetime'y i pamięć — 1–20](#ownership-lifetimey-i-pamięć--120)
- [System typów, generyki i traity — 21–45](#system-typów-generyki-i-traity--2145)
- [Closures, konwersje, iteratory i błędy — 46–60](#closures-konwersje-iteratory-i-błędy--4660)
- [Async i współbieżność — 61–80](#async-i-współbieżność--6180)
- [Makra, `const`, `unsafe`, FFI i optymalizacja — 81–100](#makra-const-unsafe-ffi-i-optymalizacja--81100)
- [Projektowanie publicznego API i zaawansowane typy — 101–110](#projektowanie-publicznego-api-i-zaawansowane-typy--101110)
- [Struktury danych, bufory i zero-copy I/O — 111–120](#struktury-danych-bufory-i-zero-copy-io--111120)
- [Produkcyjne async i współbieżność — 121–130](#produkcyjne-async-i-współbieżność--121130)
- [Cargo, konfiguracja, testowanie i diagnostyka — 131–140](#cargo-konfiguracja-testowanie-i-diagnostyka--131140)
- [`no_std`, FFI, layout pamięci i wydajność — 141–150](#no_std-ffi-layout-pamięci-i-wydajność--141150)
- [Źródła](#źródła)

---

## Ownership, lifetime'y i pamięć — 1–20

### 1. Semantyka przenoszenia (`move`)

Przypisanie wartości nieimplementującej `Copy` przenosi jej ownership. Stara zmienna przestaje być dostępna, co zapobiega podwójnemu zwolnieniu zasobu.

```rust
fn consume(value: String) {
    println!("{value}");
}

fn main() {
    let name = String::from("Rust");
    consume(name);
    // println!("{name}"); // błąd: wartość została przeniesiona
}
```

**Zastosowanie:** jawne przekazywanie odpowiedzialności za pliki, sockety, bufory i uchwyty.

### 2. `Copy` kontra jawny `Clone`

`Copy` oznacza niejawne, bitowe kopiowanie bez destruktora. `Clone` może wykonywać kosztowną, głęboką kopię i dlatego jest wywoływany jawnie.

```rust
#[derive(Copy, Clone, Debug)]
struct Point { x: i32, y: i32 }

fn main() {
    let p1 = Point { x: 2, y: 3 };
    let p2 = p1;              // Copy

    let s1 = String::from("data");
    let s2 = s1.clone();      // jawna alokacja i kopia

    println!("{p1:?} {p2:?} {s1} {s2}");
}
```

**Zastosowanie:** kontrola kosztu kopiowania i projektowanie semantyki własnych typów.

### 3. Współdzielone i wyłączne borrow

W danej chwili można mieć wiele `&T` albo dokładnie jedno `&mut T`. Ta reguła eliminuje wyścigi danych już podczas kompilacji.

```rust
fn append_checksum(data: &mut Vec<u8>) {
    let checksum = data.iter().fold(0_u8, |acc, byte| acc ^ byte);
    data.push(checksum);
}

fn main() {
    let mut frame = vec![1, 2, 3];
    append_checksum(&mut frame);
}
```

**Zastosowanie:** bezpieczna mutacja bez garbage collectora i bez blokad w kodzie jednowątkowym.

### 4. Reborrow referencji mutowalnej

Przekazanie `&mut *reference` tworzy krótszy reborrow zamiast przenosić samą referencję mutowalną.

```rust
fn increment(value: &mut i32) {
    *value += 1;
}

fn twice(value: &mut i32) {
    increment(&mut *value);
    increment(&mut *value);
}

fn main() {
    let mut value = 0;
    twice(&mut value);
    assert_eq!(value, 2);
}
```

**Zastosowanie:** wielokrotne używanie jednego wyłącznego dostępu w kolejnych wywołaniach.

### 5. Non-Lexical Lifetimes (NLL)

Borrow kończy się przy ostatnim rzeczywistym użyciu referencji, a nie dopiero przy końcu bloku leksykalnego.

```rust
fn main() {
    let mut values = vec![1, 2, 3];
    let first = &values[0];
    println!("{first}");       // ostatnie użycie `first`

    values.push(4);            // mutowalny borrow jest już dozwolony
}
```

**Zastosowanie:** naturalniejszy kod bez sztucznych bloków ograniczających życie referencji.

### 6. Two-phase borrows

W wybranych, niejawnych borrowach metod Rust najpierw rezerwuje `&mut`, a aktywuje go dopiero przy wywołaniu. Dzięki temu argument może wcześniej odczytać ten sam obiekt.

```rust
fn main() {
    let mut values = vec![10, 20];
    values.push(values.len());
    assert_eq!(values, [10, 20, 2]);
}
```

**Zastosowanie:** wywołania w stylu `collection.push(collection.len())` bez ręcznych zmiennych pomocniczych.

### 7. Częściowe przeniesienie wartości

Można przenieść jedno pole struktury, pozostawiając pola typu `Copy` lub pożyczone pola nadal dostępne. Cała struktura nie może już jednak zostać użyta jako jedna wartość.

```rust
struct User {
    name: String,
    age: u8,
}

fn main() {
    let user = User { name: "Ada".into(), age: 36 };
    let name = user.name;      // przenosi tylko String
    println!("{name}, {}", user.age);
    // drop(user);             // błąd: `user` jest częściowo przeniesiony
}
```

**Zastosowanie:** rozpakowywanie agregatów bez zbędnego klonowania wszystkich pól.

### 8. `ref`, `ref mut` i binding `@` we wzorcach

Wzorzec może pożyczyć fragment wartości albo jednocześnie nazwać całą dopasowaną wartość.

```rust
enum Command {
    Send(String),
    Retry(u8),
}

fn inspect(command: Command) {
    match command {
        Command::Send(ref text) if text.len() > 3 => println!("send: {text}"),
        Command::Send(ref text) => println!("short: {text}"),
        Command::Retry(count @ 1..=3) => println!("retry {count}"),
        Command::Retry(_) => println!("retry limit exceeded"),
    }
}
```

**Zastosowanie:** precyzyjne destructuring bez niechcianego przenoszenia danych.

### 9. Jawne zależności lifetime'ów

Adnotacja lifetime nie wydłuża życia danych — opisuje relację między referencjami wejściowymi i wynikiem.

```rust
fn longest<'a>(left: &'a str, right: &'a str) -> &'a str {
    if left.len() >= right.len() { left } else { right }
}

fn main() {
    let a = String::from("abcd");
    let b = String::from("xyz");
    println!("{}", longest(&a, &b));
}
```

**Zastosowanie:** funkcje zwracające widok na jedno z wejść bez alokacji.

### 10. Reguły lifetime elision

W typowych sygnaturach kompilator sam wyprowadza lifetime'y. W metodzie wynik jest domyślnie wiązany z lifetime'em `&self`.

```rust
struct Header(String);

impl Header {
    // Odpowiednik: fn value<'a>(&'a self) -> &'a str
    fn value(&self) -> &str {
        &self.0
    }
}
```

**Zastosowanie:** zwięzłe API pożyczające dane z obiektu.

### 11. Ograniczenia lifetime: `T: 'a` i `'a: 'b`

`T: 'a` oznacza, że wszystkie referencje zawarte w `T` żyją co najmniej `'a`. Relacja `'long: 'short` pozwala skrócić dłuższy borrow.

```rust
fn shorten<'long: 'short, 'short>(value: &'long str) -> &'short str {
    value
}

struct View<'a, T: 'a> {
    value: &'a T,
}
```

**Zastosowanie:** generyczne kontenery widoków i API łączące kilka poziomów pożyczania.

### 12. Higher-Ranked Trait Bounds (`for<'a>`)

HRTB wymaga, aby ograniczenie działało dla każdego możliwego lifetime'u, a nie dla jednego wybranego przez wywołującego.

```rust
fn apply_to_any<F>(f: F)
where
    F: for<'a> Fn(&'a str) -> &'a str,
{
    let local = String::from("rust");
    assert_eq!(f(&local), "rust");
}

fn identity(value: &str) -> &str { value }

fn main() {
    apply_to_any(identity);
}
```

**Zastosowanie:** generyczne callbacki, parsery i traity operujące na dowolnie krótkich borrowach.

### 13. Wariancja lifetime'ów i typów

Referencja `&'long T` jest kowariantna po lifetime, więc można ją skrócić. Wnętrze `Cell<T>` jest inwariantne, ponieważ pozwala zastępować wartość.

```rust
use std::cell::Cell;
use std::marker::PhantomData;

struct Covariant<'a>(PhantomData<&'a ()>);
struct Invariant<'a>(PhantomData<Cell<&'a ()>>);

fn shorten<'long: 'short, 'short>(_: Covariant<'long>) -> Covariant<'short> {
    Covariant(PhantomData)
}
```

**Zastosowanie:** poprawne projektowanie typów opartych na surowych wskaźnikach i `unsafe`.

### 14. Typy fantomowe przez `PhantomData`

`PhantomData<T>` zajmuje zero bajtów, ale informuje analizę typów o logicznym posiadaniu, wariancji i auto-traitach.

```rust
use std::marker::PhantomData;

struct Meter;
struct Second;

#[derive(Copy, Clone)]
struct Quantity<Unit> {
    value: f64,
    _unit: PhantomData<Unit>,
}

let distance = Quantity::<Meter> { value: 12.0, _unit: PhantomData };
```

**Zastosowanie:** jednostki miary, identyfikatory domenowe i typestate bez kosztu runtime.

### 15. RAII i własny `Drop`

Destruktor wykonuje się deterministycznie przy wyjściu wartości z zakresu, również podczas unwindingu paniki.

```rust
struct Transaction { committed: bool }

impl Drop for Transaction {
    fn drop(&mut self) {
        if !self.committed {
            println!("rollback");
        }
    }
}

impl Transaction {
    fn commit(mut self) {
        self.committed = true;
    }
}
```

**Zastosowanie:** automatyczne zwalnianie blokad, plików, transakcji i zasobów systemowych.

### 16. `mem::take`, `replace` i `swap`

Funkcje przenoszą wartość zza `&mut` bez naruszania zasady, że miejsce musi zawsze zawierać poprawny `T`.

```rust
use std::mem;

struct Buffer { pending: Vec<u8> }

impl Buffer {
    fn flush(&mut self) -> Vec<u8> {
        mem::take(&mut self.pending) // zostawia Vec::default()
    }
}

let mut a = 1;
let mut b = 2;
mem::swap(&mut a, &mut b);
```

**Zastosowanie:** maszyny stanów, kolejki i wyjmowanie pól bez `clone`.

### 17. `Box<T>`, DST i ograniczenie `?Sized`

`Box` nadaje dynamicznie rozmiarowemu `str` lub `dyn Trait` rozmiar znanego wskaźnika. `?Sized` znosi domyślne ograniczenie `T: Sized`.

```rust
fn dynamic_size<T: ?Sized>(value: &T) -> usize {
    std::mem::size_of_val(value)
}

fn main() {
    let text: Box<str> = String::from("rust").into_boxed_str();
    assert_eq!(dynamic_size(&*text), 4);
}
```

**Zastosowanie:** typy trait object, slices i API akceptujące zarówno rozmiarowe, jak i DST.

### 18. `Rc`, `Weak` i przerywanie cykli

`Rc<T>` zapewnia współdzielony ownership w jednym wątku, a `Weak<T>` nie zwiększa silnego licznika i zapobiega cyklom.

```rust
use std::rc::{Rc, Weak};

struct Parent;

struct Child {
    parent: Weak<Parent>,
}

fn main() {
    let parent = Rc::new(Parent);
    let child = Child { parent: Rc::downgrade(&parent) };
    assert!(child.parent.upgrade().is_some());
    drop(parent);
    assert!(child.parent.upgrade().is_none());
}
```

**Zastosowanie:** drzewa, grafy i cache, w których relacja wsteczna nie powinna utrzymywać obiektu przy życiu.

### 19. Ręczne zarządzanie destruktorem przez `ManuallyDrop`

`ManuallyDrop<T>` blokuje automatyczne wywołanie `Drop`. Sam nie służy do przechowywania niezainicjalizowanej pamięci.

```rust
use std::mem::ManuallyDrop;

fn main() {
    let value = ManuallyDrop::new(String::from("owned"));
    let value = ManuallyDrop::into_inner(value);
    drop(value); // dokładnie jedno jawne zwolnienie
}
```

**Zastosowanie:** implementacje kontenerów, unionów i transfer ownershipu przez FFI.

### 20. Bezpieczna reprezentacja niezainicjalizowanej pamięci przez `MaybeUninit`

`MaybeUninit<T>` wyłącza założenie kompilatora, że pamięć już zawiera poprawny `T`. `assume_init` jest bezpieczne dopiero po pełnej inicjalizacji.

```rust
use std::mem::MaybeUninit;

fn main() {
    let mut slot = MaybeUninit::<String>::uninit();
    slot.write(String::from("ready"));

    // SAFETY: `write` zainicjalizował dokładnie ten slot.
    let value = unsafe { slot.assume_init() };
    assert_eq!(value, "ready");
}
```

**Zastosowanie:** wydajne bufory, FFI i częściowa inicjalizacja większych struktur.

---

## System typów, generyki i traity — 21–45

### 21. Newtype pattern

Jednopolowa struktura tworzy odrębny typ bez kosztu runtime i pozwala implementować obce traity dla lokalnego wrappera.

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
struct UserId(u64);

fn load_user(id: UserId) {
    println!("loading {}", id.0);
}

fn main() {
    load_user(UserId(42));
}
```

**Zastosowanie:** value objects DDD, waluty, jednostki i zapobieganie zamianie identyfikatorów.

### 22. Typestate pattern

Stan obiektu jest parametrem typu, więc niedozwolone przejścia nie mają odpowiedniej metody i nie kompilują się.

```rust
use std::marker::PhantomData;

struct Closed;
struct Open;

struct Connection<State> {
    address: String,
    _state: PhantomData<State>,
}

impl Connection<Closed> {
    fn connect(self) -> Connection<Open> {
        Connection { address: self.address, _state: PhantomData }
    }
}

impl Connection<Open> {
    fn send(&self, bytes: &[u8]) { println!("sending {}", bytes.len()); }
}
```

**Zastosowanie:** protokoły, buildery i zasoby z kontrolowaną kolejnością operacji.

### 23. Zero-Sized Types (ZST)

Typ bez pól zajmuje zero bajtów, ale nadal uczestniczy w typowaniu i dispatchu.

```rust
struct Json;
struct Binary;

trait Encoder {
    fn content_type() -> &'static str;
}

impl Encoder for Json {
    fn content_type() -> &'static str { "application/json" }
}

assert_eq!(std::mem::size_of::<Json>(), 0);
```

**Zastosowanie:** tagi typów, strategie wybierane podczas kompilacji i markery stanów.

### 24. Enum jako algebraiczny typ danych

Każdy wariant może przechowywać inne dane, a wyczerpujący `match` wymusza obsłużenie wszystkich stanów.

```rust
enum Acquisition {
    Idle,
    Running { samples: u64 },
    Failed(String),
}

fn status(value: &Acquisition) -> &str {
    match value {
        Acquisition::Idle => "idle",
        Acquisition::Running { .. } => "running",
        Acquisition::Failed(_) => "failed",
    }
}
```

**Zastosowanie:** maszyny stanów bez niepoprawnych kombinacji flag i pól opcjonalnych.

### 25. Niche optimization

Kompilator może wykorzystać niedozwoloną reprezentację typu jako discriminant `Option`. Dla typów takich jak `NonZeroUsize` gwarantuje to brak dodatkowego bajtu.

```rust
use std::mem::size_of;
use std::num::NonZeroUsize;

assert_eq!(
    size_of::<Option<NonZeroUsize>>(),
    size_of::<usize>(),
);
```

**Zastosowanie:** opcjonalne uchwyty i indeksy bez narzutu pamięci.

### 26. Typ nigdy (`!`)

`!` oznacza obliczenie, które nigdy nie zwraca sterowania. Może zostać skoercjonowane do oczekiwanego typu.

```rust
fn fatal(message: &str) -> ! {
    eprintln!("fatal: {message}");
    std::process::exit(1)
}

fn parse_or_exit(text: &str) -> u32 {
    match text.parse() {
        Ok(value) => value,
        Err(_) => fatal("invalid number"),
    }
}
```

**Zastosowanie:** zakończenie procesu, nieskończone pętle i niemożliwe gałęzie sterowania.

### 27. Const generics

Wartość stała może być parametrem typu. Różne długości tablic stają się różnymi typami sprawdzanymi przez kompilator.

```rust
struct Frame<const N: usize> {
    bytes: [u8; N],
}

impl<const N: usize> Frame<N> {
    fn len(&self) -> usize { N }
}

let header = Frame::<16> { bytes: [0; 16] };
assert_eq!(header.len(), 16);
```

**Zastosowanie:** macierze, pakiety protokołu i bufory o rozmiarze znanym w compile time.

### 28. Associated types

Associated type wiąże jedną implementację typu wynikowego z implementorem traitu i upraszcza sygnatury względem dodatkowego parametru generycznego.

```rust
trait Repository {
    type Entity;
    type Error;

    fn find(&self, id: u64) -> Result<Option<Self::Entity>, Self::Error>;
}

fn count<R: Repository>(repo: &R, id: u64) -> Result<usize, R::Error> {
    Ok(repo.find(id)?.is_some() as usize)
}
```

**Zastosowanie:** repozytoria, iteratory i traity z typem zależnym od implementacji.

### 29. Generic Associated Types (GAT)

GAT pozwala, aby associated type sam miał parametry, np. lifetime widoku pożyczonego z `self`.

```rust
trait LendingIterator {
    type Item<'a>
    where
        Self: 'a;

    fn next<'a>(&'a mut self) -> Option<Self::Item<'a>>;
}

struct Windows<'data> { data: &'data [u8], position: usize }

impl<'data> LendingIterator for Windows<'data> {
    type Item<'a> = &'a [u8] where Self: 'a;

    fn next<'a>(&'a mut self) -> Option<Self::Item<'a>> {
        let window = self.data.get(self.position..self.position + 2)?;
        self.position += 1;
        Some(window)
    }
}
```

**Zastosowanie:** lending iterators, parsery zero-copy i widoki związane z borrowem odbiorcy.

### 30. Associated constants

Trait może wymagać stałej zależnej od implementującego typu.

```rust
trait Packet {
    const MAGIC: [u8; 4];
    const VERSION: u8 = 1;
}

struct Telemetry;

impl Packet for Telemetry {
    const MAGIC: [u8; 4] = *b"TLMY";
}

assert_eq!(Telemetry::MAGIC, *b"TLMY");
```

**Zastosowanie:** parametry protokołu, metadane typów i konfiguracja bez instancji.

### 31. Złożone bounds w klauzuli `where`

`where` pozwala czytelnie opisać zależności między typami, associated types i lifetime'ami.

```rust
fn serialize_all<I, T>(items: I) -> String
where
    I: IntoIterator<Item = T>,
    T: std::fmt::Display,
{
    items.into_iter()
        .map(|item| item.to_string())
        .collect::<Vec<_>>()
        .join(",")
}
```

**Zastosowanie:** publiczne API z precyzyjnymi wymaganiami i lepszymi komunikatami kompilatora.

### 32. Supertraits

Trait może wymagać implementacji innego traitu. Metody supertraitu stają się częścią kontraktu.

```rust
use std::fmt::Display;

trait Named: Display {
    fn name(&self) -> &str;

    fn label(&self) -> String {
        format!("{} ({self})", self.name())
    }
}
```

**Zastosowanie:** warstwowe interfejsy, w których wyższy kontrakt buduje na niższym.

### 33. Domyślne metody traitu

Trait może dostarczyć implementację wykorzystującą inne wymagane metody, a konkretny typ może ją nadpisać.

```rust
trait Summary {
    fn title(&self) -> &str;

    fn summary(&self) -> String {
        format!("Tytuł: {}", self.title())
    }
}
```

**Zastosowanie:** rozszerzalne API z minimalnym obowiązkiem implementatora.

### 34. Blanket implementations

Implementacja może objąć każdy typ spełniający ograniczenie. To podstawa wielu konwersji i extension traits.

```rust
trait Loggable {
    fn log(&self);
}

impl<T> Loggable for T
where
    T: std::fmt::Debug,
{
    fn log(&self) { println!("{self:?}"); }
}

42.log();
"rust".log();
```

**Zastosowanie:** dodawanie wspólnego zachowania całym rodzinom typów.

### 35. Coherence i orphan rule

Implementacja jest dozwolona, gdy trait albo implementowany typ jest lokalny. Zapewnia to jedną, jednoznaczną implementację dla każdej pary.

```rust
use std::fmt;

struct Labels(Vec<String>); // lokalny newtype

impl fmt::Display for Labels { // obcy trait dla lokalnego typu
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.0.join(", "))
    }
}
```

**Zastosowanie:** unikanie konfliktów implementacji między niezależnymi crate'ami.

### 36. Sealed trait pattern

Publiczny trait może dziedziczyć po prywatnym traitcie, przez co użytkownik może go używać, ale nie implementować poza crate'em.

```rust
mod api {
    mod private {
        pub trait Sealed {}
        impl Sealed for u32 {}
        impl Sealed for u64 {}
    }

    pub trait WireValue: private::Sealed {
        fn encode(self) -> Vec<u8>;
    }

    impl WireValue for u32 { fn encode(self) -> Vec<u8> { self.to_le_bytes().to_vec() } }
    impl WireValue for u64 { fn encode(self) -> Vec<u8> { self.to_le_bytes().to_vec() } }
}
```

**Zastosowanie:** zachowanie możliwości dodawania metod lub wariantów bez łamania zewnętrznych implementacji.

### 37. Trait objects i dynamic dispatch

`dyn Trait` przechowuje wskaźnik do danych i vtable. Pozwala zebrać heterogeniczne typy za wspólnym interfejsem.

```rust
trait Plugin {
    fn run(&self, input: &str) -> String;
}

fn execute_all(plugins: &[Box<dyn Plugin>], input: &str) -> Vec<String> {
    plugins.iter().map(|plugin| plugin.run(input)).collect()
}
```

**Zastosowanie:** pluginy, adaptery i wybór implementacji w runtime.

### 38. Dyn compatibility

Metoda trait object nie może być generyczna, zwracać nieograniczonego `Self` ani mieć opaque return type. Niedynamiczną metodę można wyłączyć przez `where Self: Sized`.

```rust
trait Service {
    fn name(&self) -> &str; // dostępna przez `dyn Service`

    fn build<T: Default>() -> T
    where
        Self: Sized,
    {
        T::default()
    }
}
```

**Zastosowanie:** projektowanie traitów działających zarówno statycznie, jak i przez vtable.

### 39. Trait object upcasting

Obiekt podtraitu może zostać skoercjonowany do obiektu jego supertraitu. Mechanizm jest stabilny od Rust 1.86.

```rust
trait Base {
    fn id(&self) -> u64;
}

trait Extended: Base {
    fn details(&self) -> String;
}

fn base_view(value: &dyn Extended) -> &dyn Base {
    value
}
```

**Zastosowanie:** warstwowe interfejsy i przekazywanie bogatszej implementacji do prostszego API.

### 40. `impl Trait` i typy opaque

W argumentach `impl Trait` jest skrótem dla parametru generycznego. W wyniku ukrywa konkretny typ wybrany przez funkcję.

```rust
fn positive(values: impl IntoIterator<Item = i32>) -> impl Iterator<Item = i32> {
    values.into_iter().filter(|value| *value > 0)
}

let result: Vec<_> = positive([-2, 1, 3]).collect();
assert_eq!(result, [1, 3]);
```

**Zastosowanie:** ukrywanie skomplikowanych typów iteratorów i stabilniejsze publiczne API.

### 41. Return-position `impl Trait` in traits (RPITIT)

Metoda traitu może zwrócić `impl Trait`; kompilator traktuje go jak anonimowy associated type wybrany przez implementację.

```rust
trait Values {
    fn values(&self) -> impl Iterator<Item = i32> + '_;
}

impl Values for Vec<i32> {
    fn values(&self) -> impl Iterator<Item = i32> + '_ {
        self.iter().copied()
    }
}
```

**Zastosowanie:** statycznie dispatchowane iteratory bez ręcznego GAT lub `Box<dyn Iterator>`.

### 42. `async fn` w traitach

Stabilny Rust pozwala deklarować asynchroniczne metody traitu. Taki trait nie jest automatycznie dyn-compatible, ponieważ wynik jest ukrytym `Future`.

```rust
trait UserGateway {
    type Error;

    async fn load(&self, id: u64) -> Result<String, Self::Error>;
}

async fn print_user<G: UserGateway>(gateway: &G, id: u64) -> Result<(), G::Error> {
    println!("{}", gateway.load(id).await?);
    Ok(())
}
```

**Zastosowanie:** porty i adaptery async z dispatch statycznym.

### 43. Universal Function Call Syntax (UFCS)

Pełna ścieżka `<Type as Trait>::method` rozstrzyga konflikt metod albo wskazuje konkretną implementację.

```rust
trait Json { fn encode(&self) -> String; }
trait Binary { fn encode(&self) -> String; }

struct Message;
impl Json for Message { fn encode(&self) -> String { "{}".into() } }
impl Binary for Message { fn encode(&self) -> String { "00".into() } }

let message = Message;
let json = <Message as Json>::encode(&message);
let binary = Binary::encode(&message);
```

**Zastosowanie:** konflikty nazw i jawny wybór zachowania traitu.

### 44. `Deref` coercion

Implementacja `Deref` może automatycznie przekształcić `&Wrapper` do `&Target` podczas wywołania funkcji lub metody.

```rust
use std::ops::Deref;

struct Name(String);

impl Deref for Name {
    type Target = str;
    fn deref(&self) -> &str { &self.0 }
}

fn greet(name: &str) { println!("Cześć, {name}"); }

let name = Name("Ferris".into());
greet(&name);
```

**Zastosowanie:** smart pointery i przezroczyste wrappery. Nie implementuj `Deref` wyłącznie jako zamiennika zwykłej konwersji.

### 45. Auto-traity `Send` i `Sync`

`Send` pozwala przenieść wartość między wątkami, a `Sync` pozwala współdzielić `&T`. Kompilator wyprowadza je ze składowych typu.

```rust
fn assert_thread_safe<T: Send + Sync>() {}

fn main() {
    assert_thread_safe::<String>();
    assert_thread_safe::<std::sync::Arc<Vec<u8>>>();
    // assert_thread_safe::<std::rc::Rc<u8>>(); // nie jest Send ani Sync
}
```

**Zastosowanie:** statyczne sprawdzanie bezpieczeństwa struktur używanych współbieżnie.

---

## Closures, konwersje, iteratory i błędy — 46–60

### 46. Traity `Fn`, `FnMut` i `FnOnce`

Closure implementuje najsilniejszy możliwy kontrakt wynikający ze sposobu użycia przechwyconych wartości.

```rust
fn call_many(mut f: impl FnMut(i32) -> i32) -> Vec<i32> {
    [1, 2, 3].into_iter().map(&mut f).collect()
}

let mut calls = 0;
let values = call_many(|value| {
    calls += 1; // wymaga FnMut
    value * 2
});

assert_eq!(values, [2, 4, 6]);
assert_eq!(calls, 3);
```

**Zastosowanie:** callbacki z poprawnym kontraktem mutacji i konsumowania środowiska.

### 47. `move` closures

`move` wymusza przejęcie przechwytywanych wartości. Nie oznacza automatycznie, że closure implementuje tylko `FnOnce` — zależy to od użycia danych w ciele.

```rust
use std::thread;

let message = String::from("worker started");
let handle = thread::spawn(move || {
    println!("{message}");
});

handle.join().unwrap();
```

**Zastosowanie:** przenoszenie danych do wątku, zadania lub callbacku o lifetime `'static`.

### 48. Konwersje `From`, `Into`, `TryFrom` i `TryInto`

`From` opisuje konwersję bezbłędną i automatycznie daje `Into`. `TryFrom` służy do walidowanej konwersji zwracającej błąd.

```rust
use std::convert::TryFrom;

struct Port(u16);

impl TryFrom<u32> for Port {
    type Error = &'static str;

    fn try_from(value: u32) -> Result<Self, Self::Error> {
        u16::try_from(value).map(Port).map_err(|_| "port poza zakresem")
    }
}

let port = Port::try_from(8080_u32).unwrap();
assert_eq!(port.0, 8080);
```

**Zastosowanie:** walidowane value objects i spójny system konwersji.

### 49. `AsRef` kontra `Borrow`

`AsRef` jest tanią konwersją referencji. `Borrow` dodatkowo wymaga zgodnego `Eq`, `Ord` i `Hash`, dzięki czemu kolekcja może wyszukiwać kluczem innego typu.

```rust
use std::collections::HashMap;

fn byte_count(value: impl AsRef<[u8]>) -> usize {
    value.as_ref().len()
}

let mut users = HashMap::<String, u64>::new();
users.insert("alice".into(), 1);

assert_eq!(users.get("alice"), Some(&1)); // String: Borrow<str>
assert_eq!(byte_count("rust"), 4);
```

**Zastosowanie:** elastyczne API bez alokacji i heterogeniczne wyszukiwanie w mapach.

### 50. Przeciążanie operatorów

Operatory są mapowane na traity z `std::ops`. Typ wyniku nie musi być taki sam jak typ argumentów.

```rust
use std::ops::Add;

#[derive(Debug, PartialEq)]
struct Meters(f64);

impl Add for Meters {
    type Output = Meters;

    fn add(self, rhs: Self) -> Self::Output {
        Meters(self.0 + rhs.0)
    }
}

assert_eq!(Meters(2.0) + Meters(3.5), Meters(5.5));
```

**Zastosowanie:** jednostki, macierze, liczby zespolone i typy domenowe o naturalnej algebrze.

### 51. Leniwe łańcuchy iteratorów

Adaptery iteratora nie wykonują pracy, dopóki konsument nie zażąda elementów.

```rust
let result: Vec<_> = (0..)
    .inspect(|value| println!("sprawdzam {value}"))
    .filter(|value| value % 2 == 0)
    .map(|value| value * value)
    .take(4)
    .collect();

assert_eq!(result, [0, 4, 16, 36]);
```

**Zastosowanie:** strumieniowe transformacje bez kolekcji pośrednich.

### 52. Własna implementacja `Iterator`

Wystarczy zdefiniować associated type `Item` oraz `next`; pozostałe adaptery są dostarczane domyślnie.

```rust
struct Countdown(u8);

impl Iterator for Countdown {
    type Item = u8;

    fn next(&mut self) -> Option<Self::Item> {
        if self.0 == 0 { return None; }
        let current = self.0;
        self.0 -= 1;
        Some(current)
    }
}

assert_eq!(Countdown(3).collect::<Vec<_>>(), [3, 2, 1]);
```

**Zastosowanie:** własne generatory sekwencji, kursory i skanowanie protokołu.

### 53. `DoubleEndedIterator`, `ExactSizeIterator` i `FusedIterator`

Te dodatkowe kontrakty pozwalają konsumować sekwencję z obu końców, znać pozostałą długość i zagwarantować trwałe `None` po zakończeniu.

```rust
use std::iter::FusedIterator;

fn consume<I>(mut iter: I)
where
    I: DoubleEndedIterator + ExactSizeIterator + FusedIterator,
    I::Item: std::fmt::Debug,
{
    println!("len={}, first={:?}, last={:?}", iter.len(), iter.next(), iter.next_back());
}

consume([1, 2, 3, 4].iter().fuse());
```

**Zastosowanie:** wydajniejsze algorytmy, parsery dwukierunkowe i prealokacja wyniku.

### 54. `FromIterator` i zaawansowane `collect`

`collect` wybiera wynik przez `FromIterator`. Kolekcjonowanie iteratora `Result<T, E>` zatrzymuje się na pierwszym błędzie.

```rust
fn parse_all(values: &[&str]) -> Result<Vec<u32>, std::num::ParseIntError> {
    values.iter().map(|text| text.parse::<u32>()).collect()
}

assert_eq!(parse_all(&["10", "20"]).unwrap(), [10, 20]);
assert!(parse_all(&["10", "x", "20"]).is_err());
```

**Zastosowanie:** budowanie kolekcji i agregowanie walidacji bez ręcznej pętli.

### 55. Krótkie spięcie przez `try_fold`

`try_fold` łączy fold z mechanizmem `Try`, przerywając pracę po `Err` lub `None`.

```rust
fn checked_sum(values: impl IntoIterator<Item = u64>) -> Option<u64> {
    values.into_iter().try_fold(0, |sum, value| sum.checked_add(value))
}

assert_eq!(checked_sum([1, 2, 3]), Some(6));
assert_eq!(checked_sum([u64::MAX, 1]), None);
```

**Zastosowanie:** walidowane agregacje bez osobnej flagi błędu.

### 56. Zaawansowane combinatory `Option`

Combinatory pozwalają modelować brak wartości bez zagnieżdżonych instrukcji warunkowych.

```rust
fn normalized_port(value: Option<&str>) -> Option<u16> {
    value
        .map(str::trim)
        .filter(|text| !text.is_empty())
        .and_then(|text| text.parse().ok())
        .filter(|port| *port != 0)
}

assert_eq!(normalized_port(Some(" 8080 ")), Some(8080));
```

**Zastosowanie:** pipeline parsowania opcjonalnej konfiguracji.

### 57. Zaawansowane combinatory `Result`

`map`, `and_then`, `map_err`, `inspect` i `inspect_err` rozdzielają transformację sukcesu, błędu i obserwację bez zmiany wartości.

```rust
fn load_port(text: &str) -> Result<u16, String> {
    text.trim()
        .parse::<u16>()
        .inspect(|port| println!("parsed {port}"))
        .map_err(|error| format!("invalid port: {error}"))
        .and_then(|port| (port != 0).then_some(port).ok_or("port 0 forbidden".into()))
}
```

**Zastosowanie:** czytelne pipeline'y operacji zawodnych i mapowanie błędów między warstwami.

### 58. Operator `?` i automatyczna konwersja błędu

`?` zwraca wcześniej z funkcji i konwertuje błąd przez `From`, jeżeli typ błędu warstwy wyższej to obsługuje.

```rust
use std::{fs, io, num::ParseIntError};

#[derive(Debug)]
enum ConfigError { Io(io::Error), Number(ParseIntError) }

impl From<io::Error> for ConfigError {
    fn from(error: io::Error) -> Self { Self::Io(error) }
}

impl From<ParseIntError> for ConfigError {
    fn from(error: ParseIntError) -> Self { Self::Number(error) }
}

fn load_number(path: &str) -> Result<u64, ConfigError> {
    Ok(fs::read_to_string(path)?.trim().parse()?)
}
```

**Zastosowanie:** propagacja błędów z zachowaniem typowanego kontraktu warstwy.

### 59. Własny błąd z `std::error::Error::source`

Implementacja `source` zachowuje łańcuch przyczyn, który narzędzia mogą raportować lub logować.

```rust
use std::{error::Error, fmt, io};

#[derive(Debug)]
struct LoadError { path: String, source: io::Error }

impl fmt::Display for LoadError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "cannot load {}", self.path)
    }
}

impl Error for LoadError {
    fn source(&self) -> Option<&(dyn Error + 'static)> { Some(&self.source) }
}
```

**Zastosowanie:** błędy domenowe z techniczną przyczyną i pełnym kontekstem diagnostycznym.

### 60. `let else`, let-chains, `@` i guardy

Edition 2024 pozwala łączyć dopasowania `let` przez `&&`. `let else` upraszcza wczesne wyjście, a `@` zachowuje dopasowaną wartość.

```rust
fn classify(input: Option<&str>) -> &'static str {
    let Some(text) = input else { return "missing" };

    if let Ok(number @ 10..=99) = text.parse::<u32>()
        && number % 2 == 0
    {
        "two-digit even"
    } else {
        "other"
    }
}
```

**Zastosowanie:** płaskie walidacje i złożone dopasowania bez zagnieżdżonych `match`.

---

## Async i współbieżność — 61–80

### 61. `async fn` jako maszyna stanów

Wywołanie `async fn` tworzy leniwy obiekt implementujący `Future`; ciało zaczyna pracę dopiero podczas pollingu przez executor.

```rust
use std::future::Future;

async fn answer() -> u32 { 42 }

fn build_future() -> impl Future<Output = u32> {
    answer()
}

let future = build_future(); // jeszcze nie wykonuje ciała `answer`
drop(future);
```

**Zastosowanie:** nieblokujące operacje I/O i miliony lekkich zadań zarządzanych przez runtime.

### 62. Ręczna implementacja `Future`

`Future::poll` zwraca `Ready` albo `Pending`. Po `Pending` implementacja musi doprowadzić do wywołania najnowszego `Waker`, gdy pojawi się postęp.

```rust
use std::{future::Future, pin::Pin, task::{Context, Poll}};

struct Ready<T>(Option<T>);

impl<T: Unpin> Future for Ready<T> {
    type Output = T;

    fn poll(mut self: Pin<&mut Self>, _cx: &mut Context<'_>) -> Poll<T> {
        Poll::Ready(self.0.take().expect("future polled after completion"))
    }
}
```

**Zastosowanie:** własne prymitywy async, adaptery callbacków i integracja z systemowym I/O.

### 63. `Pin` i auto-trait `Unpin`

`Pin<P>` gwarantuje, że pointee nie zostanie przeniesiony, jeśli `T: !Unpin`. Większość zwykłych typów implementuje `Unpin`, więc ograniczenie ich nie dotyczy.

```rust
use std::{marker::PhantomPinned, pin::Pin};

struct Immovable {
    data: String,
    _pin: PhantomPinned,
}

let pinned: Pin<Box<Immovable>> = Box::pin(Immovable {
    data: "fixed address".into(),
    _pin: PhantomPinned,
});

assert_eq!(pinned.as_ref().get_ref().data, "fixed address");
```

**Zastosowanie:** self-referential futures i inne typy wrażliwe na zmianę adresu.

### 64. Pinowanie na stosie przez `pin!`

Makro `pin!` tworzy lokalny `Pin<&mut T>` bez alokacji. Dostęp do przypiętej wartości odbywa się przez reborrow `as_mut()`.

```rust
use std::{future::Future, pin::pin, task::{Context, Poll, Waker}};

let future = async { 42 };
let mut future = pin!(future);
let mut context = Context::from_waker(Waker::noop());

assert_eq!(future.as_mut().poll(&mut context), Poll::Ready(42));
```

**Zastosowanie:** ręczny polling i kompozycja future bez `Box::pin`.

### 65. `Waker` i minimalny executor

`Waker` informuje executor, że zadanie może zostać ponownie polled. Bezpieczny trait `Wake` pozwala zbudować waker bez ręcznej tabeli `RawWakerVTable`.

```rust
use std::{future::Future, pin::pin, sync::Arc, task::{Context, Poll, Wake}, thread};

struct ThreadWaker(thread::Thread);

impl Wake for ThreadWaker {
    fn wake(self: Arc<Self>) { self.0.unpark(); }
}

fn block_on<T>(future: impl Future<Output = T>) -> T {
    let mut future = pin!(future);
    let waker = Arc::new(ThreadWaker(thread::current())).into();
    let mut context = Context::from_waker(&waker);

    loop {
        match future.as_mut().poll(&mut context) {
            Poll::Ready(value) => return value,
            Poll::Pending => thread::park(),
        }
    }
}
```

**Zastosowanie:** zrozumienie działania runtime'ów i integracja event loop z future.

### 66. Tworzenie combinatora przez `poll_fn`

`poll_fn` zamienia closure przyjmujące `Context` w pełny `Future`. Można nim zbudować prosty `select`.

```rust
use std::{future::{self, Future}, pin::pin, task::Poll};

async fn first<T>(a: impl Future<Output = T>, b: impl Future<Output = T>) -> T {
    let (mut a, mut b) = (pin!(a), pin!(b));

    future::poll_fn(move |cx| {
        if let Poll::Ready(value) = a.as_mut().poll(cx) {
            Poll::Ready(value)
        } else {
            b.as_mut().poll(cx)
        }
    }).await
}
```

**Zastosowanie:** timeouty, select, bridge do callbacków i własne prymitywy async.

### 67. `async move` blocks

Blok async jest wyrażeniem zwracającym anonimowy `Future`. `move` przenosi przechwycone wartości do jego maszyny stanów.

```rust
fn build_request(body: String) -> impl std::future::Future<Output = usize> {
    async move {
        send_bytes(body.as_bytes()).await;
        body.len()
    }
}

async fn send_bytes(_: &[u8]) {}
```

**Zastosowanie:** future o lifetime `'static` przekazywane do executora.

### 68. Async closures i rodzina `AsyncFn`

Async closure może pożyczać przechwycone dane przez czas zwróconego future. Bounds `AsyncFn`, `AsyncFnMut` i `AsyncFnOnce` opisują sposób wywołania.

```rust
async fn repeat<F>(callback: F)
where
    F: AsyncFn(u64),
{
    callback(1).await;
    callback(2).await;
}

async fn demo() {
    repeat(async |value| {
        println!("value={value}");
    }).await;
}
```

**Zastosowanie:** generyczne callbacki async bez ręcznego boxowania future.

### 69. Warunek `Send` dla future

Future jest `Send`, jeśli wszystkie wartości przechowywane przez punkty `.await` są `Send`. `Rc` trzymane przez `.await` może uniemożliwić przeniesienie zadania między wątkami.

```rust
use std::sync::Arc;

fn assert_send<T: Send>(_: T) {}

let shared = Arc::new(String::from("data"));
let future = async move {
    yield_once().await;
    println!("{shared}");
};

assert_send(future);

async fn yield_once() {}
```

**Zastosowanie:** diagnozowanie błędów `future cannot be sent between threads safely`.

### 70. Współdzielony ownership przez `Arc`

`Arc<T>` atomowo zlicza referencje i może być współdzielony między wątkami, jeżeli `T` spełnia odpowiednie auto-traity.

```rust
use std::{sync::Arc, thread};

let data = Arc::new(vec![1, 2, 3]);
let handles: Vec<_> = (0..3)
    .map(|index| {
        let data = Arc::clone(&data);
        thread::spawn(move || data[index])
    })
    .collect();

let values: Vec<_> = handles.into_iter().map(|h| h.join().unwrap()).collect();
assert_eq!(values, [1, 2, 3]);
```

**Zastosowanie:** niezmienny stan, konfiguracja i zasoby współdzielone przez workery.

### 71. Scoped threads

`thread::scope` gwarantuje zakończenie wątków przed wyjściem z zakresu, dlatego mogą one pożyczać dane ze stosu.

```rust
use std::thread;

let values = vec![10, 20, 30, 40];

thread::scope(|scope| {
    let left = scope.spawn(|| values[..2].iter().sum::<i32>());
    let right = scope.spawn(|| values[2..].iter().sum::<i32>());
    assert_eq!(left.join().unwrap() + right.join().unwrap(), 100);
});
```

**Zastosowanie:** równoległe przetwarzanie pożyczonych fragmentów bez `Arc` i bez `'static`.

### 72. `Mutex`, RAII guard i poisoning

Guard zwalnia blokadę w `Drop`. Panika podczas posiadania locka zatruwa mutex, ostrzegając, że chronione inwarianty mogły zostać naruszone.

```rust
use std::sync::Mutex;

let state = Mutex::new(vec![1, 2]);

{
    let mut guard = state.lock().unwrap_or_else(|poisoned| poisoned.into_inner());
    guard.push(3);
} // unlock przez Drop

assert_eq!(*state.lock().unwrap(), [1, 2, 3]);
```

**Zastosowanie:** mutowalny stan współdzielony i świadome odzyskiwanie po panice.

### 73. Wielu czytelników przez `RwLock`

`RwLock` dopuszcza wielu równoczesnych czytelników albo jednego pisarza. Polityka pierwszeństwa zależy od systemu operacyjnego.

```rust
use std::sync::RwLock;

let config = RwLock::new(String::from("v1"));

{
    let a = config.read().unwrap();
    let b = config.read().unwrap();
    assert_eq!(&*a, &*b);
}

*config.write().unwrap() = "v2".into();
```

**Zastosowanie:** konfiguracja i cache z dominującym odczytem.

### 74. Oczekiwanie na warunek przez `Condvar`

Wątek zasypia bez aktywnego zużycia CPU. Predykat trzeba sprawdzać w pętli z powodu spurious wakeups.

```rust
use std::sync::{Arc, Condvar, Mutex};

let pair = Arc::new((Mutex::new(false), Condvar::new()));
let (lock, cvar) = &*pair;

let mut ready = lock.lock().unwrap();
while !*ready {
    ready = cvar.wait(ready).unwrap();
}
```

**Zastosowanie:** kolejki blokujące, pule wątków i koordynacja producent–konsument.

### 75. Synchronizacja faz przez `Barrier`

Barrier blokuje wszystkie uczestniczące wątki, dopóki zadana liczba nie osiągnie tego samego punktu.

```rust
use std::{sync::{Arc, Barrier}, thread};

let barrier = Arc::new(Barrier::new(3));
let handles: Vec<_> = (0..3).map(|id| {
    let barrier = Arc::clone(&barrier);
    thread::spawn(move || {
        prepare(id);
        barrier.wait();
        run_phase_two(id);
    })
}).collect();

for handle in handles { handle.join().unwrap(); }

fn prepare(_: usize) {}
fn run_phase_two(_: usize) {}
```

**Zastosowanie:** algorytmy wielofazowe i jednoczesny start grupy workerów.

### 76. Message passing przez `mpsc::channel`

Kanał przenosi ownership wiadomości od wielu producentów do jednego konsumenta.

```rust
use std::{sync::mpsc, thread};

let (tx, rx) = mpsc::channel();

for id in 0..3 {
    let tx = tx.clone();
    thread::spawn(move || tx.send(format!("job-{id}")).unwrap());
}
drop(tx); // pozwala iteratorowi odbiorcy zakończyć się

for message in rx {
    println!("{message}");
}
```

**Zastosowanie:** actor-like architecture i ograniczenie współdzielonej mutacji.

### 77. Backpressure przez `sync_channel`

Kanał o ograniczonym buforze blokuje producenta po zapełnieniu. Pojemność zero tworzy kanał rendezvous.

```rust
use std::sync::mpsc::sync_channel;

let (tx, rx) = sync_channel::<Vec<u8>>(2);

std::thread::spawn(move || {
    for frame in frames() {
        tx.send(frame).unwrap(); // zwalnia tempo producenta
    }
});

for frame in rx { process(frame); }

fn frames() -> Vec<Vec<u8>> { vec![vec![1], vec![2]] }
fn process(_: Vec<u8>) {}
```

**Zastosowanie:** kontrola pamięci w pipeline'ach danych i naturalne równoważenie tempa.

### 78. Atomiki i memory ordering

Atomiki zapewniają operacje bez data race. `Relaxed` gwarantuje atomowość, `Acquire`/`Release` publikację danych, a `SeqCst` dodatkowo jeden globalny porządek.

```rust
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};

static DATA: AtomicUsize = AtomicUsize::new(0);
static READY: AtomicBool = AtomicBool::new(false);

fn publish(value: usize) {
    DATA.store(value, Ordering::Relaxed);
    READY.store(true, Ordering::Release);
}

fn read() -> Option<usize> {
    READY.load(Ordering::Acquire).then(|| DATA.load(Ordering::Relaxed))
}
```

**Zastosowanie:** liczniki, flagi, lock-free structures i niskopoziomowa synchronizacja.

### 79. Jednorazowa inicjalizacja przez `OnceLock` i `LazyLock`

Oba typy są thread-safe. `OnceLock` przyjmuje inicjalizator przy użyciu, a `LazyLock` przechowuje go w samej statycznej wartości.

```rust
use std::sync::{LazyLock, OnceLock};

static CONFIG: OnceLock<String> = OnceLock::new();
static POWERS: LazyLock<Vec<u64>> = LazyLock::new(|| {
    (0..16).map(|n| 1_u64 << n).collect()
});

let config = CONFIG.get_or_init(|| "production".into());
assert_eq!(config, "production");
assert_eq!(POWERS[4], 16);
```

**Zastosowanie:** globalna konfiguracja, kosztowne tablice i inicjalizacja bez własnego `unsafe`.

### 80. Thread-local storage i dostępna równoległość

`thread_local!` tworzy osobną wartość dla każdego wątku. `available_parallelism` podaje przybliżoną liczbę workerów odpowiednią dla środowiska.

```rust
use std::{cell::Cell, thread};

thread_local! {
    static REQUESTS: Cell<u64> = const { Cell::new(0) };
}

REQUESTS.with(|counter| counter.set(counter.get() + 1));

let workers = thread::available_parallelism()
    .map(|count| count.get())
    .unwrap_or(1);

println!("workers={workers}");
```

**Zastosowanie:** cache per-thread, stan bibliotek C i dobór rozmiaru puli workerów.

---

## Makra, `const`, `unsafe`, FFI i optymalizacja — 81–100

### 81. Wielowariantowe `macro_rules!`

Makro deklaratywne dopasowuje tokeny do kolejnych reguł i może generować wyrażenia, typy, wzorce lub elementy modułu.

```rust
macro_rules! calculate {
    (double $value:expr) => { $value * 2 };
    (square $value:expr) => { $value * $value };
}

assert_eq!(calculate!(double 5), 10);
assert_eq!(calculate!(square 5), 25);
```

**Zastosowanie:** małe DSL-e i eliminowanie powtarzalnego kodu o wspólnej składni.

### 82. Fragment specifiers i repetycje makra

Makro rozróżnia m.in. `expr`, `ty`, `ident`, `pat` i `tt`. Konstrukcja `$()*` powtarza fragment dowolną liczbę razy.

```rust
macro_rules! map {
    ($( $key:expr => $value:expr ),* $(,)?) => {{
        let mut map = ::std::collections::HashMap::new();
        $( map.insert($key, $value); )*
        map
    }};
}

let ports = map! {
    "http" => 80,
    "https" => 443,
};
```

**Zastosowanie:** ergonomiczne konstruktory kolekcji i generowanie wielu podobnych elementów.

### 83. Rekurencyjny TT muncher

Makro może konsumować po jednym token tree i rekurencyjnie przetwarzać resztę wejścia.

```rust
macro_rules! count_tokens {
    () => { 0_usize };
    ($head:tt $($tail:tt)*) => { 1_usize + count_tokens!($($tail)*) };
}

assert_eq!(count_tokens!(alpha + beta * 3), 5);
```

**Zastosowanie:** parsery DSL w `macro_rules!`. Głęboka rekurencja może zwiększać czas kompilacji.

### 84. Higiena makr i ścieżka `$crate`

Identyfikatory lokalne makra nie kolidują z kodem wywołującym, a `$crate` wskazuje crate, w którym makro zostało zdefiniowane.

```rust
pub fn internal_log(message: &str) {
    eprintln!("{message}");
}

#[macro_export]
macro_rules! app_log {
    ($message:expr) => {{
        let temporary = $message;
        $crate::internal_log(temporary);
    }};
}
```

**Zastosowanie:** eksportowane makra odporne na importy i nazwy w crate użytkownika.

### 85. Funkcyjne makro proceduralne

Proc macro działa w osobnym crate typu `proc-macro` i transformuje wejściowy `TokenStream` w tokeny wynikowe.

```toml
# Cargo.toml crate'u makra
[lib]
proc-macro = true
```

```rust
use proc_macro::TokenStream;

#[proc_macro]
pub fn answer(_input: TokenStream) -> TokenStream {
    "42_u32".parse().unwrap()
}
```

```rust
let value = macros::answer!();
assert_eq!(value, 42);
```

**Zastosowanie:** generowanie kodu z własnej składni w compile time.

### 86. Własne `derive` proceduralne

Derive macro otrzymuje deklarację typu i generuje dodatkową implementację. W praktyce zwykle używa się `syn` do parsowania i `quote` do generowania.

```rust
// crate proc-macro; zależności: syn = "2", quote = "1"
#[proc_macro_derive(EntityName)]
pub fn derive_entity_name(input: proc_macro::TokenStream) -> proc_macro::TokenStream {
    let input = syn::parse_macro_input!(input as syn::DeriveInput);
    let name = input.ident;

    quote::quote! {
        impl EntityName for #name {
            fn entity_name() -> &'static str { stringify!(#name) }
        }
    }.into()
}
```

**Zastosowanie:** serializacja, ORM, walidacja i automatyczne implementacje traitów.

### 87. Attribute procedural macro

Makro atrybutowe może otrzymać własne argumenty i cały element, a następnie zastąpić go zmodyfikowaną wersją.

```rust
// crate proc-macro; zależności: syn = { version = "2", features = ["full"] }, quote = "1"
#[proc_macro_attribute]
pub fn traced(
    _args: proc_macro::TokenStream,
    item: proc_macro::TokenStream,
) -> proc_macro::TokenStream {
    let function = syn::parse_macro_input!(item as syn::ItemFn);
    let signature = function.sig;
    let block = function.block;

    quote::quote! {
        #signature {
            println!("enter {}", stringify!(#signature));
            #block
        }
    }.into()
}
```

**Zastosowanie:** tracing, routingi, test fixtures i generowanie kodu wokół funkcji.

### 88. Obliczenia compile-time przez `const fn`

`const fn` może zostać wykonana podczas kompilacji, jeżeli jest użyta w kontekście stałym, albo normalnie w runtime.

```rust
const fn fibonacci(n: usize) -> u64 {
    let (mut a, mut b, mut index) = (0, 1, 0);
    while index < n {
        (a, b) = (b, a + b);
        index += 1;
    }
    a
}

const FIB_20: u64 = fibonacci(20);
assert_eq!(FIB_20, 6765);
```

**Zastosowanie:** tablice lookup, parametry protokołu i walidacja konfiguracji podczas kompilacji.

### 89. Inline const blocks

`const { ... }` wymusza ewaluację wyrażenia w compile time i może zależeć od parametrów generycznych otaczającego elementu.

```rust
fn type_size<T>() -> usize {
    const { std::mem::size_of::<T>() }
}

let cells = [const { std::cell::Cell::new(0_u32) }; 8];
assert_eq!(cells.len(), 8);
assert_eq!(type_size::<u64>(), 8);
```

**Zastosowanie:** stałe zależne od monomorfizowanego typu i tworzenie elementów tablic bez `Copy`.

### 90. Asercje podczas kompilacji

Panika w ewaluowanym kontekście stałym powoduje błąd kompilacji, dzięki czemu można sprawdzać założenia reprezentacji.

```rust
#[repr(C)]
struct Header {
    kind: u16,
    flags: u16,
    length: u32,
}

const _: () = {
    assert!(std::mem::size_of::<Header>() == 8);
    assert!(std::mem::align_of::<Header>() >= 2);
};
```

**Zastosowanie:** weryfikacja layoutu FFI, limitów i inwariantów stałych.

### 91. `unsafe fn` i jawny kontrakt bezpieczeństwa

`unsafe fn` przenosi obowiązek spełnienia precondition na wywołującego. W Edition 2024 niebezpieczna operacja w jej ciele nadal powinna być w osobnym `unsafe` block.

```rust
/// # Safety
/// `ptr` musi wskazywać na poprawny, wyrównany `u32` dostępny do odczytu.
unsafe fn read_u32(ptr: *const u32) -> u32 {
    unsafe { ptr.read() }
}

let value = 42_u32;
// SAFETY: wskaźnik pochodzi z żywej, poprawnie wyrównanej referencji.
assert_eq!(unsafe { read_u32(&value) }, 42);
```

**Zastosowanie:** mały, audytowalny rdzeń `unsafe` otoczony bezpiecznym API.

### 92. Surowe wskaźniki i unaligned access

Raw pointer nie podlega zwykłym regułom borrow checkera, ale dereferencja wymaga poprawności, wyrównania, inicjalizacji i braku niedozwolonego aliasingu.

```rust
#[repr(C, packed)]
struct Packed {
    tag: u8,
    value: u32,
}

let packet = Packed { tag: 1, value: 0xAABBCCDD };
let ptr = std::ptr::addr_of!(packet.value);

// SAFETY: `ptr` jest poprawny do odczytu, ale może być niewyrównany.
let value = unsafe { ptr.read_unaligned() };
assert_eq!(value, 0xAABBCCDD);
```

**Zastosowanie:** parsowanie packed structures, sterowniki i pamięć mapowana.

### 93. `NonNull<T>` w implementacji kontenera

`NonNull<T>` reprezentuje kowariantny, niepusty surowy wskaźnik. Sam nie gwarantuje ważności, wyrównania ani ownershipu.

```rust
use std::ptr::NonNull;

struct Owned<T> {
    ptr: NonNull<T>,
}

impl<T> Owned<T> {
    fn new(value: T) -> Self {
        let ptr = NonNull::from(Box::leak(Box::new(value)));
        Self { ptr }
    }
}

impl<T> Drop for Owned<T> {
    fn drop(&mut self) {
        // SAFETY: `ptr` pochodzi z jednego Box::leak i jest zwalniany dokładnie raz.
        unsafe { drop(Box::from_raw(self.ptr.as_ptr())) }
    }
}
```

**Zastosowanie:** wnętrze własnych smart pointerów, list i alokatorów.

### 94. Strict provenance i adres wskaźnika

Adres liczbowy nie opisuje pełnej zdolności dostępu do obiektu. Metody `addr` i `with_addr` zachowują provenance istniejącego wskaźnika.

```rust
let values = [10_u32, 20, 30];
let base = values.as_ptr();
let second_address = base.addr() + std::mem::size_of::<u32>();
let second = base.with_addr(second_address);

// SAFETY: wyliczony adres wskazuje na drugi element tej samej żywej tablicy.
assert_eq!(unsafe { *second }, 20);
```

**Zastosowanie:** niskopoziomowe struktury danych i poprawne manipulowanie adresami bez gubienia provenance.

### 95. Stabilny layout przez `#[repr(C)]`

Domyślny layout Rusta nie jest publicznym ABI. `repr(C)` narzuca kolejność i zasady layoutu zgodne z reprezentacją platformy C.

```rust
#[repr(C)]
#[derive(Debug, Copy, Clone)]
pub struct SampleI16 {
    pub real: i16,
    pub imag: i16,
}

assert_eq!(std::mem::size_of::<SampleI16>(), 4);
```

**Zastosowanie:** FFI, formaty binarne i przekazywanie struktur do sterowników.

### 96. Przezroczysty wrapper przez `#[repr(transparent)]`

Typ ma taki sam layout i ABI jak jego jedyne niezerowe pole, zachowując jednocześnie odrębną semantykę w typach.

```rust
#[repr(transparent)]
#[derive(Copy, Clone)]
struct FileDescriptor(std::ffi::c_int);

unsafe extern "C" {
    fn close(fd: std::ffi::c_int) -> std::ffi::c_int;
}

fn close_fd(fd: FileDescriptor) -> i32 {
    // SAFETY: `fd` jest przekazywany z ABI zgodnym z c_int.
    unsafe { close(fd.0) }
}
```

**Zastosowanie:** typowane uchwyty FFI bez kosztu konwersji.

### 97. `unsafe extern` i ABI C w Edition 2024

Blok deklaracji obcych funkcji musi być `unsafe`, ponieważ poprawność sygnatur jest obowiązkiem autora. Pojedynczy element można oznaczyć jako `safe`, jeśli każdy argument jest poprawny.

```rust
use std::ffi::{c_char, CStr};

#[link(name = "c")]
unsafe extern "C" {
    safe fn abs(value: std::ffi::c_int) -> std::ffi::c_int;
    unsafe fn strlen(text: *const c_char) -> usize;
}

fn length(text: &CStr) -> usize {
    // SAFETY: CStr gwarantuje poprawny wskaźnik do NUL-terminated string.
    unsafe { strlen(text.as_ptr()) }
}
```

**Zastosowanie:** wywoływanie bibliotek C z jawną granicą odpowiedzialności.

### 98. `union` i interpretacja wspólnej pamięci

Wszystkie pola unionu współdzielą pamięć. Zapis jest bezpieczny, ale odczyt wymaga `unsafe`, ponieważ aktywny wariant nie jest śledzony.

```rust
#[repr(C)]
union Bits {
    float: f32,
    integer: u32,
}

fn bits_of(value: f32) -> u32 {
    let bits = Bits { float: value };
    // SAFETY: każdy bit pattern u32 jest poprawny; odczytujemy wspólne bajty.
    unsafe { bits.integer }
}

assert_eq!(bits_of(1.0), 0x3F80_0000);
```

**Zastosowanie:** odwzorowanie C unionów i specjalistyczne reprezentacje pamięci. Do zwykłej konwersji używaj `to_bits`.

### 99. Inline assembly przez `asm!`

`asm!` daje dostęp do instrukcji procesora i jawnie opisuje rejestry, operandy oraz efekty uboczne. Jest zależne od architektury.

```rust
#[cfg(target_arch = "x86_64")]
fn read_timestamp_counter() -> u64 {
    let low: u32;
    let high: u32;

    // SAFETY: RDTSC zapisuje tylko EDX:EAX; deklarujemy wszystkie wyniki.
    unsafe {
        std::arch::asm!(
            "rdtsc",
            out("eax") low,
            out("edx") high,
            options(nomem, nostack),
        );
    }

    ((high as u64) << 32) | low as u64
}
```

**Zastosowanie:** instrukcje niedostępne przez intrinsics, sterowniki i bardzo niskopoziomowe optymalizacje.

### 100. Portable SIMD — funkcja `nightly`

API `std::simd` zapewnia przenośne wektory SIMD, ale w Rust 1.98.1 nadal wymaga `nightly` i feature gate `portable_simd`.

```rust
#![feature(portable_simd)]

use std::simd::f32x8;

fn add_vectors(left: [f32; 8], right: [f32; 8]) -> [f32; 8] {
    (f32x8::from_array(left) + f32x8::from_array(right)).to_array()
}

fn main() {
    let result = add_vectors([1.0; 8], [2.0; 8]);
    assert_eq!(result, [3.0; 8]);
}
```

**Zastosowanie:** DSP, przetwarzanie obrazu, korelacja próbek i algorytmy numeryczne. W produkcji stabilnej rozważ arch-specific intrinsics albo sprawdzoną bibliotekę SIMD.

## Projektowanie publicznego API i zaawansowane typy — 101–110

### 101. Precyzyjne przechwytywanie parametrów przez `use<...>`

Zwracany `impl Trait` może przechwytywać parametry generyczne i lifetime'y funkcji. Bound `use<...>` pozwala jawnie ograniczyć ten zbiór, dzięki czemu niezwiązany lifetime nie staje się przypadkową częścią ukrytego typu.

```rust
fn bytes<'input, 'context>(
    input: &'input str,
    _context: &'context (),
) -> impl Iterator<Item = u8> + use<'input> {
    input.bytes()
}

fn main() {
    let context = ();
    let values = bytes("SDR", &context).collect::<Vec<_>>();
    assert_eq!(values, [83, 68, 82]);
}
```

**Zastosowanie:** stabilne sygnatury bibliotek, redukcja nadmiarowych zależności lifetime'ów i precyzyjne API zwracające iteratory albo future.

### 102. Copy-on-write przez `Cow<'a, B>`

`Cow` reprezentuje dane pożyczone albo posiadane. Funkcja może zwrócić referencję bez alokacji, gdy nie trzeba nic zmieniać, i utworzyć wartość owned dopiero w ścieżce modyfikującej.

```rust
use std::borrow::Cow;

fn lowercase_ascii(input: &str) -> Cow<'_, str> {
    if input.bytes().all(|byte| !byte.is_ascii_uppercase()) {
        Cow::Borrowed(input)
    } else {
        Cow::Owned(input.to_ascii_lowercase())
    }
}

fn main() {
    assert!(matches!(lowercase_ascii("rust"), Cow::Borrowed(_)));
    assert!(matches!(lowercase_ascii("Rust"), Cow::Owned(_)));
}
```

**Zastosowanie:** parsery, normalizacja danych, serializacja i publiczne API, w których kopiowanie ma następować tylko wtedy, gdy jest konieczne.

### 103. Interior mutability bez borrow runtime przez `Cell<T>`

`Cell<T>` pozwala zmieniać wartość przez współdzieloną referencję `&self`. Nie udostępnia referencji do wnętrza; wartości są pobierane lub zastępowane, dlatego dobrze nadaje się do małych typów `Copy`.

```rust
use std::cell::Cell;

struct Metrics {
    requests: Cell<u64>,
}

impl Metrics {
    fn record(&self) {
        self.requests.set(self.requests.get() + 1);
    }
}

fn main() {
    let metrics = Metrics { requests: Cell::new(0) };
    metrics.record();
    assert_eq!(metrics.requests.get(), 1);
}
```

**Zastosowanie:** liczniki, cache prostych wartości oraz stan pomocniczy w kodzie jednowątkowym. `Cell<T>` nie implementuje `Sync`.

### 104. Dynamiczna kontrola borrow przez `RefCell<T>`

`RefCell<T>` przenosi regułę „wiele odczytów albo jeden zapis” z kompilacji do runtime. Naruszenie reguły powoduje panic; warianty `try_borrow` i `try_borrow_mut` zwracają błąd.

```rust
use std::cell::RefCell;

struct Registry {
    names: RefCell<Vec<String>>,
}

impl Registry {
    fn register(&self, name: impl Into<String>) {
        self.names.borrow_mut().push(name.into());
    }
}

fn main() {
    let registry = Registry { names: RefCell::new(Vec::new()) };
    registry.register("correlator");
    assert_eq!(registry.names.borrow().len(), 1);
}
```

**Zastosowanie:** mutowalne wnętrze za `Rc<T>`, drzewa, grafy i implementacje traitów wymagających `&self`. W kodzie wielowątkowym używa się zwykle `Mutex` albo `RwLock`.

### 105. Typy niemobilne przez `PhantomPinned`

`PhantomPinned` wyłącza automatyczną implementację `Unpin`. Po przypięciu wartość nie może zostać bezpiecznie przeniesiona, co umożliwia utrzymywanie wskaźników do jej własnych pól.

```rust
use std::{marker::PhantomPinned, pin::Pin, ptr};

struct SelfRef {
    text: String,
    text_ptr: *const String,
    _pin: PhantomPinned,
}

impl SelfRef {
    fn new(text: String) -> Pin<Box<Self>> {
        let mut value = Box::pin(SelfRef {
            text,
            text_ptr: ptr::null(),
            _pin: PhantomPinned,
        });

        let text_ptr = &value.text as *const String;
        // SAFETY: wartość jest już na stercie i pozostanie przypięta.
        unsafe { Pin::as_mut(&mut value).get_unchecked_mut().text_ptr = text_ptr };
        value
    }

    fn text_via_pointer(self: Pin<&Self>) -> &str {
        // SAFETY: wskaźnik ustawiono po przypięciu i wskazuje na `self.text`.
        unsafe { &*self.text_ptr }.as_str()
    }
}
```

**Zastosowanie:** implementacje `Future`, intrusive collections i struktury samoreferencyjne. Kod `unsafe` powinien być zamknięty w małym, audytowalnym API.

### 106. Ewolucja publicznych typów przez `#[non_exhaustive]`

Atrybut informuje użytkowników crate'a, że w przyszłości mogą pojawić się nowe warianty enumu albo pola struktury. Kod poza crate'em musi pozostawić gałąź zapasową.

```rust
#[non_exhaustive]
pub enum ApiError {
    NotFound,
    Timeout,
}

fn message(error: &ApiError) -> &'static str {
    match error {
        ApiError::NotFound => "not found",
        ApiError::Timeout => "timeout",
        _ => "unknown error",
    }
}
```

**Zastosowanie:** biblioteki o stabilnym API, których enumy i struktury będą rozszerzane bez natychmiastowego łamania kodu zależnego.

### 107. Wymuszanie obsługi wyniku przez `#[must_use]`

`#[must_use]` generuje ostrzeżenie, gdy wywołujący ignoruje istotną wartość. Można oznaczyć funkcję albo cały typ i podać komunikat wyjaśniający.

```rust
#[must_use = "zapytanie nie wykona się, dopóki go nie przekażesz do executora"]
struct Query(String);

#[must_use]
fn build_query(text: &str) -> Query {
    Query(text.to_owned())
}

fn main() {
    let query = build_query("status");
    assert_eq!(query.0, "status");
}
```

**Zastosowanie:** buildery, obiekty żądań, guardy transakcji i funkcje zwracające rezultat, którego ciche porzucenie prawdopodobnie oznacza błąd.

### 108. Diagnostyka miejsca wywołania przez `#[track_caller]`

Funkcja oznaczona `#[track_caller]` może odczytać lokalizację swojego wywołującego zamiast lokalizacji wewnątrz funkcji pomocniczej.

```rust
use std::panic::Location;

#[track_caller]
fn require(condition: bool, message: &str) {
    if !condition {
        let caller = Location::caller();
        panic!("{message} at {}:{}", caller.file(), caller.line());
    }
}

fn main() {
    require(2 + 2 == 4, "broken invariant");
}
```

**Zastosowanie:** własne asercje, walidatory domenowe oraz biblioteki, które powinny raportować błąd w kodzie użytkownika, nie wewnątrz helpera.

### 109. Domyślne parametry typów generycznych

Parametr generyczny może mieć typ domyślny. Podstawowe użycie pozostaje krótkie, a użytkownik zaawansowany może podmienić strategię bez tworzenia osobnego typu API.

```rust
trait Codec {
    fn encode(&self, input: &str) -> Vec<u8>;
}

struct Utf8;

impl Codec for Utf8 {
    fn encode(&self, input: &str) -> Vec<u8> {
        input.as_bytes().to_vec()
    }
}

struct Client<C = Utf8> {
    codec: C,
}

let client = Client { codec: Utf8 };
assert_eq!(client.codec.encode("IQ"), b"IQ");
```

**Zastosowanie:** konfigurowalne polityki serializacji, alokacji, logowania lub transportu przy zachowaniu wygodnego przypadku domyślnego.

### 110. Złożone trait objects: `dyn Trait + Send + Sync + 'static`

Trait object może zawierać auto-traity oraz bound lifetime'u. Taki kontrakt precyzuje nie tylko zachowanie obiektu, lecz także to, czy można go współdzielić między wątkami i jak długo żyją jego przechwycone dane.

```rust
use std::sync::Arc;

#[derive(Clone)]
struct Event(String);

type Handler = dyn Fn(Event) + Send + Sync + 'static;

struct EventBus {
    handlers: Vec<Arc<Handler>>,
}

impl EventBus {
    fn emit(&self, event: Event) {
        for handler in &self.handlers {
            handler(event.clone());
        }
    }
}
```

**Zastosowanie:** event busy, callbacki, strategie runtime i porty hexagonalne przechowywane jako heterogeniczne obiekty.

## Struktury danych, bufory i zero-copy I/O — 111–120

### 111. Jednoprzebiegowa aktualizacja mapy przez Entry API

`HashMap::entry` wykonuje wyszukanie klucza tylko raz i zwraca stan `Occupied` albo `Vacant`. Combinatory `or_insert`, `or_insert_with` i `and_modify` upraszczają atomową logicznie aktualizację wartości.

```rust
use std::collections::HashMap;

fn count<'a>(words: impl IntoIterator<Item = &'a str>) -> HashMap<&'a str, usize> {
    let mut counts = HashMap::new();

    for word in words {
        counts
            .entry(word)
            .and_modify(|value| *value += 1)
            .or_insert(1);
    }

    counts
}

assert_eq!(count(["fft", "fft", "iq"])["fft"], 2);
```

**Zastosowanie:** agregacje, cache, grupowanie zdarzeń i aktualizacja stanu bez osobnego `contains_key` oraz drugiego lookupu.

### 112. Algebraiczne operacje zmiennoprzecinkowe — Rust 1.98

Metody `algebraic_add`, `algebraic_sub`, `algebraic_mul`, `algebraic_div` i `algebraic_rem` pozwalają kompilatorowi stosować przekształcenia wynikające z praw algebry liczb rzeczywistych. Dla IEEE 754 oznacza to możliwość zmiany kolejności działań i niedeterministyczne różnice zaokrągleń, ale nigdy undefined behavior.

```rust
fn energy_algebraic(samples: &[f32]) -> f32 {
    samples.iter().copied().fold(0.0_f32, |sum, sample| {
        sum.algebraic_add(sample.algebraic_mul(sample))
    })
}

fn main() {
    let value = energy_algebraic(&[1.0, -2.0, 3.0]);
    assert_eq!(value, 14.0);
}
```

**Zastosowanie:** DSP, macierze i redukcje numeryczne, gdy możliwość wektoryzacji jest ważniejsza niż identyczny bitowo wynik na każdym buildzie i procesorze. Nie używaj tych metod w obliczeniach wymagających ścisłej reprodukowalności.

### 113. Pierścieniowy bufor przez `VecDeque::make_contiguous`

`VecDeque` może być fizycznie rozdzielony na dwa fragmenty. `make_contiguous` reorganizuje dane i zwraca pojedynczy `&mut [T]`, który można przekazać algorytmowi pracującemu na slice.

```rust
use std::collections::VecDeque;

let mut queue = VecDeque::from([4, 1, 3, 2]);
queue.pop_front();
queue.push_back(5);

queue.make_contiguous().sort_unstable();

assert_eq!(queue, VecDeque::from([1, 2, 3, 5]));
```

**Zastosowanie:** ring buffery, okna próbek, kolejki audio i protokoły strumieniowe wymagające okresowego dostępu do ciągłej pamięci.

### 114. Inicjalizacja zapasu `Vec<T>` przez `spare_capacity_mut`

`Vec::spare_capacity_mut` udostępnia wolną pojemność jako `&mut [MaybeUninit<T>]`. Po zainicjalizowaniu elementów kod może zwiększyć długość wektora, ale musi dokładnie udowodnić liczbę zapisanych wartości.

```rust
fn append_sequence(output: &mut Vec<u32>, count: usize) {
    let old_len = output.len();
    output.reserve(count);

    for (index, slot) in output.spare_capacity_mut()[..count]
        .iter_mut()
        .enumerate()
    {
        slot.write(index as u32);
    }

    // SAFETY: dokładnie `count` kolejnych slotów zostało zainicjalizowanych.
    unsafe { output.set_len(old_len + count) };
}

let mut values = vec![10];
append_sequence(&mut values, 3);
assert_eq!(values, [10, 0, 1, 2]);
```

**Zastosowanie:** wydajne dekodery, FFI i wypełnianie bufora bez wcześniejszego zerowania lub tworzenia tymczasowej kolekcji.

### 115. Dowodzenie rozłączności przez `split_at_mut`

Borrow checker nie wnioskuje ogólnie, że dwa indeksy tablicy są różne. `split_at_mut` konstruuje dwa rozłączne slice'y, dzięki czemu można jednocześnie mutować obie części bez `unsafe`.

```rust
fn swap_regions(values: &mut [i32], middle: usize) {
    let (left, right) = values.split_at_mut(middle);

    for (a, b) in left.iter_mut().zip(right.iter_mut()) {
        std::mem::swap(a, b);
    }
}

let mut values = [1, 2, 3, 4];
swap_regions(&mut values, 2);
assert_eq!(values, [3, 4, 1, 2]);
```

**Zastosowanie:** algorytmy in-place, sortowanie, przetwarzanie kanałów i równoległe dzielenie buforów na niezależne regiony.

### 116. Ramki o stałym rozmiarze przez `chunks_exact`

`chunks_exact` iteruje wyłącznie po pełnych blokach i zachowuje końcową resztę. Pozwala jawnie odróżnić poprawne ramki od niekompletnego fragmentu wejścia.

```rust
fn decode_u32(input: &[u8]) -> Result<Vec<u32>, usize> {
    let mut chunks = input.chunks_exact(4);
    let values = chunks
        .by_ref()
        .map(|chunk| u32::from_le_bytes(chunk.try_into().unwrap()))
        .collect::<Vec<_>>();

    match chunks.remainder().len() {
        0 => Ok(values),
        trailing => Err(trailing),
    }
}

assert_eq!(decode_u32(&[1, 0, 0, 0, 2, 0, 0, 0]), Ok(vec![1, 2]));
```

**Zastosowanie:** dekodowanie pakietów, próbek IQ, formatów binarnych i bloków SIMD bez cichego pomijania niepełnej ramki.

### 117. Inicjalizacja tablic zależna od indeksu przez `array::from_fn`

`std::array::from_fn` buduje `[T; N]` bez wymagania, aby `T` implementował `Copy` albo `Default`. Każdy element może zależeć od swojego indeksu.

```rust
use std::array;

let channels: [String; 4] =
    array::from_fn(|index| format!("rx-{index}"));

assert_eq!(channels[2], "rx-2");

let matrix: [[usize; 3]; 3] =
    array::from_fn(|row| array::from_fn(|column| row * 3 + column));

assert_eq!(matrix[2][1], 7);
```

**Zastosowanie:** bufory o rozmiarze compile-time, macierze, tablice kanałów i inicjalizacja typów nieimplementujących `Copy`.

### 118. Odczyt bez dodatkowego bufora przez `BufRead::fill_buf`

`fill_buf` zwraca referencję do wewnętrznego bufora czytnika, a `consume` oznacza wykorzystane bajty. Kod może analizować dane bez kopiowania ich do nowego `Vec<u8>`.

```rust
use std::io::{self, BufRead};

fn count_newlines(mut reader: impl BufRead) -> io::Result<usize> {
    let mut total = 0;

    loop {
        let consumed = {
            let buffer = reader.fill_buf()?;
            if buffer.is_empty() {
                break;
            }
            total += buffer.iter().filter(|&&byte| byte == b'\n').count();
            buffer.len()
        };

        reader.consume(consumed);
    }

    Ok(total)
}
```

**Zastosowanie:** parsery strumieniowe, protokoły tekstowe i analiza dużych plików bez alokacji dla każdego fragmentu.

### 119. Scatter/gather I/O przez `read_vectored` i `write_vectored`

Operacje vectored I/O przekazują systemowi kilka buforów w jednym wywołaniu. Pozwala to np. odczytać nagłówek i payload bez wcześniejszego łączenia pamięci.

```rust
use std::io::{self, IoSliceMut, Read};

fn read_packet(mut input: impl Read) -> io::Result<(usize, [u8; 4], [u8; 12])> {
    let mut header = [0; 4];
    let mut payload = [0; 12];

    let bytes = {
        let mut buffers = [
            IoSliceMut::new(&mut header),
            IoSliceMut::new(&mut payload),
        ];
        input.read_vectored(&mut buffers)?
    };

    Ok((bytes, header, payload))
}
```

**Zastosowanie:** protokoły sieciowe, framing, logowanie i obsługa wielu segmentów danych przy mniejszej liczbie wywołań systemowych.

### 120. Formatowanie liczb bez alokacji przez `NumBuffer` — Rust 1.98

Każdy typ całkowity udostępnia `format_into`, który zapisuje reprezentację dziesiętną do bufora `NumBuffer` i zwraca pożyczony `&str`. Ten sam bufor można wielokrotnie wykorzystywać bez budowania osobnego `String` dla każdej liczby.

```rust
use std::fmt::NumBuffer;

fn append_ids(output: &mut String, ids: &[u64]) {
    let mut buffer = NumBuffer::new();

    for &id in ids {
        output.push_str(id.format_into(&mut buffer));
        output.push('\n');
    }
}

fn main() {
    let mut output = String::new();
    append_ids(&mut output, &[10, 20]);
    assert_eq!(output, "10\n20\n");
}
```

**Zastosowanie:** telemetria, logi, serializacja tekstowa i gorące ścieżki, w których dynamiczne formatowanie pojedynczych liczb stanowi mierzalny koszt.

## Produkcyjne async i współbieżność — 121–130

> Punkty 121–129 wykorzystują Tokio. Są to wzorce runtime'u, nie elementy biblioteki standardowej Rusta.

### 121. Cancellation safety w `tokio::select!`

`select!` kończy zwycięską gałąź i porzuca future z pozostałych gałęzi. Operacja jest cancellation-safe, jeżeli jej porzucenie nie gubi częściowo przetworzonego stanu ani nie narusza kolejności danych.

```rust
use tokio::sync::{mpsc, watch};

struct Job;

async fn handle(_job: Job) {}

async fn worker(
    mut jobs: mpsc::Receiver<Job>,
    mut stop: watch::Receiver<bool>,
) {
    loop {
        tokio::select! {
            changed = stop.changed() => {
                if changed.is_err() || *stop.borrow() {
                    break;
                }
            }
            job = jobs.recv() => match job {
                Some(job) => handle(job).await,
                None => break,
            },
        }
    }
}
```

**Zastosowanie:** graceful shutdown, timeouty i konkurencyjne źródła zdarzeń. Przed umieszczeniem operacji w `select!` trzeba sprawdzić jej dokumentowaną odporność na anulowanie.

### 122. Zarządzanie dynamicznym zbiorem zadań przez `JoinSet`

`JoinSet` przechowuje zadania i pozwala odbierać wyniki w kolejności ich zakończenia. Upuszczenie zbioru abortuje nadal działające zadania, dzięki czemu lifecycle jest jawnie powiązany z właścicielem.

```rust
use tokio::task::JoinSet;

async fn compute(id: u32) -> u32 {
    id * id
}

async fn run_all() -> Result<Vec<u32>, tokio::task::JoinError> {
    let mut set = JoinSet::new();

    for id in 1..=4 {
        set.spawn(compute(id));
    }

    let mut results = Vec::new();
    while let Some(result) = set.join_next().await {
        results.push(result?);
    }
    Ok(results)
}
```

**Zastosowanie:** worker pools, fan-out/fan-in i nadzorowanie dynamicznej liczby zadań bez przechowywania osobnego `JoinHandle` dla każdego z nich.

### 123. Future `!Send` na `LocalSet`

Nie każda future może przechodzić między wątkami. `LocalSet` uruchamia zadania `!Send` na jednym wątku, pozwalając używać np. `Rc<RefCell<T>>` w kodzie asynchronicznym.

```rust
use std::{cell::RefCell, rc::Rc};
use tokio::task::LocalSet;

#[tokio::main(flavor = "current_thread")]
async fn main() {
    let local = LocalSet::new();

    local.spawn_local(async {
        let state = Rc::new(RefCell::new(0_u32));
        *state.borrow_mut() += 1;
        assert_eq!(*state.borrow(), 1);
    });

    local.await;
}
```

**Zastosowanie:** GUI, WebAssembly, integracja z API przypisanym do wątku i lokalne aktory, których stan nie wymaga synchronizacji między wątkami.

### 124. Izolowanie pracy blokującej przez `spawn_blocking`

Kod blokujący nie powinien zajmować wątku executora async. `spawn_blocking` przenosi taką pracę do dedykowanej puli; jej anulowanie po rozpoczęciu nie zatrzymuje automatycznie funkcji blokującej.

```rust
use tokio::task;

fn correlate(samples: Vec<f32>) -> f32 {
    samples.iter().map(|value| value * value).sum()
}

async fn correlation(samples: Vec<f32>) -> Result<f32, task::JoinError> {
    task::spawn_blocking(move || correlate(samples)).await
}
```

**Zastosowanie:** kompresja, parsowanie dużych plików, wywołania synchronicznego FFI i krótkie obliczenia CPU. Długie obliczenia CPU wymagają dodatkowo kontrolowanej puli lub biblioteki typu Rayon.

### 125. Ograniczanie współbieżności przez `Semaphore`

Semafor przydziela określoną liczbę permitów. Owned permit można przenieść do zadania, a jego `Drop` automatycznie zwalnia limit nawet przy wcześniejszym wyjściu.

```rust
use std::sync::Arc;
use tokio::{sync::Semaphore, task::JoinHandle};

fn spawn_request(limit: Arc<Semaphore>, id: u32) -> JoinHandle<u32> {
    tokio::spawn(async move {
        let _permit = limit.acquire_owned().await.expect("semaphore closed");
        id * 2
    })
}

#[tokio::main]
async fn main() {
    let limit = Arc::new(Semaphore::new(4));
    let result = spawn_request(limit, 21).await.unwrap();
    assert_eq!(result, 42);
}
```

**Zastosowanie:** limitowanie zapytań HTTP, połączeń z bazą, zadań CPU i liczby jednocześnie przetwarzanych bloków danych.

### 126. Asynchroniczny backpressure przez bounded `mpsc`

Kanał `tokio::sync::mpsc::channel(n)` ma ograniczoną pojemność. Gdy bufor jest pełny, `send().await` czeka, przez co szybki producent nie może bez ograniczeń zwiększać zużycia pamięci.

```rust
use tokio::sync::mpsc;

#[derive(Debug)]
struct Block(Vec<i16>);

async fn produce(sender: mpsc::Sender<Block>) {
    for _ in 0..10 {
        if sender.send(Block(vec![0; 4096])).await.is_err() {
            break;
        }
    }
}

async fn consume(mut receiver: mpsc::Receiver<Block>) {
    while let Some(block) = receiver.recv().await {
        let _sample_count = block.0.len();
    }
}
```

**Zastosowanie:** pipeline'y streamingu, SDR, logowanie i kolejki robocze, w których limit pamięci jest częścią kontraktu systemu.

### 127. Dystrybucja najnowszego stanu przez kanał `watch`

Kanał `watch` przechowuje wyłącznie ostatnią wartość. Wolny odbiorca nie musi przetwarzać całej historii zmian; po przebudzeniu odczytuje aktualną konfigurację.

```rust
use tokio::sync::watch;

#[derive(Clone, Debug)]
struct Config {
    gain_db: f32,
}

async fn observe(mut receiver: watch::Receiver<Config>) {
    while receiver.changed().await.is_ok() {
        let config = receiver.borrow_and_update().clone();
        println!("gain: {} dB", config.gain_db);
    }
}

let (sender, receiver) = watch::channel(Config { gain_db: 10.0 });
sender.send(Config { gain_db: 12.5 }).unwrap();
drop((sender, receiver));
```

**Zastosowanie:** dynamiczna konfiguracja, health state, sygnały shutdown i stan, dla którego ważna jest najnowsza wersja, a nie każda zmiana.

### 128. Fan-out zdarzeń przez kanał `broadcast`

Każdy aktywny odbiorca kanału `broadcast` widzi własną kopię wiadomości. Jeżeli odbiorca pozostaje zbyt daleko w tyle, otrzymuje `Lagged(n)` i musi jawnie zdecydować, jak obsłużyć utracone zdarzenia.

```rust
use tokio::sync::broadcast;

async fn receive(mut receiver: broadcast::Receiver<String>) {
    loop {
        match receiver.recv().await {
            Ok(event) => println!("{event}"),
            Err(broadcast::error::RecvError::Lagged(skipped)) => {
                eprintln!("skipped {skipped} events");
            }
            Err(broadcast::error::RecvError::Closed) => break,
        }
    }
}

let (sender, _) = broadcast::channel(64);
let receiver_a = sender.subscribe();
let receiver_b = sender.subscribe();
drop((receiver_a, receiver_b));
```

**Zastosowanie:** powiadomienia, telemetria i eventy do wielu konsumentów. Nie jest to trwały event log — wolny konsument może utracić wiadomości.

### 129. Aktor jako właściciel stanu i command bus

Aktor przechowuje stan w jednym zadaniu i przyjmuje typowane komendy przez kanał. Zapytania mogą posiadać `oneshot::Sender`, który tworzy kanał odpowiedzi bez współdzielonego mutexu.

```rust
use tokio::sync::{mpsc, oneshot};

enum Command {
    Increment(u64),
    Value { reply: oneshot::Sender<u64> },
}

fn spawn_counter() -> mpsc::Sender<Command> {
    let (sender, mut receiver) = mpsc::channel(32);

    tokio::spawn(async move {
        let mut value = 0_u64;
        while let Some(command) = receiver.recv().await {
            match command {
                Command::Increment(by) => value += by,
                Command::Value { reply } => {
                    let _ = reply.send(value);
                }
            }
        }
    });

    sender
}
```

**Zastosowanie:** supervisor urządzenia, sesje akwizycji i izolowanie mutowalnego stanu za protokołem komend.

### 130. Pętla CAS przez `compare_exchange_weak`

Operacja compare-and-swap zapisuje nową wartość wyłącznie wtedy, gdy atomik nadal zawiera oczekiwaną starą wartość. Wariant `weak` może pozornie zawieść, dlatego używa się go w pętli aktualizującej oczekiwanie.

```rust
use std::sync::atomic::{AtomicU64, Ordering};

fn saturating_increment(counter: &AtomicU64) {
    let mut current = counter.load(Ordering::Relaxed);

    loop {
        let next = current.saturating_add(1);
        match counter.compare_exchange_weak(
            current,
            next,
            Ordering::Relaxed,
            Ordering::Relaxed,
        ) {
            Ok(_) => break,
            Err(actual) => current = actual,
        }
    }
}
```

**Zastosowanie:** lock-free liczniki, ograniczniki, flagi bitowe i aktualizacje zależne od bieżącej wartości. Dobór `Ordering` musi wynikać z synchronizowanych danych, nie z samego atomika.

## Cargo, konfiguracja, testowanie i diagnostyka — 131–140

### 131. Workspace Cargo i resolver funkcji

Workspace zarządza wieloma crate'ami przy wspólnym `Cargo.lock` oraz katalogu `target`. Resolver wersji 3 odpowiada Edition 2024 i ogranicza niepożądane łączenie feature'ów między różnymi rodzajami zależności i targetami.

```toml
[workspace]
members = [
    "crates/domain",
    "crates/application",
    "crates/adapters/http",
    "crates/runtime",
]
resolver = "3"

[workspace.package]
edition = "2024"
rust-version = "1.98"

[workspace.dependencies]
serde = { version = "1", features = ["derive"] }
```

**Zastosowanie:** systemy wielocrate'owe, architektura hexagonalna i współdzielenie wersji zależności bez łączenia wszystkich modułów w jeden crate.

### 132. Addytywne feature flags

Feature Cargo powinien dodawać możliwości, a nie wybierać wzajemnie wykluczające się tryby. Zależność może być opcjonalna i aktywowana przez zapis `dep:nazwa`.

```toml
[features]
default = []
json = ["dep:serde", "dep:serde_json"]
telemetry = ["dep:tracing"]
full = ["json", "telemetry"]

[dependencies]
serde = { version = "1", optional = true, features = ["derive"] }
serde_json = { version = "1", optional = true }
tracing = { version = "0.1", optional = true }
```

**Zastosowanie:** lekkie biblioteki, opcjonalne adaptery i ograniczanie drzewa zależności. Kod powinien działać również wtedy, gdy Cargo zjednoczy feature'y kilku użytkowników crate'a.

### 133. Kompilacja warunkowa przez `cfg` i `cfg_attr`

`#[cfg(...)]` usuwa element z danej konfiguracji kompilacji, a `#[cfg_attr(...)]` warunkowo dodaje inny atrybut. Warunki mogą dotyczyć targetu, feature'u, testów lub własnych symboli.

```rust
#[cfg_attr(not(debug_assertions), inline(always))]
fn decode_word(bytes: [u8; 4]) -> u32 {
    #[cfg(target_endian = "little")]
    {
        u32::from_le_bytes(bytes)
    }

    #[cfg(target_endian = "big")]
    {
        u32::from_be_bytes(bytes)
    }
}

#[cfg(feature = "telemetry")]
fn record_metric(name: &str) {
    tracing::info!(metric = name);
}
```

**Zastosowanie:** przenośność, opcjonalne integracje, różne backendy sprzętowe i ograniczanie kodu zależnego od platformy.

### 134. Kontrolowany build script przez `build.rs`

Build script działa przed kompilacją crate'a i komunikuje się z Cargo liniami `cargo::...`. Dyrektywy `rerun-if-changed` i `rerun-if-env-changed` zapobiegają niepotrzebnemu uruchamianiu skryptu przy każdym buildzie.

```rust
// build.rs
fn main() {
    println!("cargo::rerun-if-changed=native/wrapper.h");
    println!("cargo::rerun-if-env-changed=SDR_SDK_PATH");

    if let Ok(path) = std::env::var("SDR_SDK_PATH") {
        println!("cargo::rustc-link-search=native={path}/lib");
        println!("cargo::rustc-link-lib=dylib=sdr");
    }
}
```

**Zastosowanie:** generowanie kodu, kompilowanie C/C++, wykrywanie bibliotek systemowych i przekazywanie metadanych builda. Skrypt nie powinien śledzić niejawnych plików ani zmiennych.

### 135. Jawne linkowanie natywnej biblioteki przez `#[link]`

Atrybut `#[link]` przypisuje blok `extern` do biblioteki statycznej, dynamicznej albo frameworka. Sygnatury FFI nadal muszą dokładnie odpowiadać ABI i typom strony natywnej.

```rust
use std::ffi::{c_int, c_void};

#[link(name = "sdr")]
unsafe extern "C" {
    fn sdr_start(handle: *mut c_void) -> c_int;
}

fn start(handle: *mut c_void) -> Result<(), c_int> {
    // SAFETY: `handle` musi wskazywać na aktywne urządzenie biblioteki SDR.
    let status = unsafe { sdr_start(handle) };
    match status {
        0 => Ok(()),
        code => Err(code),
    }
}
```

**Zastosowanie:** integracja z UHD, libiio, bibliotekami C i systemowymi SDK. Bezpieczny wrapper powinien ukryć surowy uchwyt i opisać ownership.

### 136. Profile wydania, LTO i jednostki codegen

Profile Cargo sterują strategią optymalizacji całego grafu crate'ów. LTO pozwala optymalizować między jednostkami kodu, a mniejsza liczba `codegen-units` zwykle poprawia wynik kosztem czasu kompilacji.

```toml
[profile.release]
opt-level = 3
lto = "thin"
codegen-units = 1
panic = "abort"
strip = "symbols"

[profile.profiling]
inherits = "release"
debug = 1
strip = "none"
```

**Zastosowanie:** binaria produkcyjne, embedded i obciążenia obliczeniowe. Osobny profil z symbolami jest potrzebny do sensownego profilowania zoptymalizowanego kodu.

### 137. Testy dokumentacyjne jako wykonywalny kontrakt API

Bloki Rust w komentarzach dokumentacyjnych są kompilowane i uruchamiane przez `cargo test --doc`. Ukryte linie zaczynające się od `#` pozwalają dodać setup bez zaśmiecania renderowanej dokumentacji.

```rust
/// Oblicza energię bloku próbek.
///
/// # Examples
///
/// ```
/// # use signal::energy;
/// let value = energy(&[1.0, -2.0, 3.0]);
/// assert_eq!(value, 14.0);
/// ```
pub fn energy(samples: &[f32]) -> f32 {
    samples.iter().map(|sample| sample * sample).sum()
}
```

**Zastosowanie:** biblioteki publiczne, przykłady użycia odporne na starzenie oraz weryfikacja, że dokumentowana sygnatura naprawdę działa.

### 138. Property-based testing przez `proptest`

Zamiast ręcznie wybierać kilka przypadków, test właściwości generuje wiele wejść i minimalizuje przypadek powodujący błąd. Sprawdza inwariant, nie jedną zapamiętaną odpowiedź.

```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn encoding_round_trip(values in prop::collection::vec(any::<i16>(), 0..1024)) {
        let bytes = values
            .iter()
            .flat_map(|value| value.to_le_bytes())
            .collect::<Vec<_>>();

        let decoded = bytes
            .chunks_exact(2)
            .map(|chunk| i16::from_le_bytes([chunk[0], chunk[1]]))
            .collect::<Vec<_>>();

        prop_assert_eq!(decoded, values);
    }
}
```

**Zastosowanie:** parsery, kodeki, Value Objecty, algorytmy numeryczne i każda logika posiadająca własność zachodzącą dla całej klasy danych.

### 139. Wykrywanie undefined behavior przez Miri

Miri interpretuje MIR i wykrywa wiele naruszeń zasad pamięci, m.in. use-after-free, błędne wyrównanie, część naruszeń aliasingu i wycieki w testach. Nie jest dowodem pełnej poprawności ani analizatorem wyścigów między wątkami.

```bash
rustup component add miri --toolchain nightly
cargo +nightly miri setup
cargo +nightly miri test

# Dodatkowe kontrole i wiele wariantów losowego wykonania:
MIRIFLAGS="-Zmiri-strict-provenance -Zmiri-symbolic-alignment-check" \
  cargo +nightly miri test
```

**Zastosowanie:** audyt własnych kontenerów, surowych wskaźników, FFI i abstrakcji zawierających `unsafe`. Testy powinny celować w granice oraz nietypowe ścieżki `Drop`.

### 140. Modelowanie przeplotów współbieżnych przez Loom

Loom zastępuje typowe prymitywy synchronizacji własnymi odpowiednikami i systematycznie eksploruje możliwe kolejności operacji. Mały model potrafi ujawnić błąd, który w zwykłym teście występuje raz na milion uruchomień.

```rust
use loom::{
    sync::{
        atomic::{AtomicBool, AtomicUsize, Ordering},
        Arc,
    },
    thread,
};

loom::model(|| {
    let data = Arc::new(AtomicUsize::new(0));
    let ready = Arc::new(AtomicBool::new(false));

    let writer_data = Arc::clone(&data);
    let writer_ready = Arc::clone(&ready);
    let writer = thread::spawn(move || {
        writer_data.store(42, Ordering::Relaxed);
        writer_ready.store(true, Ordering::Release);
    });

    if ready.load(Ordering::Acquire) {
        assert_eq!(data.load(Ordering::Relaxed), 42);
    }

    writer.join().unwrap();
});
```

**Zastosowanie:** biblioteki współbieżne, niestandardowe prymitywy, atomiki i sprawdzanie, czy para `Release`/`Acquire` rzeczywiście publikuje oczekiwane dane.

## `no_std`, FFI, layout pamięci i wydajność — 141–150

### 141. Biblioteki bez `std` przez `#![no_std]` i crate `alloc`

`#![no_std]` usuwa zależność od biblioteki standardowej, ale pozostawia `core`. Jeżeli środowisko dostarcza allocator, crate `alloc` udostępnia m.in. `Box`, `String`, `Vec` i `Arc` bez systemowych API `std`.

```rust
#![no_std]

extern crate alloc;

use alloc::vec::Vec;

pub fn positive(values: &[i16]) -> Vec<i16> {
    values
        .iter()
        .copied()
        .filter(|value| *value > 0)
        .collect()
}
```

**Zastosowanie:** embedded, kernela, WebAssembly i biblioteki przenośne. Brak `std` nie oznacza automatycznie braku alokacji — do tego trzeba zrezygnować także z `alloc`.

### 142. Własny globalny allocator przez `GlobalAlloc`

Implementacja `GlobalAlloc` przechwytuje globalne alokacje. Każda metoda jest `unsafe`, ponieważ musi zachować wymagania layoutu, poprawnie delegować zwalnianie i nie wykonywać operacji prowadzących rekurencyjnie do kolejnej alokacji.

```rust
use std::{
    alloc::{GlobalAlloc, Layout, System},
    sync::atomic::{AtomicUsize, Ordering},
};

struct CountingAllocator;
static ALLOCATED: AtomicUsize = AtomicUsize::new(0);

unsafe impl GlobalAlloc for CountingAllocator {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        // SAFETY: przekazujemy niezmieniony, poprawny `Layout` do System.
        let pointer = unsafe { System.alloc(layout) };
        if !pointer.is_null() {
            ALLOCATED.fetch_add(layout.size(), Ordering::Relaxed);
        }
        pointer
    }

    unsafe fn dealloc(&self, pointer: *mut u8, layout: Layout) {
        ALLOCATED.fetch_sub(layout.size(), Ordering::Relaxed);
        // SAFETY: para pointer/layout pochodzi z odpowiadającej alokacji.
        unsafe { System.dealloc(pointer, layout) };
    }
}

#[global_allocator]
static GLOBAL: CountingAllocator = CountingAllocator;
```

**Zastosowanie:** embedded, telemetria pamięci, areny procesowe i integracja z allocatorem hosta. Przykładowy licznik nie obsługuje osobno `realloc`, więc nie jest kompletnym profilerem pamięci.

### 143. Wymuszone wyrównanie przez `#[repr(align(N))]`

`repr(align)` podnosi wymagane wyrównanie struktury. Zmienia również jej rozmiar i layout tablicy takich elementów, ponieważ każdy następny element musi zaczynać się pod odpowiednim adresem.

```rust
#[repr(align(64))]
struct CacheLine<T>(T);

use std::sync::atomic::AtomicU64;

struct Counters {
    producer: CacheLine<AtomicU64>,
    consumer: CacheLine<AtomicU64>,
}

assert_eq!(std::mem::align_of::<CacheLine<u8>>(), 64);
assert_eq!(std::mem::size_of::<CacheLine<u8>>(), 64);
```

**Zastosowanie:** typy wymagane przez SIMD lub DMA oraz ograniczanie false sharing. Wyrównanie jest wskazówką layoutu, nie gwarancją osobnej linii cache na każdej architekturze.

### 144. Struktury packed i bezpieczny odczyt niewyrównany

`#[repr(packed)]` usuwa padding, więc pole może znajdować się pod niewyrównanym adresem. Utworzenie zwykłej referencji do takiego pola jest undefined behavior; należy użyć surowego wskaźnika i `read_unaligned`.

```rust
#[repr(C, packed)]
struct Header {
    kind: u8,
    payload_len: u32,
}

fn payload_len(header: &Header) -> u32 {
    let pointer = std::ptr::addr_of!(header.payload_len);
    // SAFETY: wskaźnik jest poprawny dla odczytu, lecz może być niewyrównany.
    unsafe { pointer.read_unaligned() }
}

let header = Header { kind: 1, payload_len: 4096 };
assert_eq!(payload_len(&header), 4096);
```

**Zastosowanie:** dokładne odwzorowanie formatów binarnych i rejestrów sprzętowych. Często bezpieczniej zdekodować bajty do normalnie wyrównanej struktury.

### 145. Bezpieczna granica wokół `slice::from_raw_parts`

Surowa para wskaźnik–długość może zostać przedstawiona jako slice, ale caller musi zapewnić poprawność całego regionu, wyrównanie, jedną alokację oraz odpowiedni lifetime. Bezpieczne API powinno wiązać lifetime z właścicielem, gdy tylko jest to możliwe.

```rust
use std::slice;

/// # Safety
/// Dla `len > 0` wskaźnik musi wskazywać na `len` czytelnych bajtów,
/// które pozostają żywe przez całe `'a` i należą do jednej alokacji.
unsafe fn bytes_from_foreign<'a>(pointer: *const u8, len: usize) -> &'a [u8] {
    if len == 0 {
        return &[];
    }

    assert!(!pointer.is_null());
    // SAFETY: wymagania zostały przeniesione do kontraktu funkcji.
    unsafe { slice::from_raw_parts(pointer, len) }
}
```

**Zastosowanie:** FFI, pamięć mapowana, bufory sterowników i deserializacja zero-copy. Dowolny lifetime zwracany z surowego wskaźnika wymaga szczególnie ostrożnego wrappera.

### 146. Łańcuchy C przez `CString` i `CStr`

`CString` zapewnia końcowy bajt NUL i odrzuca wewnętrzne zera. `CStr` jest pożyczonym widokiem na poprawny łańcuch C; konwersja na `str` może się nie udać, ponieważ C nie gwarantuje UTF-8.

```rust
use std::ffi::{c_char, c_int, CString, NulError};

unsafe extern "C" {
    fn puts(value: *const c_char) -> c_int;
}

fn print_with_c(text: &str) -> Result<c_int, NulError> {
    let value = CString::new(text)?;
    // SAFETY: `value` jest zakończone NUL i żyje przez czas wywołania.
    Ok(unsafe { puts(value.as_ptr()) })
}
```

**Zastosowanie:** nazwy urządzeń, argumenty bibliotek C i interoperacyjność bez ręcznego zarządzania terminatorem NUL.

### 147. Opaque handle i transfer ownership przez granicę C

Rust może zwrócić C surowy wskaźnik utworzony przez `Box::into_raw`. Dokładnie jedna odpowiadająca funkcja musi później odzyskać ownership przez `Box::from_raw`.

```rust
pub struct Counter {
    value: u64,
}

#[unsafe(no_mangle)]
pub extern "C" fn counter_new() -> *mut Counter {
    Box::into_raw(Box::new(Counter { value: 0 }))
}

/// # Safety
/// `pointer` musi pochodzić z `counter_new` i nie może być zwolniony drugi raz.
#[unsafe(no_mangle)]
pub unsafe extern "C" fn counter_free(pointer: *mut Counter) {
    if !pointer.is_null() {
        // SAFETY: kontrakt wymaga unikalnego wskaźnika z `Box::into_raw`.
        unsafe { drop(Box::from_raw(pointer)) };
    }
}
```

**Zastosowanie:** stabilne C API dla biblioteki Rust, integracja z C++, Pythonem i kodem pluginów. Wszystkie operacje na uchwycie powinny sprawdzać null oraz dokumentować wątkowość.

### 148. Zatrzymywanie panic na granicy FFI przez `catch_unwind`

Panic nie powinien przekraczać zwykłej granicy `extern "C"`. Wrapper może przechwycić unwinding i przetłumaczyć zarówno błąd domenowy, jak i panic na kod statusu rozumiany przez C.

```rust
use std::panic::{catch_unwind, AssertUnwindSafe};

fn work() -> Result<(), ()> {
    Ok(())
}

#[unsafe(no_mangle)]
pub extern "C" fn run_work() -> i32 {
    match catch_unwind(AssertUnwindSafe(work)) {
        Ok(Ok(())) => 0,
        Ok(Err(())) => 1,
        Err(_) => 2,
    }
}
```

**Zastosowanie:** pluginy, biblioteki dynamiczne i callbacki C. `panic = "abort"` nie pozwala przechwycić panic, a `C-unwind` należy stosować wyłącznie przy świadomie zaprojektowanym wspólnym modelu unwindingu.

### 149. Callback C z kontekstem `userdata`

Typowy interfejs C przechowuje wskaźnik do funkcji oraz nieprzezroczysty `void*`. Rust może przekazać wskaźnik do własnego stanu, o ile zagwarantuje jego lifetime, stabilny adres i właściwą synchronizację.

```rust
use std::ffi::c_void;

type Callback = unsafe extern "C" fn(*mut c_void, u32);

unsafe extern "C" fn add_to_counter(context: *mut c_void, value: u32) {
    // SAFETY: rejestrujący przekazał unikalny wskaźnik do żywego `u64`.
    let counter = unsafe { &mut *context.cast::<u64>() };
    *counter += u64::from(value);
}

fn callback_parts(counter: &mut u64) -> (Callback, *mut c_void) {
    (add_to_counter, (counter as *mut u64).cast())
}

let mut counter = 0;
let (callback, context) = callback_parts(&mut counter);
// SAFETY: `context` nadal wskazuje na żywy i wyłącznie pożyczony licznik.
unsafe { callback(context, 5) };
assert_eq!(counter, 5);
```

**Zastosowanie:** SDK urządzeń, callbacki logowania i eventy z C/C++. Jeżeli biblioteka zachowuje callback, stan powinien zwykle trafić do `Box`, a zwalnianie musi być częścią protokołu.

### 150. Bariera optymalizatora przez `std::hint::black_box`

`black_box` utrudnia kompilatorowi usunięcie badanego obliczenia lub zastąpienie go stałym wynikiem. Nie jest mechanizmem bezpieczeństwa ani absolutną gwarancją zachowania każdej instrukcji.

```rust
use std::{hint::black_box, time::Instant};

fn energy(values: &[f32]) -> f32 {
    values.iter().map(|value| value * value).sum()
}

fn main() {
    let values = vec![0.5_f32; 1_000_000];
    let started = Instant::now();
    let result = energy(black_box(&values));
    black_box(result);
    println!("elapsed: {:?}", started.elapsed());
}
```

**Zastosowanie:** szybkie eksperymenty wydajnościowe i wnętrza frameworków benchmarkowych. Wiarygodny pomiar wymaga rozgrzewki, wielu prób, analizy wariancji i narzędzia takiego jak Criterion.

---

## Źródła

- [Rust 1.98.0 — oficjalne ogłoszenie wydania](https://blog.rust-lang.org/2026/08/20/Rust-1.98.0/)
- [The Rust Programming Language](https://doc.rust-lang.org/book/)
- [The Rust Reference](https://doc.rust-lang.org/reference/)
- [Rust 2024 Edition Guide](https://doc.rust-lang.org/edition-guide/rust-2024/)
- [The Rustonomicon](https://doc.rust-lang.org/nomicon/)
- [Standard Library API](https://doc.rust-lang.org/std/)
- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- [The Cargo Book](https://doc.rust-lang.org/cargo/)
- [The Cargo Reference](https://doc.rust-lang.org/cargo/reference/)
- [Asynchronous Programming in Rust](https://rust-lang.github.io/async-book/)
- [Tokio — dokumentacja](https://docs.rs/tokio/latest/tokio/)
- [Miri](https://github.com/rust-lang/miri)
- [The Embedded Rust Book](https://docs.rust-embedded.org/book/)
- [The Rust Performance Book](https://nnethercote.github.io/perf-book/)
- [Loom — dokumentacja](https://docs.rs/loom/latest/loom/)
- [`proptest` — dokumentacja](https://docs.rs/proptest/latest/proptest/)

---

## Proponowana kolejność nauki

1. Najpierw przećwicz ownership, reborrow, lifetime'y i `Drop` — punkty 1–20.
2. Następnie zbuduj kilka małych API opartych na newtype, typestate, GAT i traitach — punkty 21–45.
3. Opanuj iteratory, konwersje i typowane błędy — punkty 46–60.
4. Zaimplementuj minimalny `Future`, a później użyj gotowego runtime'u async — punkty 61–80.
5. `unsafe`, `MaybeUninit`, FFI i atomiki ćwicz dopiero wraz z dokumentowaniem każdego inwariantu bezpieczeństwa.
6. Projektując biblioteki, przejdź przez `Cow`, interior mutability, `#[non_exhaustive]`, `#[must_use]` i precyzyjne przechwytywanie — punkty 101–110.
7. Następnie zbuduj ograniczony pamięciowo pipeline oparty na buforach, vectored I/O, `select!`, `JoinSet`, semaforach i kanałach Tokio — punkty 111–130.
8. Na końcu przećwicz produkcję: workspace, feature flags, Miri, Loom, `no_std`, bezpieczne wrappery FFI i profilowanie — punkty 131–150.

Dobrym projektem przekrojowym jest pipeline SDR: typowany `SampleRate`, typestate sesji akwizycji, bounded channel zapewniający backpressure, supervisor-aktor, osobny worker korelacji uruchamiany poza executorem async, iteratory po ramkach, testy właściwości kodeka oraz mały bezpieczny wrapper `#[repr(C)]` na granicy UHD/FFI.
