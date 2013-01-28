import os, sys, re, io
import itertools

def usage():
    """Variable argument generator.
      vargen.py inputfile [outputfile = stdout]
    """

def braceindices(s, left='(', right=')'):
    """
    returns a 2-tuple representing the indexes of
    the first 'left' opening bracket and it's corresponding
    'right' closing bracket. None is returned if the first left bracket is
    unbalanced
    """
    open_braces = []
    for i, c in enumerate(s):
        if c == left:
            open_braces.append(i)
        elif c == right and len(open_braces) is not 0:
            start = open_braces.pop()
            if len(open_braces) is 0:
                return (start, i)
    return None

def bracematch(s, left='(', right=')'):
    """
    returns a substring of s, inside the pair of matching braces
    relative to the first opening brace.
    None is returned if the first left brace is  unbalanced
    """
    open_braces = []
    for i, c in enumerate(s):
        if c == left:
            open_braces.append(i + 1)
        elif c == right and len(open_braces) is not 0:
            start = open_braces.pop()
            if len(open_braces) is 0:
                return s[start:i]
    return None

def dollarsub(line, number):
    # matches $ prefixed or postfixed with a simple mathematical expression
    # ie.
    # 2+3+4 $ - 5 * 6
    expression = re.compile(r'(?P<value>\$\s*[\-\+\*\/]*\s*[\-0-9]+)')
    #expression = re.compile(r'(?P<value>[0-9\-]*[\-\+\*\/]{0,1}\$[\-\+\*\/]{1}[0-9\-]+)')
    match = re.findall(expression, line)
    for s in re.findall(expression, line):
        line = re.sub(expression, str(eval(s.replace('$', str(number)))), line, 1)
    return line.replace('$', str(number))

def evaldollarsigns(s,number):
  '''replaces all occurences of $ with the given number and evaulates infix expressions
  '''
  #xpr = re.compile(r'(\$[\-\+\*\/][\-0-9]*)')
  xpr = re.compile(r'(?P<value>\$\s*[\-\+\*\/]*\s*[\-0-9]+)')
  for m in re.findall(xpr,s):
    s = re.sub(xpr,str(eval(m.replace('$',str(number)))),s,1)
  return s.replace('$',str(number))

def parseopstring(s,bounds):
    def noop(contents,args):
        return contents

    def repeat(contents,args):        
        separator = '' if contents[-1] == ' ' else ', '
        return separator.join(itertools.repeat(contents,args[0]))

    def iterate(contents,args):        
        separator = '' if contents[-1] == ' ' else ', '
        lower,upper = args
        s= separator.join(evaldollarsigns(contents, i) for i in range(lower, upper + 1))
        return s
    
    begin,end = bounds
    contents = bracematch(s)
    #iterate
    m = re.search(r'@\s*([\$\+\-\/\+]*[0-9]*)\s*,\s*([\$\+\-\/\+]*[0-9]*)\s*\(',s)
    if m:
      arg1,arg2 = m.groups()
      if arg1 is '': arg1 = str(begin)
      if arg2 is '': arg2 = '$'
      return (iterate,(arg1,arg2),contents)

    #no arg iterate
    m = re.search(r'@\s*\(',s)
    if m:
      return (iterate,(str(begin),'$'),contents)

    #repeater
    m = re.search(r'@\s*([\$\+\-\/\+]*[0-9]*)\s*\(',s)
    if m:
      return (repeat,m.groups(0),contents)
    return (noop,(),'')


class _Operation:
    def __init__(self,filename,line,s,linenumber,column,bounds):
        self.string = s
        self.file = filename
        self.column = (column,column+len(s))
        self.bounds = bounds
        self.linenumber = linenumber
        self.line = line
        self.func,self.args,self.contents = parseopstring(s,bounds)

    def __len__(self):
      return self.isvalid

    def __str__(self):
      return '{0}({1}):{2}'.format(self.file,self.line,self.args)

    def __call__(self, line, bounds, current):
        begin,end = bounds
        args = tuple([eval(arg.replace('$',str(current))) for arg in self.args])        
        result = self.func(self.contents, args)
        return line.replace(self.string,result)



def extract(filename,block, line_start, bounds):
    begin,end = bounds
    rv = io.StringIO()
    regex = re.compile(r'\$\s*[\-\+\*\/]*\s*[\-0-9]*')
    lineops={}
    for offset, line in enumerate(block):
        linenumber = line_start + offset
        ops = []
        lineops[linenumber] = {k:'' for k in range(begin,end)}
        for i in [num for num, c in enumerate(line) if c == '@']:
            bracebegin,braceend = braceindices(line[i:])
            part = line[i:i + braceend + 1]# '@arg1,arg2(<contents>)'
            contents = bracematch(line[i:])# '<contents>'
            column_range = (i, i + braceend)
            ops.append(_Operation(filename,line,part,linenumber,i,bounds))

        if not ops:
          ops.append(lambda line,bounds,current: line)

        for i in range(begin,end):
            subbedline = line
            for o in ops:
                subbedline = o(subbedline,bounds,i)
            lineops[linenumber][i] = subbedline

    for i in range(begin,end):
      for offset,line in enumerate(block):
        linenumber = offset+line_start
        rv.write(evaldollarsigns(lineops[linenumber][i],i))
     
    return rv.getvalue()

class _ParseException(Exception):
    def __init__(self,message,filename,linenumber):
        self.filename = filename
        self.line = linenumber
        self.value = message

    def __str__(self):
        return  repr('in {0}({1}):{2}'.format(self.filename,self.line,self.value))

def main():
    start = re.compile(r'\s*@START\s+(?P<begin>[0-9]+)\s*,\s*(?P<end>[0-9]+)\s*$')
    code = []
    out = io.StringIO()
    inside_codeblock = False
    bounds = ()
    line_start = 1
    for num, line in enumerate(open(sys.argv[1], 'r').readlines()):
        if "@START" in line:
            if inside_codeblock: 
                raise _ParseException('Nested blocks not supported',sys.argv[1],num+1)

            m = start.match(line)
            if not m: 
                raise _ParseException('Invalid @START declaration',sys.argv[1],num+1)

            begin,end = int(m.group('begin')), int(m.group('end'))
            if end - begin <= 0: 
                raise _ParseException("Invalid range",sys.argv[1], num + 1)

            bounds = (begin, end + 1)#inclusive
            inside_codeblock = True
            line_start = num
            continue

        elif "@STOP" in line:
            if not inside_codeblock: 
                raise _ParseException('@START not found for corresponding @STOP',sys.argv[1], num + 1)
            out.write(extract(sys.argv[1],code, line_start, bounds))
            inside_codeblock = False
            bounds = ()
            code = []
            continue

        if inside_codeblock: 
            code.append(line)
        else: 
            out.write(line)

    if len(sys.argv) > 2:
        f = open(sys.argv[2], 'wt')
        print("Output written to %s" % os.path.abspath(sys.argv[2]))
        out.seek(0, 0)
        with open(sys.argv[2], 'wt') as f:
            for line in out.readlines():
                f.write(line)
    else:
        print(out.getvalue())
    out.close()

if __name__ == '__main__':
    if sys.version_info[0] != 3:
        print("vargen.py requires python 3")        
    elif len(sys.argv) == 1:
        print("no input files\n",usage.__doc__)
    else: 
        main()
