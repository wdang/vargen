@START 1, 10
template<@ (class T$)> inline void print(@ (T$&& a$)) {
  std::cout @, $-1 (<< std::forward<T$>(a$) << " " ) << std::forward<T$>(a$) << '\n';
}

@STOP
