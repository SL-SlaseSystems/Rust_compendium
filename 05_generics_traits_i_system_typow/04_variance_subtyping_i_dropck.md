[← Spis treści](../README.md)
<!-- status: expanded -->

# Variance, subtyping i drop check

> Przykłady: **stable**, Rust 1.90.0, Edition 2024. Źródła sprawdzono 11 listopada 2026 r.

## Cele

Po tym rozdziale potrafisz:

- odróżnić skrócenie lifetime od dziedziczenia nominalnych typów;
- wyjaśnić zagrożenie wynikające z covariance mutowalnego slotu;
- dobrać marker `PhantomData` do rzeczywistego ownership i sprawdzić kolejność niszczenia;

## Model — kierunek podstawienia i obserwacja w destruktorze


Variance mówi, jak relacja subtype między parametrami wpływa na typ
kontenera. W Rust praktyczna relacja subtype dotyczy głównie lifetimes:
dłuższy lifetime może być użyty tam, gdzie oczekiwany jest krótszy.

## Trzy warianty

Dla konstruktora `F<T>`:

- covariant — `T <: U` implikuje `F<T> <: F<U>`;
- contravariant — kierunek się odwraca;
- invariant — brak konwersji w obu kierunkach.

Typowe przypadki:

| Typ | Variance w `T` |
|---|---|
| `&'a T` | covariant w `'a` i `T` |
| `&'a mut T` | covariant w `'a`, invariant w `T` |
| `*const T` | covariant |
| `*mut T` | invariant |
| `fn(T) -> U` | contravariant w `T`, covariant w `U` |
| `UnsafeCell<T>` | invariant |

Mutowalność wymusza invariance, bo inaczej można byłoby włożyć krótszą
referencję do miejsca oczekiwanego jako dłuższe.

## Skracanie lifetime

~~~rust
fn skroc<'krotki>(x: &'static str, _: &'krotki ()) -> &'krotki str {
    x
}

fn main() {
    static TEKST: &str = "static";
    let lokalny = ();
    let krotszy = skroc(TEKST, &lokalny);
    assert_eq!(krotszy, "static");
}
~~~

Covariance pozwala potraktować `&'static str` jako krótsze `&'a str`.

## Dlaczego `&mut T` jest invariant

Hipotetyczna covariance pozwoliłaby:

~~~text
let mut dluga: &'static str = "żyje długo";
let slot: &mut &'short str = &mut dluga; // gdyby było dozwolone
*slot = &lokalny_string;
// dluga stałaby się wiszącą referencją po zniszczeniu lokalnej
~~~

Kompilator odrzuca potrzebną koercję. `&mut` jest jednak covariant względem
lifetime samej pożyczki, więc długą wyłączną pożyczkę można reborrowować na
krócej.

## `PhantomData`

Raw pointer w strukturze może nie informować kompilatora o logicznym
ownership. `PhantomData<T>` wpływa na variance, auto traits i drop check bez
zajmowania miejsca.

~~~rust
use std::marker::PhantomData;
use std::ptr::NonNull;

struct Wlasciciel<T> {
    ptr: NonNull<T>,
    _posiada: PhantomData<T>,
}

fn main() {
    let x = Box::new(7);
    let ptr = NonNull::from(Box::leak(x));
    let w = Wlasciciel { ptr, _posiada: PhantomData };
    let raw = w.ptr.as_ptr();
    std::mem::forget(w);
    // SAFETY: raw pochodzi z Box::leak i jest odzyskiwany dokładnie raz.
    unsafe { drop(Box::from_raw(raw)) };
}
~~~

W prawdziwym ownerze `Drop` zwalniałby pointer, a implementacja wymagałaby
analizy ZST, alignment, allocatora, covariance i panic.

`PhantomData<fn(T)>`, `PhantomData<*const T>` oraz `PhantomData<&'a T>` mają
inne skutki. Nie wybieraj formy na pamięć; sprawdź Nomicon i testy kompilacji.

## Drop check

Drop checker zapewnia, że dane potrzebne destruktorowi nie znikną przed
destruktorem. Implementacja `Drop` może obserwować pola lub referencje nawet
wtedy, gdy ciało wydaje się ich nie używać w zwykłym kodzie.

`#[may_dangle]` jest niestabilnym, unsafe mechanizmem używanym przez wybrane
typy standard library do rozluźniania dropck. Nie jest narzędziem dla zwykłej
aplikacji.

## Reguły — podtypowanie nie jest konwersją danych

Dwa nominalnie różne typy struktur nie stają się podtypami tylko dlatego, że mają identyczne pola. Rust nie ma ogólnego dziedziczenia struktur. Główne praktyczne podstawienia opisane tutaj dotyczą referencji z różnymi lifetimes oraz relacji wyższego rzędu. Koercja `&String` do `&str` pochodzi z `Deref`, a nie z podtypowania `String <: str`.

Dla `&'a mut T` rozpatruj osobno oba parametry. Możesz skrócić czas samej pożyczki przez reborrow, lecz nie możesz dowolnie skrócić lifetime referencji przechowywanej w `T`. Właśnie taki slot umożliwiałby zapis krótszej referencji do miejsca, które właściciel nadal uważa za `'static`. Invariance chroni zarówno późniejszy odczyt, jak i możliwość zapisu.

~~~rust
fn ustaw<T>(slot: &mut T, nowa: T) { *slot = nowa; }
fn main() {
    let mut tekst = String::from("pierwszy");
    {
        let krotka = &mut tekst;
        ustaw(krotka, String::from("drugi"));
    }
    tekst.push('!');
    assert_eq!(tekst, "drugi!");
}
~~~

