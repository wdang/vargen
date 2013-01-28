#pragma once
#include <functional>
namespace internal {
template<class F,class G>
struct composer<F,G,0>{
  typedef typename util::function_traits<F>::traits traits;
  typedef std::function<typename traits::result (void)> type;  
  static inline type compose(F f, G g){
    return [=](void){
      return f(g());
    };    
  }  
};

@START 1,10
template<class F,class G>
struct composer<F,G,$>{
  typedef typename util::function_traits<F>::traits traits;
  @(typedef typename util::function_traits<G>::arg$ arg$; )
  typedef std::function<typename traits::result (@(arg$))> type;
  static inline type compose(F f, G g){
    return [=](@(arg$ a$)){
      return f(g(@(a$)));
    };    
  }  
};
@STOP
