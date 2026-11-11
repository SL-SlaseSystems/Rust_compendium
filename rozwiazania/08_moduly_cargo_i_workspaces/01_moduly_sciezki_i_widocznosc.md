[← Spis treści](../../README.md)

# Rozwiązania: Moduły, ścieżki i widoczność

[Rozdział źródłowy](../../08_moduly_cargo_i_workspaces/01_moduly_sciezki_i_widocznosc.md).

## B05-1

~~~rust
mod domena {
    pub struct Limit(u8);
    impl Limit { pub fn nowy(n:u8)->Option<Self>{(n>0).then_some(Self(n))} pub fn get(&self)->u8{self.0} }
}
fn main(){assert_eq!(domena::Limit::nowy(3).unwrap().get(),3);assert!(domena::Limit::nowy(0).is_none());}
~~~

## B05-2

~~~rust
mod szczegoly { pub struct Raport; impl Raport { pub fn kod(&self)->u8{7} } }
pub use szczegoly::Raport;
fn main(){assert_eq!(Raport.kod(),7);}
~~~
Ścieżka `szczegoly` nie musi stać się publiczna, aby re-export był legalny.

## B05-3

Układ obejmuje `Cargo.toml`, `src/lib.rs`, `src/domena.rs` i `src/main.rs`. W `lib.rs` zapisz `pub mod domena;`. W `domena.rs` zdefiniuj `pub fn uruchom() {}`. W `main.rs` wywołaj `moja_aplikacja::domena::uruchom();`, gdzie nazwa odpowiada crate’owi bibliotecznemu. Nie deklaruj tam ponownie `mod domena;`: binarium używa wtedy jednego publicznego typu biblioteki, a nie własnej kopii drzewa. Jest to rozwiązanie wieloplikowe wymagające pakietu Cargo, dlatego opis nie jest samodzielnym doctestem.

