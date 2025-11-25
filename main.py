import sys
from parser import Parser
from compiler import Compiler

def main(filename: str):
    compiler = Compiler()

    lines = [line.strip() for line in open(filename, 'r')]
    for line in lines:
        # lexer = Lexer()
        # tokenize = lexer.tokenize(line)
        # print(tokenize)
        parser = Parser()
        ast = parser.parser.parse(line, lexer=parser.lexer.lexer)
        compiler.code_gen(ast)
        # print(ast)

if __name__=='__main__':
    try:
        filename = sys.argv[1]
        main(filename=filename)
    except IndexError:
        print('No file')