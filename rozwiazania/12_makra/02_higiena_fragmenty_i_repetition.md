[← Spis treści](../../README.md)

# Rozwiązania: Higiena, fragmenty i repetition

[Rozdział źródłowy](../../12_makra/02_higiena_fragmenty_i_repetition.md).

## B25-1

~~~rust
macro_rules! przypisz{($($n:ident=>$v:expr),* $(,)?)=>{$(let $n=$v;)*};}
fn main(){przypisz!(x=>2,y=>3,);assert_eq!(x*y,6);}
~~~

## B25-2

~~~rust
macro_rules! oblicz{($x:expr)=>{{let wynik=$x;wynik+1}};}
fn main(){let wynik=10;assert_eq!(oblicz!(2),3);assert_eq!(wynik,10);}
~~~
Binding wewnętrzny nie nadpisuje lokalnego bindingu wywołującego.

## B25-3

~~~rust
macro_rules! nowa{($e:expr)=>{"ogólne"};(const $e:expr)=>{"const"};}
macro_rules! zgodna{($e:expr_2021)=>{"ogólne"};(const $e:expr)=>{"const"};}
fn main(){assert_eq!(nowa!(const{2}),"ogólne");assert_eq!(zgodna!(const{2}),"const");}
~~~
W Edition 2024 pierwsze makro dopasuje ogólne ramię, a zgodnościowe zachowa specjalne. Zmiana może być istotna semantycznie, nawet jeśli obie ekspansje kompilują się poprawnie.

