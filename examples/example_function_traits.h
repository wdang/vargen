#ifndef CORE_FUNCTION_TRAITS_H
#define CORE_FUNCTION_TRAITS_H

// Provides typedefs for function signatures

// arg_traits<T> is used to forward function
// parameters. Used internally by the function_traits<T>
// @forward_type - the type as is
// @stored_type  - the type suitable for class storage. the type is converted into a type
//                 that does not need to be initialized in a class constructor:
//                 T* const becomes T*
//                 const T& becomes T
//@raw_type      - type removed of const,pointer,reference and volatile

// Using the following as examples:
//
// struct Example {
//   int DoSomething(float);
// };
//
// double StaticFunction(const Example&);
//
// Consider the two function_traits:
// 1. function_traits<Example::DoSomething>
// 2. function_traits<StaticFunction>
//
// function_traits typedefs:
// arity        - function arity
//                1. 1
//                2. 1

// @object      - object type if function is a member function signature
//                1. Example
//                2. generic_t

// @result      - return type
//                1. int
//                2. double
//
// @member      - function signature (as member function)
//                1. int (Example::*)(float)
//                2. double (generic_t::*)(const Example&)
//
// @type        - function signature (as static function)
//                1. int(*)(float)
//                2. int(*)(const Example&)
//
// @argN        - type of Nth parameter
//                1. float
//                2. const Example&
//
// @traits      - reflected typedef of function_traits class
//                1. function_traits<Example::DoSomething>
//                2. function_traits<StaticFunction>
template<class ERROR_Type_is_not_a_function_pointer_or_member_function_pointer>
struct function_traits;

// Provides __fastcall and __stdcall specializations for 32bit-windows compilations.
// __fastcall and __stdcall are equivalent to __cdecl on 64-bit compilations
#if defined(_MSC_VER) && !defined(_M_IA64) && !defined(_M_X64)

// __stdcall specializations
template<class R>
struct function_traits<R(__stdcall*) (void)> {
  enum {arity = 0};
  typedef generic_t object;
  typedef R         result;
  typedef R (__stdcall*type)(void);
  typedef R (generic_t::*member)(void);
  typedef function_traits<R(__stdcall*) (void)> traits;
};
@START 1, 10
template<class R, @(class P$)>
struct function_traits<R(__stdcall*) (@(P$))> {
  enum {arity = $};
  typedef R         result;
  typedef generic_t object;
  typedef R (__stdcall*type)(@(P$));
  typedef R (generic_t::*member)(@(P$));
  typedef function_traits<R(__stdcall*) (@(P$))> traits;
  @(typedef P$ arg$; )
  
};
@STOP

// __fastcall specializations
template<class R>
struct function_traits<R(__fastcall*) (void)> {
  enum {arity = 0};
  typedef generic_t object;
  typedef R         result;
  typedef R (__fastcall*type)(void);
  typedef R (generic_t::*member)(void);
  typedef function_traits<R(__fastcall*) (void)> traits;
};
@START 1, 10
template<class R, @(class P$)>
struct function_traits<R(__fastcall*) (@(P$))> {
  enum {arity = $};
  typedef R         result;
  typedef generic_t object;
  typedef R (__fastcall*type)(@(P$));
  typedef R (generic_t::*member)(@(P$));
  typedef function_traits<R(__fastcall*) (@(P$))> traits;
  @(typedef P$ arg$; )
  
};
@STOP
#endif

// static free specializations
template<class R>
struct function_traits<R (*)(void)> {
  enum {arity = 0};
  typedef generic_t object;
  typedef R         result;
  typedef R (*type)(void);
  typedef R (generic_t::*member)(void);
  typedef function_traits<R (*)(void)> traits;
};

@START 1, 10
template<class R, @(class P$)>
struct function_traits<R (*)(@(P$))> {
  enum {arity = $};
  typedef generic_t object;
  typedef R         result;
  typedef R (*type)(@(P$));
  typedef R (generic_t::*member)(@(P$));
  typedef function_traits<R (*)(@(P$))> traits;
  @(typedef P$ arg$; )
  
};
@STOP

// member specializations
template<class R, class T>
struct function_traits<R(T::*) (void)> {
  enum {arity = 0};
  typedef T object;
  typedef R result;
  typedef R (*type)(void);
  typedef R (T::*member)(void);
  typedef function_traits<R(T::*) (void)> traits;
};


@START 1, 10
template<class R, class T, @(class P$)>
struct function_traits<R(T::*) (@(P$))> {

  enum {arity = $};
  typedef T object;
  typedef R result;
  typedef R (*type)(@(P$));
  typedef R (T::*member)(@(P$));
  typedef function_traits<R(T::*) (@(P$))> traits;
  @(typedef P$ arg$; )
  
};
@STOP


// const member specializations
template<class R, class T>
struct function_traits<R(T::*) (void) const> {
  enum {arity = 0};
  typedef T object;
  typedef R result;
  typedef R (*type)(void);
  typedef R (T::*member)(void) const;
  typedef function_traits<R(T::*) (void) const> traits;
};

@START 1, 10
template<class R, class T, @(class P$)>
struct function_traits<R(T::*) (@(P$)) const> {
  enum {arity = $};
  typedef T object;
  typedef R result;
  typedef R (*type)(@(P$));
  typedef R (T::*member)(@(P$)) const;
  typedef function_traits<R(T::*) (@(P$)) const> traits;
  @(typedef P$ arg$; )
  
};
@STOP
