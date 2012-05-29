from locale import str
import os,sys,re,io

#DISCLAIMER: code below is not pretty :(

def Usage():
  """Variable argument c++ class template generator.
  vargen.py [options] [input] [output = stdout]

  options:
   -f inject generated code into [input] instead of stdout
  """
  return 1

def Documentation():
  """Variable argument c++ class template generator.
  vargen.py [options] [input] [output = stdout]

  options:
   -f inject generated code into [input] instead of stdout

  Grammar (incomplete): vargen is a inclusive iterator
      over a range specified in the start clause of the [input] file.

      comma        = ',';
      number       = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
      whitespace   = ? whitespace characters ? ;
      lowerbound   = number
      upperbound   = number
      start clause = '@START', [whitespace], lowerbound, comma, [whitespace], upperbound;
      stop clause  = '@STOP';
      operator     = ['+'|'-'|'*'|'/'];
      itervar      = '$',[operator], [number]
      contents     = iteration | letter | number
      iteration    = '@', [lowerbound|itervar], [comma], [number|current], '(', contents, ')';
      repetition   = '@', number, '(', contents, ')';
      operation    = iteration | repetition;


   Usage Examples:
    iteration: @i, j(contents)
      Iterates contents, substituting and evaluating itervar on each pass

      iteration overloads:
        @i, j(contents) = explicit ranged iteration from i to j inclusive
        @(contents)     = iterate from $BEGIN to itervar. Shorthand for @$BEGIN,$()
        @i,(contents)   = iterate iff itervar >= i
        @,j(contents)   = iterate iff itervar <= j

    repetition: @count(contents)
      Duplicates contents count times, substituting and evaluating itervar on each pass


  NOTES AND LIMITATIONS:
    1. @0(<contents>) generates nothing
    2. Trailing comma's are removed: commas followed by closing
    brackets from the generated code will be replaced:
       ,>  becomes >
       ,)  becomes )
       ,,} becomes }
    3. Invalid ranges havent been tested.
    4. operations must be contained on a single line
    5. A space following @ will probably break vargen

  Example 0A: Special behavior of no trailing characters in an operation.
    @START 1,3
    @(T$ member$)
    @STOP

  Result 0A:
    T1 member1, T2 member2, T3 member3

  Example 0B: Special behavior of trailing characters in an operation.
    @START 1,3
    @(T$ member$; )
    @STOP

  Result 0B:
    T1 member1; T2 member2; T3 member3;

  Example 1: Behavior of [1,3] iteration operation
    @START 1,3
    template<@(class T$)> struct List$;
    @STOP

  Result 1:
    template<class T1> struct List1;
    template<class T2> struct List2;
    template<class T3> struct List3;

  Example 2: Behavior of 3-repetition operation
    @START 1,3
    template<@3(class T$)> struct List$;
    @STOP

  Result 2:
    template<class T1, class T1, class T1> struct List1;
    template<class T2, class T2, class T2> struct List2;
    template<class T3, class T3, class T3> struct List3;


  Example 3: Behavior of [1,4] iteration with parameters
    @START 1,4
    template<@(class T$)>
    struct Args<@(class T$), @$END - $(Empty)>;
    @STOP

  Result 3:
    template<class T1>
    struct Args<T1,Empty,Empty,Empty>{};

    template<class T1, class T2>
    struct Args<T1,T2,Empty,Empty>{};

    template<class T1, class T2, class T3>
    struct Args<T1,T2,T3,Empty>{};

    template<class T1, class T2, class T3, class T4>
    struct Args<T1,T2,T3,T4>{};

   Example 4: Custom iterations
    @START 1, 3

    template<@(class T$)>
    struct Args$ : public Args$-1{
    T$ a$;

    Args$(@(T$ p$))
    : Args$-1(@,$-1(p$)),
     a$(p$){}
    };
    @STOP

  Result 4:
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
"""


_FIX_LEADING_COMMAS = re.compile(r'[,]+\s*(?P<value>[>\)])')

def ErrorExit(msg):
  print("%s\n%s: %s" % (msg,os.path.split(os.path.abspath(__file__))[1],Usage.__doc__))

  return 1


def ExtractBetween(open,close,s):
  """ Returns string between first
      matching 'open' and 'close' pairs of brackets
  """
  braces = 0
  buf = []
  for c in s:
    print(c)
    if c == open:

      if braces > 0:
        buf.append(c)
      braces += 1
      continue
    elif c == close:
      braces -= 1
      if braces == 0:
        break
    if braces > 0:
      buf.append(c)
  return ''.join(buf)


