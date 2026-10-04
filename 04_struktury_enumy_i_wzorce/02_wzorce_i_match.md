[← Spis treści](../README.md)

# Wzorce i `match`

Wzorzec jednocześnie sprawdza kształt wartości i wiąże jej części. Występuje
w `match`, `let`, parametrach funkcji, `if let`, `while let` i `let else`.

## Wyczerpujący `match`

~~~rust
#[derive(Debug)]
enum Zdarzenie {
    Klik { x: i32, y: i32 },
    Klawisz(char),
    Zamkniecie,
}

fn opis(z: Zdarzenie) -> String {
    match z {
        Zdarzenie::Klik { x: 0, y } => format!("lewa krawędź, y={y}"),
        Zdarzenie::Klik { x, y } => format!("klik {x},{y}"),
        Zdarzenie::Klawisz('q' | 'Q') => "wyjście".into(),
        Zdarzenie::Klawisz(c) if c.is_ascii_digit() => "cyfra".into(),
        Zdarzenie::Klawisz(_) => "inny klawisz".into(),
        Zdarzenie::Zamkniecie => "zamknięcie".into(),
    }
}

fn main() {
    assert_eq!(opis(Zdarzenie::Klawisz('7')), "cyfra");
    assert_eq!(opis(Zdarzenie::Klik { x: 0, y: 8 }), "lewa krawędź, y=8");
    assert_eq!(opis(Zdarzenie::Zamkniecie), "zamknięcie");
}
~~~

Ramiona są sprawdzane od góry. Guard `if` nie uczestniczy w sprawdzaniu
wyczerpującości tak precyzyjnie jak sam wzorzec.

## Refutable i irrefutable

Wzorzec `let (x, y) = para` pasuje zawsze i jest irrefutable. `Some(x)` może
nie pasować, więc wymaga `if let`, `let else` albo `match`.

~~~rust
fn dodaj(opcja: Option<i32>, suma: &mut i32) {
    if let Some(x) = opcja {
        *suma += x;
    }
}

fn main() {
    let mut suma = 0;
    for x in [Some(2), None, Some(5)] {
        dodaj(x, &mut suma);
    }
    assert_eq!(suma, 7);
}
~~~

## Destrukturyzacja i ownership

Wzorzec na wartości może przenieść pola. `ref` i `ref mut` jawnie wiążą
referencję, choć match ergonomics często robi to automatycznie, gdy dopasowana
wartość jest referencją.

~~~rust
struct Rekord {
    nazwa: String,
    wynik: u32,
}

fn main() {
    let r = Rekord { nazwa: "Ada".into(), wynik: 10 };
    let Rekord { ref nazwa, wynik } = r;
    assert_eq!(nazwa, "Ada");
    assert_eq!(wynik, 10);
    assert_eq!(r.nazwa, "Ada");
}
~~~

Operator `@` wiąże całą wartość i jednocześnie ją sprawdza:

~~~rust
fn kategoria(n: u8) -> &'static str {
    match n {
        zero @ 0 => {
            assert_eq!(zero, 0);
            "zero"
        }
        mala @ 1..=9 => {
            assert!(mala < 10);
            "mała"
        }
        _ => "duża",
    }
}

fn main() {
    assert_eq!(kategoria(7), "mała");
}
~~~

`..` ignoruje pozostałe pola lub elementy. Podkreślenie `_` niczego nie
wiąże; nazwa zaczynająca się od podkreślenia nadal może przenieść wartość.

## Powiązane tematy

- [Struktury i enumy](01_struktury_enumy_i_metody.md)
- [Sterowanie przepływem](../02_podstawy_jezyka/04_sterowanie_przeplywem.md)
- [`Option` i `Result`](../07_obsluga_bledow/01_option_i_result.md)
