[← Spis treści](../README.md)
<!-- status: expanded -->

# Siedem projektów: zakres, etapy i kryteria ukończenia

> Przykłady `rust`: biblioteka standardowa, Edition 2024. API narzędzi i bibliotek zewnętrznych opisano na podstawie źródeł sprawdzonych 11 listopada 2026 r.; szkice `text` wymagają wskazanego środowiska.

## Cele

Po tym rozdziale potrafisz:

- wybrać projekt sprawdzający określony zestaw umiejętności;
- podzielić pracę na działające przyrosty;
- ocenić ukończenie na podstawie dowodów i kontraktu;

## Model — projekt sprawdza decyzje, nie liczbę użytych bibliotek

Wybierz problem i zdefiniuj wejście, wynik, ograniczenia oraz sposób demonstracji. W pierwszym przyroście dostarcz jedną działającą ścieżkę end-to-end, potem dodaj błędy i granice, a dopiero później optymalizację. Projekt bez kryterium odrzucenia niepoprawnego wejścia nie sprawdza pełnego kontraktu. Projekt bez instrukcji uruchomienia nie jest odtwarzalnym artefaktem.

Każdy wariant poniżej kończy się README z zakresem, przykładowym wywołaniem, wymaganiami środowiska i ograniczeniami. Raport decyzji opisuje najważniejszy kompromis oraz pomiar lub test, który go uzasadnia. Nie musisz od razu wdrażać wszystkiego: kolejność projektów prowadzi od lokalnego przetwarzania do usług i niskiego poziomu.

## 1. CLI przetwarzające dane

Zbuduj narzędzie czytające rekordy ze stdin lub pliku, walidujące je i wypisujące wynik w stabilnym formacie. Pierwszy etap obsługuje mały input oraz jawne kody wyjścia. Drugi dodaje streaming, ograniczenie rekordu, potoki i `BrokenPipe`. Trzeci obejmuje argumenty, konfigurację, test procesu i dystrybucję.

Dowód ukończenia: test end-to-end dla poprawnego wejścia, wadliwego rekordu, pustego strumienia i przerwanego odbiorcy. Wykonaj pomiar dużego wejścia pokazujący ograniczoną pamięć, zamiast wczytywania całego pliku. Stdout pozostaje wynikiem do automatyzacji, stderr diagnostyką. Pułapka: log na stdout albo sukces mimo pominiętych błędów zmienia kontrakt skryptów.

## 2. Parser i model domenowy

Zacznij od gramatyki z jednoznaczną polityką białych znaków, duplikatów i zakończenia danych. Modeluj wynik enumami lub strukturami, a błąd pozycją i klasą problemu. Potem dodaj testy przykładów, własności i fuzzing. Pełny mały wzorzec zawiera [następny rozdział](02_wzorcowy_projekt_parsera.md).

Dowód ukończenia: brak paniki dla dowolnych bajtów w ograniczonej dziedzinie, zgodne wyniki dla poprawnych rekordów i minimalny przypadek regresji. Sprawdź skrajne długości, błędne UTF-8 i zagnieżdżenie, jeśli gramatyka je dopuszcza. Pułapka: testowanie wyłącznie danych wygenerowanych przez własny encoder, który powiela ten sam błąd.

## 3. Biblioteka w workspace

Wydziel bibliotekę domenową i cienki program kliencki. API ma małą publiczną fasadę, udokumentowane błędy i przykłady rustdoc. Dodaj co najmniej jedną opcjonalną integrację tak, aby wariant minimalny był użyteczny bez niej. Określ MSRV, Edition i zasady kompatybilności.

Dowód ukończenia: zewnętrzny test konsumencki korzysta wyłącznie z publicznego API, a minimalne/default features przechodzą osobno. Paczka zawiera wszystkie potrzebne pliki i nie ujawnia szczegółów implementacji. Pułapka: przypadkowe upublicznienie typu zależności jako części kontraktu lub unifikacja features ukrywająca niesamodzielny wariant minimalny.

## 4. System wielowątkowy

Zaprojektuj ograniczoną kolejkę prac i pulę wykonawców. Najpierw poprawna wersja z blokadą lub kanałem; dopiero po pomiarze rozważ atomiki. Zdefiniuj własność zadania, wynik, błąd wykonawcy i zamykanie producentów. Odróżnij gwarancję braku data race od poprawnego protokołu zakończenia.

Dowód ukończenia: każde zaakceptowane zadanie ma dokładnie określony wynik, przeciążenie nie powoduje nieograniczonej alokacji, a shutdown kończy pracę według polityki. Testuj pustą kolejkę, pełną kolejkę, panikę workera i zniknięcie odbiorcy. Pułapka: deadlock przy zamykaniu, gdy producent czeka na miejsce, a nikt już nie odbiera.

## 5. Usługa asynchroniczna

Zbuduj klienta kilku kontrolowanych źródeł z ograniczoną współbieżnością. Dodaj globalny deadline, cancellation safety oraz limity tasków i buforów. Zewnętrzne usługi zastąp deterministycznymi adapterami testowymi, które potrafią zwrócić błąd, częściowe dane i brak odpowiedzi.

