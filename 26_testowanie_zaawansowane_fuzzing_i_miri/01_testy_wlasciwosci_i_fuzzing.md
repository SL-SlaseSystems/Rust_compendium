[← Spis treści](../README.md)
<!-- status: expanded -->

# Testy właściwości, generatory i fuzzing

> Przykłady `rust`: biblioteka standardowa, Edition 2024. API narzędzi i bibliotek zewnętrznych opisano na podstawie źródeł sprawdzonych 11 listopada 2026 r.; szkice `text` wymagają wskazanego środowiska.

## Cele

Po tym rozdziale potrafisz:

- zdefiniować własność mocniejszą od pojedynczego przykładu;
- dobrać generator do dziedziny i zachować minimalną reprodukcję;
- zbudować ograniczony harness fuzzera dla niezaufanych bajtów;

## Model — przykład sprawdza punkt, własność opisuje przestrzeń

Test przykładowy utrwala zachowanie dla konkretnego wejścia. Test właściwości (property test) generuje wiele danych i sprawdza relację, która ma zawsze zachodzić: sortowanie zachowuje multizbiór, dekodowanie zakodowanej wartości odtwarza model, a operacja dodania i usunięcia przywraca poprzedni stan. Najpierw zapisz założenia. `decode(encode(x)) == x` ma sens tylko dla reprezentowalnych modeli i odpowiedniej definicji równości; nie każda liczba zmiennoprzecinkowa ani niekanoniczny tekst spełnią naiwną wersję.

Własność nie może powtarzać implementacji. Porównanie `sort` z drugim wywołaniem tej samej funkcji niczego nie sprawdza. Użyteczne są niezależny prosty model, ograniczenia zachowanego stanu i relacje między różnymi wejściami (metamorphic testing). Dla parsera sprawdź brak paniki, ograniczony rozmiar wyniku oraz zgodność poprawnych danych z referencją. Brak paniki sam nie dowodzi poprawnego parsowania.

## Mały model i reprezentatywna dziedzina

Poniższy przykład sprawdza round-trip formatu dwóch bajtów dla wszystkich wartości, nie polega na losowym szczęściu. Ten sam pomysł można skalować generatorem, gdy dziedzina jest zbyt duża.

~~~rust
fn koduj(x: u16) -> [u8; 2] { x.to_be_bytes() }
fn dekoduj(b: [u8; 2]) -> u16 { u16::from_be_bytes(b) }

fn main() {
    for x in 0..=u16::MAX {
        assert_eq!(dekoduj(koduj(x)), x);
    }
    assert_eq!(koduj(0x1234), [0x12, 0x34]);
}
~~~

Round-trip wykryłby utratę informacji, ale dwa symetrycznie błędne algorytmy mogłyby nadal przejść test. Dlatego dodano niezależny punkt odniesienia dla ustalonego porządku bajtów. Przy formacie sieciowym testuj również reprezentacje pochodzące od innej implementacji i odrzucone długości. Nie używaj natywnego endianness w formacie, który ma być przenośny.

`proptest` jest biblioteką **third-party**. Strategie opisują dane i sposób ich upraszczania po porażce (shrinking). Generator poprawnych drzew składni powinien kontrolować głębokość oraz liczbę węzłów. Jeśli generujesz prawie wyłącznie niepoprawne dane i odrzucasz je warunkiem, test może niewiele powiedzieć o właściwej domenie. Rozdziel generowanie poprawnych modeli od badania dowolnych bajtów.

## Fuzzing pokrycia i harness

Fuzzer mutuje wejścia, obserwuje wykonanie i zachowuje przypadki prowadzące do nowych ścieżek albo awarii. `cargo-fuzz` jest narzędziem **third-party**, zwykle uruchamianym z toolchainem nightly i wymaganiami platformowymi. Przypnij środowisko i zapisz komendę odtworzenia. Korpus startowy powinien obejmować poprawne małe wiadomości, granice długości i reprezentacje różnych wariantów.

Szkic harnessu wymaga `cargo-fuzz`, crate'a aplikacji i skonfigurowanego targetu; nie jest doctestem std:

