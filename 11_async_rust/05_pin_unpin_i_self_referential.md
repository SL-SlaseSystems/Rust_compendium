[← Spis treści](../README.md)
<!-- status: expanded -->

# `Pin`, `Unpin` i typy self-referential

## Cele

Po tym rozdziale potrafisz:

- odróżnić przeniesienie uchwytu od przeniesienia pointee;
- rozpoznać wymagania projekcji, Drop i bezpiecznego zastępowania;


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

        // SAFETY: obiekt jest już w Pin<Box<_>> i !Unpin; nie przeniesiemy
        // pola tekst przed Drop. Zmieniamy tylko pole z pointerem.
        unsafe {
            let this = pinned.as_mut().get_unchecked_mut();
            let ptr = NonNull::from(&this.tekst);
            this.wskazuje_na_tekst = Some(ptr);
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
- wynieść starej żywej wartości przez `mem::replace`; `Pin::set` legalnie
  niszczy ją na miejscu przed zastąpieniem;
- przenieść przypiętego pola podczas projekcji;
- ponownie użyć storage przed zakończeniem `drop`.

Sam `Pin<Box<T>>` można przenosić jako uchwyt — pointee na stercie pozostaje
pod tym samym adresem.

## Projekcja

Z `Pin<&mut Struct>` nie można automatycznie otrzymać
`Pin<&mut Field>`. Trzeba wiedzieć, które pola są strukturalnie przypięte.
`map_unchecked_mut` jest unsafe, a dowód obejmuje również `Drop`. Crate’y
**third-party** `pin-project` i `pin-project-lite` generują projekcje.

Nie każde pole musi być strukturalnie przypięte. Pole nieobjęte tą
gwarancją można udostępniać zwykłą referencją mutowalną, jeśli nie narusza
to niezmienników struktury. Destructor nadal musi respektować kontrakt
pozostałych, przypiętych pól.

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


## Model — pinning jest kontraktem API wskaźnika

`Pin` nie dodaje runtime’owej flagi do obiektu i nie zatrzymuje kompilatora przed każdym możliwym ruchem. Ogranicza dostępne bezpieczne operacje przez typ wskaźnika. Kod `unsafe`, implementacja `DerefMut` i destruktor muszą respektować ten sam kontrakt. Samo dodanie `PhantomPinned` nie stabilizuje adresu wartości stojącej zwyczajnie na stosie; dopiero utworzenie odpowiedniego przypięcia rozpoczyna gwarancję.

Dla `T: Unpin` stabilność adresu nie jest wymagana przez kontrakt typu, więc `Pin::get_mut` udostępnia zwykłe `&mut T`. Dla `!Unpin` taka ogólna referencja umożliwiłaby `mem::replace`, dlatego nie jest dostępna bez dodatkowego dowodu. `Unpin` nie oznacza „typ na stosie”, a `!Unpin` nie oznacza „typ zawsze na stercie”. Makro `pin!` daje lokalne przypięcie, natomiast `Box::pin` stabilną alokację.

~~~rust
use std::pin::Pin;
fn main() {
    let przypiety = Box::pin(String::from("dane"));
    let adres = przypiety.as_ref().get_ref() as *const String;
    let mut przeniesiony_uchwyt = przypiety;
    assert_eq!(adres, przeniesiony_uchwyt.as_ref().get_ref() as *const String);
    Pin::as_mut(&mut przeniesiony_uchwyt).get_mut().push('!');
    assert_eq!(&*przeniesiony_uchwyt, "dane!");
}
~~~

Przeniesiono pudełko jako uchwyt, a obiekt `String` pozostał w tej samej alokacji. Nie wynika z tego, że jego bufor znaków nigdy nie zmieni adresu: `push` może realokować bufor wewnętrzny. Pinning `String` stabilizuje obiekt `String` zgodnie z odpowiednim kontraktem, nie wszystkie zasoby osiągalne przez jego pola. W dodatku `String` jest `Unpin`, więc bezpieczny dostęp nie obiecuje trwałej samoreferencji do jego bufora.

Projekcja pola musi określić, czy jest ono strukturalnie przypięte. Nie można jednocześnie obiecywać `Pin<&mut Pole>` i później przenosić tego pola w `Drop`. Dla struktur `repr(packed)` powstają dodatkowe problemy alignment i potencjalnego przenoszenia pól podczas niszczenia; nie łącz ich mechanicznie z pinningiem. Wygenerowane projekcje **third-party** upraszczają audyt, ale ich konfiguracja też musi odpowiadać niezmiennikowi.

Zakaz zastępowania wymaga doprecyzowania. `mem::replace` nie może wynieść przypiętej wartości `!Unpin`. Natomiast `Pin::set` legalnie niszczy starą wartość na miejscu i dopiero instaluje nową. Nie jest to przeniesienie starej żywej wartości. Drop guarantee dotyczy zakończenia życia przed unieważnieniem storage, a nie zakazu każdej przyszłej zmiany zawartości adresu.

Future generowana przez `async` może potrzebować stabilnego adresu po rozpoczęciu poll, bo stan może zachowywać odwołania do własnych lokalnych danych. Nie polegaj na analizie „ta funkcja wygląda prosto, więc jej typ na pewno jest Unpin”. Przyjmuj kontrakt traitu i przypinaj future przez bezpieczne narzędzie.

## Diagnostyka kompilatora

Błąd braku `Unpin` przy `Pin::new(&mut future)` oznacza, że ta bezpieczna konstrukcja wymaga dodatkowego boundu. Użyj `pin!` lub `Box::pin`. Błąd `DerefMut` przy przypiętej wartości nie powinien prowadzić do bezrefleksyjnego `get_unchecked_mut`; najpierw sprawdź, czy potrzebna jest projekcja pola. Test działający po jednej relokacji nie dowodzi soundness samoreferencji: wymagania obejmują wszystkie bezpieczne ścieżki mutacji i niszczenia.

## Praktyka produkcyjna

Preferuj indeksy, offsety lub identyfikatory w arenie, jeśli eliminują potrzebę samoreferencji. Dla własnej przypiętej abstrakcji dokumentuj moment ustanowienia adresu, dopuszczalne mutacje, projekcje oraz Drop. Audytuj każdy blok `unsafe` względem tych samych niezmienników. Przenoszenie uchwytów powinno być zwykłą operacją, lecz wydobycie `T` i zmiana wewnętrznych buforów wymagają oddzielnego rozumowania. Wycieki pamięci są dozwolone w bezpiecznym Rust, więc zewnętrzny obowiązkowy cleanup nie może być jedyną podstawą soundness.

## Sprawdź, czy rozumiesz

- Czy Box::pin(String) gwarantuje stały adres jego bufora znaków?
- Dlaczego Pin::set jest dozwolone dla `!Unpin`?
- Czego samo PhantomPinned jeszcze nie zapewnia?

## Ćwiczenia

- `B23-1` — podstawowe: Przenieś uchwyt `Pin<Box<_>>` i porównaj adres pointee. [Rozwiązanie](../rozwiazania/11_async_rust/05_pin_unpin_i_self_referential.md#b23-1).
- `B23-2` — praktyczne: Przypnij lokalną future i wykonaj jeden poll natychmiastowego wyniku. [Rozwiązanie](../rozwiazania/11_async_rust/05_pin_unpin_i_self_referential.md#b23-2).
- `B23-3` — pogłębione: Wyjaśnij niezmiennik projekcji pola i legalne użycie Pin::set. [Rozwiązanie](../rozwiazania/11_async_rust/05_pin_unpin_i_self_referential.md#b23-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [Pin: model i projekcja](https://doc.rust-lang.org/std/pin/index.html)
- [Pin::set](https://doc.rust-lang.org/std/pin/struct.Pin.html#method.set)

## Powiązane tematy

- [`Future`, `Waker` i `poll`](../11_async_rust/02_executor_waker_i_poll.md)
- [`PhantomData` i variance](../05_generics_traits_i_system_typow/04_variance_subtyping_i_dropck.md)
- [`unsafe` i soundness](../21_unsafe_soundness_i_model_pamieci/01_unsafe_i_soundness.md)
