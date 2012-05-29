#ifndef EXAMPLE_STORAGE_H
#define EXAMPLE_STORAGE_H
#pragma once

#include <type_traits>

#include "function_traits.h"

#define STORAGE_INVOKE0(TYPE)\
  Return operator()(){\
    return args(routine);\
  }\
  inline static Return Invoke(const BaseStorage* header) {\
    const TYPE* o = reinterpret_cast<const TYPE*>(header);\
    return o->args(o->routine);\
  }

@START 1,6
#define STORAGE_INVOKE$(TYPE)\
  template<@,$(class P$)>\
  inline static Return Invoke(const BaseStorage* header, @,$(P$ p$)) {\
    Args$< @,$(P$)> args(@,$(p$));\
    const TYPE* o = reinterpret_cast<const TYPE*>(header);\
    return o->args(o->routine, args);\
  }\
  STORAGE_INVOKE$-1(TYPE)
@STOP

namespace core {
namespace internal {

struct BaseStorage{};

template<class S>
struct Storage0 : public BaseStorage {
 private:
  typedef typename function_traits<S>::result Return;
  Args0<> args;
  S routine;

 public:
  Storage0(S function_pointer)
  :routine(function_pointer){}
  
  Return operator()() const{
    return (*routine)();
  }  
  STORAGE_INVOKE0(Storage0);
};

@START 1,5
template<class S, @(class T$)>
struct Storage$ : public BaseStorage {
 private:
  typedef typename core::function_traits<S>::result Return;
  Args$<@(T$)> args;
  S routine;
 public:
  Storage$(S function_pointer, @(T$ p$))
    : args(@(p$)), routine(function_pointer) {}

  STORAGE_INVOKE$(Storage$);
};
@STOP

#endif
