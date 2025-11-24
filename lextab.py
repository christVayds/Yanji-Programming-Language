# lextab.py. This file automatically created by PLY (version 3.11). Don't edit!
_tabversion   = '3.10'
_lextokens    = set(('DIVIDE', 'ELSE', 'ELSEIF', 'EQUAL', 'FOR', 'ID', 'IF', 'LPAREN', 'MINUS', 'NUMBER', 'PLUS', 'RPAREN', 'TIMES', 'WHILE'))
_lexreflags   = 64
_lexliterals  = ''
_lexstateinfo = {'INITIAL': 'inclusive'}
_lexstatere   = {'INITIAL': [('(?P<t_ID>[a-zA-Z_][a-zA-Z_0-9]*)|(?P<t_NUMBER>\\d+)|(?P<t_lbrace>\\{)|(?P<t_rbrace>\\})|(?P<t_newline>\\n+)|(?P<t_ELSEIF>elseif)|(?P<t_WHILE>while)|(?P<t_ELSE>else)|(?P<t_ignore_COMMENT>\\#.*)|(?P<t_FOR>for)|(?P<t_IF>if)|(?P<t_LPAREN>\\()|(?P<t_PLUS>\\+)|(?P<t_RPAREN>\\))|(?P<t_TIMES>\\*)|(?P<t_DIVIDE>/)|(?P<t_EQUAL>=)|(?P<t_MINUS>-)', [None, ('t_ID', 'ID'), ('t_NUMBER', 'NUMBER'), ('t_lbrace', 'lbrace'), ('t_rbrace', 'rbrace'), ('t_newline', 'newline'), (None, 'ELSEIF'), (None, 'WHILE'), (None, 'ELSE'), (None, None), (None, 'FOR'), (None, 'IF'), (None, 'LPAREN'), (None, 'PLUS'), (None, 'RPAREN'), (None, 'TIMES'), (None, 'DIVIDE'), (None, 'EQUAL'), (None, 'MINUS')])]}
_lexstateignore = {'INITIAL': ' \t'}
_lexstateerrorf = {'INITIAL': 't_error'}
_lexstateeoff = {}
