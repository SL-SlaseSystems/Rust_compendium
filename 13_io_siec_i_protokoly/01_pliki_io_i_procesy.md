[← Spis treści](../README.md)
<!-- status: expanded -->

# Pliki, I/O i procesy

## Cele

Po tym rozdziale potrafisz:

- obsłużyć częściowe I/O i odróżnić flush od trwałości;
- kontrolować własność plików, buforów i procesów potomnych;


Standardowe I/O opiera się na traits `Read`, `Write`, `BufRead` i `Seek`.
Funkcje wygodne wczytują całość; API strumieniowe kontroluje pamięć.

## Pliki

~~~rust
use std::fs::{self, File};
use std::io::{BufRead, BufReader, Write};

fn main() -> std::io::Result<()> {
    let nazwa = format!("rust-kompendium-io-{}.txt", std::process::id());
    let sciezka = std::env::temp_dir().join(nazwa);
    {
        let mut plik = std::fs::OpenOptions::new()
            .write(true).create_new(true).open(&sciezka)?;
        writeln!(plik, "pierwsza")?;
        writeln!(plik, "druga")?;
        plik.flush()?;
    }
    let plik = File::open(&sciezka)?;
    let linie: Result<Vec<_>, _> = BufReader::new(plik).lines().collect();
    assert_eq!(linie?, ["pierwsza", "druga"]);
    fs::remove_file(sciezka)?;
    Ok(())
}
~~~

`lines` usuwa zakończenie linii i wymaga poprawnego UTF-8. Dla protokołów
binarnych używaj `read`/`read_exact` na bajtach.

## Częściowe operacje

`Read::read` może zwrócić mniej bajtów niż bufor nawet przed EOF. `Write::write`
może zapisać część. `read_exact` i `write_all` realizują pętlę, lecz mają
własne zachowanie przy błędzie. `Interrupted` bywa sygnałem do retry.

Nie utożsamiaj pojedynczego `read` z jedną wiadomością protokołu.

## Ścieżki

`Path` i `PathBuf` nie muszą być UTF-8. Nie zamieniaj każdej ścieżki na
`String`. Używaj `display` tylko do komunikatu dla człowieka; wynik może być
stratny. Łączenie przez `join` jest przenośniejsze niż konkatenacja separatora.

## Atomowy zapis

Typowy wzorzec konfiguracji to zapis do pliku tymczasowego w tym samym
filesystemie, `flush`/ewentualnie `sync_all`, a potem rename. Gwarancje rename,
trwałości katalogu i nadpisania zależą od platformy. Biblioteka nie oferuje
uniwersalnej transakcji filesystemu.

## Procesy

Przykład wymaga programu `rustc` w PATH i uruchomienia procesu systemowego; nie jest samodzielnym doctestem.

~~~text
use std::process::Command;

fn main() -> std::io::Result<()> {
    let wynik = Command::new("rustc").arg("--version").output()?;
    assert!(wynik.status.success());
    assert!(String::from_utf8_lossy(&wynik.stdout).contains("rustc"));
    Ok(())
}
~~~

`Command` nie uruchamia powłoki domyślnie, co ogranicza injection. Nie buduj
jednego łańcucha komendy z wejścia użytkownika. Przy `stdin/stdout(Stdio::piped())`
czytaj i zapisuj równolegle, aby nie zakleszczyć się na pełnych pipe’ach.

## Środowisko i kody wyjścia

`std::env::var_os` zachowuje nie-UTF-8. `ExitStatus` może nie mieć zwykłego
kodu, np. gdy proces zakończył sygnał. Proces potomny trzeba `wait`, inaczej
na części systemów pozostaje zombie.


## Model — operacja systemowa ma częściowy wynik

`read` zwraca liczbę rzeczywiście zapisanych bajtów i może dać krótki odczyt. `Ok(0)` dla niepustego bufora zwykle oznacza aktualny koniec źródła, ale plik może później urosnąć; dla pustego bufora zero nie dowodzi EOF. `read_exact` próbuje wypełnić bufor i zgłasza `UnexpectedEof`, gdy to się nie uda. Po błędzie nie należy zgadywać, które fragmenty bufora są znaczące poza udokumentowanym kontraktem metody.

