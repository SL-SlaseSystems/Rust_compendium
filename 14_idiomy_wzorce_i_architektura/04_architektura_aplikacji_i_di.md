[← Spis treści](../README.md)
<!-- status: expanded -->

# Architektura aplikacji i dependency injection

## Cele

Po tym rozdziale potrafisz:

- przekazać zależność jako jawny kontrakt zamiast globalnego stanu;
- rozmieścić transakcję, retry i shutdown według odpowiedzialności;


Rust nie wymaga frameworka DI. Zależności zwykle są polami struktur,
parametrami generycznymi albo trait objects, a composition root znajduje się
w `main`.

## Port przez trait

~~~rust
trait Repozytorium {
    fn nazwa(&self, id: u64) -> Option<String>;
}

struct Serwis<R> {
    repo: R,
}

impl<R: Repozytorium> Serwis<R> {
    fn powitanie(&self, id: u64) -> Result<String, &'static str> {
        let nazwa = self.repo.nazwa(id).ok_or("brak użytkownika")?;
        Ok(format!("Witaj, {nazwa}"))
    }
}

struct Pamiec;

impl Repozytorium for Pamiec {
    fn nazwa(&self, id: u64) -> Option<String> {
        (id == 1).then(|| "Ada".into())
    }
}

fn main() {
    let serwis = Serwis { repo: Pamiec };
    assert_eq!(serwis.powitanie(1).unwrap(), "Witaj, Ada");
}
~~~

Generyk daje static dispatch i czytelny typ, ale propaguje parametr przez
warstwy. `Arc<dyn Repozytorium + Send + Sync>` ogranicza rozrost typów i
pozwala wybrać implementację w runtime.

## Granice

Praktyczny podział:

- domena — typy i reguły bez I/O;
- use cases — orkiestracja portów;
- adapters — baza, HTTP, filesystem, kolejka;
- composition root — konfiguracja i połączenie implementacji.

Kierunek zależności ma prowadzić do kontraktów domenowych. Nie twórz traitu dla
każdej struktury. Trait jest użyteczny, gdy istnieje co najmniej jedna realna
granica wymienności, testowania lub dynamicznego wyboru.

## Test doubles

Prosty fake w pamięci często daje lepszy test niż framework mockujący:

~~~rust
use std::collections::HashMap;

struct FakeRepo(HashMap<u64, String>);

trait Istnieje {
    fn istnieje(&self, id: u64) -> bool;
}

impl Istnieje for FakeRepo {
    fn istnieje(&self, id: u64) -> bool { self.0.contains_key(&id) }
}

fn aktywny(repo: &impl Istnieje, id: u64) -> bool {
    repo.istnieje(id)
}

fn main() {
    let repo = FakeRepo(HashMap::from([(7, "Ada".into())]));
    assert!(aktywny(&repo, 7));
}
~~~

Testuj zachowanie, nie liczbę prywatnych wywołań, chyba że interakcja sama
jest kontraktem.

## Konfiguracja i stan

Parsuj oraz waliduj konfigurację raz. Przekazuj immutable config przez
ownership lub `Arc`. Global mutable state utrudnia testy i lifecycle. Pule
połączeń, klienci i runtime’y powinny mieć jawnego właściciela oraz shutdown.

## Moduły i crate’y

Zacznij od modułów w jednym crate. Wydziel crate, gdy potrzebujesz osobnego
cyklu kompilacji, braku zależności platformowej, stabilnej granicy lub
ponownego użycia. Zbyt wiele crate’ów zwiększa boilerplate i czas integracji.


## Model — zależność to także błędy i czas życia

Trait portu opisuje to, czego potrzebuje przypadek użycia, a nie pełną powierzchnię klienta bazy danych. Jeżeli serwis ma jedynie sprawdzić nazwę użytkownika, nie musi dostawać obiektu umożliwiającego dowolne SQL. Mały kontrakt ułatwia testy, ogranicza sprzężenie i pokazuje, kto odpowiada za błąd. Nie oznacza to jednak automatycznego tworzenia traitu dla każdej funkcji pomocniczej.

~~~rust
#[derive(Debug, PartialEq)]
enum Blad { Niedostepne, Brak }
trait Uzytkownicy { fn nazwa(&self, id: u64) -> Result<Option<String>, Blad>; }
fn powitanie(repo: &impl Uzytkownicy, id: u64) -> Result<String, Blad> {
    let nazwa = repo.nazwa(id)?.ok_or(Blad::Brak)?;
    Ok(format!("Witaj, {nazwa}"))
}
struct Fake { awaria: bool }
impl Uzytkownicy for Fake {
    fn nazwa(&self, id: u64) -> Result<Option<String>, Blad> {
        if self.awaria { Err(Blad::Niedostepne) }
        else { Ok((id == 7).then(|| "Ada".into())) }
    }
}
fn main() {
    assert_eq!(powitanie(&Fake { awaria: false }, 7).unwrap(), "Witaj, Ada");
    assert_eq!(powitanie(&Fake { awaria: false }, 8), Err(Blad::Brak));
    assert_eq!(powitanie(&Fake { awaria: true }, 7), Err(Blad::Niedostepne));
}
~~~

