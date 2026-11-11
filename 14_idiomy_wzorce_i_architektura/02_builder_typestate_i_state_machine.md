[← Spis treści](../README.md)
<!-- status: expanded -->

# Builder, typestate i state machine

## Cele

Po tym rozdziale potrafisz:

- wybrać builder, typestate lub enum według rodzaju stanu;
- zaprojektować błędne przejście bez utraty zasobu;


## Builder

Builder nazywa wiele opcjonalnych parametrów i może odroczyć walidację:

~~~rust
#[derive(Debug, PartialEq)]
struct Klient {
    host: String,
    timeout_ms: u64,
}

#[derive(Default)]
struct KlientBuilder {
    host: Option<String>,
    timeout_ms: Option<u64>,
}

impl KlientBuilder {
    fn host(mut self, host: impl Into<String>) -> Self {
        self.host = Some(host.into());
        self
    }

    fn timeout_ms(mut self, timeout: u64) -> Self {
        self.timeout_ms = Some(timeout);
        self
    }

    fn build(self) -> Result<Klient, &'static str> {
        let host = self.host.ok_or("brak hosta")?;
        let timeout_ms = self.timeout_ms.unwrap_or(1_000);
        if timeout_ms == 0 { return Err("timeout musi być dodatni"); }
        Ok(Klient { host, timeout_ms })
    }
}

fn main() {
    let k = KlientBuilder::default().host("localhost").build().unwrap();
    assert_eq!(k.timeout_ms, 1_000);
}
~~~

Consuming builder (`self -> Self`) dobrze łańcuchuje i może przenosić pola.
Mutable builder (`&mut self -> &mut Self`) ułatwia warunkową konfigurację.
`build` powinien oddać konkretny błąd walidacji.

## Typestate

Stan jest parametrem typu, a przejście konsumuje starą wartość:

~~~rust
use std::marker::PhantomData;

struct Zamkniete;
struct Otwarte;

struct Polaczenie<Stan> {
    adres: String,
    _stan: PhantomData<Stan>,
}

impl Polaczenie<Zamkniete> {
    fn nowe(adres: impl Into<String>) -> Self {
        Self { adres: adres.into(), _stan: PhantomData }
    }

    fn otworz(self) -> Polaczenie<Otwarte> {
        Polaczenie { adres: self.adres, _stan: PhantomData }
    }
}

impl Polaczenie<Otwarte> {
    fn wyslij(&self, dane: &str) -> usize {
        self.adres.len() + dane.len()
    }

    fn zamknij(self) -> Polaczenie<Zamkniete> {
        Polaczenie { adres: self.adres, _stan: PhantomData }
    }
}

fn main() {
    let p = Polaczenie::<Zamkniete>::nowe("localhost").otworz();
    assert_eq!(p.wyslij("hej"), 12);
    let _ = p.zamknij();
}
~~~

Nie da się wywołać `wyslij` na `Polaczenie<Zamkniete>`. Koszt to więcej typów,
trudniejsze przechowywanie heterogenicznego stanu i możliwy bloat.

## Enum jako state machine

Gdy stan zmienia się dynamicznie i trzeba go przechowywać w jednej kolekcji,
enum bywa prostszy:

~~~rust
enum Stan {
    Nowy,
    Aktywny { proby: u8 },
    Zakonczony,
}

fn krok(stan: Stan) -> Stan {
    match stan {
        Stan::Nowy => Stan::Aktywny { proby: 0 },
        Stan::Aktywny { proby } if proby < 2 => Stan::Aktywny { proby: proby + 1 },
        Stan::Aktywny { .. } => Stan::Zakonczony,
        Stan::Zakonczony => Stan::Zakonczony,
    }
}

fn main() {
    assert!(matches!(krok(Stan::Nowy), Stan::Aktywny { proby: 0 }));
}
~~~

Typestate dla compile-time workflow; enum dla runtime state. Nie wciskaj
typestate w publiczne API, jeśli użytkownik musi stale erase’ować typ.


## Model — stan konstrukcji i stan działania to różne problemy

Builder zbiera parametry i ustanawia niezmienniki przy `build`. Nie powinien oddawać częściowo poprawnego klienta jako pełnego obiektu. Typestate przenosi część reguł do zestawu dostępnych metod. Enum przechowuje dynamiczny stan w jednym typie, dzięki czemu nadaje się do kolekcji, serializacji i obsługi zdarzeń. Te narzędzia można łączyć, lecz każde dodaje własny koszt ergonomii.

Przykład połączenia z wcześniejszej sekcji modeluje wyłącznie dozwolone wywołania. Metoda `otworz` nie wykonuje rzeczywistego I/O, więc nie dowodzi udanego połączenia. Produkcyjne przejście może zawieść i powinno wyrażać ten fakt w wyniku. Jeśli błąd ma umożliwić ponowienie bez odtwarzania konfiguracji, zwróć również stary stan.

