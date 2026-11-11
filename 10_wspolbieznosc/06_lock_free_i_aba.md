[← Spis treści](../README.md)
<!-- status: expanded -->

# Lock-free i problem ABA

## Cele

Po tym rozdziale potrafisz:

- oddzielić atomową aktualizację wskaźnika od odzyskiwania pamięci;
- ocenić ABA, postęp i granice narzędzi testowych;


Algorytm **lock-free** gwarantuje postęp systemu jako całości: jakiś wątek
zakończy operację. **Wait-free** daje skończoną liczbę kroków każdemu
uczestnikowi. **Obstruction-free** gwarantuje postęp tylko bez konkurencji.
Żadne z nich nie znaczy automatycznie „szybsze”.

## CAS loop

Najprostszy wzorzec aktualizuje jedną wartość:

~~~rust
use std::sync::atomic::{AtomicUsize, Ordering};

fn maksimum(atom: &AtomicUsize, kandydat: usize) {
    let mut obecne = atom.load(Ordering::Relaxed);
    while kandydat > obecne {
        match atom.compare_exchange_weak(
            obecne,
            kandydat,
            Ordering::Relaxed,
            Ordering::Relaxed,
        ) {
            Ok(_) => return,
            Err(nowsze) => obecne = nowsze,
        }
    }
}

fn main() {
    let x = AtomicUsize::new(4);
    maksimum(&x, 9);
    maksimum(&x, 2);
    assert_eq!(x.load(Ordering::Relaxed), 9);
}
~~~

Operacja jest idempotentna względem retry. Closure CAS nie może wykonywać
efektu zewnętrznego zakładając, że zostanie wywołane raz.

## ABA

Wątek A odczytuje pointer o wartości A i zostaje zatrzymany. Wątek B:

1. zmienia head A → B;
2. zwalnia A;
3. allocator ponownie używa tego samego adresu;
4. ustawia head na liczbowo „A”.

CAS wątku A widzi ten sam adres i uznaje, że stan się nie zmienił, choć węzeł
ma inną tożsamość. Sam ordering nie rozwiązuje ABA.

Techniki:

- licznik wersji w tagged pointerze, jeśli zakres i alignment wystarczą;
- hazard pointers;
- epoch-based reclamation;
- reference counting zaprojektowane dla atomików;
- brak natychmiastowego ponownego użycia pamięci.

Każda ma subtelne warunki postępu, overflow, pinning wątku i cleanup.

## Reclamation jest trudniejsza niż CAS

Usunięcie pointera z listy nie znaczy, że żaden wątek go już nie odczyta.
Natychmiastowy `Box::from_raw` może dać use-after-free. Trzeba udowodnić:

- kiedy wszyscy czytelnicy przestali mieć pointer;
- jak wątek ogłasza chroniony węzeł;
- co dzieje się po panic lub zawieszeniu wątku;
- czy destructor elementu może re-enterować strukturę;
- czy shutdown odzyskuje retired nodes.

Dlatego ręczna lock-free lista jest zwykle złym pierwszym wyborem.

## Pointer tagging i provenance

Przechowuj pointer w `AtomicPtr<T>` zamiast `AtomicUsize`, jeśli to pointer.
Strict Provenance `map_addr` pozwala zmieniać bity adresu przy zachowaniu
provenance. Przed dereferencją usuń tag i udowodnij alignment oraz granice
alokacji. Liczba wolnych bitów wynika z alignment, nie intuicji.

## False sharing i contention

Dwie niezależne atomiki na jednej cache line mogą wzajemnie unieważniać cache.
Padding może pomóc, ale layout i rozmiar cache line zależą od platformy.
CAS pod wysoką konkurencją może wielokrotnie ponawiać, zużywać energię i być
wolniejszy od mutexa usypiającego wątek.

## Narzędzia

- Loom (**third-party**) eksploruje przeploty dla własnych odpowiedników
  atomików;
- Miri wykrywa część UB, ale nie jest modelem wydajności;
- sanitizery wykrywają wykonane data races;
- model checker lub formalny dowód jest właściwy dla krytycznego algorytmu.

Najpierw użyj `Mutex`, kanału albo sprawdzonej kolekcji. Lock-free wybieraj po
profilu i z planem audytu.


## Model — tożsamość, życie i postęp

Poprawna lock-free struktura potrzebuje co najmniej trzech argumentów: gdzie operacja staje się widoczna jako pojedyncza zmiana, dlaczego czytane obiekty nadal żyją oraz co gwarantuje postęp. Udany CAS może być punktem linearyzacji, ale nie rozwiązuje dwóch pozostałych pytań. „Nie używam mutexa” nie jest definicją lock-free: kod może czekać na inny wątek przez aktywne kręcenie się.

ABA nie wymaga zwolnienia pamięci. Wystarczy, że obserwowana wartość przejdzie A → B → A, a poprawność zależy od informacji o zdarzeniach pośrednich. Recykling adresów czyni problem szczególnie groźnym dla wskaźników, lecz semantyczne ABA występuje też przy indeksach i stanach protokołu. Jeżeli algorytm potrzebuje tylko aktualnego maksimum, powrót do starej wartości może być niemożliwy albo nieistotny; problem ocenia się względem niezmiennika.

