#ifndef EXAMPLE_BIND_H
#define EXAMPLE_BIND_H

#include "storage.h"

@START 1,5
template<class S, @(class T$)>
inline Storage$<S,  @(T$)>
Bind(S sig, @(const T$& a$)) {
  typedef Storage$<S, @(T$)> Storage;
  return Storage(sig,@(a$));
}
@STOP

#endif
