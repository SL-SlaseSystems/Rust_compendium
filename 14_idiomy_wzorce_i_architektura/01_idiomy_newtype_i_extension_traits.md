[← Spis treści](../README.md)
<!-- status: expanded -->

# Idiomy, newtype i extension traits

## Cele

Po tym rozdziale potrafisz:

- zakodować walidację i jednostki w odrębnych typach;
- ocenić konsekwencje Deref, konwersji i sealed trait;


Idiomy wykorzystują system typów zamiast konwencji zapisanej tylko w
komentarzu.

## Newtype

Newtype jest tuple struct z jednym polem. Tworzy odrębny typ bez koniecznej dodatkowej alokacji
lub indirection i pozwala kontrolować konstrukcję oraz implementacje traits.

~~~rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
struct UzytkownikId(u64);

impl UzytkownikId {
    fn nowy(id: u64) -> Option<Self> {
        (id != 0).then_some(Self(id))
    }

    fn get(self) -> u64 { self.0 }
}

fn pobierz(id: UzytkownikId) -> String {
    format!("użytkownik {}", id.get())
}

fn main() {
    let id = UzytkownikId::nowy(7).unwrap();
    assert_eq!(pobierz(id), "użytkownik 7");
    assert!(UzytkownikId::nowy(0).is_none());
}
~~~

Newtype rozróżnia np. `UzytkownikId` od `ZamowienieId`, omija orphan rule i
może ukryć niepożądane operacje surowego typu. `repr(transparent)` dodawaj
tylko, gdy potrzebujesz gwarancji reprezentacji, np. FFI.

## Extension trait

Trait rozszerzający dodaje metody do obcego typu bez naruszania orphan rule:

~~~rust
trait StrExt {
    fn niepusty(&self) -> Option<&str>;
}

impl StrExt for str {
    fn niepusty(&self) -> Option<&str> {
        let s = self.trim();
        (!s.is_empty()).then_some(s)
    }
}

fn main() {
    assert_eq!("  Rust ".niepusty(), Some("Rust"));
    assert_eq!("   ".niepusty(), None);
}
~~~

Użytkownik musi importować trait. Nazwa powinna wskazywać domenę; nie twórz
gigantycznego „UtilsExt”.

## Sealed trait

Jeśli konsumenci mają używać traitu w bounds, lecz nie implementować go,
dodaj prywatny supertrait:

~~~rust
mod api {
    mod sealed {
        pub trait Sealed {}
    }

    pub trait Id: sealed::Sealed {
        fn raw(&self) -> u64;
    }

    pub struct LokalnyId(pub u64);
    impl sealed::Sealed for LokalnyId {}
    impl Id for LokalnyId {
        fn raw(&self) -> u64 { self.0 }
    }
}

fn main() {
    use api::Id;
    assert_eq!(api::LokalnyId(9).raw(), 9);
}
~~~

Sealing zwiększa swobodę ewolucji, ale odbiera extensibility. Zakomunikuj tę
decyzję.

## Inne idiomy

- `Default` plus update syntax dla konfiguracji;
- `From`/`TryFrom` zamiast ad hoc `to_*`;
- `AsRef<[T]>` na elastycznym wejściu, ale bez przesady;
- iteratory zamiast zwracania tymczasowego `Vec`;
- RAII guards dla transakcji i blokad;
- enums zamiast magicznych liczb i zestawów bool.


## Model — odrębny typ to odrębny zestaw uprawnień

Alias `type UzytkownikId = u64` daje drugą nazwę tego samego typu. Newtype tworzy nowy typ, więc kompilator odrzuca pomylenie identyfikatora użytkownika z identyfikatorem zamówienia. Prywatne pole oraz kontrolowany konstruktor ustanawiają niezmiennik, którego nie da się ominąć zwykłym literałem poza modułem. Implementacje konwersji muszą zachować tę samą regułę, inaczej poprawny konstruktor staje się dekoracją.

~~~rust
mod domena {
    #[derive(Debug, PartialEq)]
    pub struct Port(u16);
    impl TryFrom<u16> for Port {
        type Error = &'static str;
        fn try_from(n: u16) -> Result<Self, Self::Error> {
            if n == 0 { Err("port zero") } else { Ok(Self(n)) }
        }
    }
    impl Port { pub fn get(&self) -> u16 { self.0 } }
}
fn main() {
    let port = domena::Port::try_from(8080).unwrap();
    assert_eq!(port.get(), 8080);
    assert!(domena::Port::try_from(0).is_err());
}
~~~

`TryFrom` jest właściwe, ponieważ konwersja może się nie udać. `From` powinno opisywać konwersję nieomylną, a nie ukrywać `unwrap` wewnątrz pozornie bezpiecznego przejścia. Zwrócenie surowej liczby przez `get` nie narusza niezmiennika, bo klient nie uzyskuje mutowalnego dostępu do pola.

