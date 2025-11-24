import ply.yacc as yacc
from lexer import Lexer
from ast import Number, Identifier, BinaryOp, Assign, Program

class Parser:

    tokens = Lexer.tokens

    precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
    )

    def __init__(self):
        self.lexer = Lexer()
        self.parser = yacc.yacc(module=self)

    # gramar: expression : expression plus expression
    def p_program_multiple(self, p):
        "program : program statement"
        p[0] = Program(p[1].statments + [p[2]])

    def p_program_single(self, p):
        """program : statement"""
        p[0] = Program(p[1])

    # assignment
    def p_statement_assign(self, p):
        "statement : ID EQUAL expression"
        p[0] = Assign(p[1], p[3])

    # expression
    def p_expression_binop(self, p):
        """expression : expression PLUS expression 
            | expression MINUS expression"""
        p[0] = BinaryOp(p[2], p[1], p[3])

    def p_expression_muldiv(self, p):
        """expression : expression DIVIDE expression
            | expression TIMES expression"""
        p[0] = BinaryOp(p[2], p[1], p[3])

    # with parenthesis
    def p_expression_group(self, p):
        """expression : LPAREN expression RPAREN"""
        p[0] = p[2]

    # numbers
    def p_expression_number(self, p):
        "expression : NUMBER"
        p[0] = Number(p[1])

    # identifiers
    def p_expression_id(self, p):
        "expression : ID"
        p[0] = Identifier(p[1])

    # type
    def p_type(self, p):
        "type : INT"
        p[0] = p[1]

    # add a rule for typed variable declaration
    def p_declaration(self, p):
        "statement : type ID EQUAL expression"
        p[0] = ('decl', 'int', p[2], p[4])

    # declaration without initialization
    def p_declaration_no_assign(self, p):
        "statement : type ID"
        p[0] = ('decl', 'int', p[2], None)

    def p_error(self, p):
        if p:
            print('Syntax Error', p)
        else:
            print('Syntax Error at EOF', p)