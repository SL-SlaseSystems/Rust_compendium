[← Spis treści](../README.md)
<!-- status: expanded -->

# Projekt referencyjny: parser konfiguracji z jawnym kontraktem

> Przykłady `rust`: biblioteka standardowa, Edition 2024. API narzędzi i bibliotek zewnętrznych opisano na podstawie źródeł sprawdzonych 11 listopada 2026 r.; szkice `text` wymagają wskazanego środowiska.

## Cele

Po tym rozdziale potrafisz:

- połączyć borrowing, błędy, kolekcje i limity w małym programie;
- zdefiniować pozycję błędu i politykę duplikatów;
- odróżnić kompletną implementację parsera od integracji I/O;

## Model — kontrakt przed implementacją

Format zawiera wiersze `klucz=wartość`. Klucz jest niepusty, ma do 64 bajtów i składa się z ASCII: liter, cyfr oraz `_`. Wartość może być pusta i zawierać kolejne `=`. Nie usuwamy spacji: biały znak w kluczu jest błędem, a w wartości pozostaje daną. Duplikat klucza jest błędem zamiast cichego nadpisania. Dokument może być pusty i może kończyć się znakiem nowej linii.

Limit wejścia wynosi 64 KiB, liczby rekordów określa wywołujący. Numer wiersza w błędzie zaczyna się od jedynki; błąd całkowitego limitu ma numer zero, bo nie jest przypisany do pojedynczego wiersza. To mały format dydaktyczny, bez komentarzy i escapingu. Rozbudowa gramatyki wymaga zmiany kontraktu i testów.

## Kompletna implementacja rdzenia

~~~rust
use std::collections::BTreeMap;

#[derive(Debug, PartialEq)]
enum Rodzaj { Rozmiar, Liczba, Separator, Klucz, Duplikat }
#[derive(Debug, PartialEq)]
struct Blad { wiersz: usize, rodzaj: Rodzaj }

fn parse(input: &str, max: usize) -> Result<BTreeMap<&str, &str>, Blad> {
    if input.len() > 65536 {
        return Err(Blad { wiersz: 0, rodzaj: Rodzaj::Rozmiar });
    }
    let mut wynik = BTreeMap::new();
    for (i, line) in input.lines().enumerate() {
        let blad = |rodzaj| Blad { wiersz: i + 1, rodzaj };
        if i >= max { return Err(blad(Rodzaj::Liczba)); }
        let (key, value) = line.split_once('=')
            .ok_or_else(|| blad(Rodzaj::Separator))?;
        if key.is_empty() || key.len() > 64
            || !key.bytes().all(|b| b.is_ascii_alphanumeric() || b == b'_') {
            return Err(blad(Rodzaj::Klucz));
        }
        if wynik.contains_key(key) { return Err(blad(Rodzaj::Duplikat)); }
        wynik.insert(key, value);
    }
    Ok(wynik)
}

