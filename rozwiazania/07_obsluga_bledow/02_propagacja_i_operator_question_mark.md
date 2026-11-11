[← Spis treści](../../README.md)

# Rozwiązania: Propagacja i operator `?`

[Rozdział źródłowy](../../07_obsluga_bledow/02_propagacja_i_operator_question_mark.md).

## B02-1

~~~rust
fn para(s: &str) -> Result<(u16, u16), &'static str> {
    let (a,b) = s.split_once(':').ok_or("brak separatora")?;
    Ok((a.parse().map_err(|_| "lewa liczba")?, b.parse().map_err(|_| "prawa liczba")?))
}
fn main() {
    assert_eq!(para("3:4"), Ok((3,4)));
    assert_eq!(para("3"), Err("brak separatora"));
    assert_eq!(para("x:4"), Err("lewa liczba"));
}
~~~

## B02-2

~~~rust
fn main() {
    let wynik: Result<Vec<u32>, _> = ["1", "2", "3"].into_iter().map(str::parse).collect();
    assert_eq!(wynik.unwrap(), [1,2,3]);
    let blad: Result<Vec<u32>, _> = ["1", "x", "3"].into_iter().map(str::parse).collect();
    assert!(blad.is_err());
}
~~~
Zebrane sukcesy nie są zwracane przy błędzie; to kontrakt tego wariantu importu.

## B02-3

~~~rust
fn import(dane: &[&str]) -> (Vec<u32>, Vec<usize>) {
    let mut dobre = Vec::new(); let mut bledy = Vec::new();
    for (i,s) in dane.iter().enumerate() {
        match s.parse() { Ok(n) => dobre.push(n), Err(_) => bledy.push(i) }
    }
    (dobre,bledy)
}
fn main() { assert_eq!(import(&["1","x","y","4"]), (vec![1,4],vec![1,2])); }
~~~
Indeksy są zerowe. W produkcji należy ograniczyć rozmiar wejścia i raportu.

