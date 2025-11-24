import sys
from lexer import Lexer
from parser import Parser

def main(filename: str):
    lines = [line.strip() for line in open(filename, 'r')]
    for line in lines:
        # lexer = Lexer()
        # tokenize = lexer.tokenize(line)
        # print(tokenize)
        parser = Parser()
        ast = parser.parser.parse(line, lexer=parser.lexer.lexer)
        print(ast)

if __name__=='__main__':
    try:
        filename = sys.argv[1]
        main(filename=filename)
    except IndexError:
        print('No file')