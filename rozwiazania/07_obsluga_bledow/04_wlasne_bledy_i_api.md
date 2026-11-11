[← Spis treści](../../README.md)

# Rozwiązania: Własne błędy i projektowanie API

[Rozdział źródłowy](../../07_obsluga_bledow/04_wlasne_bledy_i_api.md).

## B04-1

~~~rust
#[derive(Debug,PartialEq)] enum Blad { Pusty, ZaDlugi { limit: usize } }
fn sprawdz(s:&str)->Result<(),Blad> {
    if s.is_empty() { Err(Blad::Pusty) } else if s.chars().count()>3 { Err(Blad::ZaDlugi{limit:3}) } else { Ok(()) }
}
fn main() { assert_eq!(sprawdz(""),Err(Blad::Pusty)); assert!(sprawdz("Ada").is_ok()); }
~~~
Limit mierzy znaki Unicode, a nie bajty; to świadoma część kontraktu.

## B04-2

~~~rust
use std::{error::Error,fmt,num::ParseIntError};
#[derive(Debug)] struct Blad(ParseIntError);
impl fmt::Display for Blad { fn fmt(&self,f:&mut fmt::Formatter<'_>)->fmt::Result { write!(f,"niepoprawny port") } }
impl Error for Blad { fn source(&self)->Option<&(dyn Error+'static)> {Some(&self.0)} }
fn main() { let e=Blad("x".parse::<u16>().unwrap_err()); assert!(e.source().is_some()); }
~~~

## B04-3

~~~rust
#[derive(Debug,PartialEq)] enum Decyzja { PoprawDane, Ponow, UstalWynik }
enum Blad { Walidacja, PrzedWyslaniem, TimeoutPoWyslaniu }
impl Blad { fn decyzja(&self)->Decyzja { match self {
    Self::Walidacja=>Decyzja::PoprawDane,
    Self::PrzedWyslaniem=>Decyzja::Ponow,
    Self::TimeoutPoWyslaniu=>Decyzja::UstalWynik,
}} }
fn main() {
    assert_eq!(Blad::TimeoutPoWyslaniu.decyzja(),Decyzja::UstalWynik);
    assert_eq!(Blad::Walidacja.decyzja(),Decyzja::PoprawDane);
    assert_eq!(Blad::PrzedWyslaniem.decyzja(),Decyzja::Ponow);
}
~~~
Przed ponowieniem nadal obowiązują deadline i limit prób.

