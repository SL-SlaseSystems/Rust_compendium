1. System Borrowing i Ownership

    Rust zapewnia bezpieczeństwo pamięci bez garbage collectora, dzięki unikalnemu systemowi własności i pożyczania danych.

    fn main() {
        let s = String::from("Hello"); // `s` jest właścicielem danych
        let len = calculate_length(&s); // Przekazujemy referencję
        println!("Długość: {}", len);
    }

    fn calculate_length(s: &String) -> usize {
        s.len() // Możemy tylko odczytać dane
    }

2. Macros (Makra proceduralne i deklaracyjne)

    Makra pozwalają generować kod w czasie kompilacji.

    macro_rules! calculate {
        ($a:expr, $b:expr) => {
            $a + $b
        };
    }

    fn main() {
        println!("Wynik: {}", calculate!(2, 3)); // Generuje kod `2 + 3`
    }

3. Lifetime Annotations

Wskaźniki żywotności eliminują ryzyko używania nieważnych referencji.

    fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
        if x.len() > y.len() {
            x
        } else {
            y
        }
    }

    fn main() {
        let s1 = String::from("Długi tekst");
        let s2 = "Krótki";
        println!("Najdłuższy: {}", longest(&s1, s2));
    }

4. Trait Bounds i Generics

Generics pozwalają tworzyć uniwersalny kod, a trait bounds ograniczają typy.

    fn print_area<T: Area>(shape: &T) {
        println!("Pole: {}", shape.area());
    }

    trait Area {
        fn area(&self) -> f64;
    }

    struct Circle {
        radius: f64,
    }

    impl Area for Circle {
        fn area(&self) -> f64 {
            3.14 * self.radius * self.radius
        }
    }

    fn main() {
        let circle = Circle { radius: 5.0 };
        print_area(&circle);
    }

5. Concurrency i async/await

Rust obsługuje asynchroniczne programowanie dzięki async i await.

    use tokio::time::{sleep, Duration};

    async fn do_work() {
        println!("Rozpoczynam pracę...");
        sleep(Duration::from_secs(2)).await;
        println!("Praca ukończona!");
    }

    #[tokio::main]
    async fn main() {
        do_work().await;
}

6. System typów zaawansowanych z Enums i Match

Rust pozwala budować wyrafinowane struktury danych.

    enum Shape {
        Circle(f64),
        Rectangle { width: f64, height: f64 },
    }

    fn area(shape: &Shape) -> f64 {
        match shape {
            Shape::Circle(radius) => 3.14 * radius * radius,
            Shape::Rectangle { width, height } => width * height,
        }
    }

    fn main() {
        let circle = Shape::Circle(5.0);
        println!("Pole: {}", area(&circle));
    }

7. Serde – Serializacja i Deserializacja

    Serde to popularna biblioteka do pracy z JSON i innymi formatami.

    use serde::{Serialize, Deserialize};
    use serde_json;

    #[derive(Serialize, Deserialize, Debug)]
    struct User {
        name: String,
        age: u32,
    }

    fn main() {
        let user = User {
            name: String::from("Jan"),
            age: 30,
        };
        let json = serde_json::to_string(&user).unwrap();
        println!("JSON: {}", json);
    }

8. Smart Pointers i Interior Mutability

Rc, Arc, RefCell i inne pozwalają zarządzać pamięcią i współdzieleniem.

    use std::rc::Rc;

    fn main() {
        let a = Rc::new(5);
        let b = Rc::clone(&a);
        println!("a: {}, b: {}", a, b);
    }

9. FFI (Foreign Function Interface)

    Rust umożliwia wywoływanie funkcji z innych języków.

    #[link(name = "m")]
    extern "C" {
        fn cos(x: f64) -> f64;
    }

    fn main() {
        let x = unsafe { cos(0.0) };
        println!("Cosinus: {}", x);
    }

10. Zero-cost Abstractions

    Rust zapewnia wysokopoziomowe funkcje bez narzutu wydajności.

    fn map_example() {
        let numbers = vec![1, 2, 3, 4];
        let squares: Vec<_> = numbers.iter().map(|x| x * x).collect();
        println!("{:?}", squares);
    }

    fn main() {
        map_example();
    }

11. Unsafe Code i Bezpośrednie Zarządzanie Pamięcią

Rust pozwala na pisanie niebezpiecznego kodu przy użyciu bloku unsafe.

    fn main() {
        let mut x: i32 = 42;
        let r: *mut i32 = &mut x;
        
        unsafe {
            *r += 1; // Bezpośrednia manipulacja wskaźnikiem
            println!("x: {}", *r);
        }
    }

12. Typy Asocjacyjne w Traitach

Rust wspiera typy związane z traitami, co pozwala na bardziej elastyczne projektowanie.

    trait Container {
        type Item;
        fn add(&mut self, item: Self::Item);
    }

    struct Stack<T> {
        items: Vec<T>,
    }

    impl<T> Container for Stack<T> {
        type Item = T;

        fn add(&mut self, item: T) {
            self.items.push(item);
        }
    }

    fn main() {
        let mut stack: Stack<i32> = Stack { items: vec![] };
        stack.add(10);
        println!("{:?}", stack.items);
    }

13. Standard Library: Iterator i Lazy Evaluation