Przykład rozróżnia brak rekordu od niedostępności adaptera. Fake pokazuje trzy obserwowalne wyniki bez sieci i globalnej konfiguracji. Nie dowodzi jednak zachowania produkcyjnego adaptera: mapowanie błędów bazy i transakcje wymagają osobnych testów integracyjnych. Test domeny powinien być szybki, a test adaptera sprawdzać jego realny kontrakt.

Composition root składa zależności, nadaje im właściciela i ustala kolejność zamykania. `Arc` ułatwia współdzielenie, lecz może ukryć faktyczny czas życia zasobu; ostatni klon w tasku potrafi przedłużyć działanie puli po zakończeniu żądania. Przechowuj kontrolę tasków oraz shutdown obok zasobów, które posiadają. Globalny singleton utrudnia zastąpienie zegara, konfiguracji i adaptera w testach.

Generyczne `Serwis<R>` daje statyczny dispatch i możliwość inliningu, lecz parametr propaguje się przez kolejne warstwy. `dyn Trait` stabilizuje typ pola i umożliwia wybór implementacji w runtime, ale wymaga zgodnego traitu oraz ustalenia własności. `Box`, `Arc` i referencja mają różne znaczenie czasu życia. Nie wybieraj `Arc<dyn Trait + Send + Sync>` dla komponentu, który nigdy nie jest współdzielony między wątkami.

Transakcja należy do przypadku użycia, który wymaga wspólnego commit kilku operacji. Dwa niezależne porty z osobnymi `save` nie dają automatycznie atomowości. Można przekazać kontekst transakcji, udostępnić port z operacją odpowiadającą niezmiennikowi albo zastosować jawny workflow kompensacji. Retry także powinien znać idempotencję i wspólny deadline; nie każda warstwa ma samodzielnie ponawiać ten sam błąd.

Domena może być niezależna od runtime’u i formatu transportu, lecz musi znać realne reguły biznesowe: waluty, limity, stany i błędy. Całkowite usuwanie znaczenia przez ogólne `Manager<T>` nie poprawia architektury. Granica jest dobra wtedy, gdy ułatwia konkretną zmianę lub weryfikację i nie ukrywa ważnych zobowiązań.

## Diagnostyka kompilatora

Rozrost komunikatów z wieloma parametrami generycznymi może wskazywać, że typy implementacyjne przeciekają przez zbyt wiele warstw. Błąd dyn compatibility wymaga sprawdzenia metod traitu, a nie automatycznego dodania `Box`. Brak `Send` lub `Sync` ujawnia realny model dostępu. Kompilator nie wykryje utraty atomowości dwóch oddzielnych operacji repozytoriów ani dublującego się retry; to wymagania kontraktu architektonicznego.

## Praktyka produkcyjna

Zacznij od jednego crate’a i czytelnych modułów. Wydzielaj pakiety dopiero przy rzeczywistym ponownym użyciu, izolacji platform lub osobnym wydawaniu. Wstrzykuj zegar i generator identyfikatorów tam, gdzie deterministyczne testy tego potrzebują. Ustal właścicieli klientów, pul, runtime’u i tasków oraz kolejność shutdown. Dla każdego portu zapisz klasy błędów, gwarancje idempotencji i zakres transakcji. To więcej znaczy dla niezawodności niż sama nazwa wzorca architektonicznego.

## Sprawdź, czy rozumiesz

- Dlaczego fake repozytorium nie dowodzi poprawności adaptera bazy?
- Która warstwa zna atomowość całego przypadku użycia?
- Jak ukryty klon Arc wpływa na zamykanie aplikacji?

## Ćwiczenia

- `B33-1` — podstawowe: Napisz port zwracający osobno brak użytkownika i awarię. [Rozwiązanie](../rozwiazania/14_idiomy_wzorce_i_architektura/04_architektura_aplikacji_i_di.md#b33-1).
- `B33-2` — praktyczne: Przekaż zegar jako parametr, aby testować wygaśnięcie bez sleep. [Rozwiązanie](../rozwiazania/14_idiomy_wzorce_i_architektura/04_architektura_aplikacji_i_di.md#b33-2).
- `B33-3` — pogłębione: Zaprojektuj zakup obejmujący rezerwację i płatność z nieznanym wynikiem po timeout. [Rozwiązanie](../rozwiazania/14_idiomy_wzorce_i_architektura/04_architektura_aplikacji_i_di.md#b33-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [Rust Book: trait objects](https://doc.rust-lang.org/book/ch18-02-trait-objects.html)
- [Arc i współdzielenie](https://doc.rust-lang.org/std/sync/struct.Arc.html)
- [API Guidelines: elastyczność](https://rust-lang.github.io/api-guidelines/flexibility.html)

## Powiązane tematy

- [Traits i associated items](../05_generics_traits_i_system_typow/02_traits_i_associated_items.md)
- [Moduły i workspaces](../08_moduly_cargo_i_workspaces/02_crates_pakiety_i_workspaces.md)
- [Współdzielony stan](../10_wspolbieznosc/03_arc_mutex_rwlock_i_condvar.md)
