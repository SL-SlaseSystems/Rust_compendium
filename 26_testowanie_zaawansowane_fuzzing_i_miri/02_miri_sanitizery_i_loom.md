[← Spis treści](../README.md)
<!-- status: expanded -->

# Miri, sanitizery i modelowanie współbieżności

> Przykłady `rust`: biblioteka standardowa, Edition 2024. API narzędzi i bibliotek zewnętrznych opisano na podstawie źródeł sprawdzonych 11 listopada 2026 r.; szkice `text` wymagają wskazanego środowiska.

## Cele

Po tym rozdziale potrafisz:

- dobrać narzędzie do klasy błędu pamięci lub protokołu;
- wyjaśnić granice wnioskowania z czystego przebiegu;
- wydzielić mały model współbieżności bez ukrytych operacji std;

## Model — każde narzędzie obserwuje inny wycinek programu

Test funkcjonalny porównuje wynik z oczekiwaniem. Miri interpretuje kod i wykrywa niektóre naruszenia reguł Rusta. Sanitizer instrumentuje wykonanie i sygnalizuje wybrane błędy w przebytych ścieżkach. Loom eksploruje harmonogramy małego programu używającego jego prymitywów. Te techniki odpowiadają na różne pytania; użycie jednej nie zastępuje pozostałych ani przeglądu kontraktu `unsafe`.

Jeżeli bezpieczne API pozwala klientowi doprowadzić do UB, problem dotyczy soundness niezależnie od tego, czy test go znalazł. Z kolei pamięć pozostająca niewykorzystana po `mem::forget` nie jest automatycznie UB: abstrakcja nie może opierać bezpieczeństwa na bezwarunkowym wykonaniu destruktora. Oddziel gwarancje języka, założenia abstrakcji i model diagnostyczny wybranego narzędzia.

## Miri: dowód obowiązku przed eksperymentem

Przed uruchomieniem testu wskaźnikowego zapisz, skąd pochodzi alokacja, jaka jest długość, wyrównanie, inicjalizacja, aliasing i lifetime. W przykładzie wszystkie wymagania wynikają z aktywnego slice i sprawdzenia indeksu; wersja bezpieczna nadal byłaby preferowana w zwykłej aplikacji.

~~~rust
fn pierwszy(dane: &[u32]) -> Option<u32> {
    if dane.is_empty() { return None; }
    let p = dane.as_ptr();
    // SAFETY: slice ma co najmniej jeden zainicjalizowany, wyrównany
    // element; pozostaje żywy i nie jest mutowany podczas odczytu.
    Some(unsafe { p.read() })
}

fn main() {
    assert_eq!(pierwszy(&[]), None);
    assert_eq!(pierwszy(&[7, 9]), Some(7));
}
~~~

Odczyt `u32` jest kopią. Ten sam wzorzec z typem posiadającym zasób wymagałby analizy ownership; nie kopiuj bezrefleksyjnie `ptr::read` dla `String`. Test na pustym slice chroni warunek odczytu, lecz nie zastępuje uzasadnienia bezpieczeństwa wszystkich dopuszczalnych wywołań.

Miri jest narzędziem związanym z nightly. Typowa komenda to `cargo +nightly miri test`, po przygotowaniu komponentu dla wybranego toolchainu. FFI, I/O i docelowy sprzęt mogą ograniczać zakres wykonalnego testu. Modele aliasingu w narzędziu rozwijają się; wynik dla konkretnego modelu nie staje się przez to pełną specyfikacją języka. Zachowaj wersję i flagi w raporcie.

## Sanitizery: instrumentacja musi objąć badaną ścieżkę

AddressSanitizer bada między innymi wybrane niepoprawne dostępy do pamięci, a ThreadSanitizer bada część problemów synchronizacji. Wsparcie zależy od targetu, toolchainu, flag i sposobu zbudowania zależności. Nie podawaj jednej uniwersalnej komendy dla wszystkich systemów. Sięgnij do rustc Unstable Book i dokumentacji wybranego sanitizera; sprawdź, czy potrzebne jest także przebudowanie biblioteki standardowej.

Instrumentacja zmienia koszt i zachowanie programu, dlatego nie używaj jej wyników jako benchmarku produkcyjnego. Kod C/C++ wywoływany przez FFI wymaga zgodnej konfiguracji narzędzi, inaczej duża część ścieżki może pozostać niewidoczna. Błąd zależny od rozmiaru danych nie musi wystąpić w małym zestawie, mimo poprawnego uruchomienia sanitizera.