Rust pozwala na leniwe przetwarzanie danych dzięki iteratorom.

    fn main() {
        let nums = vec![1, 2, 3, 4, 5];
        let even_nums: Vec<_> = nums
            .iter()
            .filter(|&&x| x % 2 == 0)
            .map(|&x| x * 2)
            .collect();
        println!("{:?}", even_nums); // [4, 8]
    }

14. Cow (Copy-On-Write)

    Rust optymalizuje użycie danych poprzez strategię Copy-On-Write.

    use std::borrow::Cow;

    fn process_string(input: &str) -> Cow<str> {
        if input.contains(' ') {
            Cow::Owned(input.replace(" ", "_"))
        } else {
            Cow::Borrowed(input)
        }
    }

    fn main() {
        let result = process_string("Hello World");
        println!("{}", result); // Hello_World
    }

15. Advanced Pattern Matching

Rust pozwala dopasowywać złożone struktury i wartości.

    fn main() {
        let data = (1, "Rust", 3.14);

        match data {
            (1, "Rust", x) if x > 3.0 => println!("Pasuje: {:?}", data),
            _ => println!("Nie pasuje!"),
        }
    }

16. Pinning i std::pin::Pin

Zapobiega przenoszeniu danych, co jest kluczowe w przypadku wskaźników surowych i asynchronicznych operacji.

    use std::pin::Pin;

    struct Data {
        value: i32,
    }

    fn main() {
        let mut data = Data { value: 42 };
        let pinned = Pin::new(&mut data);

        println!("Pinned data value: {}", pinned.value);
    }

17. std::cell::RefCell i Mutowalność Wewnętrzna

RefCell pozwala zmieniać dane nawet w przypadku niemutowalnych struktur.

    use std::cell::RefCell;

    struct MyStruct {
        value: RefCell<i32>,
    }

    fn main() {
        let my_struct = MyStruct {
            value: RefCell::new(5),
        };

        *my_struct.value.borrow_mut() += 10;
        println!("{}", my_struct.value.borrow()); // 15
    }

18. Typy Wielowarstwowe z Wrapping

Rust wspiera pracę z typami zapewniającymi kontrolę nad przepełnieniem.

    use std::num::Wrapping;

    fn main() {
        let a = Wrapping(255u8);
        let b = Wrapping(1u8);
        println!("Wynik: {}", (a + b).0); // 0, bo nastąpiło przepełnienie
    }

19. Custom Allocators

Rust pozwala na tworzenie własnych alokatorów pamięci dla niestandardowych wymagań.

    use std::alloc::{GlobalAlloc, Layout, System};

    struct MyAllocator;

    unsafe impl GlobalAlloc for MyAllocator {
        unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
            System.alloc(layout)
        }

        unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
            System.dealloc(ptr, layout)
        }
    }

    #[global_allocator]
    static GLOBAL: MyAllocator = MyAllocator;

    fn main() {
        let a = Box::new(42);
        println!("Zaalokowana wartość: {}", a);
    }

20. No_std i Programowanie Systemowe

Rust może działać bez standardowej biblioteki, co jest kluczowe w aplikacjach wbudowanych.

    #![no_std]

    #[no_mangle]
    pub extern "C" fn main() -> ! {
        loop {}
    }

21. Zero-Cost Futures i Pin w Asynchronous Rust

Rust zapewnia asynchroniczne programowanie z minimalnym narzutem wydajności dzięki Future i Pin.

    use std::future::Future;
    use std::pin::Pin;
    use std::task::{Context, Poll};

    struct MyFuture;

    impl Future for MyFuture {
        type Output = i32;

        fn poll(self: Pin<&mut Self>, _cx: &mut Context<'_>) -> Poll<Self::Output> {
            Poll::Ready(42) // Zwracamy wynik gotowy natychmiast
        }
    }

    #[tokio::main]
    async fn main() {
        let future = MyFuture;
        println!("Wynik: {}", future.await);
    }

22. Const Generics

Const generics umożliwiają definiowanie typów parametrów opartych na stałych.

    struct ArrayWrapper<T, const N: usize> {
        data: [T; N],
    }

    impl<T, const N: usize> ArrayWrapper<T, N> {
        fn new(data: [T; N]) -> Self {
            Self { data }
        }
    }

    fn main() {
        let array = ArrayWrapper::new([1, 2, 3, 4]);
        println!("{:?}", array.data);
    }

23. Dynamically Sized Types (DSTs)

    Rust obsługuje typy o dynamicznej wielkości, takie jak str i dyn.

    fn print_str(s: &str) {
        println!("Tekst: {}", s);
    }

    fn main() {
        let string = String::from("Rust");
        print_str(&string); // `str` jest DST
    }

24. Custom Derive

Rust umożliwia implementację własnych makr proceduralnych do generowania kodu.

use proc_macro::TokenStream;

    #[proc_macro_derive(MyTrait)]
    pub fn my_trait_derive(_item: TokenStream) -> TokenStream {
        quote::quote! {
            impl MyTrait for #name {
                fn my_method(&self) {
                    println!("MyTrait implemented!");
                }
            }
        }.into()
    }

25. PhantomData

PhantomData pozwala zaznaczyć zależności typów bez przechowywania rzeczywistych wartości.

    use std::marker::PhantomData;

    struct Wrapper<T> {
        _marker: PhantomData<T>,
    }

    fn main() {
        let _x: Wrapper<i32> = Wrapper { _marker: PhantomData };
    }

26. Impl Trait

