[← Spis treści](../README.md)
<!-- status: expanded -->

# Mapy, zbiory i `Entry`

> Przykłady: **stable**, Rust 1.90.0, Edition 2024. Źródła sprawdzono 11 listopada 2026 r.

## Cele

Po tym rozdziale potrafisz:

- dobrać mapę według wyszukiwania, zakresów i wymaganej kolejności wyników;
- użyć `Entry` do aktualizacji bez osobnego sprawdzania istnienia;
- utrzymać zgodność `Eq`, `Hash`, `Ord` i pożyczonego widoku klucza;

## Model — klucz wyznacza tożsamość rekordu


Standard library oferuje mapy haszujące i uporządkowane oraz odpowiadające im
zbiory.

| Kolekcja | Porządek | Typowy dostęp |
|---|---|---|
| `HashMap<K, V>` | niegwarantowany | średnio O(1) |
| `BTreeMap<K, V>` | według `Ord` | O(log n) |
| `HashSet<T>` | niegwarantowany | średnio O(1) |
| `BTreeSet<T>` | według `Ord` | O(log n) |

Nie polegaj na kolejności iteracji `HashMap`. Może się różnić między
uruchomieniami.

## Liczenie przez `Entry`

~~~rust
use std::collections::HashMap;

fn main() {
    let mut licznik = HashMap::new();
    for slowo in "rust jest szybki rust".split_whitespace() {
        *licznik.entry(slowo).or_insert(0_u32) += 1;
    }
    assert_eq!(licznik.get("rust"), Some(&2));
    assert_eq!(licznik.get("brak"), None);
}
~~~

Entry łączy sprawdzenie obecności z uzyskaniem miejsca i rozróżnia `Occupied` od `Vacant`. Metody
`or_insert_with` i `or_default` unikają niepotrzebnego tworzenia wartości.

## Wymagania kluczy

`HashMap` wymaga `Eq + Hash`, a `BTreeMap` — `Ord`. Implementacje `Eq` i
`Hash` muszą być zgodne: jeśli `a == b`, oba muszą mieć ten sam hash.
Nie zmieniaj przez interior mutability części klucza wpływającej na hash lub
porządek, gdy klucz jest w kolekcji.

~~~rust
use std::collections::BTreeMap;

fn main() {
    let mut indeks = BTreeMap::new();
    indeks.insert(20, "dwadzieścia");
    indeks.insert(10, "dziesięć");
    let klucze: Vec<_> = indeks.keys().copied().collect();
    assert_eq!(klucze, [10, 20]);

    let zakres: Vec<_> = indeks.range(10..20).map(|(&k, &v)| (k, v)).collect();
    assert_eq!(zakres, [(10, "dziesięć")]);
}
~~~

B-tree wspiera wydajne zakresy i deterministyczną iterację. Hash map jest
dobrym wyborem dla dokładnego wyszukiwania, ale jej domyślny hasher chroni
przed pewnymi atakami kosztem wydajności. Zmiana hashera jest decyzją
bezpieczeństwa, nie tylko mikrooptymalizacją.

## Operacje zbiorowe

~~~rust
use std::collections::BTreeSet;

fn main() {
    let a = BTreeSet::from([1, 2, 3]);
    let b = BTreeSet::from([3, 4]);
    assert_eq!(a.intersection(&b).copied().collect::<Vec<_>>(), [3]);
    assert_eq!(a.difference(&b).copied().collect::<Vec<_>>(), [1, 2]);
}
~~~

## Pożyczone wyszukiwanie

Dzięki `Borrow` w `HashMap<String, V>` można wyszukiwać przez `&str` bez
alokowania nowego `String`. To ważny wzorzec projektowania kluczy API.

## Reguły — niezmienność znaczenia klucza

Hash jest pomocniczym indeksem, a nie identyfikatorem bez kolizji. Różne klucze mogą mieć ten sam hash i kolekcja musi rozstrzygnąć równość przez `Eq`. Wymaganie działa w jedną stronę: równe klucze muszą mieć zgodne hashe. Dla klucza z kilkoma polami zazwyczaj najbezpieczniej wyprowadzić `PartialEq`, `Eq` i `Hash` z tego samego zestawu pól zamiast ręcznie pomijać jedno tylko w wybranej implementacji.

Zmiana klucza przez `Cell`, globalny stan lub niepoprawne porównanie może zepsuć zachowanie kolekcji. Dokumentacja określa to jako błąd logiczny z efektami ograniczonymi do kolekcji, a nie zgodę na niezdefiniowane zachowanie w bezpiecznym kodzie. Analogicznie w `BTreeMap` relacja `Ord` powinna tworzyć spójny porządek, niezależny od chwilowej konfiguracji lub odczytu zegara.

## Entry oraz koszt inicjalizacji

`entry` opisuje jedną operację logiczną: znajdź klucz i uzyskaj zajęte albo wolne miejsce. Dzięki temu unikasz osobnego `contains_key` i późniejszego wyszukania do modyfikacji. Nie polegaj na konkretnej liczbie wywołań hashera jako gwarancji przenośnego API. `or_insert(wartosc)` oblicza argument wcześniej; `or_insert_with(|| ...)` tworzy wartość dopiero dla pustego wpisu. Klucz przekazany do `entry` i tak jest tworzony przed wywołaniem.