class Operation:
  def __init__(self, contents):
    if contents[-1:] == ' ':
      self.__separator = ' '
    else:
      self.__separator = ', '
    self.__contents =  contents
    pass


  def data(self):

    return self.__contents

  def separator(self):
    return self.__separator

  def __str__(self):
    return self.__string

  def __call__ (self, begin, end):
     pass

class Repetition(Operation):
  def __init__(self, contents, count):
    super(Iteration,self).__init__(contents)
    self.__count = count

  def __str__(self):
    return "Repetition(%s): %s" % (str(self.__count), self.data())

  def __call__(self, begin, end):
     # TODO allow arbritary number of whitespace
     return self.__separator.join([self.__contents for k in range(0,end)]).replace("$",str(current))

class Iteration(Operation):
  def __init__(self, contents, begin, end):
    super(Iteration,self).__init__(contents)
    self.__p1 = begin
    self.__p2 = end


  def __str__(self):
    return "Iteration(%s,%s): %s" % (self.__p1,self.__p2,self.data())

  def __call__(self, begin, end):
     if len(self.__p1) == 0:
       self.__p1 = begin

     if len(self.__p2) == 0:
       self.__p2 = end


     #begin = int(eval(str(self.__p1).replace('$',str(i))))
     #end = int(eval(str(self.__p2).replace('$',str(i))))
     return self.separator().join([self.data().replace("$",str(i)) for i in range(int(self.__p1),int(self.__p2))])

def ExtractIterators(line):
  """ Returns a tuple of operations:
  0. a list of operation strings found in the line
  1. a list of operation parameter pairs
  2. a list of strings to iterate over
  3. the original line substituted in a printf format
  """
  ops = []
  operations = []
  parameters = []
  contents = []

  # balance paranthesis
  braces = 0

  # between @ and the matching paranthesis
  # of the first opening after @
  inside = False

  # -1 : dont collect anything
  #  0 : collect on next iteration
  #  1 : collect for param1
  #  2 : collect for param2
  collect_params = -1
  collect_contents = False


  # How this thing extracts:
  # @ param1 , param2 ( content_buf )
  # ^                               ^
  # |                               |
  #  -------------------------------
  #                |
  #               buf
  #
  buf = []
  param1 = []
  param2 = []
  content_buf = []
  repetition = False
  for i,c in enumerate(line):
    if c == '@':
      inside = True
      collect_params = 0

    elif c == '(' and inside:
      if braces == 0:
        collect_contents = True
        if collect_params == 1:
          repetition = True
        collect_params = -1
        braces = 1
        buf.append(c)
        continue
      braces += 1

    elif c == ')' and inside:
      braces -= 1
      if braces == 0:
        buf.append(c)

        operation_str = ''.join(buf)
        line = line.replace(operation_str,"%s" )

        #append
        if repetition and len(param1) != 0:
          #ops.append(Repetition(''.join(content_buf),''.join(param1)))
          operation_str = "R" + operation_str

        operations.append(operation_str)
        parameters.append((''.join(param1),''.join(param2)))
        contents.append(''.join(content_buf))
        #ops.append(Iteration(''.join(content_buf),''.join(param1),''.join(param2)))

        #reset
        inside = False
        collect_contents = False
        collect_params = -1
        buf = []
        param1 = []
        param2 = []
        content_buf = []

    elif c == ',' and inside and collect_params:
      buf.append(c)
      collect_params = 2
      continue

    if inside:
      buf.append(c)

    if collect_contents:
      content_buf.append(c)

    if collect_params == 1:
      param1.append(c)

    if collect_params == 2:
      param2.append(c)

    if inside and collect_params==0:
      collect_params = 1



  return (operations,parameters,contents,line)

def SubstituteDollarSigns(line,iteration):
  expression = re.compile(r'(?P<value>\$[\-\+\*\/]{1}[0-9\-]+)')
  match = re.findall(expression,line)
  if len(match) != 0:
    for s in match:
      line = re.sub(expression,str(eval(s.replace('$',str(iteration)))),line,1)
  return line.replace('$',str(iteration))


def Duplicate(content,count, begin, end, separator=', '):
  expression = re.compile(r'(?P<value>\$[\-\+\*\/]{1}[0-9\-]+)')
  buf = []
  return separator.join(buf)