Uproszczenie deklaracji typów zwracanych przez funkcje dzięki impl Trait.

    fn make_iter() -> impl Iterator<Item = i32> {
        vec![1, 2, 3].into_iter()
    }

    fn main() {
        for val in make_iter() {
            println!("{}", val);
        }
    }

27. Atomic Types i Synchronizacja

Rust obsługuje typy atomowe dla programowania wielowątkowego.

    use std::sync::atomic::{AtomicUsize, Ordering};

    static COUNTER: AtomicUsize = AtomicUsize::new(0);

    fn main() {
        COUNTER.fetch_add(1, Ordering::SeqCst);
        println!("Licznik: {}", COUNTER.load(Ordering::SeqCst));
    }

28. Pinning i Future z Referencjami

Pin pozwala tworzyć asynchroniczne operacje na referencjach bez ich przenoszenia.

    use std::pin::Pin;

    struct Data {
        value: i32,
    }

    fn main() {
        let mut data = Data { value: 42 };
        let pinned_data = Pin::new(&mut data);
        println!("Wartość: {}", pinned_data.value);
    }

29. Statyczne Zmienne

    Rust wspiera bezpieczne używanie zmiennych statycznych.

    static GLOBAL: i32 = 42;

    fn main() {
        println!("Wartość globalna: {}", GLOBAL);
    }

30. Thread Local Storage (TLS)

Zmienne wątku pozwalają przechowywać dane specyficzne dla danego wątku.

    use std::cell::RefCell;
    use std::thread;

    thread_local! {
        static THREAD_LOCAL_VAR: RefCell<i32> = RefCell::new(0);
    }

    fn main() {
        let handles: Vec<_> = (0..5).map(|i| {
            thread::spawn(move || {
                THREAD_LOCAL_VAR.with(|val| {
                    *val.borrow_mut() = i;
                    println!("Wątek {}: {}", i, *val.borrow());
                });
            })
        }).collect();

        for handle in handles {
            handle.join().unwrap();
        }
    }

31. Crate-level Attributes

Crate-level attributes pozwalają kontrolować zachowanie kompilatora na poziomie całego projektu.

    #![warn(clippy::all)]
    #![allow(dead_code)]

    fn main() {
        println!("Crate-level attributes są używane!");
    }

32. Function-like Procedural Macros

Proceduralne makra funkcjonalne generują kod na podstawie wejścia.

    use proc_macro::TokenStream;

    #[proc_macro]
    pub fn generate_function(input: TokenStream) -> TokenStream {
        let name = input.to_string();
        format!(
            "fn {}() {{ println!(\"Funkcja generowana makrem\"); }}",
            name
        )
        .parse()
        .unwrap()
    }

33. Typy Never (!)

    Typ ! oznacza funkcje, które nigdy nie zwracają wartości.

    fn never_returns() -> ! {
        panic!("Nigdy nie zwraca");
    }

    fn main() {
        never_returns();
    }

34. Panic i Obsługa Błędów

Rust obsługuje kontrolowane wywołania paniki i zarządzanie błędami.

    fn divide(a: i32, b: i32) -> Result<i32, String> {
        if b == 0 {
            Err(String::from("Nie można dzielić przez zero"))
        } else {
            Ok(a / b)
        }
    }

    fn main() {
        match divide(10, 0) {
            Ok(result) => println!("Wynik: {}", result),
            Err(e) => println!("Błąd: {}", e),
        }
    }

35. Type Aliases

Type aliases upraszczają kod, tworząc przyjazne nazwy dla złożonych typów.

    type ComplexMap = std::collections::HashMap<String, Vec<i32>>;

    fn main() {
        let mut map: ComplexMap = std::collections::HashMap::new();
        map.insert(String::from("Klucz"), vec![1, 2, 3]);
        println!("{:?}", map);
    }

36. Custom Operators z Traitami

Dzięki traitom można tworzyć niestandardowe operatory.

    use std::ops::Add;

    struct Point {
        x: i32,
        y: i32,
    }

    impl Add for Point {
        type Output = Self;

        fn add(self, other: Self) -> Self {
            Point {
                x: self.x + other.x,
                y: self.y + other.y,
            }
        }
    }

    fn main() {
        let p1 = Point { x: 1, y: 2 };
        let p2 = Point { x: 3, y: 4 };
        let p3 = p1 + p2;
        println!("Nowy punkt: ({}, {})", p3.x, p3.y);
    }

37. Dynamiczne Wskaźniki (Box, Rc, Arc)

Rust pozwala na zarządzanie wskaźnikami dynamicznymi.

    use std::rc::Rc;

    fn main() {
        let a = Rc::new(5);
        let b = Rc::clone(&a);
        println!("a: {}, b: {}", a, b); // Oba mają dostęp do tej samej wartości
    }

38. Embedded Rust

Rust wspiera aplikacje na mikrokontrolery, jak ARM Cortex-M, używając no_std.

    #![no_std]
    #![no_main]

    use cortex_m_rt::entry;

    #[entry]
    fn main() -> ! {
        loop {}
    }

39. Pinning z Future i Wskaźnikami

Pinning pozwala kontrolować lokalizację w pamięci.

    use std::pin::Pin;

    struct Data {
        value: i32,
    }

    fn main() {
        let mut data = Data { value: 42 };
        let pinned = Pin::new(&mut data);
        println!("Pinned value: {}", pinned.value);
    }

40. Custom Error Types

