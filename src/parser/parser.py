import ply.yacc as yacc
from src.lexer.lexer import Lexer
from src.ast import ast

class Parser:

    tokens = Lexer.tokens
    enumCount = 0

    precedence = (
        #('right', 'MINUS'),
        #('right', 'TIMES'),
        ('nonassoc', 'EQ', 'LT', 'LTE', 'GT', 'GTE', 'NEQ'),  # nonassociative operators
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
    )

    def __init__(self):
        self.lexer = Lexer()
        self.parser = yacc.yacc(module=self)

    def p_program(self, p):
        "program : statements"
        p[0] = ast.Program(p[1])

    # gramar: expression : expression plus expression
    def p_program_multiple(self, p):
        """statements : statements statement SEMI
            | statements expression SEMI
            | statement SEMI
            | expression SEMI"""
        if len(p) == 3:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_program_block(self, p):
        """statements : statements scope
            | statements module
            | scope
            | module"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]
    
    # identefiers
    def p_expression_id(self, p):
        """expression : ID"""
        p[0] = ast.Identifier(p[1])

    # assignment
    def p_statement_assign(self, p):
        # the expression before the equal is ID
        """statement : expression EQUAL expression
            | expression EQUAL functionCall
            | expression EQUAL group
            | statement EQUAL expression"""
        p[0] = ast.Assign(p[1], p[3])

    # expression
    
    def p_pointer_expression(self, p):
        """expression : TIMES expression"""
        p[0] = ast.Pointer(p[2])

    def p_reference_expression(self, p):
        """expression : REF expression"""
        p[0] = ast.Reference(p[2])

    # BINOP
    def p_expression_addsub(self, p):
        """expression : expression PLUS expression 
            | expression MINUS expression"""
        p[0] = ast.BinaryOp(p[2], p[1], p[3])

    def p_expression_muldiv(self, p):
        """expression : expression DIVIDE expression
            | expression TIMES expression"""
        p[0] = ast.BinaryOp(p[2], p[1], p[3])

    # numbers
    def p_expression_number(self, p):
        """expression : NUMBER"""
        p[0] = ast.Number(p[1])

    # floating numbers 
    def p_expression_floatNumber(self, p):
        """expression : FLOAT"""
        p[0] = ast.Number(p[1], True)

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

    # logical
    def p_expression_logical(self, p):
        """expression : expression AND expression
            | expression OR expression
            | NOT expression"""
        if len(p) == 3:
            p[0] = ast.LogicalOp(p[1], p[2], None)
        else:
            p[0] = ast.LogicalOp(p[2], p[1], p[3])

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

    # type
    def p_type(self, p):
        """type :
            | I32
            | STR
            | IDOUBLE
            | CHARACTER
            | BOOL
            | VOID"""
        p[0] = p[1]

    # [2] - for indexing array, size of array
    def p_brackIndex(self, p):
        """BSize : LBRACK expression RBRACK
            | LBRACK RBRACK"""
        if len(p) == 4:
            p[0] = p[2]
        else:
            p[0] = "empty"

    # add a rule for typed variable declaration
    def p_declaration(self, p):
        """statement : type expression EQUAL expression
            | type expression EQUAL statement
            | type CONST expression EQUAL expression
            | type CONST expression EQUAL functionCall"""
        if len(p) == 6:
            p[0] = ast.Assign(p[3], p[5], p[1], True)
        else:
            p[0] = ast.Assign(p[2], p[4], p[1])

    def p_newStruct(self, p):
        """statement : ID expression EQUAL group
            | ID expression EQUAL expression"""
        p[0] = ast.Assign(p[2], p[4], p[1])

    # array declaration with value
    def p_arrayDeclaration(self, p):
        """statement : type expression BSize EQUAL group
            | type expression BSize EQUAL expression
            | type CONST expression BSize EQUAL group"""
        if len(p) == 7:
            p[0] = ast.Assign(p[3], p[6], ast.Array(p[1], p[4]), True)
        else:
            p[0] = ast.Assign(p[2], p[5], ast.Array(p[1], p[3]))

    # get array
    def p_getArray(self, p):
        """statement : expression BSize"""
        p[0] = ast.getArray(p[1], p[2])

    # declaration without initialization
    def p_declaration_no_assign(self, p):
        """statement : type expression
            | type expression LBRACK expression RBRACK"""
        # ex. int num
        if len(p) == 3:
            p[0] = ast.Assign(p[2], None, p[1])
        else:
            p[0] = ast.Assign(p[2], None, ast.Array(p[1], p[4]))

    # boolean
    def p_expression_true(self, p):
        "expression : TRUE"
        p[0] = ast.Bool(True)

    def p_expression_false(self, p):
        "expression : FALSE"
        p[0] = ast.Bool(False)

    # function
    def p_function_creation(self, p):
        """scope : FUNC type ID groupArgs block"""
        p[0] = ast.Function(p[3], p[2], p[4], p[5])

    # Function Call
    def p_functionCallStatement(self, p):
        """expression : functionCall"""
        p[0] = p[1]

    def p_function_call(self, p):
        """functionCall : ID groupArgs
            | ID LPAREN expression RPAREN"""
        if len(p) == 5:
            p[0] = ast.FunctionCall(p[1], ast.Group([p[3]]))
        else:
            p[0] = ast.FunctionCall(p[1], p[2]) 
    
    # return
    def p_return_statement(self, p):
        """statement : RETURN expression
            | RETURN"""
        if len(p) == 3:
            p[0] = ast.Return(p[2])
        else:
            p[0] = ast.Return(None)

    def p_controlFlow(self, p):
        """statement : BREAK
            | CONTINUE"""
        p[0] = ast.ControlFlow(p[1])

    # IO functions
    def p_print_expression(self, p):
        """statement : WRITE expression
            | WRITE groupArgs"""
        p[0] = ast.Write(p[2])

    def p_write_expression(self, p):
        """statement : READ expression"""
        p[0] = ast.Read(p[2])
    
    # groupings

    def p_groupArgs(self, p):
        """groupArgs : LPAREN groupList RPAREN"""
        p[0] = ast.Group(p[2])

    def p_group(self, p):
        """group : LBRACE groupList RBRACE"""
        p[0] = ast.Group(p[2])

    def p_single_group(self, p):
        """groupList : item
            | """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = []

    def p_multi_group(self, p):
        """groupList : groupList COMMA item"""
        p[0] = p[1] + [p[3]]

    def p_item(self, p):
        """item : expression
            | statement"""
        p[0] = p[1]

    # brace group
    def p_block(self, p):
        """block : LBRACE program RBRACE
            | LBRACE RBRACE"""
        if len(p) == 4:
            p[0] = p[2]
        else:
            p[0] = []
    
    # for struct
    def p_groupBlock(self, p):
        "groupBlock : LBRACE statements RBRACE"
        p[0] = p[2]

    # paren block
    # list of ID to store in Enum
    def p_IDs(self, p):
        """IDs : ID 
            | ID NUMBER"""
        if len(p) == 3:
            p[0] = ast.EnumVal(p[1], p[2])
            self.enumCount = int(p[2]) + 1
        else:
            p[0] = ast.EnumVal(p[1], self.enumCount)
            self.enumCount+=1

    def p_IDLists(self, p):
        """IDlists : IDlists COMMA IDs
            | IDs"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]
    
    # group of ID in Enum
    def p_groupID(self, p):
        """groupID : LBRACE IDlists RBRACE"""
        p[0] = p[2]

    # if statement

    def p_statement_if(self, p):
        """scope : IF LPAREN expression RPAREN block elseif_list else_opt"""
        p[0] = ast.IfStatement(p[3], p[5], p[6], p[7])

    def p_elseif_multi(self, p):
        """elseif_list : elseif_list elseif"""
        p[0] = p[1] + [p[2]]

    def p_elseif_empty(self, p):
        """elseif_list : """
        p[0] = []

    def p_elseif_single(self, p):
        """elseif : ELIF LPAREN expression RPAREN block"""
        p[0] = ast.ElseIfStatement(p[3], p[5])

    def p_else_opt(self, p):
        """else_opt : ELSE block
            | """
        if(len(p)) == 3:
            p[0] = ast.ElseStatement(p[2])
        else:
            p[0] = None

    # forloop and while loop

    def p_forloop(self, p):
        """scope : FOR LPAREN statement SEMI expression SEMI statement RPAREN block """
        p[0] = ast.ForLoop(p[3], p[5], p[7], p[9])

    def p_whileloop(self, p):
        """scope : WHILE LPAREN expression RPAREN block"""
        p[0] = ast.WhileLoop(p[3], p[5])
    
    def p_doWhileLoop(self, p):
        """scope : DO block WHILE LPAREN expression RPAREN"""
        p[0] = ast.doWhileLoop(p[5], p[2])

    # enum and struct

    def p_struct(self, p):
        """scope : STRUCT ID groupBlock"""
        p[0] = ast.Struct(p[2], ast.Group(p[3]))

    def p_enum(self, p):
        """scope : ENUM ID groupID"""
        p[0] = ast.Enum(p[2], p[3])
        self.enumCount = 0

    # using dot(.) to access enum, struct, etc.
    def p_dot_access(self, p):
        """statement : expression DOT expression
            | expression DOT statement
            | statement DOT statement
            | statement DOT expression"""
        p[0] = ast.Access(p[1], p[3])

    # class - object oriented
    def p_class(self, p):
        """scope : CLASS expression block"""
        p[0] = ast.Class(p[2], p[3])
    
    # define (create macros) ex. #define PI 3.14159
    def p_define(self, p):
        """statement : DEFINE expression expression"""
        p[0] = ast.Define(p[2], p[3])

    # include package : #include packageName
    def p_include_package(self, p):
        """module : INCLUDE expression"""
        p[0] = ast.Include(p[2])

    # error for syntax error
    def p_error(self, p):
        if p:
            print('(parser) Syntax Error', p)
        else:
            print('(parser) Syntax Error at EOF ->', p, '<-')
