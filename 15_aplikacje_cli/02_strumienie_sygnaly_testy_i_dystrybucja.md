[← Spis treści](../README.md)
<!-- status: expanded -->

# Strumienie, sygnały, testy procesu i dystrybucja

## Cele

Po tym rozdziale potrafisz:

- napisać silnik strumieniowy niezależny od rzeczywistego terminala;
- określić zachowanie przy częściowym zapisie, przerwanym potoku i anulowaniu;
- zaplanować test procesu oraz wydanie binarium dla konkretnego targetu.

## Model — Własność strumieni i kontrakt potoku

Standardowe wejście (stdin), wyjście (stdout) i kanał diagnostyczny (stderr) są zasobami procesu. Przyjmij prostą zasadę: stdout zawiera wynik, stderr postęp i błędy. Skrypt może wtedy przekierować sam wynik do pliku. Nie łącz obu kanałów w testach, jeżeli chcesz sprawdzać ich kontrakt. Kolejność komunikatów między dwoma niezależnymi strumieniami nie musi być identyczna z kolejnością ich późniejszego odczytania.

Silnik przyjmujący `Read`/`BufRead` oraz `Write` można sprawdzić na buforze w pamięci. Adapter procesu blokuje stdin i stdout raz, przekazuje ich pożyczki do silnika i mapuje końcowy błąd. Buforowanie ogranicza liczbę wywołań systemowych, lecz zwiększa opóźnienie widoczności wyniku. Dla narzędzia interaktywnego jawne `flush()` po prompt jest częścią poprawności; dla eksportu milionów rekordów flush po każdym wierszu może zdominować koszt.

~~~rust
use std::io::{self, BufRead, Write};
fn kopiuj<R: BufRead, W: Write>(mut wejscie: R, mut wyjscie: W)
    -> io::Result<usize>
{
    let mut linia = Vec::new();
    let mut liczba = 0;
    loop {
        linia.clear();
        if wejscie.read_until(b'\n', &mut linia)? == 0 { break; }
        wyjscie.write_all(&linia)?;
        liczba += 1;
    }
    wyjscie.flush()?;
    Ok(liczba)
}
fn main() -> io::Result<()> {
    let mut wynik = Vec::new();
    assert_eq!(kopiuj(&b"a\nb"[..], &mut wynik)?, 2);
    assert_eq!(wynik, b"a\nb");
    Ok(())
}
~~~

Ostatni rekord nie wymaga końcowego znaku nowej linii. Bufor bajtowy zachowuje wejście niebędące UTF-8, co jest dobrym kontraktem kopiarki. Parser tekstowy może zamiast tego wymagać UTF-8 i zwracać błąd z pozycją. `write_all` obsługuje krótkie zapisy; pojedyncze `write` nie gwarantuje wysłania całego rekordu. Zwrócona liczba oznacza rekordy przekazane writerowi, a dopiero poprawny flush potwierdza brak zgłoszonego błędu tego bufora. Nie stanowi to obietnicy trwałości danych na fizycznym dysku.

Przykład ma świadome ograniczenie: `read_until` może powiększać wektor aż do końca olbrzymiego wiersza. W narzędziu dla niezaufanego wejścia użyj przetwarzania fragmentami, `fill_buf`/`consume` lub ograniczonego odczytu z kontrolą przekroczenia. Sama pojemność początkowa wektora nie jest limitem pamięci.

## Przerwany potok i sygnały

