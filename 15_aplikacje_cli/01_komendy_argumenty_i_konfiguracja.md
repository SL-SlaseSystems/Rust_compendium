[← Spis treści](../README.md)
<!-- status: expanded -->

# Komendy, argumenty, kody wyjścia i konfiguracja

## Cele

Po tym rozdziale potrafisz:

- rozdzielić parsowanie argumentów, walidację konfiguracji i wykonanie operacji;
- wyznaczyć wynik konfiguracji z czterech warstw bez ukrywania błędnych wartości;
- opisać kontrakt stdout, stderr oraz kodów zakończenia dla skryptu wywołującego program.

## Model — CLI jest publicznym API

Interfejs wiersza poleceń (command-line interface, CLI) obsługuje człowiek i inny proces. Nazwy flag, format wyniku oraz znaczenie kodu wyjścia stają się kontraktem. Zmiana komunikatu na stderr zwykle mniej szkodzi automatyzacji niż dodanie banera na stdout. Zaprojektuj podstawowe scenariusze: wyświetlenie pomocy, poprawne wykonanie, błędna składnia, niepoprawne dane oraz awaria zależności. Osobno zdecyduj, czy brak dopasowania jest sukcesem, czy udokumentowanym wynikiem specjalnym.

Domena powinna przyjmować gotowy typ konfiguracji. Niech nie odczytuje `std::env` w środku obliczeń. Dzięki temu ten sam silnik da się wywołać z testu, GUI i serwera. Warstwa terminala zamienia błąd domenowy na tekst oraz status procesu. Gdy `main` zwraca `Result`, domyślny sposób raportowania błędu może nie odpowiadać oczekiwanemu kontraktowi; jawne mapowanie daje większą kontrolę.

