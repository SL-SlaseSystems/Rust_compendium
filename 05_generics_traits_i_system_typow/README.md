[← Spis treści](../README.md)

# 5. Generics, traits i system typów

## Dla kogo i po co

Dla osób, które znają już ownership i chcą projektować elastyczne API bez utraty kontroli nad typami i kosztem wykonania. Końcowe rozdziały są zaawansowane i pomagają rozumieć granice abstrakcji Rust.

## Wymagania wstępne

Ownership, lifetimes, struktury, enumy i podstawowy `match`.

## Kolejność materiałów

1. [Generics i const generics](01_generics_i_const_generics.md)
2. [Traits i associated items](02_traits_i_associated_items.md)
3. [Konwersje, DST i trait objects](03_konwersje_dst_i_trait_objects.md)
4. [Variance, subtyping i drop check](04_variance_subtyping_i_dropck.md)
5. [HRTB, GAT, RPIT i `impl Trait`](05_hrtb_gat_rpit_i_impl_trait.md)
6. [Dyn compatibility, vtables i dispatch](06_dyn_compatibility_vtables_i_dispatch.md)

## Po tym dziale

Potrafisz dobierać dispatch statyczny i dynamiczny, definiować kontrakty traitów oraz czytać bardziej wymagające sygnatury z lifetime bounds.

## Jak pracować z działem

Pierwsze trzy rozdziały tworzą podstawowy ciąg: ograniczenia algorytmu, wspólne zachowanie oraz konwersje i wymazanie typu. Czytaj je przed variance i mechanizmami wyższego rzędu. Trzy kolejne opracowania wymagają umiejętności śledzenia pożyczek i odróżniania konkretnego typu od publicznego kontraktu.

Zestawy `A18`–`A23` zawierają zadania podstawowe, praktyczne i pogłębione oraz pełne rozwiązania. Zanim użyjesz mechanizmu, nazwij potrzebę: czy klient wybiera typ, implementacja ukrywa wynik, czy lifetime wyniku zależy od każdego wywołania? Odpowiedź pozwala wybrać parametr, associated type, GAT, RPIT albo trait object bez przypadkowego mieszania ich znaczeń.

## Punkt kontrolny

Potrafisz uzasadnić każdy bound konkretną operacją, rozpoznać konflikt coherence i użyć newtype. Wyjaśniasz, dlaczego `?Sized` dopuszcza także zwykłe typy, `&mut T` jest invariant w `T`, a `dyn Trait` nie daje stabilnego ABI. Umiesz wyłączyć metodę z dynamicznego interfejsu przez `where Self: Sized`.

Przykłady są stable i sprawdzane na Rust 1.90.0, Edition 2024. Wyjątki takie jak TAIT, `generic_const_exprs` i `may_dangle` mają jawny status nightly oraz bramkę. Ich opis nie jest zapowiedzią stabilizacji.

## Co dalej

Przejdź do kolekcji i iteratorów. Do variance, HRTB i vtables wracaj przy projektowaniu bibliotek oraz analizie kodu niskopoziomowego.

Następny dział: [Kolekcje, iteratory i closures](../06_kolekcje_iteratory_i_closures/README.md).
