from llvmlite import ir, binding
from ast import ASTnode, Number, String, Program, Character, Identifier, BinaryOp, Assign

class Compiler:

    var_table = {}
    scopes = [] # list of scopes

    def __init__(self, module='module'):
        self.module = ir.Module(name=module)
        self.func_type = ir.FunctionType(ir.VoidType(), ())
        self.main_func = ir.Function(self.module, self.func_type, name='main')
        self.block = self.main_func.append_basic_block(name='entry')
        self.builder = ir.IRBuilder(self.block)

    def code_gen(self, node: ASTnode):
        print(node.statement)