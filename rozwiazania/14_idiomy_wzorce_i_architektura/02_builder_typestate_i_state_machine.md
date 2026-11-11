[← Spis treści](../../README.md)

# Rozwiązania: Builder, typestate i state machine

[Rozdział źródłowy](../../14_idiomy_wzorce_i_architektura/02_builder_typestate_i_state_machine.md).

## B31-1

~~~rust
fn konfiguracja(host:&str,timeout:u64)->Result<(&str,u64),&'static str>{if host.trim().is_empty(){return Err("pusty host")}if timeout==0{return Err("zerowy timeout")}Ok((host,timeout))}
fn main(){assert!(konfiguracja("",1).is_err());assert!(konfiguracja("localhost",0).is_err());assert!(konfiguracja("localhost",1).is_ok());}
~~~
Walidacja może być ciałem `build`; najpierw przygotuj komplet danych, potem buduj klienta.

## B31-2

~~~rust
#[derive(Debug)]struct Gotowe(String);
fn aktywuj(s:Gotowe)->Result<String,Gotowe>{if s.0.is_empty(){Err(s)}else{Ok(s.0)}}
fn main(){let stare=aktywuj(Gotowe(String::new())).unwrap_err();assert!(stare.0.is_empty());assert_eq!(aktywuj(Gotowe("ok".into())).unwrap(),"ok");}
~~~

## B31-3

~~~rust
#[derive(Debug,PartialEq)]enum Stan{Nowy,Aktywny,Koniec}
enum Zdarzenie{Start,Stop}
fn krok(s:Stan,z:Zdarzenie)->Result<Stan,Stan>{match(s,z){(Stan::Nowy,Zdarzenie::Start)=>Ok(Stan::Aktywny),(Stan::Aktywny,Zdarzenie::Stop)=>Ok(Stan::Koniec),(stary,_)=>Err(stary)}}
fn main(){let s=krok(Stan::Nowy,Zdarzenie::Start).unwrap();let s=krok(s,Zdarzenie::Stop).unwrap();assert_eq!(krok(s,Zdarzenie::Start),Err(Stan::Koniec));}
~~~
Niepoprawne zdarzenie zwraca poprzedni stan bez cichej zmiany.

