import ply.yacc as yacc
from src.lexer.lexer import Lexer
from src.ast import ast
# from ast import Number, Identifier, BinaryOp, Assign, Program, String, Character, Bool, Write

class Parser:

    tokens = Lexer.tokens

    precedence = (
        ('nonassoc', 'EQ', 'LT', 'LTE', 'GT', 'GTE', 'NEQ'),  # nonassociative operators
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        ('right', 'MINUS'),             # unary minus
    )

    def __init__(self):
        self.lexer = Lexer()
        self.parser = yacc.yacc(module=self)

    # gramar: expression : expression plus expression
    def p_program_multiple(self, p):
        """program : program statement"""
        p[0] = ast.Program(p[1].statement + [p[2]])

    def p_program_single(self, p):
        """program : statement
            | empty"""
        p[0] = ast.Program(p[1])

    # assignment
    def p_statement_assign(self, p):
        "statement : ID EQUAL expression"
        p[0] = ast.Assign(p[1], p[3])

    # expression
    def p_expression_binop(self, p):
        """expression : expression PLUS expression 
            | expression MINUS expression"""
        p[0] = ast.BinaryOp(p[2], p[1], p[3])

    def p_expression_muldiv(self, p):
        """expression : expression DIVIDE expression
            | expression TIMES expression"""
        p[0] = ast.BinaryOp(p[2], p[1], p[3])

    # numbers
    def p_expression_number(self, p):
        "expression : NUMBER"
        p[0] = ast.Number(p[1])

    # uminus operator
    def p_expression_uminus(self, p):
        "expression : MINUS expression %prec MINUS"
        p[0] = ast.BinaryOp('-', ast.Number(0), p[2])

    # compare operators
    def p_expression_compare(self, p):
        """expression : expression EQ expression
            | expression NEQ expression
            | expression LT expression
            | expression LTE expression
            | expression GT expression
            | expression GTE expression"""
        p[0] = ast.CompareOp(p[2], p[1], p[3])

    # strings
    def p_expression_string(self, p):
        "expression : STRING"
        p[0] = ast.String(p[1])

    # characters
    def p_expression_character(self, p):
        "expression : CHAR"
        p[0] = ast.Character(p[1])

    # with parenthesis
    def p_expression_group(self, p):
        """expression : LPAREN expression RPAREN"""
        p[0] = p[2]

    # identifiers
    def p_expression_id(self, p):
        "expression : ID"
        p[0] = ast.Identifier(p[1])

    # type
    def p_type(self, p):
        """type : INT 
            | STRING 
            | DOUBLE
            | CHAR
            | BOOL"""
        p[0] = p[1]

    # add a rule for typed variable declaration
    def p_declaration(self, p):
        "statement : type ID EQUAL expression"
        p[0] = ast.Assign(p[2], p[4], p[1])

    # declaration without initialization
    def p_declaration_no_assign(self, p):
        "statement : type ID"
        # p[0] = ('decl', 'int', p[2], None)
        p[0] = ast.Assign(p[2], None, p[1])

    # boolean
    def p_expression_true(self, p):
        "expression : TRUE"
        p[0] = ast.Bool(True)

    def p_expression_false(self, p):
        "expression : FALSE"
        p[0] = ast.Bool(False)

    # empty line
    def p_empty(self, t):
        "empty :"
        pass

    # write or print
    def p_print_statement(self, p):
        "statement : WRITE STRING"
        p[0] = ast.Write(ast.String(p[2]))

    def p_print_expression(self, p):
        "statement : WRITE expression"
        p[0] = ast.Write(p[2])

    def p_error(self, p):
        if p:
            print('(parser) Syntax Error', p)
        else:
            print('(parser) Syntax Error at EOF ->', p, '<-')