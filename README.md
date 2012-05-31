vargen
========
Script for generating variable argument c++ class/function templates. 

Requires python 3.2.2 

Check the examples/ folder for examples of using vargen syntax.

### Why
  Support for variable argument(C++11) class and function templates 
  aren't fully supported in most C++ compilers so writing template libraries
  that require unique specializations can be a chore and error prone. 
  I needed a quick and dirty script to generate boilerplate template code using a simple syntax.
  vargen isn't unique, there are alternatives that are more feature complete:
  
  [boost preprocessor](http://www.boost.org/doc/libs/1_49_0/libs/preprocessor/doc/index.html)
  
  [google pump] (http://code.google.com/p/googletest/wiki/PumpManual)

### Examples:
##### Example 0A: Special behavior of no trailing characters in an operation.
```
@START 1,3
@(T$ member$)
@STOP
```
##### Generates:
```
T1 member1, T2 member2, T3 member3
```


##### Example 0B: Special behavior of trailing characters in an operation.
```
@START 1,3
@(T$ member$; )
@STOP
```
##### Generates:
```
T1 member1; T2 member2; T3 member3;
```
#####  Example 1: Behavior of [1,3] iteration operation
```
@START 1,3
template<@(class T$)> struct List$;
@STOP
```
##### Generates:
```
template<class T1> struct List1;
template<class T2> struct List2;
template<class T3> struct List3;
```
##### Example 2: Behavior of 3-repetition operation
```
@START 1,3
template<@3(class T$)> struct List$;
@STOP
```
##### Generates:
```
template<class T1, class T1, class T1> struct List1;
template<class T2, class T2, class T2> struct List2;
template<class T3, class T3, class T3> struct List3;
```

##### Example 3: Behavior of [1,4] iteration with parameters
```
@START 1,4
template<@(class T$)>
struct Args<@(class T$), @$END - $(Empty)>;
@STOP
```
##### Generates:
  ```
template<class T1>
struct Args<T1,Empty,Empty,Empty>{};

template<class T1, class T2>
struct Args<T1,T2,Empty,Empty>{};

template<class T1, class T2, class T3>
struct Args<T1,T2,T3,Empty>{};

template<class T1, class T2, class T3, class T4>
struct Args<T1,T2,T3,T4>{};
```
##### Example 4: Custom iterations
```
@START 1, 3
template<@(class T$)>
struct Args$ : public Args$-1{
  T$ a$;

  Args$(@(T$ p$))
  : Args$-1(@,$-1(p$)),
    a$(p$){}
};
@STOP
```
##### Generates:
  ```
template<class T1>
struct Args1 : public Args0{
  T1 a1;

  Args1(T1 p1)
   : Args0(),
     a1(p1){}
};


template<class T1, class T2>
struct Args2 : public Args1{
  T2 a2;

  Args2(T1 p1, T2 p2)
   : Args1(p1),
     a2(p2){}
};


template<class T1, class T2, class T3>
struct Args3 : public Args2{
  T3 a3;

  Args3(T1 p1, T2 p2, T3 p3)
   : Args2(p1, p2),
     a3(p3){}
};
```