Rust pozwala tworzyć niestandardowe typy błędów.

    use std::fmt;

    #[derive(Debug)]
    struct CustomError {
        details: String,
    }

    impl fmt::Display for CustomError {
        fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
            write!(f, "CustomError: {}", self.details)
        }
    }

    fn error_function() -> Result<(), CustomError> {
        Err(CustomError {
            details: String::from("Wystąpił błąd"),
        })
    }

    fn main() {
        if let Err(e) = error_function() {
            println!("{}", e);
        }
    }

41. Impl Trait w Parametrach Funkcji

Rust umożliwia użycie impl Trait jako uproszczenie dla generyków.

    fn print_items(items: impl Iterator<Item = i32>) {
        for item in items {
            println!("{}", item);
        }
    }

    fn main() {
        let vec = vec![1, 2, 3];
        print_items(vec.into_iter());
    }

42. Typy Cell i RefCell

Zapewniają wewnętrzną mutowalność, nawet w przypadku niemutowalnych struktur.

    use std::cell::Cell;

    struct MyStruct {
        value: Cell<i32>,
    }

    fn main() {
        let my_struct = MyStruct { value: Cell::new(42) };
        my_struct.value.set(100); // Zmiana wartości mimo niemutowalnego obiektu
        println!("Wartość: {}", my_struct.value.get());
    }

43. Option i Result jako Monady

    Rust obsługuje idiomatyczne przekształcenia wyników i opcjonalnych wartości.

    fn divide(a: i32, b: i32) -> Option<i32> {
        if b == 0 {
            None
        } else {
            Some(a / b)
        }
    }

    fn main() {
        let result = divide(10, 2).unwrap_or(0);
        println!("Wynik: {}", result);
    }

44. Rustdoc – Wbudowana Dokumentacja

Rust posiada wbudowany system generowania dokumentacji.

    /// Funkcja dodaje dwie liczby.
    /// 
    /// # Przykład
    /// ```
    /// let wynik = add(2, 3);
    /// assert_eq!(wynik, 5);
    /// ```
    fn add(a: i32, b: i32) -> i32 {
        a + b
    }

45. Wskaźniki surowe (*const i *mut)

Rust obsługuje wskaźniki surowe dla bardziej zaawansowanych operacji pamięciowych.

    fn main() {
        let mut x = 10;
        let ptr: *mut i32 = &mut x;

        unsafe {
            *ptr += 1;
            println!("Wartość: {}", *ptr);
        }
    }

46. Deklaracje const fn

Rust pozwala definiować funkcje stałe, które mogą być wywoływane w czasie kompilacji.

    const fn square(x: i32) -> i32 {
        x * x
    }

    const RESULT: i32 = square(5);

    fn main() {
        println!("Wynik: {}", RESULT);
    }

47. Typy Arc i Wielowątkowość

Arc to wskaźnik liczony atomowo, idealny dla wielowątkowości.

    use std::sync::Arc;
    use std::thread;

    fn main() {
        let data = Arc::new(vec![1, 2, 3]);
        let data_clone = Arc::clone(&data);

        let handle = thread::spawn(move || {
            println!("Dane: {:?}", data_clone);
        });

        handle.join().unwrap();
    }

48. Wyrażenia i Bloki jako Wyniki

W Rust wszystko jest wyrażeniem, co pozwala na bardziej elegancki kod.

    fn main() {
        let result = {
            let x = 10;
            let y = 20;
            x + y // Wynik bloku
        };

        println!("Wynik: {}", result);
    }

49. Custom Allocators z GlobalAlloc

Rust pozwala tworzyć własne alokatory pamięci.

    use std::alloc::{GlobalAlloc, Layout, System};

    struct MyAllocator;

    unsafe impl GlobalAlloc for MyAllocator {
        unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
            println!("Alokowanie: {:?}", layout);
            System.alloc(layout)
        }

        unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
            println!("Zwalnianie: {:?}", layout);
            System.dealloc(ptr, layout)
        }
    }

    #[global_allocator]
    static GLOBAL: MyAllocator = MyAllocator;

    fn main() {
        let _x = Box::new(42);
    }

50. unsafe Traits

Rust pozwala definiować trójkąty bezpieczeństwa dla bardziej zaawansowanych operacji.

    unsafe trait UnsafeTrait {
        fn unsafe_method(&self);
    }

    struct MyStruct;

    unsafe impl UnsafeTrait for MyStruct {
        fn unsafe_method(&self) {
            println!("Unsafe trait method called");
        }
    }

    fn main() {
        let obj = MyStruct;
        unsafe { obj.unsafe_method() };
    }

51. Wielowątkowość z Mutex i RwLock

Rust zapewnia mechanizmy synchronizacji, takie jak Mutex i RwLock.

    use std::sync::{Arc, Mutex};
    use std::thread;

    fn main() {
        let counter = Arc::new(Mutex::new(0));
        let mut handles = vec![];

        for _ in 0..10 {
            let counter = Arc::clone(&counter);
            let handle = thread::spawn(move || {
                let mut num = counter.lock().unwrap();
                *num += 1;
            });
            handles.push(handle);
        }

        for handle in handles {
            handle.join().unwrap();
        }

        println!("Wynik: {}", *counter.lock().unwrap());
    }

52. Smart Pointers: Box, Rc, Arc i Weak

