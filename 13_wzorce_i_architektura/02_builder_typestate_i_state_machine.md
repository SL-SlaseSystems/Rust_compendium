[← Spis treści](../README.md)

# Builder, typestate i state machine

## Builder

Builder nazywa wiele opcjonalnych parametrów i może odroczyć walidację:

~~~rust
#[derive(Debug, PartialEq)]
struct Klient {
    host: String,
    timeout_ms: u64,
}

#[derive(Default)]
struct KlientBuilder {
    host: Option<String>,
    timeout_ms: Option<u64>,
}

impl KlientBuilder {
    fn host(mut self, host: impl Into<String>) -> Self {
        self.host = Some(host.into());
        self
    }

    fn timeout_ms(mut self, timeout: u64) -> Self {
        self.timeout_ms = Some(timeout);
        self
    }

    fn build(self) -> Result<Klient, &'static str> {
        let host = self.host.ok_or("brak hosta")?;
        let timeout_ms = self.timeout_ms.unwrap_or(1_000);
        if timeout_ms == 0 { return Err("timeout musi być dodatni"); }
        Ok(Klient { host, timeout_ms })
    }
}

fn main() {
    let k = KlientBuilder::default().host("localhost").build().unwrap();
    assert_eq!(k.timeout_ms, 1_000);
}
~~~

Consuming builder (`self -> Self`) dobrze łańcuchuje i może przenosić pola.
Mutable builder (`&mut self -> &mut Self`) ułatwia warunkową konfigurację.
`build` powinien oddać konkretny błąd walidacji.

## Typestate

Stan jest parametrem typu, a przejście konsumuje starą wartość:

~~~rust
use std::marker::PhantomData;

struct Zamkniete;
struct Otwarte;

struct Polaczenie<Stan> {
    adres: String,
    _stan: PhantomData<Stan>,
}

impl Polaczenie<Zamkniete> {
    fn nowe(adres: impl Into<String>) -> Self {
        Self { adres: adres.into(), _stan: PhantomData }
    }

    fn otworz(self) -> Polaczenie<Otwarte> {
        Polaczenie { adres: self.adres, _stan: PhantomData }
    }
}

impl Polaczenie<Otwarte> {
    fn wyslij(&self, dane: &str) -> usize {
        self.adres.len() + dane.len()
    }

    fn zamknij(self) -> Polaczenie<Zamkniete> {
        Polaczenie { adres: self.adres, _stan: PhantomData }
    }
}

fn main() {
    let p = Polaczenie::<Zamkniete>::nowe("localhost").otworz();
    assert_eq!(p.wyslij("hej"), 12);
    let _ = p.zamknij();
}
~~~

Nie da się wywołać `wyslij` na `Polaczenie<Zamkniete>`. Koszt to więcej typów,
trudniejsze przechowywanie heterogenicznego stanu i możliwy bloat.

## Enum jako state machine

Gdy stan zmienia się dynamicznie i trzeba go przechowywać w jednej kolekcji,
enum bywa prostszy:

~~~rust
enum Stan {
    Nowy,
    Aktywny { proby: u8 },
    Zakonczony,
}

fn krok(stan: Stan) -> Stan {
    match stan {
        Stan::Nowy => Stan::Aktywny { proby: 0 },
        Stan::Aktywny { proby } if proby < 2 => Stan::Aktywny { proby: proby + 1 },
        Stan::Aktywny { .. } => Stan::Zakonczony,
        Stan::Zakonczony => Stan::Zakonczony,
    }
}

fn main() {
    assert!(matches!(krok(Stan::Nowy), Stan::Aktywny { proby: 0 }));
}
~~~

Typestate dla compile-time workflow; enum dla runtime state. Nie wciskaj
typestate w publiczne API, jeśli użytkownik musi stale erase’ować typ.

## Powiązane tematy

- [Struktury i enumy](../04_typy_i_modelowanie/01_struktury_enumy_i_metody.md)
- [`PhantomData` i variance](../zaawansowane/04_variance_subtyping_i_dropck.md)
- [Projektowanie API](03_projektowanie_api_i_semver.md)
