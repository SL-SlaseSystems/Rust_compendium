[← Spis treści](../README.md)

# Mapy, zbiory i `Entry`

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

Entry wykonuje wyszukiwanie raz i rozróżnia `Occupied` od `Vacant`. Metody
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

## Powiązane tematy

- [Traits i associated items](../04_typy_i_modelowanie/04_traits_i_associated_items.md)
- [Iteratory](05_iteratory.md)
- [Wydajność i lokalność cache](../13_wzorce_i_architektura/05_wydajnosc_i_zero_cost.md)
