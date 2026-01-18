# Yanji Programming Language

**Yanji** is a powerful, general purpose and procedural programming language, its started to developed by Christian Vaydal in November 2025.
Yanji is low-level memory access, very fast and easy to learn. Its inspired by ***C/C++, Rust, and Python***.

The Yanji's compiler is **Yanc**, which is powered by LLVM, making it very fast that similar to Clang, Rustc.

**Example syntax:**
```c
#include STDIO

// this is the main function
function i32 main() {
  std::write("hello world");
}
```
- Syntax is very similar to C++, Rust and Python.
- Its very fast, comparable to Rust.
- Lightweight.
- Easy to understand.

**More complex code example:**
```c
#include STDIO

enum Team{
	Green,
	Blue,
	Yellow,
	Red
};

struct Student{
	char *name;
	i32 age;
	idouble grade;
	Team team;
};
// this is the main function
function i32 main() {
  Student student{
	  "John",
	  21,
	  89.9,
	  Team.Red
  };

	std::write("Name: %s\nAge: %d\nGrade: %f", student.name, student.age, student.grade);
}
```


**Compile:**
```bash
yanc -o main main.yan
./main
```

