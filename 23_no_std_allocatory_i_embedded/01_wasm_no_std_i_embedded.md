[← Spis treści](../README.md)
<!-- status: expanded -->

# WebAssembly, `no_std` i embedded

## Cele

Po tym rozdziale potrafisz:

- odróżnić środowisko WebAssembly, bibliotekę no_std i binarium bare metal;
- wydzielić logikę działającą na core oraz adapter platformy;
- wskazać wymagania startu, panic i alokacji dla docelowego artefaktu;

## Model — mechanizm i kontrakt

Te trzy obszary rezygnują z części założeń zwykłej aplikacji systemowej, ale
nie są tym samym targetem ani modelem wykonania.

## WebAssembly

Popularne targety:

- `wasm32-unknown-unknown` — minimalne środowisko, np. przeglądarka przez
  JavaScript glue;
- targety WASI — system interface dla runtime’u WASI, zależny od wspieranej
  wersji i komponentów toolchainu.

~~~text
rustup target add wasm32-unknown-unknown
cargo build --release --target wasm32-unknown-unknown
~~~

`wasm-bindgen` i `wasm-pack` są **third-party**. Ułatwiają integrację z JS,
ale generują warstwę ABI i glue. Minimalizuj przekazywanie wielu małych
wartości przez granicę; kopiowanie pamięci może dominować koszt.

WebAssembly nie oznacza automatycznie sandboxu o dowolnych gwarancjach.
Możliwości modułu zależą od host imports, runtime’u i konfiguracji.

## `#![no_std]`

~~~text
#![no_std]

pub fn suma(dane: &[u32]) -> u32 {
    dane.iter().copied().sum()
}
~~~

Ten fragment jest biblioteką, więc nie potrzebuje `main` ani panic handlera.
`no_std` usuwa automatyczne linkowanie `std`, ale udostępnia `core`.
Jeżeli środowisko ma allocator, crate `alloc` daje `Vec`, `String` i `Box`.

## Co zapewniają warstwy

- `core` — typy i traits bez OS ani alokatora;
- `alloc` — kolekcje wymagające globalnego alokatora;
- `std` — I/O, wątki, sieć, filesystem i integracja platformy.

Feature `std` biblioteki powinien być addytywny:

~~~text
#![cfg_attr(not(feature = "std"), no_std)]

#[cfg(feature = "std")]
impl std::error::Error for MojBlad {}
~~~

## Bare metal

Binarium bez runtime’u może wymagać `#![no_main]`, własnego punktu wejścia,
linker scriptu, panic handlera, target specification i obsługi przerwań.
Szczegóły są zależne od architektury i crate’ów embedded.

Volatile nie oznacza atomic ani synchronizacji. Dostęp do memory-mapped I/O
powinien używać właściwych volatile operations i typów HAL. `static mut`
łatwo łamie aliasing; preferuj bezpieczne singletony i critical sections.

## Embedded ecosystem

Traits embedded-hal i implementacje PAC/HAL są **third-party**, choć
utrzymywane w szerokim ekosystemie Rust Embedded. Oddziel kod sterownika
oparty na traits od konkretnego mikrokontrolera. Testuj logikę na hoście,
a warstwę sprzętową na urządzeniu lub emulatorze.

## Rozmiar i panic

W embedded ważne są `opt-level = "s"`/`"z"`, LTO, `panic = "abort"` i analiza
sekcji linkera. Każda zmiana ma trade-off z czasem, debugowalnością i
wydajnością. Mierz wynik binarny.

## Trzy niezależne pytania

Pytaj osobno: jaki zestaw instrukcji wykonuje program, jakie usługi daje host i które crate’y są dostępne. WebAssembly określa maszynę wykonawczą, a WASI dodatkowy interfejs hosta; przeglądarka ma jeszcze inny zestaw integracji. `no_std` jest decyzją na poziomie crate’a, którą można zastosować także na zwykłym hoście. Bare metal oznacza odpowiedzialność za uruchomienie i sprzęt bez typowej warstwy OS. Żadne z tych pojęć samo nie mówi, czy program używa sterty.