Dowód ukończenia: timeout kończy lokalne oczekiwanie, a raport wyraźnie opisuje możliwe skutki zdalne. Wszystkie taski mają właściciela, retry wspólny budżet, a shutdown termin. Pułapka: spawn dla każdego elementu zbioru bez limitu albo utrzymywanie guarda blokady przez `await`.

## 6. Web, dane i obserwowalność

Zrealizuj jedną domenową operację z walidacją, autoryzacją, transakcją i odpowiedzią HTTP. Dodaj migrację schematu, test kontraktowy i izolowaną bazę testową. Potem instrumentuj ścieżkę i określ jej SLI/SLO. Wydanie ma identyfikowalny artefakt, smoke test i plan cofnięcia zgodny z danymi.

Dowód ukończenia: testy odmowy dla obcego tenanta, duplikatu operacji i niedostępności bazy; kontrolowane odrzucenie przeciążenia i procedura odtworzenia. Pułapka: uznanie poprawnego tokenu za autoryzację do dowolnego rekordu albo przekonanie, że rollback binarium cofa transakcje.

## 7. Bezpieczna abstrakcja nad `unsafe`

Wybierz mały problem, np. kontrolowany bufor częściowo inicjalizowanych wartości. Najpierw zapisz niezmienniki reprezentacji i wszystkie poprawne stany. Publiczne safe API musi je zachowywać także przy błędzie, panice i niewykonaniu destruktora klienta. Każdy blok `unsafe` ma lokalne uzasadnienie `SAFETY`.

Dowód ukończenia: przegląd kontraktu przez inną osobę, testy pustego bufora, granic pojemności, częściowej inicjalizacji i paniki konstruktora oraz odpowiedni przebieg Miri. Fuzzing i testy nie zastępują argumentu soundness. Pułapka: zwolnienie niezainicjalizowanej wartości lub podwójne zniszczenie zasobu po `ptr::read`.

## Zapis kryterium jako jawnej reguły

~~~rust
struct Dowody { kontrakt: bool, testy: bool, instrukcja: bool }
fn gotowy(d: Dowody) -> bool { d.kontrakt && d.testy && d.instrukcja }
fn main() {
    assert!(!gotowy(Dowody { kontrakt: true, testy: true, instrukcja: false }));
    assert!(gotowy(Dowody { kontrakt: true, testy: true, instrukcja: true }));
}
~~~

To model kryteriów, nie automatyczny audyt jakości. Dla swojego projektu zastąp trzy ogólne flagi konkretnymi wynikami: nazwa testu, komenda i oczekiwany rezultat.

## Diagnostyka kompilatora

W projekcie pokaż co najmniej jeden rzeczywisty błąd kompilatora związany z kontraktem: move po konsumpcji, niespełnione `Send` albo nielegalne borrow. Objaśnij przyczynę i dobór naprawy, zamiast dodawać losowe `clone` i `Arc<Mutex<_>>`. Błędy runtime i logiczne wymagają osobnych testów; nie każdy z nich ma sensowny przykład `compile_fail`.

## Praktyka produkcyjna

Nie zaczynaj siedmiu projektów jednocześnie. Wybierz jeden i doprowadź go do odtwarzalnego wyniku. Rozdziel wymagania podstawowe od rozszerzeń, a pomiary wykonuj w opisanych warunkach. Przy demonstracji pokaż także przewidywalne zachowanie błędu. Jeśli integracja wymaga konta, sprzętu lub usługi, dostarcz testowy adapter i wyraźnie opisz, które fragmenty sprawdzono w rzeczywistym środowisku.

## Sprawdź, czy rozumiesz

1. Który dowód odróżnia działający projekt od katalogu szkiców?
2. Dlaczego poprawność kolejki nie wynika tylko z braku data race?
3. Co projekt unsafe musi wykazać poza przejściem Miri?

## Ćwiczenia

- `D13-1` — podstawowe: Wybierz projekt i zapisz jego najmniejszą działającą ścieżkę. [Rozwiązanie](../rozwiazania/30_projekty_przekrojowe/01_siedem_projektow_kryteria_i_etapy.md#d13-1).
- `D13-2` — praktyczne: Ułóż trzy przyrosty projektu wielowątkowego z kryterium każdego. [Rozwiązanie](../rozwiazania/30_projekty_przekrojowe/01_siedem_projektow_kryteria_i_etapy.md#d13-2).
- `D13-3` — pogłębione: Napisz plan weryfikacji bezpiecznej otoczki bufora częściowej inicjalizacji. [Rozwiązanie](../rozwiazania/30_projekty_przekrojowe/01_siedem_projektow_kryteria_i_etapy.md#d13-3).

## Źródła i granice weryfikacji

Projekty są autorskimi specyfikacjami ćwiczeń łączących rozdziały kompendium. Dla reguł języka korzystaj z [Rust Reference](https://doc.rust-lang.org/reference/), a dla obowiązków unsafe z dokumentacji konkretnych funkcji i rozdziałów działu 21. Kryteria projektów nie są deklaracją, że siedem aplikacji zostało zaimplementowanych lub wdrożonych.

## Powiązane tematy

- [Parser referencyjny](02_wzorcowy_projekt_parsera.md)
- [Architektura](../14_idiomy_wzorce_i_architektura/04_architektura_aplikacji_i_di.md)
- [Testy zaawansowane](../26_testowanie_zaawansowane_fuzzing_i_miri/README.md)