def Iterate(content,begin,end,separator = ', '):
  expression = re.compile(r'(?P<value>\$[\-\+\*\/]{1}[0-9\-]+)')
  buf = []
  for i in range(begin,end):
    s = content
    match = re.findall(expression,s)
    if len(match) != 0:
      for m in match:
        expr = str(eval(m.replace('$',str(i))))
        s = s.replace(m,expr)
    while '$' in s:

      s = s.replace('$',str(i))
    buf.append(s)
  return separator.join(buf)

def ParseLine(line): pass



def Generate(lines,begin,end):

  # holds the final generated code
  out = io.StringIO()

  # Inclusive upper bound
  end+=1

  expression = re.compile(r'(?P<value>\$[\-\+\*\/]{1}[0-9\-]+)')
  operations = []
  for i in range(begin,end):
    for num,line in enumerate(lines):
      # operation[0] = list of operation strings
      # operation[1] = list of pairs, representing iteration limits
      # operation[2] = list of strings to iterate over
      # operation[3] = substituted line in printf format
      operation = ExtractIterators(line)


      op_len = len(operation[0])
      # No iteration operations found just substitute iteration
      # symbols
      if op_len == 0:
        out.write(SubstituteDollarSigns(line,i))
        continue

      # Evaluate our iteration parameters for each operation
      parameters = operation[1]
      contents = operation[2]
      subs =[]

      # call each operation
      for j in range(0,op_len):
        lower = begin
        upper = i
        p = parameters[j]

        # Get iteration parameters
        if p[0] != '':
          lower = eval(p[0].replace('$',str(i)))
        if p[1] != '':
          upper = eval(p[1].replace('$',str(i)))

        # Inclusive upper bound: +1
        upper = min(upper,i) + 1

        # Custom delimiter?
        separator = ', '
        if contents[j][-1:] == " ":
          separator = ' '

        # repetition or iteration?
        if operation[0][j][:1] == "R":
          generated = separator.join([contents[j] for k in range(begin,upper)])
          subs.append(generated.replace('$',str(upper)))
        else:
          subs.append(Iterate(contents[j],lower,upper,separator))
      # substitute generated code
      line = operation[3] % tuple(subs)

      # final output
      out.write(SubstituteDollarSigns(line,i))

  out.seek(0,0)
  result = out.getvalue()
  out.close()
  return result

def Main():
  argc = len(sys.argv)
  if(argc == 1):
     return ErrorExit("No input files!")

  if(argc == 2 and sys.argv[1] == '-h'):
    print(Documentation.__doc__)
    return 0


  START = re.compile(r'\s*@START\s+(?P<begin>[0-9]+)\s*,\s*(?P<end>[0-9]+)\s*$')
  STOP = re.compile('^@STOP\s*$')

  code = []
  input = []
  #resulting output
  out = io.StringIO()

  #inside @START and @STOP
  collecting = False

  #lower and upper bounds
  begin = 0
  end = 0

  recursion = -1
  blocks = []
  with open(sys.argv[1],'r') as f:
    for line in f:
      input.append(line)


  for line_num,line in enumerate(open(sys.argv[1],'r').readlines()):

    if "@START" in line:
      m = START.match(line)
      begin = int(m.group('begin'))
      end = int(m.group('end'))
      if end - begin <= 0:
        return ErrorExit("Invalid range in %s(%d): %s" % (sys.argv[1],line_num+1,line))
      recursion += 1
      blocks.append([])
      collecting = True
      continue

    if "@STOP" in line:
      collecting = False
      recursion -=1
      out.write(Generate(code,begin,end))
      begin = 0
      end = 0
      code = []
      continue

    if recursion > -1:
      blocks[recursion].append(line)
      code.append(line)
    else:
      out.write(line)

  if collecting:
    return ErrorExit("@STOP was not found!")

  if len(sys.argv) > 2:
    f = open(sys.argv[2],'wt')
    print("Writing to %s" % os.path.abspath(sys.argv[2]))
    out.seek(0,0)
    with open(sys.argv[2],'wt') as f:
      for line in out.readlines():
        f.write(line)
  else:
    print(out.getvalue())
  out.close()

if __name__ == '__main__':
  if sys.version_info[0] != 3:
    print("vargen.py requires python 3.2.2")
    pass
  else:
    Main()