Target `wasm32-unknown-unknown` może udostępniać `std`, ale część funkcji wymagających systemu nie działa jak na pulpicie. Sam sukces kompilacji wywołania filesystemu lub wątków nie potwierdza obsługi podczas wykonania. Dobierz imports i narzędzia testowania do hosta. Aktualne ograniczenia opisuje [rustc: wasm32-unknown-unknown](https://doc.rust-lang.org/rustc/platform-support/wasm32-unknown-unknown.html), sprawdzone 2026-11-11. Nie zakładaj, że `cfg(target_arch = "wasm32")` jednoznacznie oznacza przeglądarkę.

## Logika rdzenia testowana na hoście

Poniższy przykład używa tylko typów i metod `core` w silniku. `main` jest hostowym harnessem: nie przedstawia kompletnego firmware ani modułu Wasm z eksportem.

~~~rust
#[derive(Debug, PartialEq)]
enum Blad { ZaMaloMiejsca }
fn koduj_u16(dane: &[u16], wynik: &mut [u8]) -> Result<usize, Blad> {
    let n = dane.len().checked_mul(2).ok_or(Blad::ZaMaloMiejsca)?;
    if wynik.len() < n { return Err(Blad::ZaMaloMiejsca); }
    for (x, para) in dane.iter().zip(wynik[..n].chunks_exact_mut(2)) {
        para.copy_from_slice(&x.to_le_bytes());
    }
    Ok(n)
}
fn main() {
    let mut bufor = [0; 4];
    assert_eq!(koduj_u16(&[1, 513], &mut bufor), Ok(4));
    assert_eq!(bufor, [1, 0, 1, 2]);
    assert_eq!(koduj_u16(&[1, 2, 3], &mut bufor), Err(Blad::ZaMaloMiejsca));
}
~~~

Wywołujący dostarcza bufor, więc silnik nie alokuje i jawnie raportuje za mało miejsca. Kontrola rozmiaru poprzedza pierwszy zapis: na błędzie ten przykład nie modyfikuje bufora. Jawne little-endian daje taki sam format na różnych CPU. Dopiero adapter decyduje, czy bufor pochodzi ze stosu, statycznego magazynu, sterty czy pamięci przekazanej przez hosta.

Biblioteka `no_std` nie potrzebuje własnego entry point ani panic handlera. Końcowe binarium dobiera je do środowiska. Zależność od `alloc` nie dostarcza automatycznie alokatora dla każdego targetu. Warstwy opisują [Embedded Rust Book: no_std](https://docs.rust-embedded.org/book/intro/no-std.html) i [dokumentacja alloc](https://doc.rust-lang.org/alloc/index.html), sprawdzone 2026-11-11. Część ekosystemu może pośrednio ponownie włączyć `std`; sprawdzaj drzewo features.

## Diagnostyka kompilatora

Komunikat „cannot find macro vec” w crate `no_std` może oznaczać brak `alloc` i właściwego importu makra, a nie brak możliwości używania kolekcji w samym języku. `println!`, pliki i `std::thread` wymagają konkretnej integracji platformowej. Nie zastępuj ich pustymi funkcjami tylko po to, aby build przeszedł, jeśli produkt potrzebuje realnej komunikacji.

Błędy brakującego panic handlera, entry pointu albo symboli linkera dotyczą składu końcowego programu. Dodanie `#![no_main]` nie tworzy poprawnego wektora resetu i nie inicjalizuje pamięci. Ustal, co robi runtime platformy: stos, sekcja `.data`, zerowanie `.bss`, tablica przerwań i pamięć peryferiów. Te kroki są zależne od architektury; test hostowy silnika ich nie obejmuje.

## Praktyka produkcyjna

Oddziel sterownik od konkretnego układu. **Third-party:** `embedded-hal` 1.0 zawiera traity blocking, a `embedded-hal-async` osobne odpowiedniki async. Kod sterownika oparty na traitach można testować mockiem na hoście, podczas gdy adapter PAC/HAL odpowiada za piny i zegary. Zakres interfejsu sprawdzono w [embedded-hal 1.0](https://docs.rs/embedded-hal/1.0.0/embedded_hal/), 2026-11-11. Zgodność traitu nie dowodzi zgodności elektrycznej ani czasowej urządzenia.

Zapisz budżety RAM, stosu, flash i czasu odpowiedzi. Duża tablica lokalna nie alokuje sterty, lecz może przepełnić mały stos. Generyczny sterownik może tworzyć wiele instancji kodu; ograniczenie formatowania zmniejsza firmware, ale utrudnia diagnozę. Mierz finalny obraz i mapę sekcji, nie samą wielkość pliku pośredniego.

Dla Wasm testuj integrację z rzeczywistym hostem oraz przenoszenie danych przez granicę. Dla embedded testuj scenariusze resetu, błędu peryferium i braku pamięci na sprzęcie. Hostowe testy regresji działają szybko i dają szerokie pokrycie logiki, ale nie wykrywają złego linker scriptu lub niewłaściwej szerokości dostępu do rejestru. Zmiana panic na abort nie zastępuje planu bezpiecznego stanu urządzenia.

## Sprawdź, czy rozumiesz

- Czy `no_std` zabrania użycia sterty, a Wasm wymusza `no_std`?
- Dlaczego bufor na stosie może być złą decyzją mimo braku alokacji dynamicznej?
- Co musi jeszcze zostać sprawdzone po pozytywnym teście hostowym kodera?

## Ćwiczenia

- `C18-1` — podstawowe: Przypisz core, alloc i std do: Option, Vec, TcpStream oraz parsera pracującego na slices. Wyjaśnij ograniczenie Wasm. [Rozwiązanie](../rozwiazania/23_no_std_allocatory_i_embedded/01_wasm_no_std_i_embedded.md#c18-1).
- `C18-2` — praktyczne: Rozbuduj test koduj_u16 o pusty input i bufor za krótki o jeden bajt. Sprawdź niezmienność bufora przy błędzie. [Rozwiązanie](../rozwiazania/23_no_std_allocatory_i_embedded/01_wasm_no_std_i_embedded.md#c18-2).
- `C18-3` — pogłębione: Zaprojektuj podział sterownika czujnika na rdzeń, trait transportu i adapter HAL. Rozdziel testy hostowe od testów wymagających sprzętu. [Rozwiązanie](../rozwiazania/23_no_std_allocatory_i_embedded/01_wasm_no_std_i_embedded.md#c18-3).

## Powiązane tematy

- [`no_std`, allocatory i embedded — zaawansowane](../23_no_std_allocatory_i_embedded/02_no_std_allocatory_i_embedded.md)
- [Profile i build scripts](../08_moduly_cargo_i_workspaces/04_profile_build_scripts_i_publikowanie.md)
- [FFI i ABI](../22_ffi_i_interoperacyjnosc/01_ffi_abi_i_repr.md)
