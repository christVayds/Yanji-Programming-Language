import sys
from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.compiler.compiler import Compiler

def main(filename: str):
    compiler = Compiler()
    compiler.createMain()

    lines = [line.strip() for line in open(filename, 'r')]
    for line in lines:
        # lexer = Lexer()
        # tokenize = lexer.tokenize(line)
        # print(tokenize)
        parser = Parser()
        ast = parser.parser.parse(line, lexer=parser.lexer.lexer)
        print(ast)
        # compiler.code_gen(ast)

    # exit main function
    compiler.finish()

    # print module
    # print(f'{compiler.module}\n\n')

    # JIT compile execution
    if compiler.success:
        # compiler.JITExec()
        pass

if __name__=='__main__':
    count = len(sys.argv)
    if count > 1:
        filename = sys.argv[1]
        filename = f'test/{filename}'
        main(filename=filename)
    else:
        print("no file")
