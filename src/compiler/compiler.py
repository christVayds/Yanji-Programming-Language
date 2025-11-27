from llvmlite import ir, binding
from src.ast import ast
import ctypes

class Compiler:

    symbol_table = {}
    scopes = [] # list of scopes
    globalStrCount = 0

    success = True

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

        # printf
        printf_ty = ir.FunctionType(
            ir.IntType(32),
            [ir.IntType(8).as_pointer()],
            var_arg=True
        )

        self.printf = ir.Function(self.module, printf_ty, name='printf')

    def createMain(self):
        func_type = ir.FunctionType(ir.VoidType(), ())
        self.func = ir.Function(self.module, func_type, name='main')
        block = self.func.append_basic_block(name='entry')
        self.builder = ir.IRBuilder(block)

    def code_gen(self, node: ast.ASTnode):
        if isinstance(node, ast.Program):               # program
            self.code_gen(node.statement)
        elif isinstance(node, ast.Assign):              # Assign
            return self.nodeAssign(node)
        elif isinstance(node, ast.Number):              # Number
            return self.nodeNumber(node)
        elif isinstance(node, ast.BinaryOp):            # BinaaryOp
            return self.nodeBinOP(node)
        elif isinstance(node, ast.Identifier):          # Identifier
            return self.nodeID(node)
        elif isinstance(node, ast.Character):           # Character
            return self.nodeChar(node)
        elif isinstance(node, ast.String):              # String
            return self.nodeString(node)
        elif isinstance(node, ast.Write):               # print / write
            return self.nodeWrite(node.expr)
        elif isinstance(node, ast.Bool):                # bool
            return self.nodeBool(node)
        
    def NodeValue(self, node: ast.ASTnode):
        pass

    def nodeNumber(self, node: ast.Number):
        return ir.Constant(ir.IntType(32), node.value)
    
    def nodeString(self, node: ast.String):
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
    
    def nodeChar(self, node: ast.Character):
        return ir.Constant(ir.IntType(8), ord(node.value))
    
    def nodeBool(self, node: ast.Bool):
        bool_type = ir.IntType(1)
        if node.value:
            return ir.Constant(bool_type, 1)
        return ir.Constant(bool_type, 0)
    
    def nodeBinOP(self, node: ast.ASTnode):
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
    
    def nodeAssign(self, node: ast.ASTnode):
        # value = self.code_gen(node.value)

        if node.type == 'int':
            return self.storeInt(node.name, node.value)
        elif node.type == 'char':
            return self.storeChar(node.name, node.value)
        elif node.type == 'str':
            return self.storeString(node.name, node.value)
        elif node.type == 'bool':
            return self.storeBool(node.name, node.value)
        else:
            if node.name in self.symbol_table:
                pass

    def storeInt(self, name, node):
        value = self.nodeNumber(node)

        ptr = self.builder.alloca(ir.IntType(32))
        self.builder.store(value, ptr)
        self.symbol_table[name] = {'ptr': ptr, 'type': 'int'}
        return ptr
    
    def storeString(self, name, node):
        value = ast.String(node)
        
        var_ptr = self.nodeString(node)
        str_ptr = self.builder.bitcast(var_ptr, ir.IntType(8).as_pointer())
        textbytes = bytearray(str(value.value.value).encode('utf8') + b'\00')
        
        ptr = self.builder.alloca(ir.IntType(8).as_pointer())
        self.builder.store(str_ptr, ptr)
        self.symbol_table[name] = {'ptr': ptr, 'type': 'str', 'textbytes': textbytes}
        return ptr
    
    def storeChar(self, name, node):
        value = self.nodeChar(node)

        ptr = self.builder.alloca(ir.IntType(8))
        self.builder.store(value, ptr)
        self.symbol_table[name] = {'ptr': ptr, 'type': 'char'}
        return ptr
    
    def storeBool(self, name, node):
        value = self.code_gen(node)

        ptr = self.builder.alloca(ir.IntType(1))
        self.builder.store(value, ptr)
        self.symbol_table[name] = {'ptr': ptr, 'type': 'bool'}
        return ptr
    
    def nodeID(self, node: ast.ASTnode):
        ptr = self.symbol_table[node.name]['ptr']
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
    
    def create_internal_printf(self):
        fmt_ty = ir.IntType(8).as_pointer()
        # int_ty = ir.IntType(32)

        # void _internal_printf_int(i8*, i32) - create new function for printing
        func_ty = ir.FunctionType(ir.VoidType(), [fmt_ty])
        func = ir.Function(self.module, func_ty, name='_internal_printf')
        block = func.append_basic_block(name='entry')
        builder = ir.IRBuilder(block)

        #load printf
        printf = self.module.globals.get('printf')

        # forward the string and integer to printf
        builder.call(printf, [func.args[0]])

        builder.ret_void()
        return func
    
    def string_Constant(self, text: str, text_bytes = None):
        string_ty = None
        # codegen
        if not text_bytes:
            text_bytes = bytearray(text.encode('utf8') + b'\00')
            string_ty = ir.ArrayType(ir.IntType(8), len(text_bytes))
        else:
            string_ty = ir.ArrayType(ir.IntType(8), len(text_bytes))

        gvar = ir.GlobalVariable(self.module, string_ty, name=f'.str{len(self.module.globals)}')
        gvar.global_constant = True
        gvar.initializer = ir.Constant(string_ty, text_bytes)

        # return pointer to first character
        return gvar
    
    def nodeWrite(self, expr):
        # expr = node
        textstr = ""
        var_bytes = None

        if isinstance(expr, ast.String):
            textstr = expr.value
        elif isinstance(expr, ast.Number):
            pass
        elif isinstance(expr, ast.Character):
            pass
        elif isinstance(expr, ast.Bool):
            pass
        elif isinstance(expr, ast.Identifier):
            if expr.name in self.symbol_table:
                var_info = self.symbol_table[expr.name]
                var_bytes = var_info['textbytes'] if 'textbytes' in var_info else None
                textstr = None
        
        # ensure print exist
        if '_internal_printf' not in self.module.globals:
            self.create_internal_printf()

        internal_printf = self.module.globals['_internal_printf']

        # create the global string
        gstr = self.string_Constant(textstr, var_bytes)

        # create pointer to first character
        ptr = self.builder.gep(gstr, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])

        # call the internal printf
        self.builder.call(internal_printf, [ptr])
    
    def finish(self):
        self.builder.ret_void()

    def generate_llvmIR(self):
        with open('output.ll', 'w') as f:
            f.write(str(self.module))

    def JITExec(self):
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

        print("\n\nProgram Executed Successfully")
