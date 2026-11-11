[← Spis treści](../README.md)
<!-- status: expanded -->

# Reprodukcja błędu, backtrace i debugger

> Przykłady `rust`: biblioteka standardowa, Edition 2024. API narzędzi i bibliotek zewnętrznych opisano na podstawie źródeł sprawdzonych 11 listopada 2026 r.; szkice `text` wymagają wskazanego środowiska.

## Cele

Po tym rozdziale potrafisz:

- zredukować problem do kontrolowanego przypadku;
- odróżnić punkt wykrycia błędu od jego przyczyny;
- dobrać symbole i obserwacje do diagnozowanej warstwy;

## Model — objaw jest końcem łańcucha przyczyn

Panika w indeksowaniu może wynikać z błędnego parsera, a timeout bazy z wyczerpania puli przez niezakończone operacje. Zaczynaj od obserwowalnej niezgodności: jakie było wejście, oczekiwany wynik i rzeczywisty rezultat. „Nie działa” nie określa eksperymentu. Zapisz też częstość, warunki oraz ostatnią znaną działającą wersję. Jedna poprawka powinna sprawdzać jedną hipotezę.

Minimalna reprodukcja usuwa nieistotne zależności, zachowując błąd. Nie redukuj jednocześnie danych, liczby wątków i profilu kompilacji, bo nie ustalisz, co usunęło objaw. Po każdym uproszczeniu uruchom ten sam test. Dla niepowtarzalnej awarii najpierw zbierz identyfikator operacji, liczebność kolejki, stan pamięci i wersję artefaktu; losowe opóźnienia nie zastępują tych danych.

## Od zgłoszenia do małego testu

Poniższa funkcja odrzuca błędny format zamiast panikować na `split(...).nth(1).unwrap()`. Przypadki testowe kodują konkretny kontrakt: wymagany separator, niepusty klucz i dozwolony pusty wynik.

~~~rust
#[derive(Debug, PartialEq)]
enum Blad { Separator, PustyKlucz }

fn para(s: &str) -> Result<(&str, &str), Blad> {
    let (klucz, wartosc) = s.split_once('=').ok_or(Blad::Separator)?;
    if klucz.is_empty() { return Err(Blad::PustyKlucz); }
    Ok((klucz, wartosc))
}

fn main() {
    assert_eq!(para("port=8080"), Ok(("port", "8080")));
    assert_eq!(para("port="), Ok(("port", "")));
    assert_eq!(para("port"), Err(Blad::Separator));
    assert_eq!(para("=8080"), Err(Blad::PustyKlucz));
    assert_eq!(para("x=a=b"), Ok(("x", "a=b")));
}
~~~

`split_once` zachowuje dalsze separatory w wartości. To świadoma decyzja formatu, którą test `x=a=b` chroni przed przypadkową zmianą. Wynik pożycza dane wejścia, więc redukcja nie wprowadza dodatkowej alokacji ani problemu synchronizacji. Samo zastąpienie `unwrap` przez `unwrap_or_default` ukryłoby uszkodzone wejście i mogłoby przenieść awarię dalej.

## Backtrace pokazuje stos, nie historię całego procesu

Backtrace pomaga znaleźć drogę dojścia do miejsca awarii w danym wątku. `RUST_BACKTRACE=1` jest typowym początkiem badania paniki; dokładność nazw i linii zależy od symboli, optymalizacji i platformy. `Backtrace::capture` uwzględnia konfigurację środowiska, a `force_capture` wymusza próbę zebrania stosu. Zbieranie może kosztować, dlatego nie umieszczaj go bez pomiaru w każdej iteracji.

Stos wątku executora nie jest pełną historią żądania async. Future mogła być wcześniej obsługiwana gdzie indziej; potrzebujesz również kontekstu taska i skorelowanych zdarzeń. Pierwsza ramka biblioteki nie dowodzi błędu w bibliotece: sprawdź jej wymagania i wejście dostarczone przez aplikację.

