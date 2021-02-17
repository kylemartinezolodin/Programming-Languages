import sys
from lexer import *
from symbolTable import *

# Parser keeps track of current token and checks if the code matches to the grammar of CFPL <3.
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        # FOR PARSER CURRENT LINE AND COLUMN
        self.curLine = None 
        self.curCol = None
        # FOR LEXER CURRENT LINE AND COLUMN
        self.lexLine = None
        self.lexCol = None

        self.variables = set()    # Variables declared so far.

        self.curToken = None
        self.peekToken = None
        self.nextToken()
        self.nextToken() # Call this twice to initialize current and peek.

        # FOR VARIABLE ASSIGNMENT #BAG-OH NI
        self.symbol_table = SymbolTable(self)
        self.symbo_name = ""
        self.symbo_type = None
        self.symbo_value = None
    
    # Return true if current token matches. This helps parser decide which grammar rule to apply given the current token or the next one.
    def checkToken(self, kind):
        return kind == self.curToken.kind

    # Return true if next token matches. This helps parser decide which grammar rule to apply given the current token or the next one.
    def checkPeek(self, kind):
        return kind == self.peekToken.kind

    # Try to match current token. If not, error. Advances the current token.
    def match(self, kind):
        # CHECKS IF THE IDENTIFIER ALREADY EXIST IN THE SYMBOL TABLE #BAG-OH NI
        if not self.checkToken(kind):
            self.abort("Expected " + kind.name + ", got " + self.curToken.kind.name)
        self.nextToken()

    # Advances the current token.
    def nextToken(self):
        # PARSER MUST BE BEHIND THE LEXER
        self.curToken = self.peekToken
        self.curLine = self.lexLine 
        self.curCol = self.lexCol
        # LEXER MUST BE AHEAD THAN PARSER
        self.peekToken = self.lexer.getToken()
        self.lexLine = self.lexer.curLine
        self.lexCol = self.lexer.curCol

    def abort(self, message):
        sys.exit("Parsing error @ line " +str(self.curLine) +", col " +str(self.curCol) +"\n" + message)

    # program ::= {statement}
    def program(self):
        print("PROGRAM")

        # Since some newlines are required in our grammar, need to skip the excess.
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        # Parse all the statements in the program. Will continue to call statement until there is nothing left.
        while not self.checkToken(TokenType.EOF):
            self.statement()

    # statement ::= "OUTPUT:" (expression | string) nl
   
    def statement(self):
        # Check the first token to see what kind of statement this is.

        # "PRINT" (expression | string)
        if self.checkToken(TokenType.PRINT):
            print("STATEMENT-PRINT")
            self.nextToken()

            if self.checkToken(TokenType.STRING):
                # Simple string.
                print(self.curToken.text) # PRINT THE STRING
                self.nextToken()
            else:
                # Expect an expression.
                print(self.expression())

        # "VAR" ident "=" (number | char | boolean | {expression} | ident) AS (INT | FLOAT | CHAR | BOOL)
        elif self.checkToken(TokenType.VAR):
            print("VAR-STATEMENT")
            self.varstmt()
        
        # This is not a valid statement. Error!
        else:
            self.abort("Invalid statement at " + self.curToken.text + " (" + self.curToken.kind.name + ")")

        # Newline.
        self.nl() #BAG-OH NI

    # "VAR" function
    def varstmt(self):
        
        # typeNum = 0 #0 if int, 1 if float for error handling later
        print("VAR")
        self.nextToken()

        #  Check if identifier exists in symbol table. If not, declare it.
        #  Check if ident exists in symbol table. If not, declare it.
        if self.curToken.text not in self.variables:
            self.variables.add(self.curToken.text)

        if self.checkToken(TokenType.IDENT): #ierase later
            print("<IDENT>")
            if self.symbol_table.doesNotExist(self.curToken.text):
                print(self.curToken.text)
                self.symbo_name = self.curToken.text
            else:
                self.abort("Existing variable \"" +self.curToken.text + "\" redeclaration")
            self.nextToken()

        if self.checkToken(TokenType.EQUAL):
            self.nextToken()
            if self.checkToken(TokenType.CHAR):
                self.nextToken()
            else:
                self.symbo_value = self.expression()

        if self.checkToken(TokenType.COMMA):
            self.series()
        
        if self.checkToken(TokenType.AS): #ierase later
            print("AS")
            self.match(TokenType.AS)              

        if self.checkToken(TokenType.INT):
            print("INT")
            self.nextToken()
            self.symbo_type = TokenType.INT

        if self.checkToken(TokenType.FLOAT):
            self.nextToken()

        if self.checkToken(TokenType.CHAR):
            print("CHAR")
            self.symbo_type = TokenType.CHAR
            self.nextToken()    

        if self.checkToken(TokenType.BOOL):
            print("BOOL")
            self.symbo_type = TokenType.BOOL
            self.nextToken()

        symbol = Symbol(self.symbo_name, self.symbo_type, self.symbo_value) #BAG-OH NI
        self.symbol_table.insert(symbol)
        print("ADDED A SYMBOL")

    # series of variable declaration
    def series(self):
        print("SERIES")    
        self.varstmt()

    # expression ::= term {( "-" | "+" ) | term}  #BAG-OH NI #WTF FIX THIS
    def expression(self):
        print("<EXPRESSION>")

        left = self.term()
        right = 0
        # Can have 0 or more +/- and expressions.
        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.nextToken()
            right += self.term()

        return left + right
        
    # term ::= unary {( "/" | "*" ) | unary} #BAG-OH NI #WTF FIX THIS
    def term(self):
        print("<TERM>")

        left = self.unary()
        right = 1
        # Can have 0 or more *// and expressions.
        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH):
            self.nextToken()
            right += self.unary()

        return left * right

    # unary ::= ["+" | "-"] primary #BAG-OH NI
    def unary(self):
        print("<UNARY>")
        result = None

        sign = 1
        # Optional unary +/-
        if self.checkToken(TokenType.PLUS):
            self.nextToken()
        elif self.checkToken(TokenType.MINUS):
            sign = -1
            self.nextToken()

        result = sign * self.primary()
        return result
        
    def primary(self): #BAG-OH NI
        print("PRIMARY (" + self.curToken.text + ")")
        value = None

        if self.checkToken(TokenType.INUMBER): 
            value = int(self.curToken.text)

        elif self.checkToken(TokenType.FNUMBER):
            value = float(self.curToken.text)

        elif self.checkToken(TokenType.ICHAR):
            pass

        elif self.checkToken(TokenType.STRING):
            pass
        
        elif self.checkToken(TokenType.IDENT): 
            value = self.symbol_table.lookup(self.curToken.text).value
        else:
            # Error!
            self.abort("Unexpected token at " + self.curToken.text)

        self.nextToken()
        return value

    def nl(self):
        print("NEWLINE")
		
        # Require at least one newline.
        self.match(TokenType.NEWLINE)
        # But we will allow extra newlines too, of course.
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

    def errorhandling(self):
        if self.checkToken(TokenType.FNUMBER):
            return 1
        else:
            return 0