Rust pozwala na kontrolowanie cykli referencji przy użyciu Weak.

    use std::rc::{Rc, Weak};

    struct Node {
        value: i32,
        parent: Option<Weak<Node>>,
        children: Vec<Rc<Node>>,
    }

    fn main() {
        let parent = Rc::new(Node {
            value: 10,
            parent: None,
            children: vec![],
        });

        let child = Rc::new(Node {
            value: 5,
            parent: Some(Rc::downgrade(&parent)),
            children: vec![],
        });

        println!("Rodzic: {}", parent.value);
        println!("Dziecko: {}", child.value);
    }

53. Deklaracje dyn w Trait Objects

Rust pozwala na dynamiczne dopasowanie implementacji traitów w czasie wykonywania.

    trait Drawable {
        fn draw(&self);
    }

    struct Circle;

    impl Drawable for Circle {
        fn draw(&self) {
            println!("Rysuję okrąg");
        }
    }

    fn draw_object(obj: &dyn Drawable) {
        obj.draw();
    }

    fn main() {
        let circle = Circle;
        draw_object(&circle);
    }

54. GATs (Generic Associated Types)

GATs umożliwiają bardziej elastyczne definicje typów generycznych związanych z traitami.

    trait StreamingIterator {
        type Item<'a>;

        fn next<'a>(&'a mut self) -> Option<Self::Item<'a>>;
    }

    struct MyIterator {
        data: Vec<i32>,
        pos: usize,
    }

    impl StreamingIterator for MyIterator {
        type Item<'a> = &'a i32;

        fn next<'a>(&'a mut self) -> Option<Self::Item<'a>> {
            if self.pos >= self.data.len() {
                None
            } else {
                let item = &self.data[self.pos];
                self.pos += 1;
                Some(item)
            }
        }
    }

    fn main() {
        let mut iter = MyIterator {
            data: vec![1, 2, 3],
            pos: 0,
        };

        while let Some(item) = iter.next() {
            println!("{}", item);
        }
    }

55. Typy Enum z Danymi

Enumy mogą przechowywać różne typy danych w jednej strukturze.

    enum Message {
        Text(String),
        Number(i32),
        Float(f64),
    }

    fn process_message(msg: Message) {
        match msg {
            Message::Text(text) => println!("Tekst: {}", text),
            Message::Number(num) => println!("Liczba całkowita: {}", num),
            Message::Float(float) => println!("Liczba zmiennoprzecinkowa: {}", float),
        }
    }

    fn main() {
        let msg = Message::Text(String::from("Witaj"));
        process_message(msg);
    }

56. Intrinsics i SIMD

Rust obsługuje instrukcje SIMD do optymalizacji.

    use std::arch::x86_64::*;

    fn main() {
        unsafe {
            let a = _mm_set1_ps(1.0); // Ustawienie wektora 4x1.0
            let b = _mm_set1_ps(2.0); // Ustawienie wektora 4x2.0
            let result = _mm_add_ps(a, b); // Dodanie wektorów
            let mut output = [0.0; 4];
            _mm_storeu_ps(output.as_mut_ptr(), result);
            println!("{:?}", output);
        }
    }

57. Obsługa Stosu i Sterty

Rust pozwala na precyzyjną kontrolę alokacji na stosie (stack) i stercie (heap).

    fn main() {
        let stack_var = 10; // Zmienna na stosie
        let heap_var = Box::new(20); // Zmienna na stercie

        println!("Stack: {}, Heap: {}", stack_var, *heap_var);
    }

58. NonNull do Zarządzania Pamięcią

NonNull pozwala zarządzać wskaźnikami bez zerowych wartości.

    use std::ptr::NonNull;

    fn main() {
        let mut value = 42;
        let ptr = NonNull::new(&mut value as *mut i32).expect("Wskaźnik nie może być null");
        unsafe {
            *ptr.as_ptr() = 100;
        }
        println!("Nowa wartość: {}", value);
    }

59. ManuallyDrop

ManuallyDrop pozwala na ręczne zarządzanie destruktorami.

    use std::mem::ManuallyDrop;

    fn main() {
        let value = ManuallyDrop::new(String::from("Rust"));

        println!("Wartość: {}", value);

        // Bez wywołania drop() String nie zostanie zniszczony automatycznie.
    }

60. Liczba Kresów w Typach Generycznych

Rust pozwala na definiowanie typów z wieloma ograniczeniami traitów.

    fn display<T: ToString + Clone>(item: T) {
        println!("{}", item.to_string());
    }

    fn main() {
        display(String::from("Witaj!"));
    }

61. TryFrom i TryInto

Rust obsługuje konwersje typów z możliwością obsługi błędów.

    use std::convert::TryFrom;

    struct EvenNumber(i32);

    impl TryFrom<i32> for EvenNumber {
        type Error = String;

        fn try_from(value: i32) -> Result<Self, Self::Error> {
            if value % 2 == 0 {
                Ok(EvenNumber(value))
            } else {
                Err(String::from("Nieparzysta liczba"))
            }
        }
    }

    fn main() {
        match EvenNumber::try_from(4) {
            Ok(num) => println!("Parzysta: {}", num.0),
            Err(e) => println!("Błąd: {}", e),
        }
    }

62. Unit Tests i Makro #[test]

Rust posiada wbudowany system testowania.

    fn add(a: i32, b: i32) -> i32 {
        a + b
    }

    #[cfg(test)]
    mod tests {
        use super::*;

        #[test]
        fn test_add() {
            assert_eq!(add(2, 3), 5);
        }
    }

63. std::any::TypeId

