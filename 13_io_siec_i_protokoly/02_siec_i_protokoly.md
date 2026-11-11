[← Spis treści](../README.md)
<!-- status: expanded -->

# Sieć i protokoły

## Cele

Po tym rozdziale potrafisz:

- zaprojektować framing, limity i częściowy stan parsera;
- odróżnić zakończenie transportu od wyniku operacji biznesowej;


Standard library zapewnia blokujące TCP i UDP. TLS, HTTP, DNS async,
retry middleware i rozbudowane kodeki należą do ekosystemu.

## TCP

TCP jest strumieniem bajtów, nie strumieniem wiadomości. Jeden `write_all` po
stronie nadawcy może wymagać wielu `read` po stronie odbiorcy i odwrotnie.

Przykład wymaga możliwości otwarcia lokalnego socketu TCP i obsługi wątków; jest szkicem integracji środowiskowej, nie testem wykonywanym przez rustdoc.

~~~text
use std::io::{Read, Write};
use std::net::TcpListener;
use std::thread;

fn main() -> std::io::Result<()> {
    let listener = TcpListener::bind("127.0.0.1:0")?;
    let adres = listener.local_addr()?;

    let serwer = thread::spawn(move || -> std::io::Result<()> {
        let (mut stream, _) = listener.accept()?;
        let mut buf = [0_u8; 4];
        stream.read_exact(&mut buf)?;
        stream.write_all(&buf)?;
        Ok(())
    });

    let mut klient = std::net::TcpStream::connect(adres)?;
    klient.write_all(b"rust")?;
    let mut odpowiedz = [0_u8; 4];
    klient.read_exact(&mut odpowiedz)?;
    assert_eq!(&odpowiedz, b"rust");
    serwer.join().unwrap()?;
    Ok(())
}
~~~

Prawdziwy protokół wymaga framingu: stałej długości, delimitera z escaping,
prefiksu długości lub formatu samoopisującego. Zawsze ogranicz maksymalny
rozmiar ramki.

## UDP

UDP zachowuje granice datagramów, ale może gubić, duplikować i zmieniać
kolejność pakietów. Datagram większy niż bufor może zostać obcięty zależnie od
API. Jeżeli potrzebujesz niezawodności, kontroli przeciążenia i sesji, użyj
odpowiedniego protokołu zamiast odtwarzać TCP bez pełnego projektu.

## Adresy i DNS

`ToSocketAddrs` może rozwiązywać nazwę blokująco i zwrócić wiele adresów.
Klient powinien obsłużyć IPv4/IPv6 oraz próbować adresy według strategii z
deadline. Nie loguj tokenów z URL ani nagłówków.

## Timeouty i retry

Sockety blokujące mają `set_read_timeout` i `set_write_timeout`, ale szczegóły
błędów różnią się systemowo. Retry jest bezpieczny tylko dla operacji
idempotentnej lub wyposażonej w klucz idempotency. Używaj exponential backoff
z jitter i wspólnego deadline.

## Endianness

Sieciowy porządek bajtów jest zwykle big-endian. Konwertuj jawnie:

~~~rust
fn main() {
    let n = 0x1234_u16;
    assert_eq!(n.to_be_bytes(), [0x12, 0x34]);
    assert_eq!(u16::from_be_bytes([0x12, 0x34]), n);
}
~~~

Nie przesyłaj surowego layoutu struktury Rust jako protokołu. Padding,
endianness, wersjonowanie i ABI nie są kontraktem sieciowym.

## TLS i HTTP

Rustls, native-tls, hyper, reqwest, tonic i frameworki są **third-party**.
Wybór wymaga aktualnej oceny wersji, backendu kryptograficznego, root store,
HTTP/2/3, proxy i polityki certyfikatów.


## Model — transport przenosi bajty, protokół nadaje znaczenie

Granice `read` zależą od dostępności danych i bufora, nie od wywołań nadawcy. Parser powinien obsłużyć nagłówek podzielony na kilka odczytów i kilka ramek w jednym odczycie. Prefix długości upraszcza framing, ale otwiera wektor przeciążenia pamięci: długość trzeba sprawdzić przed alokacją i arytmetyką rozmiaru. Zarezerwowanie ogromnego bufora na żądanie niezaufanego klienta nie staje się bezpieczne dzięki samemu `u32`.

~~~rust
#[derive(Debug, PartialEq)]
enum Blad { ZaDuza }
fn pierwsza(dane: &[u8]) -> Result<Option<(&[u8], &[u8])>, Blad> {
    if dane.len() < 2 { return Ok(None); }
    let n = usize::from(u16::from_be_bytes([dane[0], dane[1]]));
    if n > 1024 { return Err(Blad::ZaDuza); }
    if dane.len() - 2 < n { return Ok(None); }
    Ok(Some((&dane[2..2+n], &dane[2+n..])))
}
fn main() {
    assert_eq!(pierwsza(&[0]), Ok(None));
    assert_eq!(pierwsza(&[0, 2, b'a']), Ok(None));
    assert_eq!(pierwsza(&[0, 2, b'a', b'b', 9]), Ok(Some((&b"ab"[..], &b"\x09"[..]))));
    assert_eq!(pierwsza(&[4, 1]), Err(Blad::ZaDuza));
}
~~~

