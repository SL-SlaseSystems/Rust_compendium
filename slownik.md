# Słownik pojęć Rust

[← Spis treści](README.md)

Polskie tłumaczenia pomagają w nauce, ale kod, dokumentacja i komunikaty
kompilatora używają angielskich terminów. W zespole warto podać angielską
nazwę przy pierwszym użyciu.

| Termin | Znaczenie |
|---|---|
| ABI | Application Binary Interface: konwencja wywołań, layout i reguły współpracy binarnej. |
| abstraction | Abstrakcja ukrywająca szczegóły za kontraktem. |
| aliasing | Istnienie kilku sposobów dostępu do tej samej pamięci. |
| alignment | Wymagane wyrównanie adresu wartości w pamięci. |
| allocation | Przydzielony obszar pamięci z własną tożsamością i czasem życia. |
| associated item | Typ, stała lub funkcja należąca do traitu albo implementacji. |
| atomic | Operacja niepodzielna względem współbieżnych obserwatorów. |
| auto trait | Trait wyprowadzany automatycznie ze składu typu, np. `Send`. |
| backpressure | Mechanizm ograniczenia producenta przez tempo konsumenta. |
| binding | Powiązanie nazwy ze zmienną/wartością, zwykle przez `let`. |
| blanket implementation | Implementacja traitu dla całej rodziny typów spełniających bounds. |
| borrow | Pożyczka wartości przez referencję bez przejęcia ownership. |
| borrow checker | Analiza kompilatora sprawdzająca reguły pożyczek. |
| bound | Wymaganie na parametrze, np. `T: Display + Send`. |
| cancellation safety | Odporność operacji async na przerwanie przez drop future. |
| channel | Kanał przekazujący wiadomości między wykonawcami. |
| closure | Anonimowa funkcja mogąca przechwycić otoczenie. |
| coherence | Reguły zapewniające jednoznaczność implementacji traits. |
| const generic | Parametr generyczny będący wartością stałą. |
| crate | Jednostka kompilacji Rusta. |
| data race | Niesynchronizowany konflikt dostępów między wątkami; jest UB. |
| deadlock | Zakleszczenie: uczestnicy czekają na siebie bez możliwości postępu. |
| discriminant | Wartość określająca aktywny wariant enumu. |
| dispatch | Wybór implementacji wywoływanej metody: statyczny lub dynamiczny. |
| drop check | Analiza ważności danych używanych podczas destrukcji. |
| DST | Dynamically Sized Type, np. `str`, `[T]`, `dyn Trait`. |
| edition | Zestaw kompatybilnych reguł składni i idiomów języka. |
| executor | Mechanizm pollujący i planujący futures. |
| fat pointer | Pointer z metadanymi, np. długością slice lub vtable. |
| feature flag | Nazwana opcja Cargo włączająca addytywną funkcjonalność crate’a. |
| FFI | Foreign Function Interface, granica z innym językiem/ABI. |
| future | Wartość reprezentująca obliczenie mogące być jeszcze niegotowe. |
| fuzzing | Automatyczne generowanie wejść w celu znajdowania awarii i naruszeń invariants. |
| GAT | Generic Associated Type: associated type z własnymi parametrami. |
| guard | Wartość RAII utrzymująca zasób lub blokadę do `Drop`. |
| happens-before | Relacja widoczności i porządku w modelu pamięci. |
| HRTB | Higher-Ranked Trait Bound, np. `for<'a> Fn(&'a T)`. |
| hygiene | Reguły zapobiegające przypadkowemu przechwytywaniu nazw przez makra. |
| interior mutability | Kontrolowana mutacja przez `&T`, oparta na `UnsafeCell`. |
| invariant | Warunek, który musi zawsze pozostawać prawdziwy dla typu/operacji. |
| lifetime | Statyczny opis okresu, w którym referencja jest ważna. |
| lock-free | Gwarancja postępu systemu bez globalnej blokady. |
| macro expansion | Zastąpienie wywołania makra wygenerowanymi tokenami. |
| MIR | Mid-level Intermediate Representation używana wewnątrz rustc. |
| monomorphization | Generowanie wyspecjalizowanego kodu dla podstawień generics. |
| observability | Zdolność wyjaśniania stanu systemu na podstawie logów, metryk i trace'ów. |
| move | Przeniesienie ownership unieważniające poprzedni binding. |
| MSRV | Minimum Supported Rust Version. |
| newtype | Nowy typ jako struktura z jednym polem. |
| NLL | Non-Lexical Lifetimes: analiza kończąca loans według użycia i przepływu. |
| orphan rule | Reguły lokalności implementacji traitu i pokrycia parametrów; lokalny typ może umożliwiać implementację obcego traitu przy spełnieniu szczegółowych warunków. |
| ownership | Własność określająca, kto odpowiada za wartość i jej `Drop`. |
| package | Jednostka Cargo opisana manifestem. |
| panic | Nienormalne zakończenie bieżącego przepływu przez unwind lub abort. |
| pattern | Wzorzec dopasowujący i rozkładający wartość. |
| pinning | Gwarancja stabilności adresu pointee dla typu `!Unpin`. |
| place | Lokalizacja pamięci w modelu kompilatora, np. zmienna lub pole. |
| provenance | Pochodzenie pointera i uprawnienie do konkretnej alokacji. |
| RAII | Resource Acquisition Is Initialization: zasób powiązany z lifetime wartości. |
| raw pointer | `*const T` lub `*mut T` bez gwarancji referencji. |
| reborrow | Krótsza pożyczka utworzona z istniejącej referencji. |
| RPIT | Return-Position `impl Trait`: ukryty konkretny typ wyniku. |
| RPITIT | RPIT w metodzie traitu, modelowany jako anonimowy associated type. |
| safety invariant | Warunek wymagany, aby unsafe operacja nie prowadziła do UB. |
| Send | Auto trait pozwalający przenieść wartość między wątkami. |
| shadowing | Nowy binding o tej samej nazwie co poprzedni. |
| slice | Widok `[T]` na ciągłą sekwencję, zwykle przez `&[T]`. |
| soundness | Niemożność wywołania UB przez dowolne użycie bezpiecznego API. |
| static dispatch | Wybór implementacji podczas kompilacji, zwykle przez generics. |
| stream | Asynchroniczna sekwencja wartości; trait głównie z ekosystemu. |
| Sync | Auto trait pozwalający współdzielić `&T` między wątkami. |
| target | Konkretny artefakt Cargo albo platforma kompilacji — znaczenie wynika z kontekstu. |
| trait | Kontrakt współdzielonego zachowania i associated items. |
| trait object | `dyn Trait` używany do dynamic dispatch. |
| UB | Undefined behavior: naruszenie założeń języka bez gwarantowanego wyniku. |
| unwind | Rozwijanie stosu po panic wraz z wykonywaniem destruktorów. |
| variance | Wpływ subtypingu parametru na subtyping całego typu. |
| vtable | Tablica używana konceptualnie do dynamic dispatch i obsługi obiektu. |
| wake | Sygnał dla executora, że task należy ponownie pollować. |
| workspace | Grupa pakietów Cargo ze wspólnym lockfile i katalogiem build. |
| ZST | Zero-Sized Type, typ o rozmiarze zero. |

