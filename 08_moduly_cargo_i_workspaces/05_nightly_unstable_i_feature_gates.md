[← Spis treści](../README.md)

# Nightly, unstable i feature gates

Rust wydaje stable co około sześć tygodni, beta jako kandydat i nightly
codziennie. Edition jest osobnym mechanizmem zgodności i nie oznacza kanału.

## Wybór toolchainu

~~~text
rustup toolchain install stable beta nightly
cargo +stable test
cargo +nightly test
rustup override set nightly
rustup override unset
~~~

Lepszy od lokalnego override dla zespołu jest wersjonowany
`rust-toolchain.toml`:

~~~toml
[toolchain]
channel = "nightly-2026-08-01"
components = ["rustfmt", "clippy"]
profile = "minimal"
~~~

Przypięta data daje powtarzalność, ale wymaga regularnej, testowanej
aktualizacji ze względu na poprawki bezpieczeństwa.

## Feature gates

Niestabilna funkcja języka wymaga atrybutu crate:

~~~text
#![feature(type_alias_impl_trait)]

type Wynik = impl Iterator<Item = u32>;
~~~

Ten przykład jest **nightly** i nie jest testowany jako stable. Gate nie jest
obietnicą stabilizacji ani ostatecznej składni.

Przykładowe obszary nadal wymagające sprawdzenia w Unstable Book
(stan 2026-08-12):

- `type_alias_impl_trait`;
- `generic_const_exprs`;
- `trait_alias`;
- wybrane allocator APIs;
- liczne flagi `-Z` i compiler intrinsics.

Nie kopiuj tej listy jako wiecznej prawdy — sprawdź aktualny toolchain:

~~~text
rustc +nightly --version
rustc +nightly -Z help
rustup doc --toolchain nightly --path
~~~

## Unstable library features

API standard library oznaczone `#[unstable(feature = "...")]` także wymaga
odpowiedniego `#![feature(...)]`. Czasem stabilna alternatywa istnieje pod
inną nazwą. Sprawdź dokumentację wersji stable przed wprowadzeniem nightly.

## Ryzyko

- feature może zmienić składnię lub semantykę;
- nightly snapshot może mieć regresję;
- rustfmt i Clippy nightly zmieniają wyniki;
- zależność wymagająca nightly narzuca go całemu grafowi build;
- MSRV staje się niejasne;
- plugin/compiler-internal API ma szczególnie małą stabilność.

Nigdy nie ustawiaj `RUSTC_BOOTSTRAP`, aby obchodzić gates w produkcyjnym
projekcie. To wewnętrzny mechanizm bootstrappingu, nie wspierana ścieżka.

## Strategia izolacji

1. zamknij nightly za osobnym crate’em lub feature;
2. udostępnij stabilny fallback, jeśli możliwe;
3. przypnij toolchain z datą;
4. testuj aktualizację w CI;
5. śledź tracking issue i Unstable Book;
6. zapisz plan usunięcia gate po stabilizacji;
7. nie eksponuj niestabilnego typu w publicznym ABI.

## Migracja do stable

Po stabilizacji usuń `#![feature]`, podnieś MSRV do wersji stabilizującej,
uruchom testy stable i sprawdź release notes. Stabilna wersja może różnić się
od eksperymentalnej; sama zbieżność nazwy nie wystarcza.

## Kiedy nightly ma sens

- rozwój kompilatora i standard library;
- embedded/niestandardowy target wymagający konkretnej funkcji;
- eksperyment badawczy;
- narzędzie deweloperskie izolowane od artefaktu produkcyjnego;
- funkcja z jasno policzoną wartością i akceptowanym kosztem utrzymania.

Zwykła aplikacja nie potrzebuje nightly tylko dlatego, że „jest nowsze”.

## Powiązane tematy

- [Instalacja i toolchain](../01_wprowadzenie_i_toolchain/02_instalacja_i_toolchain.md)
- [HRTB, GAT, RPIT i TAIT](../05_generics_traits_i_system_typow/05_hrtb_gat_rpit_i_impl_trait.md)
- [Clippy, rustfmt i linty](../09_dokumentacja_testowanie_i_jakosc/03_clippy_rustfmt_i_linty.md)
