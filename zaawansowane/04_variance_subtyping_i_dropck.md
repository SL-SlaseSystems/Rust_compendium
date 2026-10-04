[← Spis treści](../README.md)

# Variance, subtyping i drop check

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

## Powiązane tematy

- [Lifetimes](../03_ownership_i_pamiec/05_lifetimes.md)
- [HRTB i GAT](05_hrtb_gat_rpit_i_impl_trait.md)
- [Layout i niezainicjalizowana pamięć](03_layout_alignment_i_uninitialized_memory.md)