## Pojęcia projektowe i produkcyjne

| Termin | Znaczenie i granica |
|---|---|
| authentication | Ustalenie tożsamości; samo nie przyznaje dostępu do konkretnego zasobu. |
| authorization | Decyzja o dozwolonej operacji na zasobie dla ustalonej tożsamości. |
| budget | Wspólny limit kosztu, czasu lub prób, obejmujący także kolejki i retry. |
| cardinality | Liczba różnych kombinacji etykiet metryki; nieograniczone identyfikatory mogą mnożyć koszt backendu. |
| deadline | Ostateczny termin całej operacji; różni się od ponawianego timeoutu każdej próby. |
| drain | Faza zamykania: odmowa nowych prac i kontrolowane kończenie już przyjętych. |
| error budget | Dopuszczona część niespełnienia SLO w określonym oknie i mierze. |
| harness | Mały adapter uruchamiający badany kod w kontrolowanych warunkach testu/fuzzera. |
| host / guest | Gospodarz udostępnia możliwości, gość wykonuje moduł, np. WebAssembly. |
| idempotency | Powtórzenie logicznie tej samej operacji nie tworzy kolejnego skutku według ustalonego kontraktu. |
| liveness probe | Kontrola, czy proces wymaga odzyskania działania, np. restartu; nie musi oznaczać gotowości do obsługi ruchu. |
| readiness probe | Kontrola gotowości do przyjmowania nowych operacji. |
| provenance artefaktu | Informacja o źródłach i procesie budowania; odrębna od provenance wskaźnika. |
| round-trip | Własność odtworzenia modelu przez decode(encode(x)); wymaga założeń o reprezentacji i równości. |
| SBOM | Software Bill of Materials: lista komponentów artefaktu; sama nie dowodzi ich bezpieczeństwa. |
| shrinking | Upraszczanie wejścia zachowującego porażkę property testu. |
| SLI | Service Level Indicator: mierzalny wskaźnik zachowania usługi z jawnym mianownikiem. |
| SLO | Service Level Objective: cel dla SLI w określonym oknie. |
| span | Okres i kontekst pracy w telemetrii; w diagnostyce kompilatora także zakres tekstu źródłowego. |
| threat model | Opis aktywów, zagrożeń, granic zaufania i założeń ochrony. |

## Powiązane tematy

- [Pamięć i własność](03_ownership_i_pamiec/02_ownership_move_i_copy.md)
- [Traits](05_generics_traits_i_system_typow/02_traits_i_associated_items.md)
- [`unsafe`, soundness i model pamięci](21_unsafe_soundness_i_model_pamieci/README.md)
- [Testowanie zaawansowane, fuzzing i Miri](26_testowanie_zaawansowane_fuzzing_i_miri/README.md)
- [Observability i produkcja](29_observability_i_produkcja/README.md)
