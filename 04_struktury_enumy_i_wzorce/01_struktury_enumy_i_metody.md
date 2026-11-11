[← Spis treści](../README.md)
<!-- status: expanded -->

# Struktury, enumy i metody

> Przykłady: **stable**, Rust 1.90.0, Edition 2024. Źródła sprawdzono 11 listopada 2026 r.

## Cele

Po tym rozdziale potrafisz:

- zamodelować stany wykluczające się enumem zamiast niezależnymi flagami;
- utrzymać niezmiennik przez prywatne pola i walidowany konstruktor;
- dobrać `self`, `&self` oraz `&mut self` do skutku metody;

## Model — iloczyn pól i suma wariantów


Typy użytkownika pozwalają nadać danym znaczenie i utrzymywać invariants.
Struktura grupuje pola obecne jednocześnie, enum opisuje jeden z kilku
wariantów.

## Struktury

~~~rust
#[derive(Debug, PartialEq)]
struct Prostokat {
    szerokosc: u32,
    wysokosc: u32,
}

impl Prostokat {
    fn nowy(szerokosc: u32, wysokosc: u32) -> Self {
        Self { szerokosc, wysokosc }
    }

    fn pole(&self) -> u32 {
        self.szerokosc * self.wysokosc
    }

    fn skaluj(&mut self, mnoznik: u32) {
        self.szerokosc *= mnoznik;
        self.wysokosc *= mnoznik;
    }
}

fn main() {
    let mut p = Prostokat::nowy(3, 4);
    p.skaluj(2);
    assert_eq!(p.pole(), 48);
}
~~~

`Self` oznacza implementowany typ. Pierwszy parametr metody bywa `self`,
`&self` lub `&mut self` i jawnie opisuje ownership.

Tuple struct nadaje znaczenie pozycyjnym polom, np. `struct Metry(f64);`.
Unit struct nie ma pól i może być markerem. Widoczność typu i każdego pola
jest osobna — publiczna struktura może zachować prywatne invariants.

## Aktualizacja struktury

~~~rust
#[derive(Debug)]
struct Ustawienia {
    host: String,
    port: u16,
    tls: bool,
}

fn main() {
    let bazowe = Ustawienia {
        host: "localhost".into(),
        port: 8080,
        tls: false,
    };
    let produkcja = Ustawienia {
        host: "example.com".into(),
        tls: true,
        ..bazowe
    };
    assert_eq!(produkcja.port, 8080);
    assert!(produkcja.tls);
}
~~~

Update syntax przenosi pola niebędące `Copy`. Tutaj `bazowe.host` zostałoby
przeniesione, gdyby nie podano nowego `host`; zawsze analizuj ownership pól.

## Enumy

Każdy wariant może nieść inne dane:

~~~rust
enum Komenda {
    Zakoncz,
    Przesun { x: i32, y: i32 },
    Napis(String),
}

impl Komenda {
    fn wykonaj(self) -> String {
        match self {
            Self::Zakoncz => "koniec".into(),
            Self::Przesun { x, y } => format!("ruch {x},{y}"),
            Self::Napis(t) => t,
        }
    }
}

fn main() {
    assert_eq!(Komenda::Przesun { x: 2, y: -1 }.wykonaj(), "ruch 2,-1");
    assert_eq!(Komenda::Napis("hej".into()).wykonaj(), "hej");
    assert_eq!(Komenda::Zakoncz.wykonaj(), "koniec");
}
~~~

`Option<T>` i `Result<T, E>` są najważniejszymi enumami standard library.
Enum plus wyczerpujący `match` dobrze modeluje state machine i zamknięty zbiór
przypadków.

## Dobre praktyki

- waliduj w konstruktorze i ukrywaj pola, jeśli typ ma invariants;
- preferuj enum zamiast kilku booli opisujących wzajemnie wykluczające stany;
- dodawaj `#[non_exhaustive]` do publicznego typu tylko świadomie;
- nie uzależniaj protokołu binarnego od domyślnego layoutu typu.

## Reguły — reprezentuj tylko legalne stany

Struktura jest typem iloczynowym: wartość zawiera wszystkie swoje pola jednocześnie. Enum jest typem sumowym: wartość wybiera dokładnie jeden wariant wraz z jego polami. Gdy połączenie ma być albo rozłączone, albo połączone z uchwytem, enum wyklucza sprzeczność `polaczony == false` i niepustego aktywnego uchwytu. Dwie niezależne flagi wymagałyby ciągłego pilnowania tej relacji.

Prywatność obowiązuje na granicy modułu, nie między funkcjami tego samego modułu. Samo nazwanie metody `new` nie zmienia reguł języka: można nazwać konstruktor dowolnie i zwracać z niego `Result` lub `Option`. Jeżeli użytkownik może swobodnie zapisać publiczne pole, ominie walidację konstruktora. Ukryj więc pola wymagające niezmiennika i udostępnij tylko operacje, które go zachowują.

