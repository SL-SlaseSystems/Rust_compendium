[← Spis treści](../README.md)
<!-- status: expanded -->

# SLI, SLO, graceful shutdown i procedury operacyjne

> Przykłady `rust`: biblioteka standardowa, Edition 2024. API narzędzi i bibliotek zewnętrznych opisano na podstawie źródeł sprawdzonych 11 listopada 2026 r.; szkice `text` wymagają wskazanego środowiska.

## Cele

Po tym rozdziale potrafisz:

- zdefiniować mierzalny wskaźnik doświadczenia użytkownika;
- zamknąć usługę w fazach z kontrolą zadań i danych;
- przygotować alert i procedurę, które prowadzą do działania;

## Model — cel dotyczy obserwowanej usługi

Wskaźnik poziomu usługi (SLI) mierzy wybrane zachowanie: odsetek zakończonych poprawnie operacji albo udział operacji w określonym czasie. Cel (SLO) ustala wymagany poziom w danym oknie. Definicja musi nazwać kwalifikujące się zdarzenia, dobry wynik, źródło pomiaru i zakres czasu. „99,9% dostępności” bez mianownika nie określa, czy liczymy requesty, minuty, regiony czy klientów.

Budżet błędów to dopuszczona część niespełnienia celu. Dla miliona kwalifikujących się operacji i celu 99,9% budżet wynosi tysiąc złych operacji. Nie utożsamiaj tego automatycznie z liczbą minut, jeżeli SLI jest oparty na requestach. Zachowanie przy braku ruchu trzeba określić osobno: zero zdarzeń nie jest dowodem idealnej dostępności.

~~~rust
fn spelnia(dobre: u64, wszystkie: u64, cel_na_milion: u32) -> Option<bool> {
    if wszystkie == 0 || dobre > wszystkie || cel_na_milion > 1_000_000 {
        return None;
    }
    Some(u128::from(dobre) * 1_000_000
        >= u128::from(wszystkie) * u128::from(cel_na_milion))
}
fn main() {
    assert_eq!(spelnia(999, 1000, 999_000), Some(true));
    assert_eq!(spelnia(998, 1000, 999_000), Some(false));
    assert_eq!(spelnia(0, 0, 999_000), None);
}
~~~

Rachunek `u128` zapobiega przepełnieniu iloczynu dwóch wartości z pokazanych zakresów, a porównanie nie wprowadza zaokrąglenia zmiennoprzecinkowego. To obliczenie dla zamkniętego zbioru zdarzeń, nie implementacja przesuwanego okna, opóźnionych metryk ani alertu. Wymagania operacyjne obejmują także jakość danych pomiarowych.

## Alert powinien wskazywać potrzebne działanie

Wzrost liczby błędów przez minutę może oznaczać krótki incydent lub szum. Alert na szybkie zużywanie budżetu wiąże sygnał z zagrożeniem celu; dobór kilku okien pomaga odróżnić intensywną awarię od długotrwałej degradacji. Ustal właściciela, priorytet i instrukcję weryfikacji, zanim dodasz powiadomienie.

Playbook podaje: jak potwierdzić problem, które dane obejrzeć, jakie działania są odwracalne, kiedy eskalować i jak zweryfikować poprawę. Nie zakładaj, że osoba dyżurująca pamięta niedawną zmianę konfiguracji. Link do wykresu bez objaśnienia progów nie jest procedurą. Przetestuj playbook podczas kontrolowanego ćwiczenia.

## Zamykanie jest protokołem aplikacji

Graceful shutdown składa się z wykrycia sygnału, rozgłoszenia decyzji i oczekiwania na zakończenie pracy. W usłudze dodaj kolejność: przestań deklarować gotowość, zatrzymaj przyjmowanie nowych operacji, zakończ lub anuluj aktywne, zapisz wymagany stan i zamknij eksportery. Nie usypiaj procesu na stałą liczbę sekund, zakładając, że wszystkie taski zdążyły.

