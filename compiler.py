from lexer import *
from parse import *
import sys

def main():
    print("Teeny Tiny Compiler")

    if len(sys.argv) != 2:
        sys.exit("Error: Compiler needs source file as argument.")
    with open(sys.argv[1], 'r') as inputFile:
        input = inputFile.read()


    #input = "LET kungpao = 123 \0"
    lexer = Lexer(input)
    parser = Parser(lexer)

    parser.program()
    print("Parsing completed.")

    #token = lexer.getToken()
    #while token.kind != TokenType.EOF:
    #    print(token.kind)  
    #    token = lexer.getToken()

main()