~~~rust
use std::sync::atomic::{AtomicUsize, Ordering};
fn main() {
    let stan = AtomicUsize::new(1);
    let oczekiwane = stan.load(Ordering::SeqCst);
    stan.store(2, Ordering::SeqCst);
    stan.store(1, Ordering::SeqCst);
    assert_eq!(stan.compare_exchange(oczekiwane, 3, Ordering::SeqCst, Ordering::SeqCst), Ok(1));
}
~~~

CAS nie zna historii. Nawet SeqCst nie nakazuje mu odrzucać powrotu do tej samej wartości. Ten samowystarczalny przykład pokazuje ograniczenie kontraktu API, a nie błąd bezpieczeństwa pamięci. W strukturze wskaźnikowej odczyt historycznej krawędzi listy po takim sukcesie może naruszyć cały algorytm.

Znacznik wersji zwiększa ilość porównywanej informacji, ale ma ograniczony zakres. Po zawinięciu licznika stara para adres–wersja może wrócić. Alignment udostępnia tylko określoną liczbę niskich bitów; nie wolno zakładać, że dowolna platforma ma wolne bity w wysokiej części adresu. Ponadto trzeba sprawdzić szerokość i dostępność atomowego porównania całej reprezentacji. Tagging nie jest automatycznie mechanizmem ochrony czasu życia.

W reclamation najpierw usuwa się węzeł z osiągalnej struktury, następnie odkłada do późniejszego odzyskania, a dopiero po odpowiednim warunku niszczy. Epoch-based reclamation może opóźniać sprzątanie, gdy uczestnik długo pozostaje aktywny. Hazard pointers wymagają poprawnej publikacji ochrony i ponownej weryfikacji odczytanego wskaźnika. W obu technikach shutdown, reentrancy i destructory są częścią kontraktu.

Ścisłe provenance i odpowiednie operacje na wskaźnikach pomagają zachować informację o alokacji podczas manipulacji adresem. Nie dowodzą jednak, że alokacja nadal istnieje ani że aliasowanie jest poprawne. Przekonwertowanie pointera na liczbę i z powrotem nie jest uniwersalnym substytutem jawnego zarządzania czasem życia.

## Diagnostyka kompilatora

Kompilator zaakceptuje CAS o błędnej semantyce ABA, jeśli typy się zgadzają. Miri może wykryć wykonane niepoprawne dereferencje, ale nie udowodni ogólnego postępu. Model checker działa na opisanym modelu; test wykorzystujący zwykłe atomiki zamiast odpowiedników narzędzia może nie podlegać oczekiwanej eksploracji. Błąd braku atomiki określonej szerokości wymaga sprawdzenia `target_has_atomic` i projektu reprezentacji, a nie bezwarunkowego `unsafe`.

## Praktyka produkcyjna

Przed wdrożeniem porównaj zwykły mutex i sprawdzoną kolekcję **third-party**. Mierz nie tylko średnią przepustowość, ale też ogony opóźnień, zużycie CPU i tempo odzyskiwania pamięci. Określ zakres gwarancji postępu, uwzględniając allocator, destruktory oraz bibliotekę reclamation. Pod presją wiele nieudanych CAS może zdominować koszt pracy. Wybór lock-free powinien mieć uzasadniony cel, dokumentację dowodu oraz właściciela audytu; sam pozytywny stress test nie zamyka zadania poprawności.

## Sprawdź, czy rozumiesz

- Czy ABA wymaga użycia allocatora?
- Dlaczego SeqCst nie pozwala CAS odtworzyć historii?
- Co może zatrzymać odzyskiwanie pamięci w schemacie epokowym?

## Ćwiczenia

- `B18-1` — podstawowe: Pokaż sekwencję A → B → A, po której CAS nadal kończy się sukcesem. [Rozwiązanie](../rozwiazania/10_wspolbieznosc/06_lock_free_i_aba.md#b18-1).
- `B18-2` — praktyczne: Rozpisz fazy usunięcia węzła i warunek jego bezpiecznego zniszczenia. [Rozwiązanie](../rozwiazania/10_wspolbieznosc/06_lock_free_i_aba.md#b18-2).
- `B18-3` — pogłębione: Porównaj mutex i lock-free według postępu, opóźnień i pamięci dla przeciążonej kolejki. [Rozwiązanie](../rozwiazania/10_wspolbieznosc/06_lock_free_i_aba.md#b18-3).

## Źródła

Kontrakty zweryfikowano 11 listopada 2026. Przykłady `std` przeznaczono dla Rust 1.90, Edition 2024; źródła internetowe mogą opisywać nowsze wydanie.

- [AtomicPtr i uwaga o ABA](https://doc.rust-lang.org/std/sync/atomic/struct.AtomicPtr.html#method.compare_exchange)
- [Pointer provenance](https://doc.rust-lang.org/std/ptr/index.html#provenance)

## Powiązane tematy

- [Atomiki i memory ordering](05_atomics_i_memory_ordering.md)
- [Raw pointers i provenance](../21_unsafe_soundness_i_model_pamieci/02_raw_pointers_aliasing_i_provenance.md)
- [`Arc` i blokady](../10_wspolbieznosc/03_arc_mutex_rwlock_i_condvar.md)