Rust pozwala sprawdzać typy w czasie wykonywania.

    use std::any::TypeId;

    fn main() {
        let x = 42;
        println!("Typ x: {:?}", TypeId::of::<i32>());
    }

64. Implementacja Własnych Ograniczeń Traitów

Rust pozwala na definiowanie zaawansowanych ograniczeń przy użyciu where.

    fn calculate<T>(x: T)
    where
        T: PartialOrd + Copy,
    {
        if x > T::default() {
            println!("Większe od domyślnej wartości");
        }
    }

    fn main() {
        calculate(42);
    }

65. Statyczna Analiza Wartości (static_assertions)

Biblioteki pozwalają na przeprowadzanie statycznych asercji.

    use static_assertions::const_assert;

    const VALUE: i32 = 10;
    const_assert!(VALUE > 0);

    fn main() {
        println!("Wartość jest poprawna!");
    }

66. Sized Trait i Typy o Nieokreślonym Rozmiarze

Rust wymusza sprawdzenie, czy typ ma znany rozmiar.

    fn print_size<T: ?Sized>(_: &T) {
        println!("Typ ma nieokreślony rozmiar");
    }

    fn main() {
        let s: &str = "Rust";
        print_size(s);
    }

67. Default Trait

Rust umożliwia ustawianie domyślnych wartości dla typów.

    #[derive(Default)]
    struct Config {
        width: u32,
        height: u32,
    }

    fn main() {
        let config: Config = Default::default();
        println!("Szerokość: {}, Wysokość: {}", config.width, config.height);
    }

68. Wielokrotne Mutowalne Referencje z RefCell

RefCell umożliwia mutowalne referencje w czasie wykonywania.

    use std::cell::RefCell;

    fn main() {
        let data = RefCell::new(42);
        {
            let mut value = data.borrow_mut();
            *value += 10;
        }
        println!("Wartość: {}", data.borrow());
    }

69. async w Komunikacji Sieciowej

Rust wspiera asynchroniczne połączenia sieciowe.

    use tokio::net::TcpStream;

    #[tokio::main]
    async fn main() {
        let stream = TcpStream::connect("127.0.0.1:8080").await;
        match stream {
            Ok(_) => println!("Połączono!"),
            Err(e) => println!("Błąd: {}", e),
        }
    }

70. unsafe z Custom Allocators

Rust pozwala na niestandardowe zarządzanie pamięcią w sposób bezpieczny.

    use std::alloc::{GlobalAlloc, Layout, System};

    struct MyAllocator;

    unsafe impl GlobalAlloc for MyAllocator {
        unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
            println!("Alokowanie pamięci: {:?}", layout);
            System.alloc(layout)
        }

        unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
            println!("Zwalnianie pamięci: {:?}", layout);
            System.dealloc(ptr, layout);
        }
    }

    #[global_allocator]
    static GLOBAL: MyAllocator = MyAllocator;

    fn main() {
        let _x = Box::new(42);
    }

71. PhantomPinned

Rust pozwala blokować przemieszczanie obiektów w pamięci przy użyciu PhantomPinned.

    use std::marker::PhantomPinned;
    use std::pin::Pin;

    struct MyStruct {
        data: String,
        _pin: PhantomPinned,
    }

    impl MyStruct {
        fn new(data: String) -> Pin<Box<Self>> {
            Box::pin(MyStruct {
                data,
                _pin: PhantomPinned,
            })
        }
    }

    fn main() {
        let my_struct = MyStruct::new(String::from("Rust"));
        println!("Zainicjalizowano obiekt: {}", my_struct.data);
    }

72. Typy Generyczne z Box<dyn Trait>

Rust obsługuje dynamiczne polimorfizmy z generykami.

    trait Draw {
        fn draw(&self);
    }

    struct Circle;

    impl Draw for Circle {
        fn draw(&self) {
            println!("Rysuję okrąg");
        }
    }

    fn render(shape: Box<dyn Draw>) {
        shape.draw();
    }

    fn main() {
        let circle = Box::new(Circle);
        render(circle);
    }

73. Leniwe Alokacje z Lazy

Leniwa inicjalizacja wartości może być osiągnięta przy użyciu Lazy.

    use once_cell::sync::Lazy;

    static CONFIG: Lazy<String> = Lazy::new(|| {
        println!("Inicjalizuję konfigurację");
        String::from("Rust Configuration")
    });

    fn main() {
        println!("Przed dostępem do CONFIG");
        println!("CONFIG: {}", *CONFIG);
    }

74. Deklaracje Box i Struktury Rekurencyjne

Rust wymaga Box do rekurencyjnych typów danych.

    enum List {
        Node(i32, Box<List>),
        Empty,
    }

    fn main() {
        let list = List::Node(1, Box::new(List::Node(2, Box::new(List::Empty))));
    }


75. Interfejsy API z Builder Pattern

Rust pozwala na tworzenie wzorca projektowego budowniczego.

    struct Config {
        width: u32,
        height: u32,
    }

    struct ConfigBuilder {
        width: u32,
        height: u32,
    }

    impl ConfigBuilder {
        fn new() -> Self {
            ConfigBuilder { width: 0, height: 0 }
        }

        fn width(mut self, width: u32) -> Self {
            self.width = width;
            self
        }

        fn height(mut self, height: u32) -> Self {
            self.height = height;
            self
        }

        fn build(self) -> Config {
            Config {
                width: self.width,
                height: self.height,
            }
        }
    }

    fn main() {
        let config = ConfigBuilder::new().width(800).height(600).build();
        println!("Szerokość: {}, Wysokość: {}", config.width, config.height);
    }

