#ifndef BIND_HELPERS_H
#define BIND_HELPERS_H

#include <functional>
#if _MSC_VER == 1500 
namespace std{
namespace placeholders {using namespace tr1::placeholders;}
using std::bind;
using std::function;
}
// const-member functions
@START 1,9
template<class R,class T, @(class T$)>
inline std::function<R(@(T$))> Bind(R(T::*member)(@(T$)) const,  const T* instance) {  
  return std::bind(member,instance,@(std::placeholders::_$));
}
@STOP


// member functions
@START 1,9
template<class R,class T, @(class T$)>
inline std::function<R(@(T$))> Bind(R(T::*member)(@(T$)), T* instance) {  
  return std::bind(member,instance,@(std::placeholders::_$));
}
@STOP

// static functions
@START 1,9
template<class R,@(class T$)>
inline std::function<R(@(T$))> Bind(R (*func)(@(T$))) {  
  return std::bind(member,@(std::placeholders::_$));
}
@STOP
#endif//MSC_VER == 1500
#endif//BIND_HELPERS_H
