#ifndef EXAMPLE_INTERNAL_INVOKER_H
#define EXAMPLE_INTERNAL_INVOKER_H
#pragma once

#include "function_traits.h"
#include <type_traits>

#if defined(_MSC_VER) && _MSC_VER < 1600
template<class S, bool IsMemberFunction = std::tr1::is_member_function_pointer<S>::value>
struct Invoker;
#else
template<class S, bool IsMemberFunction = std::is_member_function_pointer<S>::value>
struct Invoker;
#endif

/// Member function invoker
template<class S>
struct Invoker<S, true> {
  typedef typename function_traits<S>::result Return;
  @START 1,5
  template<@(class T$)>
  static Return Invoke(S f, @(T$ a$)) {
    return (a1->*f)(@2,(a$));
  }
  @STOP
};

/// static/free function invoker
template<class S>
struct Invoker<S, false> {
  typedef typename function_traits<S>::result Return;
  @START 1,5
  template<@(class T$)>
  static Return Invoke(S f, @(T$ a$)) {
    return (*f)(@(a$));
  }
  @STOP
};



#endif
