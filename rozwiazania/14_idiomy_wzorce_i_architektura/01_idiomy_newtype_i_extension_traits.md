[← Spis treści](../../README.md)

# Rozwiązania: Idiomy, newtype i extension traits

[Rozdział źródłowy](../../14_idiomy_wzorce_i_architektura/01_idiomy_newtype_i_extension_traits.md).

## B30-1

~~~rust
struct UzytkownikId(u64);struct ZamowienieId(u64);
fn main(){let u=UzytkownikId(1);let z=ZamowienieId(2);assert_ne!(u.0,z.0);}
~~~
Przypisanie `let z: ZamowienieId = u;` byłoby niezgodnością typów.

## B30-2

~~~rust
mod api{#[derive(Debug)]pub struct Dodatnia(u32);impl TryFrom<u32>for Dodatnia{type Error=&'static str;fn try_from(n:u32)->Result<Self,Self::Error>{if n==0{Err("zero")}else{Ok(Self(n))}}}impl Dodatnia{pub fn get(&self)->u32{self.0}}}
fn main(){assert!(api::Dodatnia::try_from(0).is_err());assert_eq!(api::Dodatnia::try_from(2).unwrap().get(),2);}
~~~

## B30-3

~~~rust
trait DlugoscDomeny{fn rozmiar(&self)->usize;}
impl DlugoscDomeny for str{fn rozmiar(&self)->usize{self.chars().count()}}
trait DlugoscBajtow{fn rozmiar(&self)->usize;}
impl DlugoscBajtow for str{fn rozmiar(&self)->usize{self.len()}}
fn main(){assert_eq!(DlugoscDomeny::rozmiar("ą"),1);assert_eq!(DlugoscBajtow::rozmiar("ą"),2);}
~~~
Pełna kwalifikacja określa, który trait ma dostarczyć metodę. Obie jednostki rozmiaru są jawne.