**Stable:** `ExitCode::SUCCESS`, `FAILURE` i `From<u8>` pozwalają zwracać status z `main`. Własne liczby, np. `2` dla błędu użycia, są konwencją tego programu, a ich pełne znaczenie nie jest przenośną gwarancją systemu. Zweryfikowano 2026-11-11 w [dokumentacji ExitCode](https://doc.rust-lang.org/std/process/struct.ExitCode.html).

## Warstwy konfiguracji i walidacja

Praktyczna kolejność to: wartości domyślne, plik, środowisko, argumenty. Późniejsza warstwa nadpisuje wcześniejszą tylko wtedy, gdy rzeczywiście podaje wartość. `Option<bool>` rozróżnia brak decyzji, jawne `false` i jawne `true`; zwykłe `bool` tego nie potrafi. Dla list ustal, czy nadpisujesz całość, czy dopisujesz elementy. Automatyczne łączenie dwóch list adresów może niespodziewanie wysłać dane do dodatkowego odbiorcy.

Najpierw sparsuj wartości poszczególnych źródeł, następnie połącz warstwy, a potem zweryfikuj relacje: liczba workerów musi być dodatnia, limit kolejki co najmniej równy wielkości partii. Nie zamieniaj błędnego `APP_LIMIT=abc` na domyślną liczbę przez `.ok()`. Odróżniaj brak zmiennej od błędu kodowania i błędu wartości. Przy diagnozie pokaż nazwę klucza oraz źródło, a przy sekrecie pomiń jego zawartość.

~~~rust
#[derive(Default)]
struct Warstwa {
    limit: Option<usize>,
    json: Option<bool>,
}
#[derive(Debug, PartialEq)]
struct Konfiguracja {
    limit: usize,
    json: bool,
}
fn polacz(warstwy: impl IntoIterator<Item = Warstwa>)
    -> Result<Konfiguracja, &'static str>
{
    let mut wynik = Konfiguracja { limit: 100, json: false };
    for w in warstwy {
        if let Some(limit) = w.limit { wynik.limit = limit; }
        if let Some(json) = w.json { wynik.json = json; }
    }
    if wynik.limit == 0 { return Err("limit musi być dodatni"); }
    Ok(wynik)
}
fn main() {
    let plik = Warstwa { limit: Some(50), json: Some(true) };
    let cli = Warstwa { limit: None, json: Some(false) };
    assert_eq!(polacz([plik, cli]),
        Ok(Konfiguracja { limit: 50, json: false }));
    assert!(polacz([Warstwa { limit: Some(0), json: None }]).is_err());
}
~~~

Pętla koduje jawny priorytet źródeł. `None` zachowuje wcześniejszą decyzję, więc brak flagi nie usuwa ustawienia pliku. Walidacja następuje po scaleniu; to pozwala poprawić niskopriorytetową wartość przez jawny argument. Jeżeli produkt wymaga odrzucania każdego niepoprawnego pliku, waliduj także każdą warstwę osobno i udokumentuj tę surowszą politykę. Wynikowy typ nie przechowuje już opcji oznaczających brak decyzji.

Do prawdziwego parsera argumentów można użyć **third-party** `clap`, ale parser nie rozwiązuje reguł domenowych. `OsString` i `PathBuf` zachowują ścieżki niebędące UTF-8 na systemach, które na to pozwalają. Własny parser na `env::args()` może spanikować na takim argumencie; `args_os()` jest właściwym wejściem, gdy interfejs akceptuje ścieżki. Ciąg po `--` traktuj według dokumentowanej gramatyki jako argument pozycyjny, również gdy zaczyna się od minusa.

## Diagnostyka kompilatora

Częsty błąd dotyczy pożyczania argumentu z tymczasowej kolekcji:

~~~compile_fail
fn main() {
    let nazwa = vec![String::from("raport")][0].as_str();
    println!("{nazwa}");
}
~~~

Kompilator zgłasza zniszczenie wartości tymczasowej, gdy referencja nadal jest potrzebna. Zachowaj kolekcję w nazwanej zmiennej albo przenieś wybraną `String` do konfiguracji. Nie naprawiaj błędu przez wyciek pamięci lub wymuszanie `'static`. W konfiguracji żyjącej przez cały proces własność `PathBuf` i `String` zwykle upraszcza projekt za niewielki koszt jednorazowej alokacji.

## Praktyka produkcyjna

Udostępnij stabilny format maszynowy, np. JSON Lines, i osobny format dla ludzi. Wersjonuj kontrakt wyniku, ustal kodowanie i zakończenia wierszy. Nie włączaj kolorów w danych przeznaczonych do potoku; rozpoznanie terminala jest wskazówką, natomiast jawna flaga ma ostatnie słowo. Pomoc i wersja powinny działać bez połączenia z siecią lub bazą.

Konfigurację czytaj raz podczas startu. W Edition 2024 `set_var` i `remove_var` wymagają uwzględnienia bezpieczeństwa; przenośny proces wielowątkowy powinien unikać ich używania. Testom przekazuj warstwę środowiska jako dane, a procesowi potomnemu ustawiaj `Command::env`. Zobacz [kontrakt set_var](https://doc.rust-lang.org/std/env/fn.set_var.html), zweryfikowany 2026-11-11. To eliminuje także wyścigi testów o wspólne zmienne.

Rejestruj pochodzenie ustawień, np. `limit=50 (plik)`, lecz nigdy token dostępu. Wbudowana komenda pokazująca konfigurację powinna redagować sekrety niezależnie od implementacji `Debug`. Zmianę domyślnego limitu traktuj jak zmianę zachowania publicznego: może wpłynąć na pamięć, opóźnienie i skrypty mimo niezmienionej składni.

## Sprawdź, czy rozumiesz

- Dlaczego `Option<bool>` jest potrzebne w warstwie, lecz zbędne w gotowej konfiguracji?
- Która warstwa powinna zamienić błąd walidacji na kod procesu?
- Co zgubisz, konwertując ścieżkę przez `to_string_lossy()` przed otwarciem pliku?

## Ćwiczenia

- `C01-1` — podstawowe: Wyznacz wynik dla domyślnego limitu 100, pliku 50, środowiska 20 i braku flagi; następnie dodaj flagę 7 i opisz pochodzenie wartości. [Rozwiązanie](../rozwiazania/15_aplikacje_cli/01_komendy_argumenty_i_konfiguracja.md#c01-1).
- `C01-2` — praktyczne: Zaprojektuj mapowanie czterech wyników: sukces, błąd argumentów, niepoprawny rekord wejścia i brak dostępu do pliku. Podaj kanał komunikatu oraz kod. [Rozwiązanie](../rozwiazania/15_aplikacje_cli/01_komendy_argumenty_i_konfiguracja.md#c01-2).
- `C01-3` — pogłębione: Dodaj do scalania opcjonalną wielkość partii i warunek partia <= limit. Pokaż test granicy oraz wyjaśnij różnicę walidacji warstw i wyniku. [Rozwiązanie](../rozwiazania/15_aplikacje_cli/01_komendy_argumenty_i_konfiguracja.md#c01-3).

## Powiązane tematy

- [Strumienie i testy procesu](02_strumienie_sygnaly_testy_i_dystrybucja.md)
- [Konfiguracja i integracje](../18_serializacja_konfiguracja_i_integracje/02_konfiguracja_sekrety_i_odpornosc_integracji.md)
- [Własne błędy](../07_obsluga_bledow/04_wlasne_bledy_i_api.md)
