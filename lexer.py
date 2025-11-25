import ply.lex as lex

class Lexer:

    # list of token names
    tokens = [
        'NUMBER',
        'PLUS',
        'MINUS',
        'TIMES',
        'DIVIDE',
        'LPAREN',
        'RPAREN',
        'ID',
        'EQUAL',
        'IF',
        'ELSE',
        'ELSEIF',
        'WHILE',
        'FOR',
        'INT',
        'STRING',
        'DOUBLE',
        'BOOL',
        'NULL',
        'CHAR',
        'TRUE',
        'FALSE'
    ]

    reserved = {
        'if': 'IF',
        'else': 'ELSE',
        'elseif': 'ELSEIF',
        'while': 'WHILE',
        'for': 'FOR',
        'int': 'INT',
        'str': 'STRING',
        'char': 'CHAR',
        'double': 'DOUBLE',
        'bool': 'BOOL',
        'null': 'NULL',
        'true': 'TRUE',
        'false': 'FALSE'
    }

    # regular expression rules for simple token
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_EQUAL = r'='
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_IF = r'if'
    t_ELSE = r'else'
    t_ELSEIF = r'elseif'
    t_WHILE = r'while'
    t_FOR = r'for'
    t_INT = r'int'
    t_DOUBLE = r'double'
    t_BOOL = r'bool'
    t_TRUE = r'true'
    t_FALSE = r'false'
    t_NULL = r'null'
    t_ignore_COMMENT = r'//.*'
    # t_ID = r'[a-zA-Z_][a-zA-Z0-9_]*'

    # a string conataining ignore characters (spaces and tabs)
    t_ignore = ' \t\r\n'

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

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = self.reserved.get(t.value, 'ID')
        return t

    def tokenize(self, text):
        self.lexer.input(text)
        return list(self.lexer)
    
    def t_lbrace(self, t):
        r'\{'
        t.type = '{'
        return t
    
    def t_rbrace(self, t):
        r'\}'
        t.type = '}'
        return t

    # track line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # error handling
    def t_error(self, t):
        print('Illegal character %s' % repr(t.value[0]), 'at line[', t.lexer.lineno, ']')
        t.lexer.skip(1)