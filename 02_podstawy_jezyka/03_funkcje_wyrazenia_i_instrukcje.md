[← Spis treści](../README.md)
<!-- status: expanded -->

# Funkcje, wyrażenia i instrukcje

> Stan opisu: Rust 1.98.1, Edition 2024, zweryfikowany 10 września 2026 r.;
> przykłady wykonano lokalnie przez Rust 1.90.0.

## Cele

Po tym rozdziale:

- odróżnisz deklarację elementu, instrukcję deklaracji i instrukcję wyrażeniową
  od wyrażenia,
- przewidzisz typ i wartość bloku na podstawie jego wyrażenia końcowego,
- rozpoznasz role `return`, typu `!` i koercji,
- odróżnisz element funkcyjny od wskaźnika `fn` i closure,
- potraktujesz sygnaturę, ABI i `#[inline]` jako świadome granice projektu,
- użyjesz bloku do czytelnego ograniczenia pożyczki albo czasu życia zasobu.

## Model — elementy, instrukcje i wartości

Rust jest językiem zorientowanym na wyrażenia, ale ciało bloku nie jest tylko
ciągiem wyrażeń. Warto rozdzielić pięć pojęć:

- **deklaracja elementu** (*item declaration*), na przykład `fn pomocnicza() {}`,
  wprowadza nazwany element. Sama deklaracja nie jest kolejną akcją wykonywaną
  w czasie działania programu;
- **instrukcja deklaracji** (*declaration statement*) umieszcza w bloku element
  albo wiązanie `let`;
- **wyrażenie** oblicza wartość i ma typ — wyrażeniami są między innymi
  wywołanie, blok, `if` oraz `match`;
- **instrukcja wyrażeniowa** (*expression statement*) oblicza wyrażenie dla
  efektu i ignoruje jego wartość. Zwykle powstaje po dopisaniu średnika;
- **wyrażenie końcowe** (*tail expression*) to opcjonalne ostatnie wyrażenie
  bloku bez średnika. Jego wartość i typ stają się wartością i typem bloku.

Gdy wyrażenia końcowego nie ma, blok zwraca jedyną wartość typu jednostkowego:
`()`. Typ i jego wartość zapisuje się tak samo.

~~~rust
fn etykieta(wynik: u8) -> &'static str {
    fn prog() -> u8 {
        50
    }

    let zaliczone = wynik >= prog();
    if zaliczone {
        "zaliczone"
    } else {
        "do poprawy"
    }
}

fn main() {
    let liczba = {
        let bazowa = 20;
        bazowa + 1
    };
    let jednostka = {
        liczba + 1;
    };

    assert_eq!(liczba, 21);
    assert_eq!(jednostka, ());
    assert_eq!(etykieta(72), "zaliczone");
}
~~~

Lokalny element `prog` istnieje jako funkcja, lecz wykona się dopiero po
wywołaniu. W przeciwieństwie do closure taka lokalnie zadeklarowana funkcja nie
przechwytuje wiązań z otaczającego bloku.

## Sygnatura jako granica API i inferencji

W sygnaturze `fn nazwa(parametr: Typ) -> Wynik` typ każdego parametru jest
jawny. Kompilator wnioskuje wiele typów wewnątrz ciała, ale nie używa ciała do
zmiany kontraktu widzianego przez wywołujących. Jawny wynik opisuje między innymi
własność wartości i sposób raportowania błędu. Brak `-> Wynik` oznacza `-> ()`.

Parametr jest **wzorcem nieobalalnym** (*irrefutable pattern*): musi pasować do
każdej wartości zadeklarowanego typu. Pozwala to rozpakować krotkę od razu na
granicy funkcji.

~~~rust
fn srodkowa((_, y, _): (i32, i32, i32)) -> i32 {
    y
}

fn zapisz(komunikat: &str) {
    println!("{komunikat}");
}

fn main() {
    assert_eq!(srodkowa((10, 20, 30)), 20);
    assert_eq!(zapisz("gotowe"), ());
}
~~~

Wzorzec obalalny, taki jak `Some(x)`, nie może być parametrem: dla `None` nie
utworzyłby wiązania `x`.

~~~compile_fail
fn zawartosc(Some(x): Option<i32>) -> i32 {
    x
}

