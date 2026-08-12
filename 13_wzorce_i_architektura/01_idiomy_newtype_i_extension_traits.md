[← Spis treści](../README.md)

# Idiomy, newtype i extension traits

Idiomy wykorzystują system typów zamiast konwencji zapisanej tylko w
komentarzu.

## Newtype

Newtype jest tuple struct z jednym polem. Tworzy odrębny typ bez kosztu
runtime i pozwala kontrolować konstrukcję oraz implementacje traits.

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

## Powiązane tematy

- [Traits i orphan rule](../04_typy_i_modelowanie/04_traits_i_associated_items.md)
- [Builder i typestate](02_builder_typestate_i_state_machine.md)
- [Projektowanie API](03_projektowanie_api_i_semver.md)