`Deref` nie jest ogólnym mechanizmem dziedziczenia. Automatyczne udostępnienie całego API opakowanego typu może pozwolić na mutacje łamiące walidację albo stworzyć obietnicę kompatybilności ze wszystkimi jego metodami. Dla jednostki domenowej zwykle czytelniejsze są jawne metody. `repr(transparent)` ustanawia określone gwarancje reprezentacji, jeśli są potrzebne, ale nie zastępuje kontroli konstrukcji i nie czyni dowolnych konwersji FFI bezpiecznymi.

Stwierdzenie o braku kosztu runtime należy rozumieć jako brak koniecznej dodatkowej alokacji lub indirection wyłącznie z powodu opakowania. Layout i ABI wymagają oddzielnych gwarancji, a sama walidacja, klonowanie lub dodatkowe metody mogą kosztować. Newtype nie jest gwarancją, że optymalizator usunie każdy możliwy koszt wynikający z użycia API.

Extension trait jest legalny, bo trait należy do twojego crate’a, nawet gdy implementowany typ jest obcy. Metody wymagają traitu w zasięgu, co może prowadzić do konfliktów nazw. Jeśli obcy typ dostanie własną metodę o podobnej nazwie, rozwiązywanie wywołania może się zmienić; pełna kwalifikacja `Trait::metoda(...)` usuwa dwuznaczność. Dobieraj nazwy domenowe zamiast powszechnych, krótkich nazw.

Sealing blokuje zewnętrzne implementacje przez niedostępny do nazwania supertrait. Nadal trzeba uważać na blanket impl i re-exporty, które mogłyby niechcący otworzyć ścieżkę. Sealed trait daje autorowi większą swobodę rozwoju, ale ogranicza integracje klientów. To decyzja o rozszerzalności API, którą należy nazwać w dokumentacji, a nie ukryty trik wersjonowania.

## Diagnostyka kompilatora

Niezgodność `UzytkownikId` i `ZamowienieId` jest pożądaną diagnostyką, nie przeszkodą wymagającą dereferencji. Błąd orphan rule oznacza, że nie wolno implementować obcego traitu dla obcego typu w danej konfiguracji; własny newtype albo własny extension trait tworzy właściwą granicę. Brak metody extension trait może wynikać z braku importu. Nie otwieraj pola wrappera tylko po to, aby wyeliminować świadomie ustanowiony błąd typów.

## Praktyka produkcyjna

Używaj newtype tam, gdzie eliminuje realną klasę pomyłek: jednostki, identyfikatory, zwalidowane dane. Nie twórz kilkudziesięciu wrapperów bez odmiennych reguł i operacji. Audytuj wszystkie konwersje oraz mutowalny dostęp. Dla publicznych extension traits planuj konflikty nazw i blanket impl. Sealed trait wybierz wtedy, gdy zestaw implementacji jest własnością biblioteki; otwarty trait wtedy, gdy możliwość integracji klienta jest realnym wymaganiem.

## Sprawdź, czy rozumiesz

- Czym alias różni się od newtype przy sprawdzaniu argumentów?
- Jak DerefMut może podważyć walidowany wrapper?
- Dlaczego TryFrom jest lepsze od panikującego From?

## Ćwiczenia

- `B30-1` — podstawowe: Utwórz dwa odrębne typy identyfikatorów. [Rozwiązanie](../rozwiazania/14_idiomy_wzorce_i_architektura/01_idiomy_newtype_i_extension_traits.md#b30-1).
- `B30-2` — praktyczne: Zaimplementuj TryFrom dla dodatniej wartości bez publicznego pola. [Rozwiązanie](../rozwiazania/14_idiomy_wzorce_i_architektura/01_idiomy_newtype_i_extension_traits.md#b30-2).
- `B30-3` — pogłębione: Zaprojektuj extension trait i pokaż pełną kwalifikację metody przy konflikcie nazw. [Rozwiązanie](../rozwiazania/14_idiomy_wzorce_i_architektura/01_idiomy_newtype_i_extension_traits.md#b30-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [API Guidelines: newtype](https://rust-lang.github.io/api-guidelines/type-safety.html)
- [Deref: decyzja o API](https://doc.rust-lang.org/std/ops/trait.Deref.html)
- [TryFrom](https://doc.rust-lang.org/std/convert/trait.TryFrom.html)

## Powiązane tematy

- [Traits i orphan rule](../05_generics_traits_i_system_typow/02_traits_i_associated_items.md)
- [Builder i typestate](02_builder_typestate_i_state_machine.md)
- [Projektowanie API](03_projektowanie_api_i_semver.md)
