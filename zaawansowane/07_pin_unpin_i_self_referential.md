[← Spis treści](../README.md)

# `Pin`, `Unpin` i typy self-referential

`Pin<P>` gwarantuje, że pointee nie zostanie przeniesiony z miejsca, jeżeli
typ nie implementuje `Unpin`. Gwarancja dotyczy stabilności adresu, nie
„niemutowalności”.

## Dlaczego ruch szkodzi

Struktura przechowująca pointer do własnego pola staje się niepoprawna po
bitowym przeniesieniu: pole trafia pod nowy adres, a pointer nadal wskazuje
stary. Zwykły konstruktor nie może bezpiecznie zbudować takiej relacji przed
ustabilizowaniem miejsca.

## `Unpin`

Większość typów jest `Unpin` automatycznie. Dla nich `Pin<&mut T>` można
bezpiecznie rozpakować do `&mut T`, bo ruch nie łamie invariants.
`PhantomPinned` wyłącza auto-`Unpin`.

~~~rust
use std::marker::PhantomPinned;
use std::pin::Pin;
use std::ptr::NonNull;

struct Samoodniesienie {
    tekst: String,
    wskazuje_na_tekst: Option<NonNull<String>>,
    _pin: PhantomPinned,
}

impl Samoodniesienie {
    fn nowe(tekst: String) -> Pin<Box<Self>> {
        let mut pinned = Box::pin(Self {
            tekst,
            wskazuje_na_tekst: None,
            _pin: PhantomPinned,
        });

        let ptr = NonNull::from(&pinned.as_ref().get_ref().tekst);
        // SAFETY: obiekt jest już w Pin<Box<_>> i !Unpin; nie przeniesiemy
        // pola tekst przed Drop. Zmieniamy tylko pole z pointerem.
        unsafe {
            pinned.as_mut().get_unchecked_mut().wskazuje_na_tekst = Some(ptr);
        }
        pinned
    }

    fn tekst(self: Pin<&Self>) -> &str {
        let ptr = self.wskazuje_na_tekst.expect("inicjalizacja");
        // SAFETY: pointer wskazuje pole tekst tego przypiętego, żywego obiektu.
        unsafe { ptr.as_ref().as_str() }
    }
}

fn main() {
    let x = Samoodniesienie::nowe("stabilny adres".into());
    assert_eq!(x.as_ref().tekst(), "stabilny adres");
}
~~~

Ten wzorzec jest edukacyjny. W praktyce preferuj indeksy, offsety, arena
allocation albo crate generujący poprawne projekcje. Ręczne struktury
self-referential są trudne przy `Drop`, variance i mutacji pól.

## Co `Pin` gwarantuje

Gwarancja zaczyna obowiązywać, gdy wartość zostaje przypięta i musi trwać do
`drop`. Kod nie może:

- wydobyć `T` z `Pin<P>` dla `!Unpin`;
- nadpisać lub `mem::replace` przypiętej wartości;
- przenieść przypiętego pola podczas projekcji;
- ponownie użyć storage przed zakończeniem `drop`.

Sam `Pin<Box<T>>` można przenosić jako uchwyt — pointee na stercie pozostaje
pod tym samym adresem.

## Projekcja

Z `Pin<&mut Struct>` nie można automatycznie otrzymać
`Pin<&mut Field>`. Trzeba wiedzieć, które pola są strukturalnie przypięte.
`map_unchecked_mut` jest unsafe, a dowód obejmuje również `Drop`. Crate’y
**third-party** `pin-project` i `pin-project-lite` generują projekcje.

Nie każde pole musi być pinned. Pole niezależne od adresu można traktować jako
`Unpin`, ale destructor nie może go przenieść w sposób łamiący kontrakt.

## Future

Future wygenerowana przez `async` jest state machine. Może przechowywać lokalną
wartość oraz referencję do niej między punktami `await`, dlatego często jest
`!Unpin`. `Future::poll` przyjmuje `Pin<&mut Self>`, aby stan miał stabilny
adres.

`Box::pin(future)` daje przypięcie na stercie. Makro `pin!` może przypiąć
lokalnie; wynik nie może uciec poza stack frame.

## Drop guarantee

Kod opierający się na pinning może zakładać, że przed ponownym użyciem pamięci
uruchomiony zostanie destructor. Wyciekanie pamięci nadal jest możliwe i nie
jest UB samo w sobie, więc abstrakcja nie może wymagać, aby `Drop` na pewno
wykonał dowolny zewnętrzny efekt dla soundness.

## Powiązane tematy

- [`Future`, `Waker` i `poll`](../10_async/02_executor_waker_i_poll.md)
- [`PhantomData` i variance](04_variance_subtyping_i_dropck.md)
- [`unsafe` i soundness](01_unsafe_i_soundness.md)