## Debugger i zgodność artefaktu

Debugger pozwala zatrzymać proces, obejrzeć stosy, argumenty i pamięć. Zanim ustawisz breakpoint, sprawdź, czy debugujesz to samo binarium i te same dane, dla których wystąpił problem. Dla awarii w zoptymalizowanym buildzie zachowaj optymalizację i dodaj symbole. Zmiana na profil `dev` może ukryć problem czasowy albo różnicę sprawdzania przepełnień.

Poniższy manifest jest konfiguracją projektu, nie samowystarczalnym programem:

~~~text
[profile.release]
debug = 2
strip = "none"
~~~

Poziom informacji debugowania i stripping dobieraj do narzędzia oraz platformy. Zmienne mogą być zoptymalizowane, funkcje zinline'owane, a stos niepełny; to ograniczenia obserwacji, nie dowód braku wykonania. Core dump może zawierać sekrety i dane użytkowników, więc analizuj go w kontrolowanym środowisku.

## Diagnostyka kompilatora

Rozróżniaj: błąd typu w `cargo check`, błąd linkowania po kompilacji, panikę podczas wykonania i logicznie błędny wynik bez paniki. Przy E0277 znajdź niespełniony bound w sygnaturze; przy brakującym symbolu sprawdź linkowane biblioteki i ABI. Przy panice odtwórz dane wejścia i przeczytaj pierwszą własną ramkę stosu. Reprodukcja powinna kończyć się jednoznacznym wynikiem i nie wymagać ręcznego oceniania logów.

## Praktyka produkcyjna

Zapisz zestaw dowodowy: rewizję, hash binarium, `rustc -Vv`, target, konfigurację bez sekretów i minimalne dane. Wprowadź test regresji przed poprawką, potwierdź, że zawodzi na starym kodzie, następnie uruchom go na nowym. Jeśli błąd zniknął po zmianie środowiska, udokumentuj różnicę zamiast przypisywać sukces niezwiązanej poprawce. Dla błędu współbieżności zachowaj ślad zdarzeń i model protokołu; sam debugger może zmienić harmonogram.

## Sprawdź, czy rozumiesz

1. Dlaczego wyłączenie optymalizacji może utrudnić diagnozę?
2. Co odróżnia backtrace od śladu żądania async?
3. Który test dokumentuje politykę kolejnych znaków `=`?

## Ćwiczenia

- `D03-1` — podstawowe: Dodaj test wartości zawierającej Unicode oraz dwóch separatorów. [Rozwiązanie](../rozwiazania/25_debugowanie_i_utrzymanie/01_reprodukcja_backtrace_i_debugger.md#d03-1).
- `D03-2` — praktyczne: Zredukuj awarię importera, który panikuje na wierszu bez `=`; opisz kolejność eksperymentów. [Rozwiązanie](../rozwiazania/25_debugowanie_i_utrzymanie/01_reprodukcja_backtrace_i_debugger.md#d03-2).
- `D03-3` — pogłębione: Zaprojektuj zestaw danych do zgłoszenia awarii pojawiającej się tylko w release. [Rozwiązanie](../rozwiazania/25_debugowanie_i_utrzymanie/01_reprodukcja_backtrace_i_debugger.md#d03-3).

## Źródła i granice weryfikacji

Zbieranie stosu: [std::backtrace::Backtrace](https://doc.rust-lang.org/std/backtrace/struct.Backtrace.html). Symbole i optymalizacja: [rustc codegen options](https://doc.rust-lang.org/rustc/codegen-options/index.html). Procedura redukcji i kontrakt parsera są autorskimi przykładami diagnostycznymi.

## Powiązane tematy

- [Regresje i incydenty](02_regresje_migracje_i_incydenty.md)
- [Błędy i panika](../07_obsluga_bledow/03_panic_unwind_i_abort.md)
- [Telemetria](../29_observability_i_produkcja/01_logi_metryki_i_traces.md)
