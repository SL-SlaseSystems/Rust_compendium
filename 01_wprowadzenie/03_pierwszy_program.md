[← Spis treści](../README.md)

# Pierwszy program

Minimalny program wykonywalny ma funkcję wejściową `main`:

~~~rust
fn main() {
    println!("Witaj, Rust!");
}
~~~

`fn` rozpoczyna deklarację funkcji. Ciało jest blokiem w nawiasach klamrowych.
`println!` jest makrem — wykrzyknik odróżnia wywołanie makra od funkcji.
Średnik kończy wyrażenie, którego wynik ignorujemy.

## Formatowanie wartości

Makra formatujące sprawdzają literał formatu podczas kompilacji:

~~~rust
fn main() {
    let jezyk = "Rust";
    let rok = 2015;
    println!("{jezyk} 1.0 ukazał się w {rok} roku");
    println!("hex: {rok:#x}, wyrównanie: {rok:>8}");
    println!("debug: {:?}", vec![1, 2, 3]);
}
~~~

`{}` używa `Display`, a `{:?}` — `Debug`. Wiele typów domenowych powinno
implementować `Display` dopiero wtedy, gdy istnieje jedno sensowne,
użytkowe przedstawienie.

## `main` zwracające wynik

Program może propagować błąd z `main`:

~~~rust
use std::error::Error;
use std::fs;

fn main() -> Result<(), Box<dyn Error>> {
    let katalog = std::env::temp_dir();
    let plik = katalog.join("rust-kompendium-pierwszy-program.txt");
    fs::write(&plik, "dane")?;
    let tekst = fs::read_to_string(&plik)?;
    assert_eq!(tekst, "dane");
    fs::remove_file(plik)?;
    Ok(())
}
~~~

Typ `()` oznacza brak użytecznej wartości. `Box<dyn Error>` pozwala w małym
programie przyjąć różne typy błędów. W bibliotece lepszy jest zazwyczaj
konkretny enum błędu.

## Kompilacja bez Cargo

Pojedynczy plik można skompilować bezpośrednio:

~~~text
rustc main.rs
./main
~~~

W normalnym projekcie używa się Cargo, bo zarządza strukturą, flagami,
zależnościami, testami i dokumentacją.

## Typowe błędy

- pominięcie `!` w nazwie makra;
- próba użycia niezadeklarowanej zmiennej;
- średnik po wyrażeniu, którego wartość miała zostać zwrócona;
- literówka w liczbie argumentów formatu.

Komunikaty kompilatora zawierają kod błędu. Polecenie
`rustc --explain E0382` pokazuje dłuższe objaśnienie danego kodu.

## Powiązane tematy

- [Funkcje, wyrażenia i instrukcje](../02_podstawy_jezyka/03_funkcje_wyrazenia_i_instrukcje.md)
- [Cargo w praktyce](04_cargo_w_praktyce.md)
- [`Option` i `Result`](../06_bledy/01_option_i_result.md)
