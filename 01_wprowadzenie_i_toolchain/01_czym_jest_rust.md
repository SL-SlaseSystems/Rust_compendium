[← Spis treści](../README.md)
<!-- status: expanded -->

# Czym jest Rust

> Przykłady: **stable**, Rust 1.90.0, Edition 2024. Źródła uzupełniono 11 listopada 2026 r.; nie deklarujemy testu na Rust 1.98.1.
> Przykłady: **stable**, Rust 1.90.0, Edition 2024. Źródła uzupełniono 11 listopada 2026 r.; nie deklarujemy testu na Rust 1.98.1.

## Cele

Po tym rozdziale potrafisz:

- wyjaśnić, jakie gwarancje daje bezpieczny Rust i gdzie kończy się ich zakres;
- opisać własność (ownership) jako protokół zarządzania zasobem;
- uzasadnić wybór Rusta dla konkretnego CLI, usługi sieciowej albo komponentu systemowego, nazywając koszty tej decyzji.

## Model: gwarancje i granice

Rust jest kompilowanym z wyprzedzeniem (ahead-of-time, AOT) językiem ogólnego przeznaczenia, o statycznym systemie typów. Nie potrzebuje odśmiecania pamięci (garbage collection, GC), bo sprawdza w czasie kompilacji reguły własności, pożyczania (borrowing) i czasów życia referencji. Własność jest statycznym protokołem zasobów: każda wartość ma w danej chwili jednego właściciela, przeniesienie przekazuje mu obowiązek zwolnienia zasobu, a wyjście właściciela z zakresu normalnie wywołuje `Drop`. Nie jest to bezwarunkowe: bezpieczny kod może celowo nie uruchomić destruktora przez `mem::forget`, a proces może zostać przerwany. Pożyczka udziela ograniczonego dostępu bez przekazywania tego obowiązku.

W bezpiecznym Rustcie nie da się wyrazić operacji, które naruszają te reguły. W szczególności typowe użycie referencji nie prowadzi do wiszących referencji, podwójnego zwolnienia ani wyścigu danych (data race). Brak wyścigów danych nie oznacza jednak braku wszystkich błędów współbieżności: program może nadal mieć zakleszczenie (deadlock), głodzenie, utratę komunikatu albo błędny protokół biznesowy.

