
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
        return f"Program({self.statement})"