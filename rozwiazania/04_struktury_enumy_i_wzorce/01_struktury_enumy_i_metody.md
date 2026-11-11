[← Spis treści](../../README.md)

# Rozwiązania: Struktury, enumy i metody

## A16-1

Odczyt używa `&self`, więc można wykonać go ponownie. Newtype odróżnia metry od innych liczb.

~~~rust
struct Metry(u32);
impl Metry { fn wartosc(&self) -> u32 { self.0 } }
fn main() {
    let m = Metry(12);
    assert_eq!(m.wartosc(), 12);
    assert_eq!(m.wartosc(), 12);
}
~~~

## A16-2

Dane wyniku są obecne wyłącznie w wariancie `Gotowy`. Konsumpcja `self` pozwala oddać `String` bez alokacji kopii.

~~~rust
enum Stan { Oczekuje, Gotowy(String) }
impl Stan {
    fn wynik(self) -> Option<String> {
        match self { Self::Oczekuje => None, Self::Gotowy(s) => Some(s) }
    }
}
fn main() {
    assert_eq!(Stan::Oczekuje.wynik(), None);
    assert_eq!(Stan::Gotowy("ok".into()).wynik().as_deref(), Some("ok"));
}
~~~

## A16-3

Nowe wartości wyliczamy przed przypisaniem. Błąd drugiego mnożenia nie zostawi częściowo zmienionej szerokości.

~~~rust
#[derive(Debug, PartialEq)]
struct Prostokat { szerokosc: u32, wysokosc: u32 }
impl Prostokat {
    fn skaluj(&mut self, mnoznik: u32) -> Option<()> {
        let szerokosc = self.szerokosc.checked_mul(mnoznik)?;
        let wysokosc = self.wysokosc.checked_mul(mnoznik)?;
        self.szerokosc = szerokosc;
        self.wysokosc = wysokosc;
        Some(())
    }
}
fn main() {
    let mut p = Prostokat { szerokosc: 2, wysokosc: u32::MAX };
    assert_eq!(p.skaluj(2), None);
    assert_eq!(p, Prostokat { szerokosc: 2, wysokosc: u32::MAX });
    let mut q = Prostokat { szerokosc: 3, wysokosc: 4 };
    assert_eq!(q.skaluj(2), Some(()));
    assert_eq!(q, Prostokat { szerokosc: 6, wysokosc: 8 });
}
~~~

Prywatność wobec klientów wymaga umieszczenia typu w module z publicznymi metodami. Test mechanizmu pozostaje w tym samym module, aby móc porównać wszystkie pola.