76. Kontrola Pamięci z Arc i Mutex

Rust pozwala na bezpieczne współdzielenie danych w wielowątkowości.

    use std::sync::{Arc, Mutex};
    use std::thread;

    fn main() {
        let data = Arc::new(Mutex::new(0));
        let mut handles = vec![];

        for _ in 0..5 {
            let data = Arc::clone(&data);
            let handle = thread::spawn(move || {
                let mut num = data.lock().unwrap();
                *num += 1;
            });
            handles.push(handle);
        }

        for handle in handles {
            handle.join().unwrap();
        }

        println!("Wynik: {}", *data.lock().unwrap());
    }

77. Obsługa Środowiska env! i option_env!

Makra pozwalają na wbudowaną obsługę zmiennych środowiskowych.

    fn main() {
        const RUST_VERSION: &str = env!("CARGO_PKG_VERSION");
        println!("Wersja Rust: {}", RUST_VERSION);

        if let Some(path) = option_env!("PATH") {
            println!("PATH: {}", path);
        }
    }

78. Dynamiczna Obsługa Błędów z anyhow

Biblioteka anyhow upraszcza pracę z błędami.

    use anyhow::{Context, Result};

    fn might_fail(value: i32) -> Result<()> {
        if value < 0 {
            Err(anyhow::anyhow!("Negatywna wartość"))?;
        }
        Ok(())
    }

    fn main() -> Result<()> {
        might_fail(-1).context("Wystąpił problem")?;
        Ok(())
    }

79. Definiowanie Modułów z mod

Rust wspiera hierarchiczne zarządzanie kodem.

    mod my_module {
        pub fn greet() {
            println!("Witaj z modułu!");
        }
    }

    fn main() {
        my_module::greet();
    }

80. Tworzenie Loggerów z log

Rust pozwala na implementację uniwersalnych loggerów.

    use log::{info, warn};

    fn main() {
        env_logger::init();
        info!("Informacja logowania");
        warn!("Ostrzeżenie logowania");
    }

81. Tworzenie Własnych Atrybutów Proceduralnych

Proceduralne makra atrybutów mogą modyfikować funkcje, struktury lub moduły.

    use proc_macro::TokenStream;

    #[proc_macro_attribute]
    pub fn my_attribute(_attr: TokenStream, item: TokenStream) -> TokenStream {
        let input = item.to_string();
        let output = format!("fn main() {{ println!(\"Zmienione: {}\" ); }}", input);
        output.parse().unwrap()
    }

82. Dynamiczne Ładowanie Bibliotek (dlopen)

Rust obsługuje dynamiczne ładowanie bibliotek.

    use libloading::{Library, Symbol};

    fn main() {
        let lib = Library::new("libm.so.6").unwrap();
        unsafe {
            let cos: Symbol<unsafe extern "C" fn(f64) -> f64> = lib.get(b"cos").unwrap();
            println!("Cosinus: {}", cos(0.0));
        }
    }

83. VecDeque dla Dwukierunkowych Kolejek

VecDeque umożliwia wydajną manipulację na obu końcach.

    use std::collections::VecDeque;

    fn main() {
        let mut deque: VecDeque<i32> = VecDeque::new();
        deque.push_front(1);
        deque.push_back(2);
        println!("Deque: {:?}", deque);
    }


84. Obsługa Globalnych Zmiennych z lazy_static!

lazy_static! pozwala na inicjalizację zmiennych globalnych w czasie wykonywania.

    #[macro_use]
    extern crate lazy_static;

    use std::sync::Mutex;

    lazy_static! {
        static ref GLOBAL: Mutex<i32> = Mutex::new(0);
    }

    fn main() {
        {
            let mut data = GLOBAL.lock().unwrap();
            *data += 1;
        }
        println!("GLOBAL: {}", *GLOBAL.lock().unwrap());
    }

85. Obsługa Wskaźników NonNull

NonNull pozwala zarządzać wskaźnikami bez zerowych wartości.

    use std::ptr::NonNull;

    fn main() {
        let mut x = 42;
        let ptr = NonNull::new(&mut x as *mut i32).unwrap();
        unsafe {
            *ptr.as_ptr() += 10;
        }
        println!("Nowa wartość: {}", x);
    }

86. Iteratory Nad Słownikami (HashMap)

Rust obsługuje iteracje nad kluczami i wartościami.

    use std::collections::HashMap;

    fn main() {
        let mut map = HashMap::new();
        map.insert("a", 1);
        map.insert("b", 2);

        for (key, value) in map.iter() {
            println!("Klucz: {}, Wartość: {}", key, value);
        }
    }

87. Implementacja Własnych Makr z macro_rules!

Makra deklaratywne pozwalają na generowanie kodu.

    macro_rules! repeat {
        ($value:expr, $count:expr) => {
            vec![$value; $count]
        };
    }

    fn main() {
        let repeated = repeat!(42, 5);
        println!("{:?}", repeated);
    }

88. Custom Error Types z thiserror

