from llvmlite import ir, binding
from ast import ASTnode, Number, String, Program, Character, Identifier, BinaryOp, Assign
import ctypes

class Compiler:

    symbol_table = {}
    scopes = [] # list of scopes
    globalStrCount = 0

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
        self.target_machine = target.create_target_machine()

        # set datalayout
        self.module.data_layout=self.target_machine.target_data

    def createMain(self):
        func_type = ir.FunctionType(ir.VoidType(), ())
        self.func = ir.Function(self.module, func_type, name='main')
        block = self.func.append_basic_block(name='entry')
        self.builder = ir.IRBuilder(block)

    def code_gen(self, node: ASTnode):
        if isinstance(node, Program):               # program
            self.code_gen(node.statement)
        elif isinstance(node, Assign):              # Assign
            return self.nodeAssign(node)
        elif isinstance(node, Number):              # Number
            return self.nodeNumber(node.value)
        elif isinstance(node, BinaryOp):            # BinaaryOp
            return self.nodeBinOP(node)
        elif isinstance(node, Identifier):          # Identifier
            return self.nodeID(node)
        elif isinstance(node, Character):           # Character
            return self.nodeChar(node.value)
        elif isinstance(node, String):              # String
            return self.nodeString(node)

    def nodeNumber(self, value: int):
        return ir.Constant(ir.IntType(32), value)
    
    def nodeString(self, node: String):
        text = node.value
        name = f'str_ptr_{self.globalStrCount}'
        self.globalStrCount+=1

        # create LLVM string: null terminated
        byte_array = bytearray(str(text).encode('utf8')) + b'\00'

        # llvm array type [len x i8]
        str_type = ir.ArrayType(ir.IntType(8), len(byte_array))

        # global variable to store a string
        gvar = ir.GlobalVariable(self.module, str_type, name=name)
        gvar.linkage = 'internal'
        gvar.global_constant = True
        gvar.initializer = ir.Constant(str_type, byte_array)

        str_ptr = self.builder.gep(gvar, [ir.IntType(32)(0), ir.IntType(32)(0)], name=name)

        return str_ptr
    
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
            return self.sdiv(left, right)
    
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
        elif node.type == 'str':
            ptr = self.builder.alloca(ir.IntType(8).as_pointer(), name='str_var')
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
    
    def sdiv(self, left, right):
        return self.builder.sdiv(left, right)
    
    def udiv(self, left, right):
        return self.builder.udiv(left, right)
    
    def finish(self):
        self.builder.ret_void()

    def generate_llvmIR(self):
        with open('output.ll', 'w') as f:
            f.write(str(self.module))

    def JITExe(self):
        # create JIT execution engine

        llvm_ir = str(self.module)
        mod = binding.parse_assembly(llvm_ir)
        mod.verify()

        engine = binding.create_mcjit_compiler(mod, self.target_machine)
        engine.finalize_object() # finalized the code for execution
        engine.run_static_constructors()

        # get function pointer and call it
        func_ptr = engine.get_function_address("main")

        # call it from python using Ctypes
        cfunc = ctypes.CFUNCTYPE(None)(func_ptr) # none for void function
        cfunc() # runs the llvm main function

        print("Program Executed Successfully")