~~~rust
use std::collections::HashMap;
fn main() {
    let mut grupy: HashMap<&str, Vec<u32>> = HashMap::new();
    for (grupa, id) in [("A", 1), ("B", 2), ("A", 3)] {
        grupy.entry(grupa).or_default().push(id);
    }
    assert_eq!(grupy.get("A").unwrap(), &[1, 3]);
    assert_eq!(grupy.get("B").unwrap(), &[2]);
    assert!(!grupy.contains_key("C"));
}
~~~

`or_default` tworzy pusty `Vec` wyłącznie dla nowej grupy. Kolejność wartości wewnątrz wektora jest kolejnością dodawania, lecz kolejność samych grup w `HashMap` nie jest określona. Jeżeli wynik ma być stabilnym raportem, przejdź do posortowanego widoku kluczy albo użyj `BTreeMap`. To osobna decyzja od sposobu aktualizacji wpisów.

## Wyszukiwanie przez pożyczkę

`HashMap<String, V>::get("klucz")` korzysta z `Borrow<str>` i nie musi alokować `String`. Typ pożyczony musi mieć zgodne `Hash` i `Eq`. Własny klucz porównywany bez wielkości liter nie może bezmyślnie pożyczać zwykłego `str` z inną semantyką równości. `AsRef<str>` nie daje mapie takiej samej obietnicy.

Set przechowuje klucze bez osobnych wartości i nadaje się do deduplikacji albo relacji przynależności. Przed użyciem `intersection`, `union` i `difference` określ, czy odbiorca potrzebuje tylko leniwego widoku wyników, czy nowego posiadanego zbioru. Zbieranie wszystkich wyników nie jest konieczne do samego sprawdzenia, czy istnieje wspólny element.

## Diagnostyka kompilatora

Aktywne pożyczenie wartości blokuje późniejszą mutację całej mapy. Realokacja oraz zmiana organizacji wpisów mogłyby unieważnić referencję.

~~~compile_fail
use std::collections::HashMap;
fn main() {
    let mut mapa = HashMap::from([("A", 1)]);
    let a = mapa.get("A").unwrap();
    mapa.insert("B", 2);
    println!("{a}");
}
~~~

Jeśli potrzebujesz tylko liczby, użyj `.copied()` przed zmianą. Jeśli chcesz aktualizować wartość, `get_mut` lub `entry` dają właściwe uprawnienie. Dla wielu wpisów trzeba użyć udokumentowanego bezpiecznego API rozdzielającego dostęp albo podzielić operację na fazy; dwa przypadkowo różne napisy nie są dla zwykłych dwóch `get_mut` dowodem rozłączności.

## Praktyka produkcyjna

Dobierz kolekcję do danych przeciwnika i kontraktu raportowania. Nie wymieniaj domyślnego hashera wyłącznie na podstawie mikrobenchmarku z małymi całkowitymi kluczami, jeżeli produkcyjny serwis przyjmuje nieufne napisy. Ochrona przed kolizjami, koszt haszowania i limity liczby wpisów należą do jednej decyzji.

W kontrolowanych raportach i migawkach wymagaj stabilnej kolejności jawnie. Nie zapisuj przypadkowej kolejności `HashMap` do testów snapshot jako kontraktu. Zwracaj uwagę również na pojemność: w obecnej implementacji iteracja `HashMap` może odwiedzać puste kubełki i kosztować O(capacity), więc mapa po usunięciu większości wpisów może być droższa niż sugeruje `len`. To szczegół aktualnej implementacji opisany w dokumentacji API, sprawdzonej 11 listopada 2026 r.

## Sprawdź, czy rozumiesz

1. Czy dwa różne klucze mogą poprawnie mieć ten sam hash?
2. Kiedy `or_insert_with` oszczędza pracę, a kiedy klucz nadal alokuje?
3. Jak uzyskać deterministyczny raport z mapy?

## Ćwiczenia

- `A26-1` — podstawowe: zlicz słowa przez `entry` i sprawdź brak klucza dla nieobecnego słowa [Rozwiązanie](../rozwiazania/06_kolekcje_iteratory_i_closures/03_mapy_zbiory_i_entry.md#a26-1).
- `A26-2` — praktyczne: w `HashMap<String, u32>` wyszukaj przez `&str`, a następnie zwiększ licznik bez klonowania klucza [Rozwiązanie](../rozwiazania/06_kolekcje_iteratory_i_closures/03_mapy_zbiory_i_entry.md#a26-2).
- `A26-3` — pogłębione: zbuduj `BTreeMap` grupujące identyfikatory i zwróć raport w porządku kluczy; zachowaj kolejność identyfikatorów w grupie [Rozwiązanie](../rozwiazania/06_kolekcje_iteratory_i_closures/03_mapy_zbiory_i_entry.md#a26-3).

## Źródła i zakres stabilności

Zgodność kluczy i koszt iteracji: [HashMap](https://doc.rust-lang.org/std/collections/struct.HashMap.html). Porządek i zakresy: [BTreeMap](https://doc.rust-lang.org/std/collections/struct.BTreeMap.html). Semantyka pożyczonego klucza: [Borrow](https://doc.rust-lang.org/std/borrow/trait.Borrow.html).

## Powiązane tematy

- [Traits i associated items](../05_generics_traits_i_system_typow/02_traits_i_associated_items.md)
- [Iteratory](05_iteratory.md)
- [Wydajność i lokalność cache](../20_wydajnosc_i_optymalizacja/01_wydajnosc_i_zero_cost.md)