~~~text
fuzz_target!(|dane: &[u8]| {
    if dane.len() > 65536 { return; }
    let _ = parser::parse(dane);
});
~~~

Limit wejścia chroni eksperyment przed badaniem wyłącznie kosztu ogromnych alokacji, ale wyklucza większe przypadki. Osobny test musi sprawdzić politykę odrzucania dużych danych. Harness nie powinien wykonywać prawdziwych requestów, otwierać dowolnych ścieżek ani zależeć od godziny; takie efekty utrudniają reprodukcję i mogą dominować czas testu.

## Awaria musi zostać w projekcie

Po wykryciu błędu odtwórz go tą samą rewizją i konfiguracją. Zminimalizuj wejście, ustal przyczynę, dodaj zwykły test regresji, popraw kod i uruchom dotknięte własności ponownie. Sam plik w katalogu wynikowym fuzzera może zniknąć przy czyszczeniu środowiska. Zachowaj też przypadek, którego poprawne zachowanie jest odrzuceniem danych, a nie akceptacją.

Wyniki interpretuj w kontekście budżetu: czas, liczba wykonań i pokrycie pomagają porównywać kampanie, ale nie stanowią dowodu braku błędów. Duży wzrost liczby iteracji po usunięciu walidacji może wręcz oznaczać pogorszenie jakości eksperymentu.

## Diagnostyka kompilatora

Błąd kompilacji harnessu dotyczy często features, widoczności parsera albo innego grafu zależności niż aplikacja. Zanim rozpoczniesz długą kampanię, skompiluj mały target i odtwórz jeden plik. Porażka asercji wskazuje niespełnioną własność; sprawdź również samą własność i generator. Nie zmieniaj limitu czasu tylko po to, by ukryć nieskończoną pętlę parsera.

## Praktyka produkcyjna

Szybkie property tests uruchamiaj w codziennej pętli, dłuższe kampanie jako osobne zadanie z zasobami i zachowaniem artefaktów. Testuj ekstremalne długości, pusty input, niepoprawne UTF-8, przepełnienia i nieukończone rekordy. Parser strumieniowy wymaga dodatkowo własności niezależności od podziału wejścia na fragmenty: te same bajty w różnych porcjach powinny dawać ten sam wynik końcowy.

## Sprawdź, czy rozumiesz

1. Dlaczego round-trip potrzebuje także testu znanej reprezentacji?
2. Jak shrinking pomaga, a jak może zmienić warunki błędu?
3. Co ograniczenie harnessu do 64 KiB pozostawia niesprawdzone?

## Ćwiczenia

- `D05-1` — podstawowe: Podaj dwie niezależne własności sortowania. [Rozwiązanie](../rozwiazania/26_testowanie_zaawansowane_fuzzing_i_miri/01_testy_wlasciwosci_i_fuzzing.md#d05-1).
- `D05-2` — praktyczne: Zaprojektuj generator poprawnych rekordów `klucz=wartość`. [Rozwiązanie](../rozwiazania/26_testowanie_zaawansowane_fuzzing_i_miri/01_testy_wlasciwosci_i_fuzzing.md#d05-2).
- `D05-3` — pogłębione: Określ własność parsera strumieniowego przy różnym podziale pakietów. [Rozwiązanie](../rozwiazania/26_testowanie_zaawansowane_fuzzing_i_miri/01_testy_wlasciwosci_i_fuzzing.md#d05-3).

## Źródła i granice weryfikacji

Strategie i shrinking: [Proptest Book](https://proptest-rs.github.io/proptest/intro.html). Kampanie i wymagania narzędzia: [Rust Fuzz Book: cargo-fuzz](https://rust-fuzz.github.io/book/cargo-fuzz.html). Wyczerpujący test `u16` to własny przykład, a opis harnessu pozostaje szkicem integracji.

## Powiązane tematy

- [Miri i modele współbieżności](02_miri_sanitizery_i_loom.md)
- [Sieć i ramkowanie](../13_io_siec_i_protokoly/02_siec_i_protokoly.md)
- [Projekt parsera](../30_projekty_przekrojowe/02_wzorcowy_projekt_parsera.md)