thiserror upraszcza tworzenie niestandardowych błędów.

    use thiserror::Error;

    #[derive(Error, Debug)]
    enum MyError {
        #[error("Błąd IO: {0}")]
        Io(#[from] std::io::Error),
        #[error("Nieznany błąd")]
        Unknown,
    }

    fn main() -> Result<(), MyError> {
        Err(MyError::Unknown)?;
        Ok(())
    }

89. Skanowanie Strumieni z Stream

Rust obsługuje operacje na strumieniach z pomocą async i Stream.

    use futures::stream::{self, StreamExt};

    #[tokio::main]
    async fn main() {
        let stream = stream::iter(vec![1, 2, 3]);
        let sum: i32 = stream.map(|x| x * 2).sum().await;
        println!("Suma: {}", sum);
    }

90. Tworzenie Własnych Kolekcji

Możesz zaimplementować swoje struktury kolekcji, takie jak stosy.

    struct Stack<T> {
        elements: Vec<T>,
    }

    impl<T> Stack<T> {
        fn new() -> Self {
            Stack { elements: vec![] }
        }

        fn push(&mut self, item: T) {
            self.elements.push(item);
        }

        fn pop(&mut self) -> Option<T> {
            self.elements.pop()
        }
    }

    fn main() {
        let mut stack = Stack::new();
        stack.push(1);
        stack.push(2);
        println!("Popped: {:?}", stack.pop());
    }

91. serde dla Serializacji i Deserializacji

Rust wspiera potężne mechanizmy serializacji i deserializacji danych z pomocą serde.

    use serde::{Serialize, Deserialize};
    use serde_json;

    #[derive(Serialize, Deserialize, Debug)]
    struct User {
        name: String,
        age: u32,
    }

    fn main() {
        let user = User {
            name: String::from("Jan"),
            age: 30,
        };

        // Serializacja
        let json = serde_json::to_string(&user).unwrap();
        println!("JSON: {}", json);

        // Deserializacja
        let deserialized: User = serde_json::from_str(&json).unwrap();
        println!("Użytkownik: {:?}", deserialized);
    }

92. Asynchroniczne Kanały z tokio

Rust obsługuje komunikację między wątkami przy użyciu asynchronicznych kanałów.

    use tokio::sync::mpsc;

    #[tokio::main]
    async fn main() {
        let (tx, mut rx) = mpsc::channel(32);

        tokio::spawn(async move {
            tx.send("Wiadomość").await.unwrap();
        });

        while let Some(msg) = rx.recv().await {
            println!("Odebrano: {}", msg);
        }
    }

93. Dynamiczna Typizacja z Any

Rust pozwala na przechowywanie i konwersję danych do typów dynamicznych.

    use std::any::Any;

    fn print_type<T: Any>(value: T) {
        if value.is::<i32>() {
            println!("To jest i32!");
        } else {
            println!("To nie jest i32.");
        }
    }

    fn main() {
        print_type(42);
        print_type("tekst");
    }

94. Iterator Adapters

Rust pozwala na łączenie adapterów iteratorów dla wydajnych przekształceń danych.

    fn main() {
        let numbers = vec![1, 2, 3, 4];
        let squares: Vec<_> = numbers
            .iter()
            .filter(|&&x| x % 2 == 0)
            .map(|&x| x * x)
            .collect();

        println!("Kwadraty: {:?}", squares);
    }

95. std::sync::Barrier do Synchronizacji Wątków

Barrier synchronizuje wiele wątków w określonym punkcie.

    use std::sync::{Arc, Barrier};
    use std::thread;

    fn main() {
        let barrier = Arc::new(Barrier::new(5));
        let mut handles = vec![];

        for _ in 0..5 {
            let c = Arc::clone(&barrier);
            let handle = thread::spawn(move || {
                println!("Przed barierą");
                c.wait();
                println!("Za barierą");
            });
            handles.push(handle);
        }

        for handle in handles {
            handle.join().unwrap();
        }
    }

96. Pin i Operacje na Referencjach

Pin zapewnia, że dane nie zostaną przeniesione w pamięci.

    use std::pin::Pin;

    struct Data {
        value: i32,
    }

    fn main() {
        let mut data = Data { value: 42 };
        let pinned = Pin::new(&mut data);
        println!("Wartość: {}", pinned.value);
    }

97. Struktury Rozproszone z DashMap

DashMap to szybka i bezpieczna mapa wielowątkowa.

    use dashmap::DashMap;

    fn main() {
        let map = DashMap::new();
        map.insert("klucz", "wartość");

        if let Some(value) = map.get("klucz") {
            println!("Wartość: {}", *value);
        }
    }

98. Cow (Copy-On-Write)

Cow pozwala na optymalizację przy współdzieleniu danych.

    use std::borrow::Cow;

    fn modify_string(input: &str) -> Cow<str> {
        if input.contains(' ') {
            Cow::Owned(input.replace(" ", "_"))
        } else {
            Cow::Borrowed(input)
        }
    }

    fn main() {
        let result = modify_string("Hello World");
        println!("{}", result);
    }

99. Iterator::fold dla Akumulacji

fold pozwala zredukować dane do jednej wartości.

    fn main() {
        let numbers = vec![1, 2, 3, 4];
        let sum = numbers.iter().fold(0, |acc, &x| acc + x);
        println!("Suma: {}", sum);
    }

100. Tworzenie no_std Aplikacji

Rust pozwala na tworzenie aplikacji bez standardowej biblioteki.

    #![no_std]
    #![no_main]

    use core::panic::PanicInfo;

    #[no_mangle]
    pub extern "C" fn _start() -> ! {
        loop {}
    }

    #[panic_handler]
    fn panic(_info: &PanicInfo) -> ! {
        loop {}
    }