~~~rust
#[derive(Debug, PartialEq)]
struct Przygotowane { adres: String }
struct Aktywne { adres: String }
impl Przygotowane {
    fn aktywuj(self) -> Result<Aktywne, (Self, &'static str)> {
        if self.adres.is_empty() { Err((self, "pusty adres")) }
        else { Ok(Aktywne { adres: self.adres }) }
    }
}
fn main() {
    let p = Przygotowane { adres: String::new() };
    let (odzyskane, blad) = match p.aktywuj() { Err(e) => e, Ok(_) => panic!("oczekiwano błędu") };
    assert_eq!(blad, "pusty adres");
    assert!(odzyskane.adres.is_empty());
    let a = Przygotowane { adres: "localhost".into() }.aktywuj().unwrap();
    assert_eq!(a.adres, "localhost");
}
~~~

To walidowane przejście modelu, nadal bez sieci. Stary obiekt jest konsumowany, a przy błędzie wraca do wywołującego. Sukces i porażka jawnie opisują własność. Dla zasobu zewnętrznego nie zawsze da się odzyskać identyczny stan, więc typ błędu powinien rozróżnić uszkodzony, zamknięty i nadal używalny uchwyt.

Consuming builder dobrze przenosi posiadane pola, ale po wywołaniu metody starej wartości już nie użyjesz. Mutable builder ułatwia warunkowe ustawianie, lecz `build(&self)` może wymagać klonów, a `build(&mut self)` wyjmowania pól i zdefiniowania stanu po wywołaniu. Nie ma uniwersalnie najlepszego odbiorcy; dokumentuj, czy builder jest wielorazowy i co oznacza drugie `build`.

Typestate ogranicza liczbę niepoprawnych programów, lecz dynamiczne wejście nadal wymaga walidacji. Uwierzytelniony stan nie dowodzi, że token nigdy nie wygaśnie ani że połączenie nie zostanie zerwane. Typ koduje to, co API może wiarygodnie obiecać w danym momencie. Dodatkowe parametry typu mnożą możliwe instancje i utrudniają przechowywanie heterogenicznego stanu.

Przy enumie przejście powinno być funkcją jawnie obsługującą stan i zdarzenie. Ramiona zapasowe potrafią ukryć pominięte zdarzenia; dla ważnego protokołu jawny błąd przejścia jest lepszy od cichego pozostania w tym samym stanie. Jeżeli przejście wykonuje efekty, oddziel wyznaczenie nowego stanu od jego zatwierdzenia, tak aby błąd nie zostawił obiektu w przypadkowym stanie pośrednim.

## Diagnostyka kompilatora

Brak metody dla typu oznaczającego zamknięty stan jest zamierzoną ochroną typestate. Błąd użycia po przeniesieniu pokazuje, że przejście konsumuje poprzedni stan. Nie dodawaj `Clone` do uchwytu tylko po to, aby ominąć liniowy przebieg; klon może podważyć semantykę własności zasobu. Jeśli `unwrap` wyniku wymaga `Debug` dla starego stanu w błędzie, dodaj sensowną diagnostykę albo jawnie obsłuż wynik.

## Praktyka produkcyjna

Wybieraj typestate dla małego, stabilnego workflow, a enum dla stanu odtwarzanego z danych i zdarzeń. Builder niech waliduje zależności między polami, nie tylko obecność każdego z osobna. Testuj brak pola, konflikt, wartość graniczną, udane przejście i zachowanie po błędzie. Publiczne markery stanów oraz dostępne metody również podlegają SemVer. Nie obiecuj gwarancji sieciowej wyłącznie na podstawie nazwy `Polaczenie<Otwarte>`.

## Sprawdź, czy rozumiesz

- Co ma zwrócić błędne przejście konsumujące obiekt, jeśli chcemy retry?
- Dlaczego typ uwierzytelniony nie gwarantuje wiecznej ważności tokenu?
- Kiedy enum jest łatwiejszy od typestate?

## Ćwiczenia

- `B31-1` — podstawowe: Dodaj walidację pustego hosta i zerowego timeoutu w builderze. [Rozwiązanie](../rozwiazania/14_idiomy_wzorce_i_architektura/02_builder_typestate_i_state_machine.md#b31-1).
- `B31-2` — praktyczne: Zwróć stary stan przy nieudanej aktywacji. [Rozwiązanie](../rozwiazania/14_idiomy_wzorce_i_architektura/02_builder_typestate_i_state_machine.md#b31-2).
- `B31-3` — pogłębione: Zaimplementuj enum maszyny stanów odrzucający zdarzenie po zakończeniu. [Rozwiązanie](../rozwiazania/14_idiomy_wzorce_i_architektura/02_builder_typestate_i_state_machine.md#b31-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [Rust Book: metody i odbiorcy](https://doc.rust-lang.org/book/ch05-03-method-syntax.html)
- [PhantomData](https://doc.rust-lang.org/std/marker/struct.PhantomData.html)

## Powiązane tematy

- [Struktury i enumy](../04_struktury_enumy_i_wzorce/01_struktury_enumy_i_metody.md)
- [`PhantomData` i variance](../05_generics_traits_i_system_typow/04_variance_subtyping_i_dropck.md)
- [Projektowanie API](03_projektowanie_api_i_semver.md)