~~~rust
use std::io::{self, Cursor, Read, Write};
fn ramka<R: Read>(mut r: R) -> io::Result<Vec<u8>> {
    let mut naglowek = [0; 2];
    r.read_exact(&mut naglowek)?;
    let n = usize::from(u16::from_be_bytes(naglowek));
    if n > 1024 { return Err(io::Error::new(io::ErrorKind::InvalidData, "ramka za duża")); }
    let mut dane = vec![0; n];
    r.read_exact(&mut dane)?;
    Ok(dane)
}
fn main() -> io::Result<()> {
    let mut zapis = Vec::new();
    zapis.write_all(&3_u16.to_be_bytes())?;
    zapis.write_all(b"abc")?;
    assert_eq!(ramka(Cursor::new(zapis))?, b"abc");
    assert!(ramka(Cursor::new([0, 3, b'a'])).is_err());
    Ok(())
}
~~~

Parser jest niezależny od pliku i socketu, więc można testować go w pamięci. Limit sprawdzany jest przed alokacją. Zwrócenie błędu w połowie nie przywraca pozycji czytnika: wywołujący musi zdecydować, czy zamyka źródło, czy ma protokół resynchronizacji. To konsekwencja częściowego postępu, również w kodzie całkowicie synchronicznym.

`BufReader` i `BufWriter` amortyzują małe operacje. Bufor odczytu może pobrać więcej niż aktualnie zażądano; nie odrzucaj go i nie kontynuuj bezrefleksyjnie bezpośrednio z wewnętrznego źródła, bo stracisz już pobrane bajty. Drop `BufWriter` próbuje sprzątać, lecz błędów zapisu nie zwróci jak zwykły `Result`. Ważny zapis zakończ jawnym `flush` lub odpowiednim zakończeniem wrappera.

`flush` przenosi dane z warstwy buforującej zgodnie z jej kontraktem, a nie obiecuje fizycznego zapisu na trwałym nośniku. `File::sync_all` prosi system o synchronizację pliku, lecz trwałość rename i wpisu katalogowego wymaga rozumowania zależnego od systemu plików. Atomowa widoczność nowej treści oraz przetrwanie utraty zasilania to różne właściwości.

Proces potomny nie ma automatycznego `wait` w Drop uchwytu `Child`. Po utracie uchwytu może nadal działać, a po zakończeniu pozostawić zasoby wymagające zebrania. Pełny stdout lub stderr pipe może zatrzymać dziecko, gdy rodzic czeka zamiast czytać. `output` zbiera dane do pamięci, więc nadaje się do ograniczonego wyniku, a nie dowolnie gadatliwego procesu. Standardowe `Command` nie uruchamia powłoki, ale argumenty nadal mogą mieć specjalne znaczenie dla samego programu, na przykład wskazywać opcje.

## `fill_buf` i `consume`: pożyczony fragment bufora

`BufRead::fill_buf` zwraca widok na aktualnie dostępne bajty czytnika, a pusty widok oznacza EOF przy poprawnym wyniku. Nie zakładaj, że fragment zawiera cały rekord. Najpierw analizuj widok, zakończ jego użycie, następnie wywołaj `consume` z liczbą faktycznie wykorzystanych bajtów. Nie konsumuj więcej, niż zwrócono. Jeśli rekord przekracza granicę bufora, przechowaj ograniczony stan parsera lub kopiuj potrzebny fragment; nie zachowuj referencji do bufora po następnym mutowalnym odczycie.

~~~rust
use std::io::{self, BufRead, Cursor};
fn main() -> io::Result<()> {
    let mut reader = Cursor::new(b"abc\nrest".to_vec());
    let zuzyto = {
        let fragment = reader.fill_buf()?;
        let koniec = fragment.iter().position(|&b| b == b'\n').unwrap();
        assert_eq!(&fragment[..koniec], b"abc");
        koniec + 1
    };
    reader.consume(zuzyto);
    assert_eq!(reader.fill_buf()?, b"rest");
    Ok(())
}
~~~

