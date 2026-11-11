[← Spis treści](../../README.md)

# Rozwiązania: `macro_rules!`

[Rozdział źródłowy](../../12_makra/01_macro_rules.md).

## B24-1

~~~rust
macro_rules! para{($a:expr,$b:expr $(,)?)=>{($a,$b)};}
fn main(){assert_eq!(para!(1,2,), (1,2));}
~~~

## B24-2

~~~rust
macro_rules! para{($a:expr,$b:expr)=>{{let a=$a;let b=$b;(a,b)}};}
fn main(){let mut log=Vec::new();let p=para!({log.push(1);3},{log.push(2);4});assert_eq!(p,(3,4));assert_eq!(log,[1,2]);}
~~~

## B24-3

~~~compile_fail
macro_rules! para{($a:expr,$b:expr)=>{($a,$b)};($($inne:tt)*)=>{compile_error!("użyj para!(lewy, prawy)")};}
fn main(){let _=para!(1);}
~~~
Poprawne ramię jest pierwsze, a rezerwowe odrzuca błędną składnię. Dla zawsze dokładnie dwóch argumentów funkcja `fn para<A,B>(a:A,b:B)->(A,B)` daje ten sam kontrakt typów bez kosztów utrzymania parsera; makro uzasadnia dopiero potrzeba specjalnej składni.

