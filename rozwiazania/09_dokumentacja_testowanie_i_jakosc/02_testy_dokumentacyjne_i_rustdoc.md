[← Spis treści](../../README.md)

# Rozwiązania: Testy dokumentacyjne i rustdoc

[Rozdział źródłowy](../../09_dokumentacja_testowanie_i_jakosc/02_testy_dokumentacyjne_i_rustdoc.md).

## B11-1

~~~rust
fn ostatni(v:&[u8])->Option<u8>{v.last().copied()}
fn main(){assert_eq!(ostatni(&[1,2]),Some(2));assert_eq!(ostatni(&[]),None);}
~~~

## B11-2

~~~compile_fail
fn main(){let s=String::from("dane");let t=s;println!("{s} {t}");}
~~~
`String` nie jest `Copy`. Przypisanie do `t` przenosi własność, więc użycie `s` daje błąd użycia przeniesionej wartości.

## B11-3

Opis powinien zawierać: format i walidację wejścia, sposób przejęcia ścieżki, `# Errors` dla tworzenia/zapisu/rename, gwarancję zachowania starego pliku i rozróżnienie widoczności od trwałości danych. `# Panics` podaj wyłącznie dla realnie występujących warunków. Przykład wykonaj w izolowanym katalogu. Osobne testy powinny sprawdzać niepoprawną konfigurację przed mutacją, udany odczyt po zapisie i błąd dostępu bez utraty starej treści. Platformowych gwarancji rename nie wyprowadzaj z jednego testu na jednym systemie.

