import sys
from src.lexer.lexer import Lexer
from src.parser.parser import Parser
from src.compiler.compiler import Compiler
import pprint

def lex(line):
    lexer = Lexer()
    tokenize = lexer.tokenize(line)
    print(tokenize)

def pars(line):
    parser = Parser()
    ast = parser.parser.parse(line, lexer=parser.lexer.lexer)
    return ast

def main(filename: str):
    compiler = Compiler()
    compiler.createMain()

    with open(filename, 'r') as file:
        text = file.read()
        #lex(text)
        ast = pars(text)
        print(ast)
        #compiler.code_gen(ast)

    # exit main function
    compiler.finish()

    # print module
    # print(f'{compiler.module}\n\n')

    # JIT compile execution
    if compiler.success:
        #compiler.JITExec()
        print("executed success.")

if __name__=='__main__':
    count = len(sys.argv)
    if count > 1:
        filename = sys.argv[1]
        filename = f'test/{filename}'
        main(filename=filename)
    else:
        print("no file")
