[← Spis treści](../README.md)

# Sieć i protokoły

Standard library zapewnia blokujące TCP i UDP. TLS, HTTP, DNS async,
retry middleware i rozbudowane kodeki należą do ekosystemu.

## TCP

TCP jest strumieniem bajtów, nie strumieniem wiadomości. Jeden `write_all` po
stronie nadawcy może wymagać wielu `read` po stronie odbiorcy i odwrotnie.

~~~no_run
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

## Powiązane tematy

- [Pliki, I/O i procesy](01_pliki_io_i_procesy.md)
- [Async i blokowanie](../11_async_rust/04_anulowanie_timeouty_i_blocking.md)
- [Layout i alignment](../21_unsafe_soundness_i_model_pamieci/03_layout_alignment_i_uninitialized_memory.md)
