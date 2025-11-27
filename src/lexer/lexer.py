import ply.lex as lex # type: ignore

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
        'INT',      # INT
        'INT64',
        'INT8',
        'UINT',     # UINT
        'UINT64',
        'UINT8',
        'STRING',   # STRING
        'DOUBLE',   # DOUBLE
        'DOUBLE8',
        'DOUBLE64',
        'UDOUBLE',  # UDOUBLE
        'UDOUBLE8',
        'UDOUBLE64',
        'BOOL',     # BOOL
        'NULL',
        'CHAR',
        'TRUE',
        'FALSE',
        'WRITE',
    ]

    reserved = {
        'if': 'IF',
        'else': 'ELSE',
        'elseif': 'ELSEIF',
        'while': 'WHILE',
        'for': 'FOR',
        'int': 'INT',               # INT
        'int8': 'INT8',
        'int64': 'INT64',
        'uint': 'UINT',             # UINT
        'uint8': 'UINT8',
        'uint64': 'UINT64',
        'str': 'STRING',            # STR
        'char': 'CHAR',
        'double': 'DOUBLE',         # DOUBLE
        'double8': 'DOUBLE8',
        'double64': 'DOUBLE64',
        'udouble': 'UDOUBLE',       # UDOUBLE
        'udouble8': 'UDOUBLE8',
        'udouble64': 'UDOUBLE64',
        'bool': 'BOOL',
        'null': 'NULL',
        'true': 'TRUE',
        'false': 'FALSE',
        'write': 'WRITE',           # write or printf
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

    # INT
    t_INT = r'int'
    t_INT8 = r'int8'
    t_INT64 = r'int64'

    # UINT
    t_UINT = r'uint'
    t_UINT8 = r'uint8'
    t_UINT64 = r'uint64'

    # DOUBLE
    t_DOUBLE = r'double'
    t_DOUBLE8 = r'double8'
    t_DOUBLE64 = r'double64'

    # UDOUBLE
    t_UDOUBLE = r'udouble'
    t_UDOUBLE8 = r'udouble8'
    t_UDOUBLE64 = r'udouble64'


    t_BOOL = r'bool'
    t_TRUE = r'true'
    t_FALSE = r'false'
    t_NULL = r'null'
    t_ignore_COMMENT = r'//.*'
    t_WRITE = r'write'                  # write or printf
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
        print('(lexer) Illegal character %s' % repr(t.value[0]), 'at line[', t.lexer.lineno, ']')
        t.lexer.skip(1)