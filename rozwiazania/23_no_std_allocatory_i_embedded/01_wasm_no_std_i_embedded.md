[← Spis treści](../../README.md)

# Rozwiązania: Środowiska no_std

## C18-1

`Option`, slices, podstawowe traity i logika parsera należą do `core`. `Vec` wymaga `alloc` oraz dostępnej alokacji. `TcpStream` pochodzi ze `std` i wymaga wsparcia platformy. Samo posiadanie crate’a `std` na target Wasm nie gwarantuje działania każdej usługi OS; host i target określają faktyczne możliwości. Parser może działać na hoście, bare metal i Wasm, jeśli nie wciąga platformowych zależności przez features.

## C18-2

Dla pustego wejścia wynik to `Ok(0)`, a bufor pozostaje bez zmian. Dla `[1,2]` potrzebne są cztery bajty; przy buforze długości 3 funkcja zwraca `ZaMaloMiejsca` przed pętlą. Szkic testów wymaga dołączenia funkcji z rozdziału:

~~~text
let mut pusty_bufor = [9; 3];
assert_eq!(koduj_u16(&[], &mut pusty_bufor), Ok(0));
assert_eq!(pusty_bufor, [9; 3]);
let mut krotki = [9; 3];
assert_eq!(koduj_u16(&[1, 2], &mut krotki), Err(Blad::ZaMaloMiejsca));
assert_eq!(krotki, [9; 3]);
~~~

Ten kontrakt atomowości dotyczy błędu walidacji rozmiaru w pokazanej funkcji. Nie wolno przenosić go automatycznie na writer sieciowy, który może wysłać prefix przed błędem.

## C18-3

Rdzeń dekoduje rejestry czujnika, sprawdza flagi i skaluje surowe liczby. Trait transportu opisuje konkretną operację odczytu/zapisu z błędem, bez adresów MMIO i globalnego stanu. Adapter HAL implementuje ten trait przy użyciu właściwego I2C/SPI oraz ustawia piny, zegary i opóźnienia na wybranym układzie. Sterownik posiada uchwyt transportu albo pożycza go na wyraźny czas.

Na hoście mock sprawdza sekwencję komend, endian, wartości graniczne i propagację błędu. Na sprzęcie sprawdź timing, częstotliwość magistrali, reset, odłączenie czujnika, timeout i konkurencję z innymi peryferiami. Emulator może wesprzeć test startu, ale nie zastąpi sprawdzenia zachowania elektrycznego oraz DMA/cache. Osobno kompiluj rdzeń bez domyślnych features, aby testy hostowe nie ukryły przypadkowej zależności od std.
