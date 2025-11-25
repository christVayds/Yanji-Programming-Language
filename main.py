import sys
from lexer import Lexer
from parser import Parser
from compiler import Compiler

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
        compiler.code_gen(ast)

    compiler.finish()
    print(compiler.module)
    compiler.JITExe()

if __name__=='__main__':
    try:
        filename = sys.argv[1]
        main(filename=filename)
    except IndexError:
        print('No file')