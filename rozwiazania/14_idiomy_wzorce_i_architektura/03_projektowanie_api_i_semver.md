[← Spis treści](../../README.md)

# Rozwiązania: Projektowanie API i SemVer

[Rozdział źródłowy](../../14_idiomy_wzorce_i_architektura/03_projektowanie_api_i_semver.md).

## B32-1

~~~rust
mod api{pub struct Limit{n:u32}impl Limit{pub fn nowy(n:u32)->Option<Self>{(n>0).then_some(Self{n})}pub fn get(&self)->u32{self.n}}}
fn main(){assert_eq!(api::Limit::nowy(5).unwrap().get(),5);assert!(api::Limit::nowy(0).is_none());}
~~~

## B32-2

~~~rust
pub struct Klient{stan:std::sync::Arc<std::sync::Mutex<u32>>}
fn oczekiwane<T:Send+Sync>(){}
fn main(){oczekiwane::<Klient>();let k=Klient{stan:Default::default()};assert_eq!(*k.stan.lock().unwrap(),0);}
~~~
Zmiana pola na `Rc` spowodowałaby błąd asercji typu i ujawniła zmianę kontraktu.

## B32-3

Dodanie wariantu do wyczerpującego publicznego enumu jest zmianą łamiącą konsumentów. Dodanie prywatnego pola do struktury, która już miała prywatne pola, zwykle zachowuje konstrukcję, ale trzeba sprawdzić auto traits i rozmiar tam, gdzie layout jest obiecany. Nowy wymagany bound zawęża dopuszczalne programy i jest zmianą łamiącą. Zmiana serializowanego formatu może łamać dane mimo zachowanej kompilacji. Każdy przypadek oceniaj względem udokumentowanego kontraktu i przyjętej polityki wersjonowania.

