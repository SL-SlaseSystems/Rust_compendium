[← Spis treści](../../README.md)

# Rozwiązania: Architektura aplikacji i dependency injection

[Rozdział źródłowy](../../14_idiomy_wzorce_i_architektura/04_architektura_aplikacji_i_di.md).

## B33-1

~~~rust
#[derive(Debug,PartialEq)]enum Blad{Awaria}
trait Repo{fn istnieje(&self,id:u64)->Result<bool,Blad>;}
struct Fake;
impl Repo for Fake{fn istnieje(&self,id:u64)->Result<bool,Blad>{if id==0{Err(Blad::Awaria)}else{Ok(id==7)}}}
fn main(){assert_eq!(Fake.istnieje(7),Ok(true));assert_eq!(Fake.istnieje(8),Ok(false));assert_eq!(Fake.istnieje(0),Err(Blad::Awaria));}
~~~

## B33-2

~~~rust
trait Zegar{fn teraz(&self)->u64;}
struct Staly(u64);impl Zegar for Staly{fn teraz(&self)->u64{self.0}}
fn wygaslo(z:&impl Zegar,deadline:u64)->bool{z.teraz()>=deadline}
fn main(){assert!(!wygaslo(&Staly(9),10));assert!(wygaslo(&Staly(10),10));}
~~~
Zegar produkcyjny musi mieć kontrakt odpowiedni dla deadline; czasu ściennego nie utożsamiaj z monotonicznym.

## B33-3

Przypadek użycia zapisuje identyfikator zakupu i rezerwację w trwałym stanie, po czym wywołuje płatność z kluczem idempotencji. Po timeout oznacza wynik jako nieznany i zleca uzgodnienie temu samemu właścicielowi workflow. Nie zwalnia bezwarunkowo rezerwacji, jeżeli płatność mogła się powieść. Po potwierdzeniu sukcesu zatwierdza zakup, po potwierdzonym odrzuceniu zwalnia rezerwację. Oddzielne transakcje zewnętrznych systemów wymagają automatu i kompensacji; trait DI nie tworzy rozproszonej transakcji. Testy obejmują utraconą odpowiedź, duplikat i restart między etapami.