fn main() {}
~~~

## Wyrażenie końcowe, `return` i typ `!`

Wartość końcową zwykle zwraca się bez `return`. Jawne `return wyrazenie` jest
czytelne przy wcześniejszym wyjściu, na przykład w klauzuli ochronnej. Samo
wyrażenie `return` ma typ `!`, bo sterowanie nigdy nie biegnie dalej tą ścieżką.

~~~rust
fn bezpieczne_dzielenie(a: i32, b: i32) -> Option<i32> {
    if b == 0 {
        return None;
    }
    Some(a / b)
}

fn main() {
    assert_eq!(bezpieczne_dzielenie(8, 2), Some(4));
    assert_eq!(bezpieczne_dzielenie(8, 0), None);
}
~~~

Typ `!`, nazywany typem nigdy, opisuje obliczenie, które nie kończy się zwykłą
wartością. Należą do nich `return`, `break` z odpowiedniego kontekstu,
`continue`, `panic!` oraz wywołanie funkcji zadeklarowanej jako `-> !`. W miejscu
koercji `!` może zostać dopasowane do oczekiwanego typu.

~~~rust
fn liczba_albo_panika(tekst: &str) -> u32 {
    match tekst.parse() {
        Ok(wartosc) => wartosc,
        Err(_) => panic!("oczekiwano liczby"),
    }
}

fn main() {
    assert_eq!(liczba_albo_panika("42"), 42);
}
~~~

Oba ramiona `match` mają jeden wspólny typ `u32`, ponieważ rozbieżne ramię z
`panic!` koercjonuje się z `!` do `u32`. To nie znaczy, że powstaje fikcyjna
wartość — ta ścieżka po prostu nie wraca.

## Element funkcyjny, wskaźnik `fn` i closure

Nazwa funkcji użyta jako wartość tworzy **element funkcyjny** (*function item*).
Każda funkcja — a także każda jej monomorfizacja — ma własny, nienazywalny
bezpośrednio typ elementu. Typ ten ma rozmiar zero, bo sama wartość jednoznacznie
wskazuje funkcję już przez swój typ.

`fn(A) -> R` jest natomiast typem **wskaźnika funkcji**. Może przechować różne
funkcje o zgodnej sygnaturze i umożliwia wywołanie pośrednie. Koercja z elementu
funkcyjnego do wskaźnika zachodzi wtedy, gdy kontekst oczekuje `fn`, na przykład
przez adnotację typu, argument funkcji albo ujednolicenie ramion `if`.

~~~rust
fn zwieksz(x: i32) -> i32 {
    x + 1
}

fn zmniejsz(x: i32) -> i32 {
    x - 1
}

fn wybierz(w_gore: bool) -> fn(i32) -> i32 {
    if w_gore { zwieksz } else { zmniejsz }
}

fn main() {
    let element = zwieksz;
    assert_eq!(std::mem::size_of_val(&element), 0);

    let wskaznik: fn(i32) -> i32 = zwieksz;
    let bez_przechwycenia: fn(i32) -> i32 = |x| x * 2;

    assert_eq!(wskaznik(4), 5);
    assert_eq!(bez_przechwycenia(4), 8);
    assert_eq!(wybierz(false)(4), 3);
}
~~~

Nieasynchroniczne closure, które niczego nie przechwytuje, może koercjonować się
do zgodnego wskaźnika `fn`. Closure przechwytujące ma stan, więc taka konwersja
nie istnieje. Gdy API powinno przyjmować także funkcje ze stanem, właściwsze są
granice oparte na `Fn`, `FnMut` albo `FnOnce`.

## ABI funkcji

ABI (*application binary interface*) określa między innymi konwencję wywołania:
jak przekazywane są argumenty i wynik. Zwykła deklaracja `fn` używa domyślnego
ABI Rust, czyli `extern "Rust"`. To ABI służy kodowi Rust, ale **nie gwarantuje
stabilności między wersjami kompilatora** i nie jest kontraktem FFI ani ABI
wtyczek.

~~~rust
extern "Rust" fn rustowa(x: i32) -> i32 {
    x + 1
}

extern "C" fn dla_c(x: i32) -> i32 {
    x + 1
}

