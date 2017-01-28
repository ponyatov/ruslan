# [Sym]bolic class tree

class Sym:
    tag = 'sym'
    def __init__(self, V): self.val = V ; self.nest = [] ; self.sel = {}
    def push(self,o): self.nest.append(o)
    def __iadd__(self,o): self.push(o) ; return self # +=
    def __repr__(self): return self.head()
    def head(self): return "<%s:%s>" % (self.tag, self.val)
    def pad(self, n): return '\t' * n
    def dump(self, depth=0):
        S = "\n" + self.pad(depth) + self.head()
        for i in self.sel:
            S += '\n'+self.pad(depth+1)+i
            S += self.sel[i].dump(depth + 2)
        for i in self.nest:
            S += i.dump(depth + 1)
        return S
    def eval(self,env):
        if self.val in env.sel: return env.sel[self.val] # lookup
        for i in range(len(self.nest)):
            self.nest[i] = self.nest[i].eval(env)
        return self
    def pfxplus(self):  raise BaseException('+ ' + self.head())
    def pfxminus(self): raise BaseException('- ' + self.head())
    def add(self,o):    raise BaseException('%s + %s' % (self, o))
    def sub(self,o):    raise BaseException('%s - %s' % (self, o))
    def mul(self,o):    raise BaseException('%s * %s' % (self, o))
    def div(self,o):    raise BaseException('%s / %s' % (self, o))
    def pow(self,o):    raise BaseException('%s ^ %s' % (self, o))
    def eq(self, env, o): env.sel[self.val] = o ; return o

class Env(Sym): tag = 'env'    
glob = Env('global')

class Num(Sym):
    tag = 'num'
    def eval(self,env): return self
    def pfxplus(self): return self
    def pfxminus(self): return Num(-self.val)
    def add(self,o):
        if o.tag == 'num': return Num(self.val + o.val)
        else: Sym.div(self,o)
    def sub(self,o):
        if o.tag == 'num': return Num(self.val - o.val)
        else: Sym.div(self,o)
    def mul(self,o):
        if o.tag == 'num': return Num(self.val * o.val)
        else: Sym.div(self,o)
    def div(self,o):
        if o.tag == 'num': return Num(self.val / o.val)
        else: Sym.div(self,o)
    def pow(self,o):
        if o.tag == 'num': return Num(self.val ** o.val)
        else: Sym.div(self,o)

class Op(Sym):
    tag = 'op'
    def eval(self,env):
        if self.val == '~': return nest[0] # quote operator
        else: Sym.eval(self,env) # nonlazy deep evaluation
        if len(self.nest) == 1:
            if self.val == '+': return self.nest[0].pfxplus()
            if self.val == '-': return self.nest[0].pfxminus()
            raise BaseException('unary op: ' + self.dump())
        if len(self.nest) == 2:
            if self.val == '=': return self.nest[0].eq(env,self.nest[1])
            if self.val == '+': return self.nest[0].add(self.nest[1])
            if self.val == '-': return self.nest[0].sub(self.nest[1])
            if self.val == '*': return self.nest[0].mul(self.nest[1])
            if self.val == '/': return self.nest[0].div(self.nest[1])
            if self.val == '^': return self.nest[0].pow(self.nest[1])
            raise BaseException('binary op: ' + self.dump())
        raise BaseException(self.dump())  # undefined operator
    
# parser

import ply.lex  as lex
import ply.yacc as yacc 

src = open('src.src','r')
log = open('log.log','w')

tokens = [ 'SYM' , 'NUM' ,
          'LP', 'RP',
          'EQ',
          'ADD', 'SUB', 'MUL', 'DIV', 'POW' ]

t_ignore = ' \t\r'
t_ignore_comment = r'\#[^\n]*'
def t_newline(t):
    r'\n'
    t.lexer.lineno += 1

def t_NUM(t):
    r'(\d+(\.\d*)?|\.\d+)([eE][\+\-]?\d+)?'
    t.value = Num(float(t.value)) ; return t
def t_EQ(t):
    r'\='
    t.value = Op(t.value) ; return t
def t_ADD(t):
    r'\+'
    t.value = Op(t.value) ; return t
def t_SUB(t):
    r'\-'
    t.value = Op(t.value) ; return t
def t_MUL(t):
    r'\*'
    t.value = Op(t.value) ; return t
def t_DIV(t):
    r'\/'
    t.value = Op(t.value) ; return t
def t_POW(t):
    r'\^'
    t.value = Op(t.value) ; return t
def t_LP(t):
    r'\('
    t.value = Op(t.value) ; return t
def t_RP(t):
    r'\)'
    t.value = Op(t.value) ; return t
def t_SYM(t):
    r'[a-zA-Z0-9_]+'
    t.value = Sym(t.value) ; return t
    
precedence = [
    ('left','ADD','SUB'),
    ('left','MUL','DIV'),
    ('left','POW'),
    ('right','PFX')
    ]

def p_REPL_none(p):
    ' REPL : '
def p_REPL_recur(p):
    ' REPL : REPL ex '
    print >>log, p[2].dump()
    print >>log, '-'*20,
    print >>log, p[2].eval(glob).dump()
    print >>log, '-'*20,
    print >>log, glob.dump()
    print >>log, '='*40
def p_scalar(p):
    ''' scalar : SYM
                | NUM '''
    p[0] = p[1]
def p_ex_scalar(p):
    ' ex : scalar '
    p[0] = p[1]
def p_ex_parens(p):
    ' ex : LP ex RP '
    p[0] = p[2]
def p_ex_pfxplus(p):
    ' ex : ADD ex %prec PFX '
    p[0] = p[1] ; p[0] += p[2]
def p_ex_pfxminus(p):
    ' ex : SUB ex %prec PFX '
    p[0] = p[1] ; p[0] += p[2]
def p_ex_eq(p):
    ' ex : ex EQ ex '
    p[0] = p[2] ; p[0] += p[1] ; p[0] += p[3]
def p_ex_add(p):
    ' ex : ex ADD ex '
    p[0] = p[2] ; p[0] += p[1] ; p[0] += p[3]
def p_ex_sub(p):
    ' ex : ex SUB ex '
    p[0] = p[2] ; p[0] += p[1] ; p[0] += p[3]
def p_ex_mul(p):
    ' ex : ex MUL ex '
    p[0] = p[2] ; p[0] += p[1] ; p[0] += p[3]
def p_ex_div(p):
    ' ex : ex DIV ex '
    p[0] = p[2] ; p[0] += p[1] ; p[0] += p[3]
def p_ex_pow(p):
    ' ex : ex POW ex '
    p[0] = p[2] ; p[0] += p[1] ; p[0] += p[3]

def t_error(t): print 'lexer/error:',t
def p_error(p): print 'parse/error:',p

lexer = lex.lex()
parser = yacc.yacc(debug=False, write_tables=False)
parser.parse(src.read())