Odbiorca taki jak `head` może zamknąć potok po odczytaniu kilku rekordów. Piszący proces może zobaczyć `ErrorKind::BrokenPipe`; szczegóły sygnałów zależą od platformy i konfiguracji procesu. Ustal, czy taki przypadek uznajesz za oczekiwane zakończenie, czy błąd. Nie ignoruj wszystkich błędów zapisu tylko po to, aby uciszyć tę jedną sytuację. Brak miejsca na dysku powinien nadal dać status niepowodzenia. Kontrakty `Write` i buforowania sprawdzono 2026-11-11 w [dokumentacji Write](https://doc.rust-lang.org/std/io/trait.Write.html) oraz [BufWriter](https://doc.rust-lang.org/std/io/struct.BufWriter.html).

Obsługa Ctrl-C wymaga adaptera platformowego albo crate’a **third-party**. Handler surowego sygnału POSIX nie może dowolnie alokować, logować i brać mutexów. Biblioteka może przekazać zdarzenie do normalnego wątku; dopiero tam uruchom kontrolowane zamykanie. Wzorzec to flaga zatrzymania, sprawdzana między rekordami, oraz termin końcowy. Flaga nie przerwie automatycznie blokującego odczytu: potrzebujesz rozwiązania dostosowanego do źródła I/O.

Przy zapisie raportu wybierz politykę publikacji: tymczasowy plik i końcowa podmiana albo udokumentowane częściowe dane. Szczegóły atomowości podmiany oraz trwałości po awarii zależą od systemu plików. Anulowanie usuwa plik roboczy przez strażnika RAII, lecz nie cofa danych wysłanych do potoku ani efektów zewnętrznego API.

## Diagnostyka kompilatora

Writer pożyczony mutowalnie nie może być odczytywany, kiedy aktywnie korzysta z niego długotrwały adapter. Zakończ zakres `BufWriter<&mut Vec<u8>>`, zanim obejrzysz wektor, i sprawdź wynik jawnego `flush`. Destructor bufora nie zapewnia kanału do zgłoszenia błędu. Z kolei `lines()` wymaga importu traitu `BufRead`; komunikat o brakującej metodzie często wskazuje właśnie brak traitu w zakresie, a nie nieodpowiedni typ pliku.

## Praktyka produkcyjna

Test jednostkowy silnika powinien obejmować puste wejście, brak końcowego newline, błędne kodowanie według przyjętego kontraktu i writer wykonujący krótkie zapisy. Test end-to-end uruchamia gotowe binarium, ustawia argumenty i środowisko potomka, podaje stdin, a następnie osobno porównuje stdout, stderr i status. Dla długich wyników czytaj potoki równolegle: pełny stderr może zablokować dziecko, podczas gdy rodzic czeka na zakończenie. Test potrzebuje też deadline, aby regresja nie zawiesiła CI.

Dystrybucja wymaga podania systemu, architektury i wymagań runtime’u. Target triple nie gwarantuje samodzielnego linkowania wszystkich bibliotek. Przetestuj artefakt na minimalnym wspieranym systemie, opublikuj sumy kontrolne i informację o wersji, uwzględnij licencje zależności. Kompilacja krzyżowa oraz podpisywanie zależą od platformy; nie nazywaj binarium uniwersalnym po samym `cargo build --release`.

## Sprawdź, czy rozumiesz

- Dlaczego błąd flush może zmienić sukces obliczenia w błąd procesu?
- Kiedy rodzic i dziecko zablokują się na dwóch potokach?
- Co flaga anulowania gwarantuje między rekordami, a czego nie gwarantuje podczas blokującego read?

## Ćwiczenia

- `C02-1` — podstawowe: Podaj oczekiwane bajty i liczbę rekordów dla wejść pustego, b"x" i b"x\n\n" w funkcji kopiuj. [Rozwiązanie](../rozwiazania/15_aplikacje_cli/02_strumienie_sygnaly_testy_i_dystrybucja.md#c02-1).
- `C02-2` — praktyczne: Zaimplementuj writer akceptujący najwyżej dwa bajty na write. Sprawdź, że write_all zachowa cały pięciobajtowy rekord. [Rozwiązanie](../rozwiazania/15_aplikacje_cli/02_strumienie_sygnaly_testy_i_dystrybucja.md#c02-2).
- `C02-3` — pogłębione: Zaprojektuj test procesu generującego duży stdout i stderr, z limitem 5 sekund. Opisz równoległy odczyt i sprzątanie po timeout. [Rozwiązanie](../rozwiazania/15_aplikacje_cli/02_strumienie_sygnaly_testy_i_dystrybucja.md#c02-3).

## Powiązane tematy

- [Komendy i konfiguracja](01_komendy_argumenty_i_konfiguracja.md)
- [Pliki i procesy](../13_io_siec_i_protokoly/01_pliki_io_i_procesy.md)
- [Testowanie i jakość](../09_dokumentacja_testowanie_i_jakosc/README.md)