fn main() {
    let a: fn(i32) -> i32 = rustowa;
    let b: extern "C" fn(i32) -> i32 = dla_c;
    assert_eq!((a(4), b(4)), (5, 5));
}
~~~

`extern "C"` wybiera ABI C i tworzy inny typ wskaźnika niż zwykłe `fn`. Samo
ABI C nie rozwiązuje kwestii układu złożonych typów, nazw symboli, paniki ani
bezpieczeństwa pamięci. Co więcej, zapis `extern fn` bez łańcucha oznacza ABI C,
a nie domyślne ABI Rust — dlatego na granicy języków warto pisać ABI jawnie.

## Blok jako granica pożyczki i zasobu

Blok jest wyrażeniem, a zarazem wyznacza zakres nazw i moment niszczenia wartości.
Może więc dokumentować, że widok przez referencję albo strażnik zasobu nie jest
potrzebny w dalszej części funkcji.

~~~rust
use std::cell::Cell;

struct Straznik<'a>(&'a Cell<bool>);

impl Drop for Straznik<'_> {
    fn drop(&mut self) {
        self.0.set(true);
    }
}

fn main() {
    let mut tekst = String::from("Rust");
    {
        let prefiks = &tekst[..2];
        assert_eq!(prefiks, "Ru");
    }
    tekst.push_str("!");

    let zakonczono = Cell::new(false);
    {
        let _zasob = Straznik(&zakonczono);
        assert!(!zakonczono.get());
    } // `Drop` strażnika zachodzi deterministycznie tutaj.

    assert_eq!(tekst, "Rust!");
    assert!(zakonczono.get());
}
~~~

Dzięki NLL (*non-lexical lifetimes*) pożyczka może często skończyć się już przy
ostatnim użyciu referencji, nawet bez dodatkowego bloku. Jawny zakres nie jest
więc obowiązkowym „trikiem na borrow checker”. Pozostaje użyteczny, gdy granica
ma być widoczna dla czytelnika albo gdy deterministyczny moment `Drop` wpływa na
zachowanie programu, na przykład zwalnia blokadę lub zamyka transakcję.

## Diagnostyka kompilatora

### Średnik zmienia wynik na `()`

~~~compile_fail
fn odpowiedz() -> i32 {
    40 + 2;
}

fn main() {}
~~~

Kompilator zgłasza niezgodność oczekiwanego `i32` i znalezionego `()`. Usuń
średnik, aby wyrażenie stało się końcowym, albo jawnie zwróć `return 40 + 2;`.

### Brak kontekstu koercji elementu funkcyjnego

~~~compile_fail
fn dodaj_jeden(x: i32) -> i32 { x + 1 }
fn odejmij_jeden(x: i32) -> i32 { x - 1 }

fn main() {
    let mut operacja = dodaj_jeden;
    operacja = odejmij_jeden;
    assert_eq!(operacja(10), 9);
}
~~~

Pierwsze przypisanie wywnioskowało unikatowy typ elementu `dodaj_jeden`, a nie
ogólny `fn(i32) -> i32`. Naprawą jest podanie oczekiwanego typu już przy
wiązaniu: `let mut operacja: fn(i32) -> i32 = dodaj_jeden;`.

### Kod nieosiągalny

~~~compile_fail
#![deny(unreachable_code)]

fn wynik() -> i32 {
    return 42;
    7
}

fn main() {
    let _ = wynik();
}
~~~

Po `return` sterowanie nie przejdzie do `7`. Zwykle jest to ostrzeżenie lintu;
`deny(unreachable_code)` celowo podnosi je tutaj do błędu. Usuń martwy kod lub
napraw warunek sterujący — nie wyciszaj automatycznie informacji o zgubionej
ścieżce.

## Praktyka produkcyjna

- Traktuj sygnaturę funkcji jak mały kontrakt: pokazuj w niej pożyczanie,
  własność, błędy i ograniczenia generyczne, zamiast polegać na domysłach z ciała.
- Użyj `fn` dla jednorodnego, bezstanowego callbacku. Gdy wywoływalny obiekt ma
  przechwytywać konfigurację, przyjmij odpowiednią rodzinę `Fn*`.
- Nie wystawiaj ABI Rust jako stabilnej granicy między niezależnie budowanymi
  artefaktami. Dla FFI zaprojektuj osobną, wąską granicę i jawnie wybierz ABI.
