#ifndef EXAMPLE_FUNCTION_H
#define EXAMPLE_FUNCTION_H

@START 1, 5
template<class R, @(class T$)>
class Function<R(@(T$))> {
 private:
  typedef R (*Invoker)(const internal::BaseStorage*, @(T$));
  BaseStorage* storage;
  Invoker invoker;

 public:
  typedef R (*Signature)(@(T$));

  R operator()(@(T$ p$)) const {
    return invoker(storage, @(p$));
  }
};

@STOP


#endif
