from llvmlite import ir, binding
from src.ast import ast
import ctypes
import subprocess

class SymbolTable:
    def __init__(self):
        self.scopes = []

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        self.scopes.pop()

    def define(self, name, ptr):
        self.scopes[-1][name] = ptr

    def lookUp(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

class Compiler:
    globalStrCount: int = 0
    ifStatementCount: int = 0
    symTable = SymbolTable()
    tempTable = SymbolTable()
    typeTable = SymbolTable()          # table for types, structs, enums etc
    loopEndBlock = []
    
    # scope tracking
    scopeTrack:str = 'global'

    success:bool = True

    i32 = ir.IntType(32)
    i8 = ir.IntType(8)
    i64 = ir.IntType(64)
    idouble = ir.DoubleType()
    ifloat = ir.FloatType()
    boolean = ir.IntType(1)
    char = ir.IntType(8)
    void = ir.VoidType()
    zero = ir.Constant(i32, 0)

    listDataTypes: dict = {
        'i32': i32,
        'idouble': idouble,
        'ifloat': ifloat,
        'boolean': boolean,
        'char': char,
        'void': void
    }

    listFunctions = {}

    def __init__(self):
        # initialize LLVM only once
        binding.initialize_native_target()
        binding.initialize_native_asmprinter()

        # create module
        self.module = ir.Module(name='module')

        # set target triple
        self.module.triple = binding.get_default_triple()

        # create target machine
        target = binding.Target.from_default_triple()
        self.target_machine = target.create_target_machine()

        # set datalayout
        self.module.data_layout=self.target_machine.target_data # type: ignore

        # std io 
        self.printf = self.initPrintf()

        # create new scope GLOBAL
        self.symTable.push_scope()
        self.typeTable.push_scope()

    # create main function
    def createMain(self, funcname:str='main', returnType:str='void', args:dict={}):
        
        # arguments
        argsTypes = list(args.values()) # dict values to list of dict 
        func_type = ir.FunctionType(self.listDataTypes[returnType], [a['argType'] for a in argsTypes])
        func = ir.Function(self.module, func_type, name=funcname)

        block = func.append_basic_block(name='entry')
        self.builder = ir.IRBuilder(block)

        i:int = 0 
        for name in args:
            func.args[i].name = name
            ptr = self.builder.alloca(func.args[i].type, name=name)
            self.builder.store(func.args[i], ptr)
            self.symTable.define(name, ptr)
            i+=1

        return func

    # function return types 

    # void return
    def voidReturn(self):
        self.builder.ret_void()

    # int32 return
    def int32Return(self, re:int=0):
        # re - return value
        self.builder.ret(re)

    # create function here
    def createFunction(self, node: ast.Function):
        functionName = node.name
        returnType = node._type
        functionArgs = node.args 
        functionBlock = node.block

        # new scope for local function
        self.symTable.push_scope()

        # change scopeTrack to function name
        self.scopeTrack = functionName

        # get arguments here
        getArgs:dict = self.getArguments(functionArgs)

        # create a function here
        nfunc = self.createMain(functionName, returnType, getArgs) # temporary
        self.listFunctions[functionName] = nfunc

        # loop to blocks
        for block in functionBlock.statement:
            self.code_gen(block)

        # check if void
        if returnType == 'void':
            self.voidReturn()

        # return the scope to global
        self.scopeTrack = 'global'

        # empty local symbol table
        self.symTable.pop_scope()

    def getArguments(self, functionArgs) -> dict:
        args = {}
        for arg in functionArgs.value:
            if isinstance(arg, ast.Assign):
                args[arg.name.name] = {'argType': self.listDataTypes[arg.type], 'type': arg.type}
        return args

    # code generator
    def code_gen(self, node: ast.ASTnode):
        if isinstance(node, ast.Program):               # program
            for block in node.statement:
                #print(block)
                self.code_gen(block)
        elif isinstance(node, ast.Function):            # function
            self.createFunction(node)
        elif isinstance(node, ast.FunctionCall):        # function call
            return self.nodeFunctionCall(node)
        elif isinstance(node, ast.Assign):              # Assign
            return self.nodeAssign(node.name, node.value, node.type, node.const)
        elif isinstance(node, ast.Number):              # Number
            return self.nodeNumber(node)
        elif isinstance(node, ast.BinaryOp):            # BinaryOp
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
        elif isinstance(node, ast.Group):               # group(list)
            return self.nodeGroup(node)
        elif isinstance(node, ast.Return):              # return
            self.nodeReturn(node)
        elif isinstance(node, ast.LogicalOp):           # LogicalOp
            return self.nodeLogic(node)
        elif isinstance(node, ast.CompareOp):           # CompareOp
            return self.nodeCompare(node)
        elif isinstance(node, ast.IfStatement):         # If statement
            self.nodeIfStatement(node)
        elif isinstance(node, ast.WhileLoop):           # WhileLoop statement
            self.nodeWhileLoop(node)
        elif isinstance(node, ast.ControlFlow):         # ControlFlow break continue
            return self.nodeControlFlow(node)
        elif isinstance(node, ast.ForLoop):             # ForLoop statement
            self.nodeForLoop(node)
        elif isinstance(node, ast.getArray):            # Array Access
            return self.nodeGetArray(node)
        elif isinstance(node, ast.Struct):              # Struct statement 
            return self.nodeStruct(node)
        elif isinstance(node, ast.Access):              # Dot for accessing struct, enum, etc.
            return self.nodeAccess(node)
        elif isinstance(node, ast.Enum):                # Enum 
            self.nodeEnum(node)
        elif isinstance(node, ast.Reference):           # Reference
            return self.nodeReference(node)
        elif isinstance(node, ast.Pointer):             # pointer
            return self.nodePointer(node)

    # RETURN 
    def nodeReturn(self, node: ast.Return):
        retVal = self.code_gen(node.value)

        # for int32 datatype
        self.int32Return(retVal) # type: ignore

    # NUMBERS
    def nodeNumber(self, node: ast.Number):
        const = None

        # check if number is int, double or float(not yet)
        if not node._float:
            const = ir.Constant(self.i32, node.value)
        else:
            const = ir.Constant(self.idouble, node.value)
        
        return const
    
    # STRINGS

    def nodeString(self, node: ast.String):
        text: str = bytes(node.value, 'utf-8').decode("unicode_escape") + '\x00'
        
        name: str = f'str_ptr_{self.globalStrCount}'
        self.globalStrCount+=1

        # create LLVM string: null terminated
        byte_array = bytearray(text.encode('utf8'))

        # llvm array type [len x i8]
        str_type = ir.Constant(ir.ArrayType(self.char, len(text)), byte_array)

        # global variable to store a string
        gvar = ir.GlobalVariable(self.module, str_type.type, name=name)
        gvar.linkage = 'internal'
        gvar.global_constant = True
        gvar.initializer = str_type # type: ignore

        return gvar
   
    # CHARACTERS
    def nodeChar(self, node: ast.Character):
        const = ir.Constant(self.char, ord(node.value))
        
        return const
    
    # BOOLEAN
    def nodeBool(self, node: ast.Bool):
        const = None
        if node.value:
            const = ir.Constant(self.boolean, 1)
        else:
            const = ir.Constant(self.boolean, 0)
        
        return const
    
    # BINARY OPERATORS
    def nodeBinOP(self, node: ast.BinaryOp):
        left = self.code_gen(node.left)
        right = self.code_gen(node.right)
        
        result = None
        if node.op == '+':
            result = self.add(left, right)
        elif node.op == '-':
            result = self.sub(left, right)
        elif node.op == '*':
            result = self.mul(left, right)
        elif node.op == '/':
            result = self.sdiv(left, right)
        
        return result
    
    # ASSIGNING - storing ptr
    def nodeAssign(self, name, value, _type, const):
        val = None
        
        # check for type 
        if self.typeTable.lookUp(_type):                        # for struct, enum, etc.
            val = self.lookType(_type, name, value)
        elif _type == 'i32' or _type == self.i32:               # i32
            val = self.storeNewInt(name, value, const)
        elif _type == 'idouble' or _type == self.idouble:       # idouble
            val = self.storeNewFloat(name, value, const)
        elif _type == 'char' or _type == self.char:             # char
            val = self.storeNewChar(name, value, const)
        elif _type == 'str' or _type == self.char.as_pointer(): # str
            val = self.storeNewString(name, value, const)
        elif _type == 'bool' or _type == self.boolean:          # bool
            val = self.storeNewBool(name, value, const)
        elif isinstance(_type, ast.Array):                      # array
            val = self.storeNewArray(name, value, _type, const)
        elif isinstance(name, ast.Pointer):
            val = self.storePointer(name.name, value, False)
        elif not _type:
            # fix this shit
            g_name = self.getName(name)
            symExist = self.symTable.lookUp(g_name)

            if symExist:
                if isinstance(symExist.type.pointee, ir.ArrayType):     # if array: array[0]
                    val = self.storeArray(name, value)
                elif isinstance(symExist.type.pointee, ir.PointerType): # pointer
                    val = self.storePointer(name, value)
                elif symExist.type.pointee == self.i32:                 # i32
                    val = self.storeInt(name, value)
                elif symExist.type.pointee == self.idouble:             # idouble
                    val = self.storeFloat(name, value)
                elif symExist.type.pointee == self.char:                # char
                    val = self.storeChar(name, value)
                elif symExist.type.pointee == self.boolean:             # boolean
                    val = self.storeBool(name, value)
                elif symExist.type.pointee == self.char.as_pointer():   # ptr string
                    val = self.storeString(name, value)
                #elif isinstance(symExist.type.pointee, ir.PointerType):
                #    p = symExist.type.pointee  # type: ignore
                #    if p == self.char or isinstance(p, ir.ArrayType) and p.element == self.char:
                #        val = self.storeString(name, value)
            else:                                               # ERROR
                print(f'Error: Unknown type for variable: {name.name}')
                self.success = False
                return None

        return val

    def getName(self, node: ast.ASTnode):
        if isinstance(node, ast.Identifier):
            return node.name
        elif isinstance(node, ast.Pointer):
            return self.getName(node.name)
        elif isinstance(node, ast.getArray):
            return self.getName(node.name)

        return node

    # IDENTEFIER
    def nodeID(self, node: ast.Identifier):
        
        # find identefier 
        ptr = self.symTable.lookUp(node.name)
        if isinstance(ptr.type.pointee, ir.ArrayType) and ptr.type.pointee.element == self.char:
            return self.builder.gep(ptr, [self.zero, self.zero], inbounds=True, name=node.name)
        
        return self.builder.load(ptr, name=node.name)

    # GROUP
    def nodeGroup(self, node: ast.Group) -> list:
        values = node.value
        expressions = []
        for expr in values:
            expressions.append(self.code_gen(expr))

        return expressions

    # function call
    def nodeFunctionCall(self, node: ast.FunctionCall):
        functionName = node.name
        functionArgs: list = self.nodeGroup(node.args)
        nargs = []

        # TEMPORARY FIX
        for val in functionArgs:
            if isinstance(val, ir.GlobalVariable):
                printname = f'writename_{self.globalStrCount}'
                self.globalStrCount+=1
                val = self.builder.gep(val, [self.zero, self.zero], name=printname, inbounds=True)
            nargs.append(val)
        
        retFunction = self.builder.call(self.listFunctions[functionName], nargs)
        return retFunction

    # LOGICAL OPERATIONS
    def nodeLogic(self, node: ast.LogicalOp):
        left = self.code_gen(node.left)
        right = self.code_gen(node.right)
        log = node.log
        result = None

        if left.type == self.idouble:    # double, float
            left_bool, right_bool = self.logicFloat(left, right)
        elif left.type == self.boolean:    # bool
            left_bool = left
            right_bool = right
        else:                               # int, char, str, etc.
            left_bool, right_bool = self.logicInt(left, right)
        
        if log == 'and':
            result = self.builder.and_(left_bool, right_bool)
        elif log == 'or':
            result = self.builder.or_(left_bool, right_bool)
        elif log == 'not':
            result = self.builder.not_(left_bool)

        return result

    def logicInt(self, left, right):
        left = self.builder.icmp_signed("!=", left, ir.Constant(left.type, 0))
        if right:
            right = self.builder.icmp_signed("!=", right, ir.Constant(right.type, 0))

        return left, right

    def logicFloat(self, left, right):
        left = self.builder.fcmp_ordered("!=", left, ir.Constant(left.type, 0.0))
        if right:
            right = self.builder.fcmp_ordered("!=", right, ir.Constant(right.type, 0.0))

        return left, right

    # CompareOp
    def nodeCompare(self, node: ast.CompareOp):
        left = self.code_gen(node.left)
        right = self.code_gen(node.right)
        op = node.op
        
        if left.type == self.idouble:
            if op == '==':
                return self.builder.fcmp_unordered(op, left, right)
            return self.builder.fcmp_ordered(op, left, right)
        return self.builder.icmp_signed(op, left, right)

    def nodeIfStatement(self, node: ast.IfStatement):
        func = self.listFunctions[self.scopeTrack]

        nIfBlock = func.append_basic_block(f'if{self.ifStatementCount}')
        nEndBlock = func.append_basic_block(f'end{self.ifStatementCount}')

        has_else = node.elseif_branch or node.else_branch
        if has_else:
            else_block = func.append_basic_block(f"else{self.ifStatementCount}") if has_else else nEndBlock
        else:
            else_block = nEndBlock

        cond = self.code_gen(node.condition)
        self.builder.cbranch(cond, nIfBlock, else_block)

        # if block
        self.builder.position_at_end(nIfBlock)
        self.symTable.push_scope()
        self.code_gen(node.then_branch)
        self.symTable.pop_scope()
        self.builder.branch(nEndBlock)
        if not self.builder.block.is_terminated:
            self.builder.branch(nEndBlock)

        currentElse = else_block
        
        # else block 
        for i, elseif in enumerate(node.elseif_branch):
            self.builder.position_at_end(currentElse)

            then_block = func.append_basic_block(f"elseif_then_{self.ifStatementCount}.{i}")
            nextElse = (
                func.append_basic_block(f"elseif_else_{self.ifStatementCount}.{i}") if (i<len(node.elseif_branch)-1 or node.else_branch) else nEndBlock
            )

            cond_val = self.code_gen(elseif.condition)
            self.builder.cbranch(cond_val, then_block, nextElse)

            # elseif then
            self.builder.position_at_end(then_block)
            self.symTable.push_scope()
            self.code_gen(elseif.then_branch)
            self.symTable.pop_scope()

            if not self.builder.block.is_terminated:
                self.builder.branch(nEndBlock)

            currentElse = nextElse

        # final else 
        if node.else_branch:
            self.builder.position_at_end(currentElse)
            self.symTable.push_scope()
            self.code_gen(node.else_branch.then_branch)
            self.symTable.pop_scope()

            if not self.builder.block.is_terminated:
                self.builder.branch(nEndBlock)
    
        # end block
        self.builder.position_at_end(nEndBlock) 

        self.ifStatementCount+=1

    def nodeWhileLoop(self, node: ast.WhileLoop):
        func = self.listFunctions[self.scopeTrack]

        whileBlock = func.append_basic_block(f'while{self.ifStatementCount}')
        whileBody = func.append_basic_block(f'whileBody{self.ifStatementCount}')
        nEndBlock = func.append_basic_block(f'end{self.ifStatementCount}')
        self.loopEndBlock.append(nEndBlock)

        # condition block
        self.builder.branch(whileBlock) # jump to conditional block
        self.builder.position_at_end(whileBlock)
        cond = self.code_gen(node.condition)
        self.builder.cbranch(cond, whileBody, nEndBlock)
        
        # while body
        self.builder.position_at_end(whileBody)
        self.symTable.push_scope()
        self.code_gen(node.block)
        self.symTable.pop_scope()
        self.builder.branch(whileBlock)
        if not self.builder.block.is_terminated:
            self.builder.branch(nEndBlock)
        
        #endblock 
        self.builder.position_at_end(nEndBlock)
        self.loopEndBlock.pop()

        self.ifStatementCount+=1

    def nodeForLoop(self, node: ast.ForLoop):
        func = self.listFunctions[self.scopeTrack]
        
        initLoop = func.append_basic_block(f'initLoop{self.ifStatementCount}')
        loopCond = func.append_basic_block(f'loopCond{self.ifStatementCount}')
        loopExpr = func.append_basic_block(f'loopExpr{self.ifStatementCount}')
        loopBody = func.append_basic_block(f'loopBody{self.ifStatementCount}')
        nEndBlock = func.append_basic_block(f'end{self.ifStatementCount}')
        self.loopEndBlock.append(nEndBlock)

        self.symTable.push_scope()          # push new scope
        self.builder.branch(initLoop)       # jump to for loop
        self.builder.position_at_end(initLoop)
        self.code_gen(node.exp1)            # expression
        
        # condition
        self.builder.branch(loopCond)
        self.builder.position_at_end(loopCond)
        cond = self.code_gen(node.exp2)
        self.builder.cbranch(cond, loopBody, nEndBlock)  # jump to body or end

        # expr
        self.builder.position_at_end(loopExpr)
        self.code_gen(node.exp3)
        self.builder.branch(loopCond)        # jump to condition 

        # body
        self.builder.position_at_end(loopBody)
        self.code_gen(node.block)
        self.builder.branch(loopExpr)    # back to expr
        if not self.builder.block.is_terminated:
            self.builder.branch(nEndBlock)
        
        # endblock
        self.builder.position_at_end(nEndBlock)
        self.loopEndBlock.pop()
        self.symTable.pop_scope()

        self.ifStatementCount+=1

    def nodeControlFlow(self, node: ast.ControlFlow): # this bitch still not working
        controlFlow = node.name

        if controlFlow == 'break' and self.loopEndBlock:
            return controlFlow
        else:
            pass 

        return

    # STORING VALUES (GLOBAL)

    def globalStoreInt(self, name, value, _const=False):
        
        if isinstance(name, ast.Pointer):
            valName = name.name.name
            g_int = ir.GlobalVariable(self.module, self.i32.as_pointer(), name=valName)
        else:
            valName = name.name
            g_int = ir.GlobalVariable(self.module, self.i32, name=valName)
        g_int.initializer = value
        g_int.linkage = 'internal'

        self.symTable.define(valName, g_int)

        return g_int

    def globalStoreFloat(self, name, value, _const=False):
        idouble = self.idouble
        
        if isinstance(name, ast.Pointer):
            valName = name.name.name
            g_float = ir.GlobalVariable(self.module, idouble.as_pointer(), name=valName)
        else:
            valName = name.name
            g_float = ir.GlobalVariable(self.module, idouble, name=valName)
        g_float.initializer = value
        g_float.linkage = 'internal'

        self.symTable.define(valName, g_float)

        return g_float

    def globalStoreChar(self, name, value, _const=False):
        if isinstance(name, ast.Pointer):
            valName = name.name.name
            g_char = ir.GlobalVariable(self.module, self.char.as_pointer(), name=valName)
        else:
            valName = name.name
            g_char = ir.GlobalVariable(self.module, self.char, name=valName)
        g_char.initializer = value
        g_char.linkage = 'internal'

        self.symTable.define(valName, g_char)

        return g_char

    def globalStoreBool(self, name, value, _const=False):
        if isinstance(name, ast.Pointer):
            valName = name.name.name
            g_bool = ir.GlobalVariable(self.module, self.boolean, name=valName)
        else:
            valName = name.name
            g_bool = ir.GlobalVariable(self.module, self.boolean, name=valName)
        g_bool.initializer = value
        g_bool.linkage = 'internal'

        self.symTable.define(valName, g_bool)

        return g_bool

    def globalStoreArray(self, name, value, _type, _size, _const=False):
        if isinstance(value, ast.Group):
            value = self.code_gen(value)
        elif isinstance(value, ast.String):
            value = value.value
            value = bytes(value, 'utf-8').decode("unicode_escape") + '\x00'
            values = []
            for val in value:
                values.append(ir.Constant(self.char, ord(val)))
            value = values
        
        if _size != 'empty':
            _size = _size.value
        else:
            _size = len(value)

        rType = self.listDataTypes[_type]
        arrayType = ir.ArrayType(rType, _size)
        init = ir.Constant(arrayType, value)

        global_arr = ir.GlobalVariable(self.module, arrayType, name=name)
        global_arr.initializer = init # type: ignore
        global_arr.linkage = 'internal'
        self.symTable.define(name, global_arr)

        return global_arr

    def globalStruct(self, structName, name, block):
        getStruct = self.typeTable.lookUp(structName)
        struct_ptr = getStruct['ptr'] # type: ignore
        struct_arg = getStruct['arg'] # type: ignore
        
        gStruct = ir.GlobalVariable(self.module, struct_ptr, name=name)
        gStruct.initializer = ir.Constant(struct_ptr, block) # type: ignore

        items = {}
        for i, item in enumerate(block):
            items[struct_arg[i]] = [item, i]

        newStruct = {'ptr': gStruct, 'args': items}
        self.symTable.define(name, newStruct)

    # STORING VALUES (LOCAL)

    # Arrays
    def storeNewArray(self, name, value, array, _const=False):
        _type = array._type
        name = name.name

        if self.scopeTrack == 'global':
            return self.globalStoreArray(name, value, _type, array.size, _const=False)
       
        if isinstance(value, ast.Group):
            value = self.code_gen(value)
        elif isinstance(value, ast.String):
            value = value.value
            value = bytes(value, 'utf-8').decode("unicode_escape") + '\x00'
            values = []
            for val in value:
                values.append(ir.Constant(self.char, ord(val)))
            value = values

        if array.size != 'empty':
            _size = array.size.value
        else:
            _size = len(value)

        array_type = ir.ArrayType(self.listDataTypes[_type], _size)
        ptr = self.builder.alloca(array_type, name=name)

        if value:
            for i, val in enumerate(value):
                self.storeArrayAtIndex(ptr, val, i)
        
        self.symTable.define(name, ptr)
        return ptr

    def storeArrayAtIndex(self, arr_ptr, value, idx):
        index = ir.Constant(self.i32, idx)

        elem_ptr = self.builder.gep(arr_ptr, [self.zero, index], inbounds=True)
        self.builder.store(value, elem_ptr)

    def nodeGetArray(self, node: ast.getArray):
        name = node.name.name
        index = self.code_gen(node.index)
        arr_ptr = self.symTable.lookUp(name)

        elem_ptr = self.builder.gep(arr_ptr, [self.zero, index], inbounds=True)
        value = self.builder.load(elem_ptr, name=name)

        return value

    def storeArray(self, array, value):
        value = self.code_gen(value)
        name = array.name.name 
        idx = array.index.value
        arr_ptr = self.symTable.lookUp(name)
        self.storeArrayAtIndex(arr_ptr, value, idx)

    # Struct [Create a struct]
    def nodeStruct(self, node: ast.Struct):
        name = node.name
        block = node.block

        getArgs = self.getArguments(block)
        args = list(getArgs.values())
        
        # create new struct
        nStruct = ir.LiteralStructType([arg['argType'] for arg in args])
        self.typeTable.define(name, {'ptr': nStruct, 'arg': list(getArgs), 'type': 'struct'})

        return nStruct

    def storeNewStruct(self, structName, name, values):
        if self.scopeTrack == 'global':
            return self.globalStruct(structName, name.name, values)
        name = name.name

        struct_ptr = self.typeTable.lookUp(structName)
        newStruct = self.builder.alloca(struct_ptr['ptr'], name=name) # type: ignore

        items = {}
        for i, item in enumerate(values):
            if isinstance(item, ir.GlobalVariable):
                item = self.builder.gep(item, [self.zero, self.zero], inbounds=True)
            
            field_ptr = self.builder.gep(newStruct, [self.zero, ir.Constant(self.i32, i)], inbounds=True)
            self.builder.store(item, field_ptr)
            items[struct_ptr['arg'][i]] = [field_ptr, i] # type: ignore
        
        ptr = {'ptr': newStruct, 'args': items}
        self.symTable.define(name, ptr)

        return newStruct

    def nodeEnum(self, node: ast.Enum):
        name = node.name
        enumVals = self.getEnumVal(node.block)

        enum_type = self.i32

        self.typeTable.define(name, {'enum': enum_type, 'args': enumVals, 'type': 'enum'})

    def getEnumVal(self, block):
        ret = {}
        for val in block:
            ret[val.name] = ir.Constant(self.i32, val.value)

        return ret

    def storeNewEnum(self, enumName, name, value):
        enum_type = self.typeTable.lookUp(enumName)
        value_ptr = enum_type['args'][value] # type: ignore

        ptr = self.builder.alloca(enum_type['enum'], name=name.name) # type: ignore
        self.builder.store(value_ptr, ptr)
        self.symTable.define(name.name, ptr)

        return ptr

    def lookType(self, _type, name, value):
        value = self.code_gen(value)
        ptr = self.typeTable.lookUp(_type)
        if ptr['type'] == 'enum': # type: ignore
            return self.storeNewEnum(_type, name, value)
        else:
            return self.storeNewStruct(_type, name, value)

    def nodeAccess(self, node: ast.Access):
        left = node.left.name
        right = node.right.name 

        obj = self.symTable.lookUp(left)
        ptr = obj['ptr'] # type: ignore
        args = obj['args'][right] # type: ignore

        idx = ir.Constant(self.i32, args[1])
        get_field = self.builder.gep(ptr, [self.zero, idx], inbounds=True)

        return self.builder.load(get_field, name=f'{left}.{right}')

    # Reference
    def nodeReference(self, node: ast.Reference):
        name = node.name.name
        ptr = self.symTable.lookUp(name)
        return ptr

    def nodePointer(self, node: ast.Pointer):
        name = node.name.name
        ptr_p = self.symTable.lookUp(name)
        ptr = self.builder.load(ptr_p)
        return self.builder.load(ptr, name=name)

    # POINTER
    def storePointer(self, name, value, addr=True):
        name = name.name

        value = self.code_gen(value)                    # code gen for the value
        ptr = self.symTable.lookUp(name)                # search for the name in symTable
        
        if addr:                                        # check if value is a reference(address)
            self.builder.store(value, ptr)              # store the value to the ptr pointed
        else:
            ptr = self.builder.load(ptr, name=name)     # load this shit
            self.builder.store(value, ptr)
        return ptr

    # INT
    def storeNewInt(self, name, value, _const=False):
        value = self.code_gen(value)

        # store global
        if self.scopeTrack == 'global':
            return self.globalStoreInt(name, value, _const)

        # store local
        
        # check if Pointer
        if isinstance(name, ast.Pointer):
            valName = name.name.name
            ptr = self.builder.alloca(self.i32.as_pointer(), name=valName)
        else:
            valName = name.name
            ptr = self.builder.alloca(self.i32, name=valName)
        
        self.symTable.define(valName, ptr)
        if value:
            self.builder.store(value, ptr)
        return ptr

    def storeInt(self, name, value):
        value = self.code_gen(value)
        ptr = self.symTable.lookUp(name.name)

        self.builder.store(value, ptr)
        return ptr

    # DOUBLE
    def storeNewFloat(self, name, value, _const=False):
        value = self.code_gen(value)
        # global
        if self.scopeTrack == 'global':
            return self.globalStoreFloat(name, value, _const)
        idouble = self.idouble
        
        # check if pointer
        if isinstance(name, ast.Pointer):
            valName = name.name.name
            ptr = self.builder.alloca(idouble.as_pointer(), name=valName)
        else:
            valName = name.name
            ptr = self.builder.alloca(idouble, name=name.name)

        self.symTable.define(valName, ptr)
        if value:
            self.builder.store(value, ptr)
        return ptr

    def storeFloat(self, name, value):
        value = self.code_gen(value)
        ptr = self.symTable.lookUp(name.name)
        
        self.builder.store(value, ptr)
        return ptr
    
    # STR
    def storeNewString(self, name, value, _const=False):
        value = self.code_gen(value)
        if self.scopeTrack == 'global':
            ptr = ir.GlobalVariable(self.module, self.char.as_pointer(), name=name.name)
            ptr.initializer = ir.Constant.bitcast(value, self.char.as_pointer())
            self.symTable.define(name.name, ptr)
            return ptr

        if isinstance(value, ir.GlobalVariable):
            value = self.builder.gep(value, [self.zero, self.zero], name=name.name, inbounds=True)
        
        ptr = self.builder.alloca(self.char.as_pointer(), name=name.name)
        
        self.symTable.define(name.name, ptr)
        if value:
            self.builder.store(value, ptr)
        return ptr

    def storeString(self, name, value):
        value = self.code_gen(value)
        
        if isinstance(value, ir.GlobalVariable):
            value = self.builder.gep(value, [self.zero, self.zero], name=name.name, inbounds=True)
        
        ptr = self.symTable.lookUp(name.name)
        self.builder.store(self.builder.bitcast(value, self.char.as_pointer()), ptr)
        return ptr
   
    # CHAR
    def storeNewChar(self, name, value, _const=False):
        value = self.code_gen(value)
        if self.scopeTrack == 'global':
            return self.globalStoreChar(name, value, _const)
        
        if isinstance(name, ast.Pointer):
            valName = name.name.name
            if isinstance(value, ir.GlobalVariable):
                value = self.builder.gep(value, [self.zero, self.zero], name=valName, inbounds=True)

            ptr = self.builder.alloca(self.char.as_pointer(), name=valName)
        else:
            valName = name.name
            ptr = self.builder.alloca(self.char, name=valName)

        self.symTable.define(valName, ptr)
        if value:
            self.builder.store(value, ptr)
        return ptr

    def storeChar(self, name, value):
        value = self.code_gen(value)
        ptr = self.symTable.lookUp(name.name)
        
        self.builder.store(value, ptr)
        return ptr
   
    # BOOL
    def storeNewBool(self, name, value, _const=False):
        value = self.code_gen(value)
        if self.scopeTrack == 'global':
            return self.globalStoreBool(name, value, _const)
        
        if isinstance(name, ast.Pointer):
            valName = name.name.name
            ptr = self.builder.alloca(self.boolean.as_pointer(), name=valName)
        else:
            valName = name.name
            ptr = self.builder.alloca(self.boolean, name=name.name)

        self.symTable.define(valName, ptr)
        if value:
            self.builder.store(value, ptr)
        return ptr

    def storeBool(self, name, value):
        value = self.code_gen(value)
        ptr = self.symTable.lookUp(name.name)
        
        self.builder.store(value, ptr)
        return ptr

    # BINARY OPERATIONS

    # ADD
    def add(self, left, right):
        result = None
        if left.type == self.i32:
            result = self.builder.add(left, right)
        elif left.type == self.idouble:
            result = self.builder.fadd(left, right)

        return result
    
    # SUB
    def sub(self, left, right):
        result = None
        if left.type == self.i32:
            result = self.builder.sub(left, right)
        elif left.type == self.idouble:
            result = self.builder.fsub(left, right)
        return result
    
    # MUL
    def mul(self, left, right):
        result = None
        if left.type == self.i32:
            result = self.builder.mul(left, right)
        elif left.type == self.idouble:
            result = self.builder.fmul(left, right)
        return result
    
    # DIV (unsigned)
    def sdiv(self, left, right):
        result = None
        if left.type == self.i32:
            result = self.builder.sdiv(left, right)
        elif left.type == self.idouble:
            result = self.builder.fdiv(left, right)
        return result

    
    # DIV (signed)
    def udiv(self, left, right):
        result = None
        if left.type == self.i32:
            result = self.builder.udiv(left, right)
        elif left.type == self.idouble:
            result = self.builder.fudiv(left, right)
        return result


    # WRITE FUNCTION - NEED TO FIX THIS SHIT
    def nodeWrite(self, expr):
        value = self.code_gen(expr)

        if not isinstance(value, list):
            value = [value]

        nargs = []
        # temporary fix
        for val in value:
            if isinstance(val, ir.GlobalVariable):
                printname = f'writename_{self.globalStrCount}'
                self.globalStrCount+=1
                val = self.builder.gep(val, [self.zero, self.zero], name=printname, inbounds=True)
            nargs.append(val)

        self.builder.call(self.printf, nargs)

    # generate llvm
    def generate_llvmIR(self, objname='main'):
        with open(f'build/{objname}.ll', 'w') as f:
            f.write(str(self.module))

        subprocess.run(['llc', '-filetype=obj', f'build/{objname}.ll', '-relocation-model=pic', '-o', f'build/{objname}.o'], check=True)
        subprocess.run(['gcc', f'build/{objname}.o', '-o', objname, '-fno-pie'], check=True)

    # init printf
    def initPrintf(self):
        if 'printf' not in self.module.globals:
            printf_ty = ir.FunctionType(
                self.i32,
                [self.char.as_pointer()],
                var_arg=True
            )

            printf = ir.Function(self.module, printf_ty, name='printf')

            return printf

    # JIT Execution
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