Określ globalny deadline i właściciela każdego taska. Upuszczenie uchwytu do zadania może mieć inny skutek niż upuszczenie samej future; reguły zależą od runtime'u. Token anulowania jest informacją, którą operacja musi obserwować. Zadanie CPU-bound bez punktu współpracy nie kończy się tylko dlatego, że sygnał został wysłany.

Dla operacji zewnętrznej timeout lokalny nie cofa skutku po stronie odbiorcy. Jeśli zamykasz usługę po wysłaniu zlecenia, potrzebujesz protokołu idempotencji albo późniejszego uzgodnienia stanu. Decyzja „zakończ po deadline” powinna nazwać ryzyko utraty lub powtórzenia pracy.

## Health, readiness i limity

Liveness odpowiada, czy proces wymaga restartu; readiness, czy może przyjmować ruch. Awaria bazy nie zawsze uzasadnia restart wszystkich instancji: może spowodować dodatkową falę połączeń. Test gotowości powinien odzwierciedlać model zależności i być tani. Rozdziel diagnostykę szczegółową od prostego endpointu używanego często przez infrastrukturę.

Profile produkcyjne obejmują limity pamięci, file descriptors, wątków, puli połączeń i kolejek. Ograniczenie tylko pojedynczego requestu nie gwarantuje ograniczenia sumy. Przetestuj zachowanie przy pełnej kolejce i niedostępnej zależności. Mierz również czas drain oraz liczbę operacji przerwanych podczas rollout.

## Diagnostyka kompilatora

Kompilator nie potwierdzi znaczenia SLI ani poprawności kolejności zamykania usługi. Sprawdzaj testem brak nowych przyjęć po przejściu do drain, zakończenie aktywnej operacji oraz osiągnięcie deadline dla operacji niekooperującej. Brak eksportu końcowej metryki może wynikać z zbyt wczesnego zamknięcia odbiorcy. Nie testuj shutdown wyłącznie przez natychmiastowe zabicie procesu.

## Praktyka produkcyjna

Dokumentuj jednostki, okno i politykę brakujących danych. Alert utrzymuj wraz z usługą: właściciel i procedura muszą zmieniać się z architekturą. Przy rollout obserwuj wynik użytkownika, kolejki i odrzucenia, a nie tylko fakt uruchomienia nowych procesów. Procedura awaryjna powinna chronić dane i odwracać możliwie mały zakres zmiany; kryterium sukcesu stanowi poprawa tego samego sygnału, który wykazał awarię.

## Sprawdź, czy rozumiesz

1. Dlaczego zero requestów nie musi znaczyć spełnienia SLO?
2. Co różni readiness od liveness przy awarii bazy?
3. Dlaczego wysłanie tokenu nie gwarantuje zakończenia taska?

## Ćwiczenia

- `D12-1` — podstawowe: Policz budżet błędów dla 2 000 000 operacji i celu 99,95%. [Rozwiązanie](../rozwiazania/29_observability_i_produkcja/02_slo_shutdown_i_operacje.md#d12-1).
- `D12-2` — praktyczne: Zaprojektuj test shutdown z jednym szybkim i jednym zawieszonym taskiem. [Rozwiązanie](../rozwiazania/29_observability_i_produkcja/02_slo_shutdown_i_operacje.md#d12-2).
- `D12-3` — pogłębione: Napisz procedurę dla alertu gwałtownego wzrostu timeoutów integracji. [Rozwiązanie](../rozwiazania/29_observability_i_produkcja/02_slo_shutdown_i_operacje.md#d12-3).

## Źródła i granice weryfikacji

Przykład runtime'owego protokołu: [Tokio graceful shutdown](https://tokio.rs/tokio/topics/shutdown). Definicje celów i budżetu: [Google SRE: Service Level Objectives](https://sre.google/sre-book/service-level-objectives/). Licznik SLO jest własnym przykładem dydaktycznym; test nie wdraża infrastruktury alertowania.

## Powiązane tematy

- [Logi, metryki i traces](01_logi_metryki_i_traces.md)
- [Timeouty](../11_async_rust/04_anulowanie_timeouty_i_blocking.md)
- [Wydania](../28_ci_cd_i_release_engineering/02_wydania_artefakty_i_rollback.md)
