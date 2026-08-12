[← Spis treści](../README.md)

# Architektura aplikacji i dependency injection

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

## Powiązane tematy

- [Traits i associated items](../04_typy_i_modelowanie/04_traits_i_associated_items.md)
- [Moduły i workspaces](../07_moduly_i_cargo/02_crates_pakiety_i_workspaces.md)
- [Współdzielony stan](../09_wspolbieznosc/03_arc_mutex_rwlock_i_condvar.md)