Krótka pożyczka całego `String` nie zmienia typu danych w slocie. Odróżniaj ją od próby podstawienia `&mut &'short str` w miejsce `&mut &'static str`. W analizie variance zapisanie pełnego typu z oboma poziomami referencji zwykle wyjaśnia, który lifetime naprawdę się zmienia.

## PhantomData nie jest dowodem bezpieczeństwa

Marker ma zerowy rozmiar, lecz wpływa na relacje typu. `PhantomData<&'a T>` modeluje zależność od współdzielonej pożyczki, `PhantomData<T>` logiczną własność, a `PhantomData<fn(T)>` pozycję argumentową z contravariance. Ich wpływ na auto traits również się różni: sygnatura funkcji nie oznacza fizycznego przechowywania `T`. Wybranie markera tylko po to, aby uzyskać `Send` może ukryć rzeczywistą zależność od niebezpiecznego zasobu.

W przykładzie `Wlasciciel` powyżej nazwa jest demonstracyjna: typ nie ma kompletnej implementacji właściciela i ręcznie odzyskuje `Box` dokładnie raz. Nie kopiuj tego szkicu jako gotowego smart pointera. Prawdziwa abstrakcja musi rozstrzygać niezmienniki alokatora, ważność i wyrównanie wskaźnika, inicjalizację, aliasowanie oraz zachowanie przy częściowej inicjalizacji i panice.

Drop checking jest osobnym obowiązkiem od zwykłego ostatniego użycia. Destruktor może odczytać pożyczone dane przy wyjściu z zakresu, więc dane muszą wtedy nadal istnieć. Nawet jeśli obecne ciało `Drop` niczego nie czyta, generyczny kontrakt nie powinien opierać bezpieczeństwa na przypadkowym braku odczytu. `#[may_dangle]` jest **nightly**, związane z `dropck_eyepatch` i wymaga niebezpiecznej deklaracji oraz dodatkowych zobowiązań; nie stosuj go jako sposobu uciszenia zwykłego błędu lifetime.

## Diagnostyka kompilatora

Poniżej zapis wymagałby przedłużenia `'a` do `'static`. Kompilator odrzuca go, ponieważ mutowalny slot musi nadal przechowywać referencję spełniającą deklarowany typ.

~~~compile_fail
fn podmien<'a>(slot: &mut &'static str, krotki: &'a str) {
    *slot = krotki;
}
fn main() {}
~~~

Dodanie `'a: 'static` zmieniłoby wymaganie na przyjmowanie wyłącznie odpowiednio długich referencji; nie umożliwiłoby zapisywania lokalnego tekstu. W błędach dropck sprawdź kolejność deklaracji właściciela i strażnika, a nie tylko ostatnią linię jawnego użycia referencji. Struktura z destruktorem może być używana niejawnie przy końcu scope.

## Praktyka produkcyjna

Większość kodu aplikacyjnego nie potrzebuje ręcznego projektowania variance. Korzystaj z `Vec`, `Box`, `Rc` i standardowych referencji, których kontrakty są już przeanalizowane. W bibliotece wykorzystującej raw pointers zapisuj, co marker ma modelować, i testuj pożądane oraz zabronione koercje.

Test kompilacji jest przykładem kontraktu, nie dowodem soundness dla wszystkich parametrów. Do analizy własnego kontenera dodaj przegląd auto traits, destruktora i możliwości wywołania każdego publicznego bezpiecznego API. Rozważ, czy założenia nadal obowiązują po zmianie pola z referencji na `Cell`, bo interior mutability może zmienić covariance w invariance.

## Sprawdź, czy rozumiesz

1. Czy `Deref` i subtyping są tym samym mechanizmem?
2. W którym parametrze `&'a mut T` jest covariant, a w którym invariant?
3. Dlaczego pusty destruktor może zmienić wymagania lifetime typu generycznego?

## Ćwiczenia

- `A21-1` — podstawowe: napisz funkcję skracającą `&'static str` do lifetime lokalnego argumentu [Rozwiązanie](../rozwiazania/05_generics_traits_i_system_typow/04_variance_subtyping_i_dropck.md#a21-1).
- `A21-2` — praktyczne: zastąp własny surowy właściciel bezpiecznym `Box<T>` i pokaż, kto niszczy wartość [Rozwiązanie](../rozwiazania/05_generics_traits_i_system_typow/04_variance_subtyping_i_dropck.md#a21-2).
- `A21-3` — pogłębione: zbuduj strażnik z `Drop`, który czyta pożyczony tekst; ustaw zakresy tak, aby właściciel zawsze przeżywał strażnika [Rozwiązanie](../rozwiazania/05_generics_traits_i_system_typow/04_variance_subtyping_i_dropck.md#a21-3).

## Źródła i zakres stabilności

Pierwszeństwo ma [Reference: subtyping and variance](https://doc.rust-lang.org/reference/subtyping.html). Analizę destruktorów i `may_dangle` uzupełnia [Rustonomicon: drop check](https://doc.rust-lang.org/nomicon/dropck.html); marker opisuje [PhantomData](https://doc.rust-lang.org/std/marker/struct.PhantomData.html).

## Powiązane tematy

- [Lifetimes](../03_ownership_i_pamiec/05_lifetimes.md)
- [HRTB i GAT](05_hrtb_gat_rpit_i_impl_trait.md)
- [Layout i niezainicjalizowana pamięć](../21_unsafe_soundness_i_model_pamieci/03_layout_alignment_i_uninitialized_memory.md)
