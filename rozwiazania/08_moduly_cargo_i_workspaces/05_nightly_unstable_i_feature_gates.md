[← Spis treści](../../README.md)

# Rozwiązania: Nightly, unstable i feature gates

[Rozdział źródłowy](../../08_moduly_cargo_i_workspaces/05_nightly_unstable_i_feature_gates.md).

## B09-1

~~~rust
fn parzyste(v:&[u32])->impl Iterator<Item=u32>+'_ {v.iter().copied().filter(|n|n%2==0)}
fn main(){assert_eq!(parzyste(&[1,2,3,4]).collect::<Vec<_>>(),[2,4]);}
~~~
Jest to stabilny typ niejawny w pozycji wyniku, bez aliasu TAIT.

## B09-2

Zadanie MSRV uruchamia `cargo +1.90.0 test --locked`, jeśli właśnie 1.90 jest deklarowanym minimum projektu. Zadanie stable używa jawnie wybranej stabilnej wersji i wykonuje testy oraz dokumentację. Trzecie zadanie przypina dostępny snapshot nightly i wykonuje wybrane narzędzie audytu. Jego wynik nie zastępuje dwóch pierwszych. Rzeczywiste dostępne komponenty i snapshot należy sprawdzić przed wpisaniem ich do konfiguracji; te polecenia są procedurą, a nie deklaracją wykonania tutaj.

## B09-3

Przykładowa decyzja: eksperymentalny parser wymaga konkretnego niestabilnego API, ponieważ stabilna alternatywa zwiększa zmierzony czas przetwarzania o 20%. Właściciel mierzy oba warianty na zapisanym zbiorze co kwartał. Kod pozostaje w osobnym crate bez wycieku niestabilnych typów. Powrót do stable następuje po stabilizacji wymaganej funkcji i przejściu testów zgodności albo gdy różnica stabilnej alternatywy spadnie poniżej 5%. Liczby są jawnymi kryteriami przykładowej decyzji, a nie wynikami benchmarku kompendium.

