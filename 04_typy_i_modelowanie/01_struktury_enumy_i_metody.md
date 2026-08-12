[← Spis treści](../README.md)

# Struktury, enumy i metody

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

## Powiązane tematy

- [Wzorce i `match`](02_wzorce_i_match.md)
- [Builder, typestate i state machine](../13_wzorce_i_architektura/02_builder_typestate_i_state_machine.md)
- [Layout, alignment i `repr`](../zaawansowane/03_layout_alignment_i_uninitialized_memory.md)