~~~rust
mod domena {
    #[derive(Debug, PartialEq)]
    pub struct Port(u16);
    impl Port {
        pub fn nowy(n: u16) -> Option<Self> {
            (n != 0).then_some(Self(n))
        }
        pub fn numer(&self) -> u16 { self.0 }
    }
}
fn main() {
    let port = domena::Port::nowy(8080).unwrap();
    assert_eq!(port.numer(), 8080);
    assert!(domena::Port::nowy(0).is_none());
}
~~~

Moduł zapewnia, że kod klienta nie skonstruuje `Port(0)` ani nie zmieni wnętrza po walidacji. Zakaz zera należy do przykładowej domeny, nie jest ogólną regułą wszystkich systemowych portów. Dwa typy takie jak `Port` i `LimitBajtow` zapobiegają również pomyleniu parametrów, nawet gdy oba mają liczbową reprezentację.

Receiver `&self` daje odczyt istniejącego obiektu, `&mut self` pozwala zmieniać tę samą tożsamość, a `self` konsumuje wartość. Metoda `do_wiadomosci(self) -> Wiadomosc` może przenieść posiadany bufor bez klonowania. `fn nowy(...) -> Self` nie ma receivera i jest funkcją skojarzoną, wywoływaną przez `Typ::nowy`.

Aktualizacja `..bazowe` pobiera tylko pola, których nie podano jawnie. Jeśli wszystkie pobrane pola są `Copy`, stara struktura może pozostać używalna. Gdy choć jedno posiadane pole zostaje przeniesione, analizuj częściową dostępność zamiast zakładać klon całego obiektu. W konstrukcji `Prostokat` powyżej działania liczbowe pokazują mechanikę metod; dla rozmiarów z zewnątrz produkcyjna metoda powinna użyć arytmetyki sprawdzanej.

## Diagnostyka kompilatora

Prywatne pole jest granicą walidacji. Próba bezpośredniej konstrukcji poza modułem nie przechodzi; to oczekiwana ochrona API.

~~~compile_fail
mod domena {
    pub struct Port(u16);
}
fn main() {
    let _port = domena::Port(0);
}
~~~

E0382 po aktualizacji struktury oznacza zwykle użycie przeniesionego pola. E0596 przy metodzie z `&mut self` może oznaczać brak `mut` na właścicielu albo próbę mutacji przez `&T`. Najpierw sprawdź, czy operacja powinna zmieniać obiekt; nie zamieniaj wszystkich metod na `&mut self` tylko po to, aby ujednolicić sygnatury.

## Praktyka produkcyjna

Dodawanie pola publicznej struktury może zepsuć konstrukcje literałowe klientów. Dodawanie wariantu enuma może zepsuć ich wyczerpujące `match`. `#[non_exhaustive]` sygnalizuje możliwość rozszerzeń na granicy crate'ów, ale utrudnia konstrukcję i wymusza gałąź rezerwową. Zaplanuj to przed publikacją API; w wewnętrznej maszynie stanów pełne sprawdzenie wariantów często jest cenniejsze.

Nie serializuj domyślnego układu pamięci przez kopiowanie bajtów struktury. Kolejność i wyrównanie pól oraz reprezentacja enuma nie tworzą automatycznie formatu pliku. Oddziel typ domenowy od formatu wymiany i jawnie waliduj deserializację. Dzięki temu zmiana reprezentacji nie zmienia przypadkowo protokołu.

## Sprawdź, czy rozumiesz

1. Jak enum usuwa nielegalne kombinacje dwóch flag?
2. Czy prywatne pole jest niedostępne dla innych funkcji tego samego modułu?
3. Kiedy receiver `self` pozwala uniknąć klonowania?

## Ćwiczenia

- `A16-1` — podstawowe: utwórz tuple struct `Metry(u32)` i metodę odczytującą wartość bez konsumowania [Rozwiązanie](../rozwiazania/04_struktury_enumy_i_wzorce/01_struktury_enumy_i_metody.md#a16-1).
- `A16-2` — praktyczne: zamodeluj `Stan::Oczekuje` i `Stan::Gotowy(String)`; metoda konsumująca ma oddać `Option<String>` [Rozwiązanie](../rozwiazania/04_struktury_enumy_i_wzorce/01_struktury_enumy_i_metody.md#a16-2).
- `A16-3` — pogłębione: zaprojektuj prywatne wymiary prostokąta i skalowanie, które przy przepełnieniu zachowuje obiekt bez zmian [Rozwiązanie](../rozwiazania/04_struktury_enumy_i_wzorce/01_struktury_enumy_i_metody.md#a16-3).

## Źródła i zakres stabilności

Kształt typów: [Reference: structs](https://doc.rust-lang.org/reference/items/structs.html) i [enumerations](https://doc.rust-lang.org/reference/items/enumerations.html). Wpływ rozszerzalności: [non_exhaustive](https://doc.rust-lang.org/reference/attributes/type_system.html#the-non_exhaustive-attribute).

## Powiązane tematy

- [Wzorce i `match`](02_wzorce_i_match.md)
- [Builder, typestate i state machine](../14_idiomy_wzorce_i_architektura/02_builder_typestate_i_state_machine.md)
- [Layout, alignment i `repr`](../21_unsafe_soundness_i_model_pamieci/03_layout_alignment_i_uninitialized_memory.md)
