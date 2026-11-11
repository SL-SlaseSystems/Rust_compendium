[← Spis treści](../../README.md)

# Rozwiązania: Sieć i protokoły

[Rozdział źródłowy](../../13_io_siec_i_protokoly/02_siec_i_protokoly.md).

## B29-1

~~~rust
fn main(){let n=258_u16;assert_eq!(n.to_be_bytes(),[1,2]);assert_eq!(u16::from_be_bytes([1,2]),n);}
~~~

## B29-2

~~~rust
fn ramka(b:&[u8])->Option<(&[u8],&[u8])>{let h=b.get(..2)?;let n=u16::from_be_bytes([h[0],h[1]])as usize;if n>1024{return None}Some((b.get(2..2+n)?,b.get(2+n..)?))}
fn main(){assert_eq!(ramka(&[0,1,7,9]),Some((&[7][..],&[9][..])));assert!(ramka(&[0,2,7]).is_none());}
~~~
Wersja uproszczona łączy brak pełnej ramki i przekroczony limit. Publiczny parser powinien rozdzielić je przez `Result<Option<_>, _>`, jak w rozdziale.

## B29-3

Dla wire `[0,3,a,b,c]` sprawdź podziały po 0, 1, 2, 3, 4 i 5 bajtach. Po pierwszym fragmencie wynik ma być niekompletny, chyba że zawiera już całość; po dołączeniu drugiego payload ma wynosić `abc`. Dla dwóch ramek parser zwraca pierwszą oraz dokładną resztę. Dla retry nadaj trwały identyfikator operacji przed wysłaniem; serwer deduplikuje go i umożliwia odczyt wyniku. Po timeout klient pyta o ten sam identyfikator, a nie tworzy nowe żądanie. Osobny test sprawdza deduplikację po utracie odpowiedzi.

