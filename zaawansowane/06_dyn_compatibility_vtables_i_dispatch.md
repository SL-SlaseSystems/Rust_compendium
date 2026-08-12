[← Spis treści](../README.md)

# Dyn compatibility, vtables i dispatch

Trait object `dyn Trait` umożliwia wywołanie zachowania typu wybranego w
runtime. Jest DST, więc używa się go przez `&dyn Trait`, `Box<dyn Trait>`,
`Arc<dyn Trait>` lub inny pointer.

## Dynamic dispatch

~~~rust
trait Render {
    fn render(&self) -> String;
}

struct Tekst(&'static str);
struct Liczba(i32);

impl Render for Tekst {
    fn render(&self) -> String { self.0.into() }
}
impl Render for Liczba {
    fn render(&self) -> String { self.0.to_string() }
}

fn polacz(elementy: &[Box<dyn Render>]) -> String {
    elementy
        .iter()
        .map(|e| e.render())
        .collect::<Vec<_>>()
        .join(",")
}

fn main() {
    let x: Vec<Box<dyn Render>> =
        vec![Box::new(Tekst("a")), Box::new(Liczba(2))];
    assert_eq!(polacz(&x), "a,2");
}
~~~

Konceptualnie fat pointer zawiera data pointer i vtable pointer. Vtable ma
informacje potrzebne do dispatch i zarządzania wartością, lecz jej dokładny
layout nie jest stabilnym ABI. Nie serializuj ani nie przekazuj vtable przez
FFI.

## Warunki dyn compatibility

W uproszczeniu trait:

- nie może wymagać `Self: Sized`;
- nie ma associated constants;
- nie ma GAT wymagających określenia w obiekcie;
- dispatchowalna metoda nie ma parametrów typów;
- metoda nie używa `Self` poza receiverem;
- receiver ma wspieraną formę, np. `&self`, `&mut self`, `Box<Self>`,
  `Arc<Self>` lub odpowiednie `Pin`;
- metoda nie zwraca opaque `impl Trait` ani `async fn`, jeśli ma być
  dispatchowalna.

Metodę niedostępną przez obiekt można oznaczyć `where Self: Sized`:

~~~rust
trait Nazwany {
    fn nazwa(&self) -> &str;

    fn opakuj(self) -> Box<Self>
    where
        Self: Sized,
    {
        Box::new(self)
    }
}

impl Nazwany for String {
    fn nazwa(&self) -> &str { self }
}

fn main() {
    let x: Box<dyn Nazwany> = String::from("Rust").opakuj();
    assert_eq!(x.nazwa(), "Rust");
}
~~~

## Associated types

Trait object musi określić niegeneryczne associated types potrzebne do pełnego
typu:

~~~rust
fn pierwszy(iter: &mut dyn Iterator<Item = i32>) -> Option<i32> {
    iter.next()
}

fn main() {
    let mut i = vec![3, 4].into_iter();
    assert_eq!(pierwszy(&mut i), Some(3));
}
~~~

## Lifetimes

`Box<dyn Trait>` w wielu miejscach domyślnie oznacza `Box<dyn Trait + 'static>`.
Nie znaczy to, że box żyje wiecznie; jego konkretny typ nie może zawierać
krótszych pożyczek. Jawne `Box<dyn Trait + 'a>` pozwala przechować obiekt
pożyczający.

Auto traits i bounds są częścią obiektu: `dyn Trait + Send + Sync` różni się
od `dyn Trait`. W wielowątkowym API deklaruj je w granicy.

## Upcasting i downcasting

Trait upcasting z `dyn SubTrait` do `dyn SuperTrait` jest wspierany w
stabilnym Rust dla odpowiednich coercions, ale nie jest downcastingiem.
Downcasting zwykle opiera się na `Any`, wymaga `'static` i ujawnia potrzebę
znajomości konkretnego typu. Częste downcasty sugerują zły kontrakt traitu.

## Static czy dynamic

Static dispatch umożliwia inline i brak vtable, ale monomorfizuje kod.
Dynamic dispatch zmniejsza liczbę wariantów kodu, umożliwia heterogeniczne
kolekcje i plugin-like wybór, lecz ma indirection. Koszt mierz w kontekście;
alokacja `Box` nie jest wymagana dla `&dyn Trait`.

## Powiązane tematy

- [Konwersje, DST i trait objects](../04_typy_i_modelowanie/05_konwersje_dst_i_trait_objects.md)
- [HRTB, GAT i RPIT](05_hrtb_gat_rpit_i_impl_trait.md)
- [Monomorfizacja i optymalizacja](13_monomorfizacja_mir_llvm_i_optymalizacja.md)
