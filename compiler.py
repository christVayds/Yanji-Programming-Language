from llvmlite import ir, binding
from ast import ASTnode, Number, String, Program, Character, Identifier, BinaryOp, Assign

class Compiler:

    symbol_table = {}
    scopes = [] # list of scopes

    def __init__(self, module:str = 'module'):
        # initialize LLVM only once
        # binding.initialize()
        binding.initialize_native_target()
        binding.initialize_native_asmprinter()

        # create module
        self.module = ir.Module(name=module)
        self.func = None
        self.builder = None

        # set target triple
        self.module.triple = binding.get_default_triple()

        # create target machine
        target = binding.Target.from_default_triple()
        target_machine = target.create_target_machine()

        # set datalayout
        self.module.data_layout=target_machine.target_data

    def createMain(self):
        func_type = ir.FunctionType(ir.VoidType(), ())
        self.func = ir.Function(self.module, func_type, name='main')
        block = self.func.append_basic_block(name='entry')
        self.builder = ir.IRBuilder(block)

    def code_gen(self, node: ASTnode):
        if isinstance(node, Program):
            self.code_gen(node.statement)
        elif isinstance(node, Assign):
            return self.nodeAssign(node)
        elif isinstance(node, Number):
            return self.nodeNumber(node.value)
        elif isinstance(node, BinaryOp):
            return self.nodeBinOP(node)
        elif isinstance(node, Identifier):
            return self.nodeID(node)
        elif isinstance(node, Character):
            return self.nodeChar(node.value)

    def nodeNumber(self, value: int):
        return ir.Constant(ir.IntType(32), value)
    
    def nodeString(self, node: ASTnode):
        return
    
    def nodeChar(self, value: str):
        return ir.Constant(ir.IntType(8), ord(value))
    
    def nodeBinOP(self, node: ASTnode):
        left = self.code_gen(node.left)
        right = self.code_gen(node.right)
        if node.op == '+':
            return self.add(left, right)
        elif node.op == '-':
            return self.sub(left, right)
        elif node.op == '*':
            return self.mul(left, right)
        elif node.op == '/':
            return self.div(left, right)
    
    def nodeAssign(self, node: ASTnode):
        value = self.code_gen(node.value)

        if node.type == 'int':
            ptr = self.builder.alloca(ir.IntType(32))
            self.builder.store(value, ptr)
            self.symbol_table[node.name] = ptr
            return ptr
        elif node.type == 'char':
            ptr = self.builder.alloca(ir.IntType(8))
            self.builder.store(value, ptr)
            self.symbol_table[node.name] = ptr
            return ptr
    
    def nodeID(self, node: ASTnode):
        ptr = self.symbol_table[node.name]
        return self.builder.load(ptr, name=node.name)
    
    def add(self, left, right):
        return self.builder.add(left, right)
    
    def sub(self, left, right):
        return self.builder.sub(left, right)
    
    def mul(self, left, right):
        return self.builder.mul(left, right)
    
    def div(self, left, right):
        return self.builder.div(left, right)
    
    def finish(self):
        self.builder.ret_void()