`Cursor` udostępnia w teście całe wejście; `BufReader` może oddać krótszą porcję. `unwrap` opiera się tutaj na znanym fixture, nie na założeniu o dowolnym strumieniu. Produkcyjny parser musi obsłużyć brak separatora, limit rekordu, częściowe UTF-8 i zakończenie danych. To oszczędza dodatkowe kopiowanie podczas analizy dostępnej porcji, ale nie gwarantuje braku wszystkich kopii w całym systemie. Kontrakt: [BufRead](https://doc.rust-lang.org/std/io/trait.BufRead.html).

## Scatter/gather i częściowy postęp

`read_vectored` przyjmuje `IoSliceMut`, a `write_vectored` — `IoSlice`. Wynik jest liczbą bajtów przetworzonych łącznie, w kolejności segmentów; może kończyć się w środku dowolnego z nich. Nagłówek i payload nie muszą zostać obsłużone w jednym wywołaniu. Domyślna implementacja może użyć tylko pierwszego niepustego bufora, a zoptymalizowana nie obiecuje jednego syscall na każdej platformie.

~~~rust
use std::io::{self, IoSlice, IoSliceMut, Read, Write};
fn main() -> io::Result<()> {
    let mut input = &b"ABCD"[..];
    let mut header = [0_u8; 2];
    let mut body = [0_u8; 2];
    let n = input.read_vectored(&mut [
        IoSliceMut::new(&mut header), IoSliceMut::new(&mut body)
    ])?;
    assert_eq!(n, 4); // kontrakt konkretnego czytnika slice w tym teście
    assert_eq!((&header, &body), (b"AB", b"CD"));
    let mut output = Vec::new();
    let zapisano = output.write_vectored(&[
        IoSlice::new(&header), IoSlice::new(&body)
    ])?;
    assert_eq!(zapisano, 4); // Vec zapisuje tu całość
    assert_eq!(output, b"ABCD");
    Ok(())
}
~~~

Dla ogólnego writer/reader prowadź pozycję segmentu i offset w nim. Po częściowym sukcesie przesuń je o zwróconą liczbę bajtów; po `Interrupted` ponów pozostałą pracę, a brak postępu przy niepustym zapisie obsłuż jako `WriteZero`. Jeśli nie potrzebujesz jednej operacji wektorowej, `write_all` kolejno dla segmentów ma prostszy kontrakt niż błędna pętla ponawiająca całe nagłówki. Odczyt niezerowej długości zwracający zero oznacza koniec, który trzeba odróżnić od kompletnej wiadomości. Kontrakty: [Read](https://doc.rust-lang.org/std/io/trait.Read.html) i [Write](https://doc.rust-lang.org/std/io/trait.Write.html).

## Diagnostyka kompilatora

Błąd przeniesienia `File` po przekazaniu go do `BufReader::new` oznacza transfer własności. Użyj jednego właściciela bufora i pożyczek z jasno określonym zakresem. Błąd braku metody `read_exact` lub `write_all` często wynika z braku importu traitu. `io::ErrorKind` jest kontraktem lepszym od porównywania tekstu systemowego; nie zakładaj jednak identycznego błędu platformowego dla każdego scenariusza timeoutu lub uprawnień.

## Praktyka produkcyjna

Używaj unikalnych plików tworzonych atomowo, a nie stałej nazwy w katalogu tymczasowym współdzielonej przez testy. Ogranicz wejście, rozmiar linii i wynik procesu. Waliduj konfigurację przed zastąpieniem pliku, jawnie obsługuj błędy końcowego zapisu i oddziel gwarancje trwałości od widoczności. Dla procesów określ timeout, zamknięcie stdin, odbiór obu wyjść, ewentualne kill oraz wait. Test parsera w pamięci nie dowodzi przenośności ścieżek ani zachowania systemu plików.

## Sprawdź, czy rozumiesz

- Czy `read` zwracające zero dla pustego bufora dowodzi EOF?
- Dlaczego flush nie jest obietnicą trwałości po utracie zasilania?
- Co może się stać po upuszczeniu Child bez wait?

## Ćwiczenia

- `B28-1` — podstawowe: Odczytaj dwubajtowy nagłówek i wykryj ucięte wejście przez read_exact. [Rozwiązanie](../rozwiazania/13_io_siec_i_protokoly/01_pliki_io_i_procesy.md#b28-1).
- `B28-2` — praktyczne: Zapisz i odczytaj ramkę z limitem 1024 bajtów bez systemu plików. [Rozwiązanie](../rozwiazania/13_io_siec_i_protokoly/01_pliki_io_i_procesy.md#b28-2).
- `B28-3` — pogłębione: Rozpisz lifecycle procesu z piped stdout/stderr i ograniczeniem rozmiaru wyniku. [Rozwiązanie](../rozwiazania/13_io_siec_i_protokoly/01_pliki_io_i_procesy.md#b28-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [Read: częściowe odczyty](https://doc.rust-lang.org/std/io/trait.Read.html)
- [Write i flush](https://doc.rust-lang.org/std/io/trait.Write.html)
- [Child: brak automatycznego wait](https://doc.rust-lang.org/std/process/struct.Child.html)

## Powiązane tematy

- [`String`, `str` i Unicode](../06_kolekcje_iteratory_i_closures/02_string_str_i_unicode.md)
- [Sieć i protokoły](02_siec_i_protokoly.md)
- [Własne błędy](../07_obsluga_bledow/04_wlasne_bledy_i_api.md)
