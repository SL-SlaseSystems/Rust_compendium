[← Spis treści](../../README.md)

# Rozwiązania: Pliki, I/O i procesy

[Rozdział źródłowy](../../13_io_siec_i_protokoly/01_pliki_io_i_procesy.md).

## B28-1

~~~rust
use std::io::Read;
fn main(){let mut wejscie=&[1_u8][..];let mut h=[0;2];assert_eq!(wejscie.read_exact(&mut h).unwrap_err().kind(),std::io::ErrorKind::UnexpectedEof);}
~~~

## B28-2

~~~rust
use std::io::{self,Read,Write};
fn main()->io::Result<()>{let dane=b"rust";let mut wire=Vec::new();wire.write_all(&(dane.len()as u16).to_be_bytes())?;wire.write_all(dane)?;
 let mut r=&wire[..];let mut h=[0;2];r.read_exact(&mut h)?;let n=u16::from_be_bytes(h)as usize;if n>1024{return Err(io::ErrorKind::InvalidData.into())}let mut v=vec![0;n];r.read_exact(&mut v)?;assert_eq!(v,dane);Ok(())}
~~~

## B28-3

Rodzic tworzy proces z jawnymi argumentami i piped wyjściami. Dwa czytniki równolegle opróżniają stdout i stderr, licząc bajty oraz raportując przekroczenie limitu; nie przerywają bez planu, który pozwoli dziecku dalej pisać. Rodzic zamyka stdin po wysłaniu wejścia, obserwuje deadline i przy jego przekroczeniu uruchamia uzgodnione zakończenie lub kill. Następnie zawsze wykonuje wait i dołącza czytniki. Limit pamięci wymaga strumieniowego zbierania lub obcięcia danych, a nie samego `Command::output`.

