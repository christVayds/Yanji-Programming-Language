
class ASTnode:
    pass

class Number(ASTnode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Number({self.value})"
    
class String(ASTnode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"String({self.value})"
    
class Character(ASTnode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Character({self.value})"
    
class Bool(ASTnode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Bool({self.value})"

class Identifier(ASTnode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Identifier({self.name})"

class BinaryOp(ASTnode):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"BinaryOp({self.op}, {self.left}, {self.right})"
    
class CompareOp(ASTnode):
    def __init__(self, op, left, right):
        self.op = op                        # ==, !=, <, <=, >, >=
        self.left = left
        self.right = right

    def __repr__(self):
        return f"CompareOp({self.op}, {self.left}, {self.right})"

# statement nodes
class Assign(ASTnode):
    def __init__(self, name, value, _type=None):
        self.name = name
        self.value = value
        self.type = _type

    def __repr__(self):
        return f"Assign({self.name}, {self.value}, {self.type})"

class Program(ASTnode):
    def __init__(self, statement):
        self.statement = statement

    def __repr__(self):
        item = '\n\t'.join(str(line) for line in self.statement)
        #return f"Program\n\t{item}"
        return f"Progarm(\n{self.statement}\n)"
    
class Write(ASTnode):
    def __init__(self, expr):
        self.expr = expr # string literal or expression

    def __repr__(self):
        return f"Write({self.expr})"

class IfStatement(ASTnode):
    def __init__(self, condition, then_branch, elseif_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.elseif_branch = elseif_branch
        self.else_branch = else_branch

    def __repr__(self):
        #return f"IfStatement({self.condition}, \n\t{self.then_branch}, {self.else_branch})"
        return f"IfStatement({self.condition}, {self.then_branch}, {self.elseif_branch}, {self.else_branch})"

class ElseIfStatement(ASTnode):
    def __init__(self, condition, then_branch):
        self.condition = condition
        self.then_branch = then_branch

    def __repr__(self):
        return f"ElseIfStatement({self.condition}, {self.then_branch})"

class ElseStatement(ASTnode):
    def __init__(self, then_branch):
        self.then_branch = then_branch

    def __repr__(self):
        return f"ElseStatement({self.then_branch})"
