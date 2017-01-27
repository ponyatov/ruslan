import ply.lex  as lex
import ply.yacc as yacc 

src = open('src.src','r')
log = open('log.log','w')

tokens = [ 'SYM' , 'NUM' , 'OP' ]

t_ignore = ' \t\r'
def t_newline(tok):
    r'\n'
    tok.lexer.lineno += 1

t_ignore_comment = r'\#[^\n]*'

def t_NUM(tok):
    r'[0-9]+(\.[0-9]+)?([eE][\+\-]?[0-9]+)?'
#     tok.value = float(tok.value)
    return tok
def t_SYM(tok):
    r'[a-zA-Z0-9]+'
    return tok
def t_OP(tok):
    r'[\=\+\-\*\/]'
    return tok

def t_error(tok): print 'error:',tok

lexer = lex.lex()
lexer.input(src.read())
for i in lexer: print >>log,i