- `#[inline]`, `#[inline(always)]` i `#[inline(never)]` są wskazówkami, a nie
  gwarancjami. Kompilator może je zignorować. Nadmierne wymuszanie może zwiększyć
  rozmiar kodu i czas kompilacji, a przez presję na cache instrukcji nawet
  pogorszyć wydajność — decyzję potwierdź pomiarem w profilu zbliżonym do produkcji.
- Dodawaj osobny blok, gdy wyraża ważną granicę pożyczki lub `Drop`; nie mnoż go,
  jeśli NLL już daje czytelny i poprawny kod.

Źródła normatywne:

- [The Rust Reference — Functions](https://doc.rust-lang.org/reference/items/functions.html)
- [The Rust Reference — Statements](https://doc.rust-lang.org/reference/statements.html)
- [The Rust Reference — Expressions](https://doc.rust-lang.org/reference/expressions.html)
- [The Rust Reference — Block expressions](https://doc.rust-lang.org/reference/expressions/block-expr.html)
- [The Rust Reference — Function item types](https://doc.rust-lang.org/reference/types/function-item.html)
- [The Rust Reference — Function pointer types](https://doc.rust-lang.org/reference/types/function-pointer.html)
- [The Rust Reference — ABI](https://doc.rust-lang.org/reference/items/external-blocks.html#abi)
- [The Rust Reference — Type coercions](https://doc.rust-lang.org/reference/type-coercions.html)
- [The Rust Reference — `inline` attribute](https://doc.rust-lang.org/reference/attributes/codegen.html#the-inline-attribute)

## Sprawdź, czy rozumiesz

1. Dlaczego `{ oblicz(); }` ma typ `()`, choć `oblicz()` może zwracać liczbę?
2. Dlaczego dwie funkcje o tej samej sygnaturze nie mają tego samego typu
   elementu funkcyjnego, ale mogą trafić do jednej zmiennej typu `fn`?
3. Kiedy dodatkowy blok ma znaczenie mimo działania NLL?
4. Dlaczego `extern "Rust" fn` nie powinno być trwałym ABI wtyczki?

## Ćwiczenia

### P03-1 · Poziom: podstawowe

Bez uruchamiania kodu przewidź typ i wartość `a`, `b` oraz `c`. Wyjaśnij rolę
każdego średnika, a dopiero potem sprawdź przewidywanie kompilatorem.

~~~rust
fn main() {
    let a = { 20 + 1 };
    let b = { 20 + 1; };
    let c = {
        let x = a * 2;
        x
    };
    let _ = (a, b, c);
}
~~~

[Rozwiązanie](../rozwiazania/02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md#p03-1)

### P03-2 · Poziom: praktyczne

Napraw program z diagnostyki o elementach funkcyjnych tak, aby `operacja` mogła
najpierw wskazywać `dodaj_jeden`, a potem `odejmij_jeden`. Następnie przypisz do
drugiego wskaźnika nieasynchroniczne closure bez przechwyceń i przetestuj oba
wywołania. Nie używaj `Box`, `dyn` ani rzutowania `as`.

[Rozwiązanie](../rozwiazania/02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md#p03-2)

### P03-3 · Poziom: pogłębione

Zaprojektuj dwie różne granice wywołania: funkcję przetwarzającą kolekcję przez
politykę, która może przechwycić konfigurację, oraz callback o ABI C. Dobierz
typy (`Fn*`, `fn` albo `extern "C" fn`), przygotuj test obu granic i uzasadnij,
dlaczego nie powinny mieć jednego wspólnego typu.

[Rozwiązanie](../rozwiazania/02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md#p03-3)

## Powiązane tematy

- [Sterowanie przepływem](04_sterowanie_przeplywem.md)
- [Closures i rodzina `Fn`](../06_kolekcje_iteratory_i_closures/04_closures_i_fn_traits.md)
- [Ownership i przenoszenie](../03_ownership_i_pamiec/02_ownership_move_i_copy.md)
- [Pożyczanie i referencje](../03_ownership_i_pamiec/03_referencje_i_borrowing.md)
- [Propagacja i operator `?`](../07_obsluga_bledow/02_propagacja_i_operator_question_mark.md)
