import ply.lex as lex

class Lexer:

    # list of token names
    tokens = [
        'NUMBER',
        'FLOAT',
        'PLUS',
        'MINUS',
        'TIMES',
        'DIVIDE',
        'LPAREN',
        'RPAREN',
        'LBRACE',
        'RBRACE',
        'LBRACK',
        'RBRACK',
        'ID',
        'EQUAL',
        'IF',
        'ELSE',
        'ELIF',
        'WHILE',
        'DO',
        'FOR',
        'STRUCT',
        'ENUM',
        'STRING',   # STRING
        'STR',
        'BOOL',     # BOOL
        'NULL',     # null
        'CHAR',     # char
        'CHARACTER',
        'TRUE',     # true
        'FALSE',    # false
        'WRITE',
        'READ',     # read
        'EQ',       # ==
        'NEQ',      # !=
        'LT',       # <
        'LTE',      # <=
        'GT',       # >
        'GTE',      # >=
        'SEMI',
        'COMMA',
        'FUNC',
        'RETURN',
        'DOT',
        'AND',
        'NOT',
        'OR',
        'CONTINUE',
        'BREAK',
        'CLASS',
        'VOID',
        'CONST',
        'DEFINE',
        'INCLUDE',
        'REF',
        'I32',
        'IDOUBLE'
    ]

    reserved = {
        'if': 'IF',
        'else': 'ELSE',
        'elif': 'ELIF',
        'while': 'WHILE',
        'do': 'DO',
        'for': 'FOR',
        'struct': 'STRUCT',
        'enum': 'ENUM',
        'i32': 'I32',
        'idouble': 'IDOUBLE',
        'bool': 'BOOL',
        'char': 'CHARACTER',
        'null': 'NULL',
        'true': 'TRUE',
        'false': 'FALSE',
        'write': 'WRITE',           # write or printf
        'read': 'READ',             # read or getf
        'function': 'FUNC',
        'return': 'RETURN',
        'and': 'AND',
        'or': 'OR',
        'not': 'NOT',
        'str': 'STR',
        'continue': 'CONTINUE',
        'break': 'BREAK',
        'class': 'CLASS',
        'void': 'VOID',
        'const': 'CONST',
        '#define': 'DEFINE',
        '#include': 'INCLUDE'
    }

    def t_FLOAT(self, t):
        r'\d+\.\d+'
        t.value = float(t.value)
        return t
    
    # regular expression rules for simple token
    t_PLUS          = r'\+'
    t_MINUS         = r'-'
    t_TIMES         = r'\*'
    t_DIVIDE        = r'/'
    t_EQUAL         = r'='
    t_LPAREN        = r'\('
    t_RPAREN        = r'\)'
    t_LBRACE        = r'\{'
    t_RBRACE        = r'\}'
    t_LBRACK        = r'\['
    t_RBRACK        = r'\]'
    t_EQ            = r'=='
    t_NEQ           = r'!='
    t_LT            = r'<'
    t_LTE           = r'<='
    t_GT            = r'>'
    t_GTE           = r'>='
    t_AND           = r'and'
    t_OR            = r'or'
    t_NOT           = r'not'
    t_SEMI          = r';'
    t_COMMA         = r','
    t_DOT           = r'\.'
    t_REF           = r'\&'
    t_IF            = r'if'
    t_ELSE          = r'else'
    t_ELIF        = r'elif'
    t_WHILE         = r'while'
    t_DO            = r'do'
    t_FOR           = r'for'
    t_FUNC          = r'function'       # function
    t_RETURN        = r'return'
    t_CONTINUE      = r'continue'
    t_BREAK         = r'break'
    t_CLASS         = r'class'          # class
    t_VOID          = r'void'
    t_CONST         = r'const'
    t_DEFINE        = r'\#define'
    t_INCLUDE       = r'\#include'

    t_STR           = r'str'
    t_CHARACTER     = r'char'

    # INT
    t_I32           = r'i32'
    t_IDOUBLE       = r'idouble'

    t_BOOL              = r'bool'
    t_NULL              = r'null'
    t_ignore_COMMENT    = r'//.*'
    t_WRITE             = r'write'                  # write or printf
    t_READ              = r'read'
    # t_ID = r'[a-zA-Z_][a-zA-Z0-9_]*'

    # a string conataining ignore characters (spaces and tabs)
    t_ignore            = ' \t\r'

    def __init__(self):
        self.lexer = lex.lex(module=self)

    # a regular expression rule with some action
    def t_NUMBER(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    # string
    def t_STRING(self, t):
        r'\"([^\\\"]|\\.)*\"'
        t.value = t.value[1:-1]
        return t
    
    def t_CHAR(self, t):
        r"'(.)'"
        t.value = t.value[1] # extract the inner character
        return t
    
    def t_TRUE(self, t):
        r'true'
        t.value = True
        return t
    
    def t_FALSE(self, t):
        r'false'
        t.value = False
        return t

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = self.reserved.get(t.value, 'ID')
        return t

    def tokenize(self, text):
        self.lexer.input(text)
        return list(self.lexer)

    # track line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # error handling
    def t_error(self, t):
        print('(lexer) Illegal character %s' % repr(t.value[0]), 'at line[', t.lexer.lineno, ']')
        t.lexer.skip(1)
