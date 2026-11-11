[← Spis treści](../../README.md)

# Rozwiązania: Zaawansowane makra proceduralne

[Rozdział źródłowy](../../12_makra/04_zaawansowane_makra_proceduralne.md).

## B27-1

~~~rust
trait Liczba{fn n()->usize;}
struct Bufor<'a,const N:usize>(&'a [u8;N]);
impl<'a,const N:usize>Liczba for Bufor<'a,N>{fn n()->usize{N}}
fn main(){assert_eq!(Bufor::<4>::n(),4);let b=Bufor(b"rust");assert_eq!(b.0.len(),4);}
~~~

## B27-2

Parser ma akceptować `rename = "nazwa"` raz albo `skip` raz. Drugie `rename`, drugie `skip`, nieznany klucz i jednoczesne `rename`/`skip` są błędami. Walidacja najpierw gromadzi opcje z ich spans, potem sprawdza konflikty, a dopiero na końcu tworzy model emisji. Przy trzech niezależnych błędach zwraca trzy komunikaty skojarzone z właściwymi tokenami. Generator nie powinien otrzymać modelu zawierającego sprzeczne opcje; to zmniejsza liczbę jego ścieżek.

## B27-3

Pozytywny fixture używa typu `Marker<T>` z polem `PhantomData<T>` i parametrem bez generowanego traitu; sukces dowodzi braku zbędnego boundu w tym przypadku. Drugi używa lifetime, const generic i istniejącego `where`. Trzeci konsument zmienia nazwę runtime’u w Cargo i przekazuje tę ścieżkę atrybutem. Negatywne fixtures sprawdzają nieznany klucz, duplikat i sprzeczność. Runtime testuje rzeczywiste zachowanie wygenerowanej implementacji. Żaden pojedynczy snapshot nie zastępuje tego zestawu.

