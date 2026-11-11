[← Spis treści](../../README.md)

# Rozwiązania: Strumienie i proces

## C02-1

Puste wejście daje pusty wynik i `0`. `b"x"` daje dokładnie `b"x"` i `1`. `b"x\n\n"` daje te same trzy bajty i `2`: drugi rekord jest pustym wierszem zakończonym newline. Funkcja nie dopisuje końca wiersza, nie interpretuje tekstu i nie liczy dodatkowego rekordu po ostatnim delimiterze.

## C02-2

~~~rust
use std::io::{self, Write};
struct Krotki(Vec<u8>);
impl Write for Krotki {
    fn write(&mut self, buf: &[u8]) -> io::Result<usize> {
        let n = buf.len().min(2);
        self.0.extend_from_slice(&buf[..n]);
        Ok(n)
    }
    fn flush(&mut self) -> io::Result<()> { Ok(()) }
}
fn main() -> io::Result<()> {
    let mut w = Krotki(Vec::new());
    w.write_all(b"abcde")?;
    assert_eq!(w.0, b"abcde");
    Ok(())
}
~~~

`write_all` ponawia wywołania z niewysłaną częścią bufora. Przy niepustym wejściu writer nie może stale zwracać `Ok(0)` i oczekiwać postępu: helper zgłosi `WriteZero`.

## C02-3

Uruchom dziecko przez `Command` z piped stdout i stderr, odbierz oba uchwyty i uruchom dwa czytające wątki. Każdy opróżnia własny potok, zapisując co najwyżej ustalony limit danych; nadmiar może dalej odczytywać i odrzucać, aby nie blokować dziecka. Rodzic cyklicznie sprawdza `try_wait` względem monotonicznego `Instant`. Po 5 sekundach wywołuje `kill`, następnie zawsze `wait`, zamyka stdin i dołącza wątki. Test porównuje status oraz osobne bufory, a informację o timeout traktuje jako porażkę.

Dla procesów tworzących własne dzieci samo `kill` może nie wystarczyć. Harness potrzebuje grupy procesów albo mechanizmu systemowego i limitów odziedziczonych deskryptorów. W przeciwnym razie wnuk nadal trzyma otwarty pipe i wątki czytające nie widzą EOF. Nie wystarczy użyć `sleep(5)` i porzucić handle dziecka.