`None` oznacza niekompletną ramkę, nie koniec połączenia. Sukces oddaje payload i resztę, więc kolejne wiadomości nie giną. Bufor wejściowy musi mieć właściciela utrzymującego go między odczytami. Przy EOF z niepustą niekompletną ramką protokół powinien zgłosić ucięcie, a nie udawać poprawny koniec.

Deadline powinien obejmować DNS, próby różnych adresów, połączenie i wymianę danych. Timeout pojedynczego odczytu nie ogranicza automatycznie całej sesji, jeśli klient regularnie przysyła pojedynczy bajt. Ogranicz czas nagłówka, rozmiar bufora i całkowity budżet operacji. Dla usług o wielu klientach limit liczby połączeń i aktywnych żądań jest tak samo ważny jak limit ramki.

Zerwanie TCP nie rozstrzyga, czy serwer zatwierdził ostatnie żądanie. Jeśli klient wysłał polecenie, lecz nie otrzymał odpowiedzi, wynik może być nieznany. Retry tworzącego zasób żądania wymaga idempotency key albo sprawdzenia stanu, a nie tylko reconnect. Numer żądania, wersja protokołu i jednoznaczne klasy błędów ułatwiają bezpieczne uzgodnienie.

UDP zachowuje datagramy, ale duży datagram może przekroczyć MTU i podlegać fragmentacji sieciowej. Własna niezawodność wymaga również kontroli przeciążenia, okien, retransmisji i ochrony przed duplikatami. Jeśli te wymagania dominują, wybierz istniejący protokół zamiast ad hoc dodawanej flagi ACK. TLS chroni transport według własnego kontraktu, lecz nie waliduje schematu wiadomości ani reguł uprawnień aplikacji.

## Diagnostyka kompilatora

Błąd borrow checkera przy zwróceniu wycinka lokalnego bufora wskazuje zły czas życia danych; parser może zwrócić wycinek wejścia albo posiadany payload. `UnexpectedEof` przy `read_exact` oznacza brak wymaganych bajtów, nie zwykły timeout. Błędy sieciowe są platformowo zależne; klasyfikuj udokumentowane kategorie i zachowuj źródło. Brak błędu kompilacji nie wykryje parsera zakładającego „jeden read = jedna wiadomość”.

## Praktyka produkcyjna

Testuj każdą granicę podziału ramki, wiele ramek razem, ucięcie, puste ramki i długość ponad limit. Osobno sprawdzaj transport w kontrolowanym środowisku, z deadline i cleanup. Dobierając TLS/HTTP **third-party**, weryfikuj aktualną dokumentację konkretnej wersji i konfiguracji certyfikatów. Nie wyłączaj walidacji certyfikatów jako rozwiązania błędu połączenia. Zapisuj metryki czasu kolejki, DNS, connect i odpowiedzi, bez sekretów z nagłówków lub payloadu.

## Sprawdź, czy rozumiesz

- Dlaczego niekompletna ramka i EOF to różne stany?
- Jak klient wysyłający bajt co chwilę może ominąć timeout odczytu?
- Dlaczego utrata TCP nie uzasadnia automatycznej ponownej płatności?

## Ćwiczenia

- `B29-1` — podstawowe: Zamień liczbę u16 na big-endian i z powrotem. [Rozwiązanie](../rozwiazania/13_io_siec_i_protokoly/02_siec_i_protokoly.md#b29-1).
- `B29-2` — praktyczne: Zaimplementuj parser prefiksowanej ramki zwracający resztę bufora. [Rozwiązanie](../rozwiazania/13_io_siec_i_protokoly/02_siec_i_protokoly.md#b29-2).
- `B29-3` — pogłębione: Zaprojektuj testy wszystkich podziałów ramki i protokół retry przy nieznanym wyniku. [Rozwiązanie](../rozwiazania/13_io_siec_i_protokoly/02_siec_i_protokoly.md#b29-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [TcpStream: kontrakty transportu](https://doc.rust-lang.org/std/net/struct.TcpStream.html)
- [UdpSocket: datagramy](https://doc.rust-lang.org/std/net/struct.UdpSocket.html)

## Powiązane tematy

- [Pliki, I/O i procesy](01_pliki_io_i_procesy.md)
- [Async i blokowanie](../11_async_rust/04_anulowanie_timeouty_i_blocking.md)
- [Layout i alignment](../21_unsafe_soundness_i_model_pamieci/03_layout_alignment_i_uninitialized_memory.md)
