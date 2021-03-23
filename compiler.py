from lexer import *
from parse import *
import sys

def main():
    print("Teeny Tiny Compiler")

    # if len(sys.argv) != 2:
    #     sys.exit("File Error: Compiler needs source file as argument.")
    #with open(sys.argv[1], 'r') as inputFile:
    with open("RecognizeVariable.cfl", 'r') as inputFile: # UNCOMMENT NYA ICOMMENT ANG BABAW VICE VERSA, GAMIT PARA NO NEED HIMOUNG ARGUMENT ANG FILE
        fileName = inputFile.name
        if fileName.endswith(".cfl"):
            input = inputFile.read()
        else:
            sys.exit("File Error: Compiler needs .cfl source file.") # EXAMPLE: hello.cfl, main.cfl

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