
class ASTnode:
    pass

class Number(ASTnode):
    def __init__(self, value, _float=False):
        self.value = value
        self._float = _float

    def __repr__(self):
        return f"Number({self.value}, {self._float})"
    
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

class LogicalOp(ASTnode):
    def __init__(self, log, left, right):
        self.log = log                      # and, or, not
        self.left = left
        self.right = right

    def __repr__(self):
        return f"LogicalOp({self.log}, {self.left}, {self.right})"

# statement nodes
class Assign(ASTnode):
    def __init__(self, name, value, _type=None, const=False):
        self.name = name        # name
        self.value = value      # value
        self.type = _type       # type of value
        self.const = const      # if constant

    def __repr__(self):
        return f"Assign({self.name}, {self.value}, {self.type}, {self.const})"

class Program(ASTnode):
    def __init__(self, statement):
        self.statement = statement

    def __repr__(self):
        return f"Program(\n{self.statement}\n)"
    
class Write(ASTnode):
    def __init__(self, expr):
        self.expr = expr # string literal or expression

    def __repr__(self):
        return f"Write({self.expr})"

class Read(ASTnode):
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"Read({self.expr})"

class IfStatement(ASTnode):
    def __init__(self, condition, then_branch, elseif_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.elseif_branch = elseif_branch
        self.else_branch = else_branch

    def __repr__(self):
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

# for Loop 
class ForLoop(ASTnode):
    def __init__(self, exp1, exp2, exp3, block):
        self.exp1 = exp1
        self.exp2 = exp2
        self.exp3 = exp3
        self.block = block

    def __repr__(self):
        return f"ForLoop({self.exp1}, {self.exp2}, {self.exp3}, {self.block})"

# while loop
class WhileLoop(ASTnode):
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block

    def __repr__(self):
        return f"WhileLoop({self.condition}, {self.block})"

# do while loop
class doWhileLoop(ASTnode):
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block

    def __repr__(self):
        return f"doWhileLoop({self.condition}, {self.block})"

class Struct(ASTnode):
    def __init__(self, name, block):
        self.name = name
        self.block = block

    def __repr__(self):
        return f"Struct({self.name}, {self.block})"

class Enum(ASTnode):
    def __init__(self, name, block: list):
        self.name = name
        self.block = block

    def __repr__(self):
        return f"Enum({self.name}, {self.block})"
class EnumVal(ASTnode):
    def __init__(self, name, value:int = 0):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"EnumVal({self.name}, {self.value})"

# Arrays
class Array(ASTnode):
    def __init__(self, _type=None, size: int=0):
        self._type = _type
        self.size = size

    def __repr__(self):
        return f"Array({self._type}, {self.size})"

class getArray(ASTnode):
    def __init__(self, name, index):
        self.name = name
        self.index = index

    def __repr__(self):
        return f"getArray({self.name}, {self.index})"

# group
class Group(ASTnode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Group({self.value})"

class Function(ASTnode):
    def __init__(self, name, _type, args, block):
        self.name = name
        self._type = _type
        self.args = args
        self.block = block

    def __repr__(self):
        return f"Function({self.name}, {self._type}, {self.args}, {self.block})"

class FunctionCall(ASTnode):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"FunctionCall({self.name}, {self.args})"

class Return(ASTnode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Return({self.value})"

class ControlFlow(ASTnode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"ControlFlow({self.name})"

class Access(ASTnode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Access({self.left}, {self.right})"

class Class(ASTnode):
    def __init__(self, name, block):
        self.name = name
        self.block = block

    def __repr__(self):
        return f"Class({self.name}, {self.block})"

class Define(ASTnode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"Define({self.name}, {self.value})"

class Include(ASTnode):
    def __init__(self, packageName):
        self.packageName = packageName

    def __repr__(self):
        return f"Include({self.packageName})"

class Pointer(ASTnode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Pointer({self.name})"

class Reference(ASTnode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Reference({self.name})"