fn main() {
    let input = String::from("port=8080
nazwa=zażółć=Rust
puste=
");
    let dane = parse(&input, 10).unwrap();
    assert_eq!(dane["port"], "8080");
    assert_eq!(dane["nazwa"], "zażółć=Rust");
    assert_eq!(dane["puste"], "");
    assert!(parse("", 0).unwrap().is_empty());
    assert_eq!(parse("x=1
x=2", 2).unwrap_err(),
        Blad { wiersz: 2, rodzaj: Rodzaj::Duplikat });
    assert_eq!(parse("x=1", 0).unwrap_err().rodzaj, Rodzaj::Liczba);
    assert_eq!(parse("a b=1", 1).unwrap_err().rodzaj, Rodzaj::Klucz);
}
~~~

## Dlaczego te typy i operacje

Wynik pożycza fragmenty inputu. `BTreeMap` alokuje węzły, ale nie kopiuje każdego klucza i wartości; właściciel tekstu musi żyć wystarczająco długo. Gdy aplikacja potrzebuje niezależnej konfiguracji, osobny etap może stworzyć własny model domenowy, np. `port: u16`. Oddzielenie tego kroku od parsowania pozwala rozróżnić błąd składni i znaczenia.

`split_once` wybiera pierwszy separator i zachowuje kolejne w wartości. `str::lines` obsługuje LF oraz CRLF, nie dodaje pustego wiersza po końcowym terminatorze. Pusty wiersz wewnątrz dokumentu zostaje odrzucony jako brak separatora. To ważne przypadki testowe: nie dopisuj `filter` usuwającego puste wiersze bez decyzji o zmianie formatu.

`BTreeMap` daje uporządkowane klucze i logarytmiczne wyszukiwanie względem liczby elementów, z kosztem porównań tekstu. Dla niewielkiej konfiguracji prostota i deterministyczna kolejność są użyteczne. Oddzielne `contains_key` i `insert` są tu czytelne; `Entry` może uniknąć ponownego wyszukiwania. Najpierw zachowaj politykę duplikatów, dopiero potem zmieniaj implementację na podstawie pomiaru.

## Granice zasobów i adapter

Limit `input.len` działa dopiero po dostarczeniu tekstu do funkcji. Adapter czytający plik lub request musi ograniczyć odczyt wcześniej, inaczej parser odrzuci dane dopiero po ogromnej alokacji. Dla surowych bajtów adapter sprawdza UTF-8 i mapuje błąd kodowania. Nie używaj `from_utf8_lossy`, jeśli format wymaga wiernego odtworzenia wartości.

To parser kompletnego dokumentu, nie parser strumieniowy. Przy dużych danych osobny projekt powinien utrzymywać niekompletny wiersz między porcjami i limitować jego długość. Zwracanie pożyczek do bufora, który następny odczyt nadpisze, wymaga zmiany modelu własności; prosta zamiana `read_to_string` na pętlę odczytu nie wystarczy.

## Diagnostyka kompilatora

Pożyczony wynik nie może przeżyć właściciela inputu. Poniższy przykład celowo nie przechodzi kompilacji; naprawa to dłużej żyjący właściciel lub własny typ wyniku, zależnie od potrzeb.

~~~compile_fail
fn main() {
    let wartosc;
    {
        let input = String::from("x=1");
        wartosc = input.split_once('=').unwrap().1;
    }
    println!("{wartosc}");
}
~~~

Nie naprawiaj problemu przez wymyśloną adnotację `'static`: lifetime nie przedłuża istnienia bufora.

## Praktyka produkcyjna

Testy wejściowe obejmują pusty dokument, duplikat, brak separatora, pusty klucz, Unicode w wartości, CRLF, granice 64 bajtów i 64 KiB oraz limit liczby wierszy. Property test może kodować model z poprawnymi kluczami i porównywać wynik. Harness fuzzera najpierw waliduje UTF-8 lub bada adapter bajtowy; sukces oznacza wynik albo jawny błąd, nigdy panikę. W aplikacji nie ujawniaj pełnych wartości konfiguracji w komunikacie błędu.

## Sprawdź, czy rozumiesz

1. Dlaczego wynik nie może przeżyć `input`?
2. Co zmieniłoby automatyczne usunięcie pustych wierszy?
3. Dlaczego limit w parserze nie zastępuje limitu odczytu?

## Ćwiczenia

- `D14-1` — podstawowe: Dopisz oczekiwane wyniki dla CRLF, pustego wiersza wewnątrz i końcowego LF. [Rozwiązanie](../rozwiazania/30_projekty_przekrojowe/02_wzorcowy_projekt_parsera.md#d14-1).
- `D14-2` — praktyczne: Dodaj etap domenowy wymagający pola `port` jako liczby u16 większej od zera. [Rozwiązanie](../rozwiazania/30_projekty_przekrojowe/02_wzorcowy_projekt_parsera.md#d14-2).
- `D14-3` — pogłębione: Zaprojektuj wersję strumieniową z limitem wiersza i tym samym kontraktem duplikatów. [Rozwiązanie](../rozwiazania/30_projekty_przekrojowe/02_wzorcowy_projekt_parsera.md#d14-3).

## Źródła i granice weryfikacji

Kontrakty biblioteki standardowej: [str::lines](https://doc.rust-lang.org/std/primitive.str.html#method.lines), [str::split_once](https://doc.rust-lang.org/std/primitive.str.html#method.split_once) i [BTreeMap](https://doc.rust-lang.org/std/collections/struct.BTreeMap.html). Kod jest kompletną autorską implementacją opisanego rdzenia; nie zawiera adaptera plików, CLI ani wdrożenia.

## Powiązane tematy

- [Wszystkie projekty](01_siedem_projektow_kryteria_i_etapy.md)
- [Slices i str](../03_ownership_i_pamiec/04_slices_i_str.md)
- [Property tests](../26_testowanie_zaawansowane_fuzzing_i_miri/01_testy_wlasciwosci_i_fuzzing.md)