Granica bezpieczeństwa nie jest hasłem marketingowym. `unsafe` pozwala użyć operacji niedostępnych w bezpiecznym podzbiorze, między innymi dereferencji surowego wskaźnika, wywołania funkcji `unsafe` czy odczytu pola `union`. Nie wyłącza reguł języka ani nie czyni niezdefiniowanego zachowania poprawnym: autor kodu `unsafe` musi udowodnić i utrzymać jego niezmienniki tak, by bezpieczny użytkownik API nie mógł wywołać niezdefiniowanego zachowania. Tę odpowiedzialność mają też granice FFI. Zobacz [Rust Reference: `unsafe`](https://doc.rust-lang.org/reference/unsafety.html) i [zachowania uznawane za niezdefiniowane](https://doc.rust-lang.org/reference/behavior-considered-undefined.html).

## Reguły własności w praktyce

Poniższy przykład pożycza tekst jako `&str`; funkcja może go odczytać, lecz wywołujący zachowuje właściciela `String`.

~~~rust
fn etykieta_dla(nazwa: &str) -> String {
    format!("zadanie: {nazwa}")
}

fn main() {
    let nazwa = String::from("indeks");
    let etykieta = etykieta_dla(&nazwa);

    assert_eq!(nazwa, "indeks");
    assert_eq!(etykieta, "zadanie: indeks");
}
~~~

Dobór `&str` jest częścią kontraktu API: funkcja nie potrzebuje zasobu na własność, więc nie powinna go żądać. Gdy funkcja ma przechować wartość lub przekazać ją do innego właściciela, parametr `String` może być właściwszy. `String::clone` tworzy osobny, własny bufor; semantyka `Clone` zależy jednak od typu — `Rc::clone` i `Arc::clone` dodają współwłasność, nie wykonują głębokiej kopii zasobu. Nie jest to naprawa błędu, którą należy stosować odruchowo. Reguły i przykłady przenoszenia opisuje [The Rust Programming Language: ownership](https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html).

## Kompilacja, abstrakcje i koszt

`rustc` zwykle buduje program w modelu AOT, a `Cargo` organizuje wywołanie kompilatora oraz zależności. Uproszczony obraz aktualnej implementacji to: tekst źródłowy → tokeny i `AST` → `HIR` → `THIR` → `MIR` → `LLVM-IR` → kod maszynowy oraz linkowanie. `HIR` służy między innymi inferencji i kontroli typów, `THIR` pomaga przy wzorcach, a `MIR` przy kontroli pożyczek i analizach przepływu danych. To mapa implementacji kompilatora, nie stabilne API języka; szczegóły mogą się zmieniać. [Przewodnik po kompilatorze](https://rustc-dev-guide.rust-lang.org/overview.html) opisuje ten przepływ.

Abstrakcje o zerowym koszcie (zero-cost abstractions), takie jak iteratory, generyki i domknięcia, nie powinny dodawać narzutu wykonania tylko dlatego, że są abstrahowane. Monomorfizacja i optymalizacja często usuwają warstwy pośrednie. Nie jest to obietnica, że każdy kod Rust będzie automatycznie szybki: alokacje, kopiowanie, zły układ danych, blokady, I/O i algorytm nadal mają koszt. Mierz konkretny scenariusz przed optymalizacją.

Ten model przenosi część pracy na kompilację. Duże grafy zależności, wiele instancji generyków, złożone granice `trait` i trudne do wywnioskowania typy mogą wydłużyć kompilację, zwiększyć zużycie pamięci kompilatora oraz utrudnić diagnostykę. Są to kompromisy, nie wada ani dowód wyższości języka.

## Co konkretnie mierzyć w prototypie

Gwarancja języka jest własnością poprawnego programu, a nie dowodem, że każda użyta zależność jest poprawna. Bezpieczna funkcja biblioteki może opierać się wewnętrznie na `unsafe`; błąd tej implementacji narusza jej obietnicę. Przy audycie odróżnij używanie bezpiecznego API od dowodu poprawności wszystkich warstw pod nim. Dotyczy to również systemowych alokatorów i kodu obcego. Przegląd granicy powinien obejmować warunki wstępne, wszystkie sposoby wywołania i zachowanie przy błędzie.

Dla przykładowego narzędzia dzienników ustal wejścia o różnych rozmiarach, limit pamięci oraz to, czy wynik można wypisywać strumieniowo. Zmierz wersję `release` na tym samym sprzęcie i tych samych danych. Zapisz osobno czas budowania od zera, czas małej zmiany i czas wykonania gotowego programu. Wynik jednego pomiaru nie rozstrzyga wszystkich trzech problemów: szybszy runtime może wymagać kosztowniejszej kompilacji.

Bezpieczeństwo pamięci dopuszcza wyciek pamięci, `panic!` i świadome przerwanie procesu. Nie oznacza też odporności na błędne uprawnienia ani wyczerpanie zasobów. Jeżeli usługa poprawnie trzyma milion aktywnych buforów, system typów nie uzna ich za błąd. Limit liczby żądań oraz rozmiaru bufora jest osobnym niezmiennikiem aplikacji. To dobry przykład przejścia od gwarancji języka do wymagania produktu.

## Diagnostyka kompilatora

Poniższy przykład celowo nie kompiluje się: `String` nie implementuje `Copy`, więc przypisanie przenosi jego własność do `drugi`. Użycie `pierwszy` po tym przeniesieniu łamie kontrakt właściciela; kompilator zwykle wskaże miejsce przeniesienia i późniejszego użycia jako „borrow of moved value”.

~~~compile_fail
fn main() {
    let pierwszy = String::from("raport");
    let drugi = pierwszy;

    println!("{pierwszy} i {drugi}");
}
~~~

Naprawa zależy od intencji: pożycz `&pierwszy`, jeśli oba miejsca tylko czytają; przenieś wartość i przestań używać starej nazwy, jeśli zmienia się właściciel; użyj `clone`, tylko gdy program rzeczywiście potrzebuje drugiego, niezależnego zasobu. Samo ukrycie komunikatu lub przypadkowe klonowanie nie naprawia modelu zasobów.

## Praktyka produkcyjna

Rust jest decyzją o ryzyku i kosztach, nie rankingiem języków.

- **CLI:** rozważ Rust, gdy narzędzie ma być pojedynczym, przenośnym binarium, szybko startować, przetwarzać pliki lub wykonywać dużo pracy lokalnie. Dla krótkiego automatu z dojrzałym SDK w innym ekosystemie krótszy czas dostawy może przeważyć nad tymi zaletami.
- **Usługa sieciowa:** Rust pasuje, gdy obciążenie, współbieżność, opóźnienia lub ograniczenia pamięci są istotne i zespół może utrzymać model własności oraz obserwowalność. Nie eliminuje błędów protokołu, limitów zasobów, problemów z bazą danych ani potrzeby limitowania ruchu. Model współbieżności Rusta pomaga wykryć wiele błędów przed uruchomieniem, lecz nie projektuje systemu za zespół; zobacz [rozdział o współbieżności](https://doc.rust-lang.org/book/ch16-00-concurrency.html).
- **Komponent systemowy:** Rust jest mocnym kandydatem przy pracy blisko pamięci, urządzeń lub FFI, gdzie koszt defektu pamięci jest wysoki. Granice `unsafe` i interfejsów obcych wymagają jednak małych, audytowalnych API, testów na platformach docelowych i jasnych niezmienników. Istniejący kod, wymagany ABI, narzędzia platformowe oraz doświadczenie zespołu pozostają ważnymi danymi wejściowymi.

W każdym z tych przypadków zapisz mierzalne kryterium decyzji: budżet pamięci, opóźnienie, czas startu, niezawodność, czas kompilacji, dostępność bibliotek albo koszt wdrożenia. Następnie sprawdź je prototypem i pomiarem.

## Sprawdź, czy rozumiesz

1. Dlaczego brak `GC` nie oznacza ręcznego `free` w typowym bezpiecznym kodzie?
2. Która część problemu współbieżności pozostaje po wyeliminowaniu wyścigów danych?
3. Dlaczego „zero-cost” nie zwalnia z pomiaru wydajności ani czasu kompilacji?

## Ćwiczenia

- `W01-1` — podstawowe: dla CLI, które przetwarza lokalnie milion wierszy dziennika, wypisz trzy kryteria wyboru Rusta i jedno kryterium, które może przemawiać za inną technologią. Porównaj z [rozwiązaniem](../rozwiazania/01_wprowadzenie_i_toolchain/01_czym_jest_rust.md#w01-1).
- `W01-2` — praktyczne: opisz granice odpowiedzialności bezpiecznego Rusta w usłudze sieciowej obsługującej współbieżne żądania. Wskaż po jednym ryzyku, którego model typów nie usuwa, i mechanizm jego ograniczenia. Porównaj z [rozwiązaniem](../rozwiazania/01_wprowadzenie_i_toolchain/01_czym_jest_rust.md#w01-2).
- `W01-3` — pogłębione: zaproponuj decyzję dla komponentu systemowego z FFI. Uzasadnij, gdzie umieścisz `unsafe`, jakie niezmienniki udokumentujesz i kiedy koszt kompilacji lub ekosystemu zmieni wybór. Porównaj z [rozwiązaniem](../rozwiazania/01_wprowadzenie_i_toolchain/01_czym_jest_rust.md#w01-3).

## Źródła i zakres stabilności

Granice `unsafe`: [Reference: unsafety](https://doc.rust-lang.org/reference/unsafety.html) i [undefined behavior](https://doc.rust-lang.org/reference/behavior-considered-undefined.html). Lokalne przykłady sprawdzane są na Rust 1.90.0; parametry wewnętrznej architektury kompilatora nie są stabilnym API.

## Powiązane tematy

- [Instalacja i toolchain](02_instalacja_i_toolchain.md)
- [Ownership, move i `Copy`](../03_ownership_i_pamiec/02_ownership_move_i_copy.md)
- [Referencje i borrowing](../03_ownership_i_pamiec/03_referencje_i_borrowing.md)
- [`unsafe` i soundness](../21_unsafe_soundness_i_model_pamieci/01_unsafe_i_soundness.md)