## Loom: mały stan zamiast prawdziwego serwera

Loom jest biblioteką **third-party** modelującą między innymi atomiki, blokady i wątki. Zastąp badane prymitywy ich odpowiednikami Loom, bo ukryte `std::sync` pozostają poza jego wiedzą. Wydziel protokół z sieci i zegara. Model z dwoma producentami i jednym slotem często ujawnia więcej niż uruchamianie całej aplikacji tysiąc razy.

Poniższy szkic wymaga zależności `loom`; `std::sync::Mutex` nie może zastąpić w nim modelowanej blokady:

~~~text
loom::model(|| {
    let stan = loom::sync::Arc::new(loom::sync::Mutex::new(0));
    let kopia = stan.clone();
    let h = loom::thread::spawn(move || *kopia.lock().unwrap() += 1);
    *stan.lock().unwrap() += 1;
    h.join().unwrap();
    assert_eq!(*stan.lock().unwrap(), 2);
});
~~~

Ograniczenia eksploracji są częścią eksperymentu. Zwiększenie granicy stanu może być kosztowne, a czysty przebieg ma znaczenie tylko dla zbudowanego modelu. Zapytaj, czy model zachowuje kolejność odczytów, publikacji i odzyskiwania pamięci prawdziwej implementacji.

## Diagnostyka kompilatora

Nie umieszczaj umyślnego UB w zwykłym `rust` docteście w nadziei, że „powinno się wywrócić”. UB nie ma wymaganego objawu. `compile_fail` służy kodowi odrzucanemu przez kompilator, a nie dowolnej błędnej semantyce. Negatywny test Miri uruchamiaj jako osobny przypadek z oczekiwanym raportem właściwego narzędzia. Odróżnij jego błąd wykonania od niespełnionego niezmiennika programu.

## Praktyka produkcyjna

Zacznij od najmniejszego modułu z `unsafe` i testów granicznych: zero elementów, częściowa inicjalizacja, panika podczas tworzenia oraz zniszczenie w każdym poprawnym stanie. Dla współbieżności zapisz niezmiennik i punkt linearyzacji. Raport powinien zawierać narzędzie, wersję, target, flagi, budżet i ograniczenia. Dobierz częstotliwość do kosztu: mały model na zmianę protokołu, dłuższy zestaw w osobnym jobie.

## Sprawdź, czy rozumiesz

1. Dlaczego `ptr::read` dla `String` zmienia obowiązki względem `u32`?
2. Czego Loom nie zobaczy po pozostawieniu blokady std?
3. Dlaczego czysty sanitizer nie dowodzi soundness?

## Ćwiczenia

- `D06-1` — podstawowe: Zapisz obowiązki bezpieczeństwa odczytu `pierwszy`. [Rozwiązanie](../rozwiazania/26_testowanie_zaawansowane_fuzzing_i_miri/02_miri_sanitizery_i_loom.md#d06-1).
- `D06-2` — praktyczne: Dobierz narzędzie do use-after-free w FFI, błędu aliasingu Rust i utraconej aktualizacji licznika. [Rozwiązanie](../rozwiazania/26_testowanie_zaawansowane_fuzzing_i_miri/02_miri_sanitizery_i_loom.md#d06-2).
- `D06-3` — pogłębione: Zaprojektuj minimalny model check-then-act dla ograniczonej kolejki. [Rozwiązanie](../rozwiazania/26_testowanie_zaawansowane_fuzzing_i_miri/02_miri_sanitizery_i_loom.md#d06-3).

## Źródła i granice weryfikacji

Zakres i ograniczenia: [Miri README](https://github.com/rust-lang/miri), [Loom API](https://docs.rs/loom/latest/loom/) oraz [rustc Unstable Book: sanitizers](https://doc.rust-lang.org/unstable-book/compiler-flags/sanitizer.html). Lokalny doctest wykonuje bezpiecznie uzasadniony przykład std; nie oznacza uruchomienia kampanii Miri, Loom ani sanitizerów.

## Powiązane tematy

- [Właściwości i fuzzing](01_testy_wlasciwosci_i_fuzzing.md)
- [Unsafe i soundness](../21_unsafe_soundness_i_model_pamieci/01_unsafe_i_soundness.md)
- [Atomiki](../10_wspolbieznosc/05_atomics_i_memory_ordering.md)
