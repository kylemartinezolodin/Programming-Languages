import sys, enum

# THIS CLASS' MAIN ROLE IS TO TOKENIZE THE SOURCE CODE OF THE CUSTOM LANGUAGE
class Lexer:
    def __init__(self, input):
        self.source = input + '\n' # Source code to lex as a string. Append a newline to simplify lexing/parsing the last token/statement.
        self.curChar = ''   # Current character in the string.
        self.curPos = -1    # Current position in the string.

        # FOR COMPILATION ABORT PURPOSES
        self.curLine = 0 
        self.curCol = 0

        # DURING INITIALIZATION 
        self.nextChar()

    # Process the next character.
    def nextChar(self):
        self.curPos += 1
        self.curLine += 1 
        if self.curPos >= len(self.source):
            self.curChar = '\0'  # EOF
        else:
            self.curChar = self.source[self.curPos]

    # Return the lookahead character.
    def peek(self):
        if self.curPos + 1 >= len(self.source):
            return '\0'
        return self.source[self.curPos+1]

    # Invalid token found, print error message and exit.
    def abort(self, message):
        sys.exit("Lexing error @ line " +str(self.curLine) +", col " +str(self.curCol) +"\n" + message)
		
    # Skip whitespace except newlines, which we will use to indicate the end of a statement.
    def skipWhitespace(self):
        while self.curChar == ' ' or self.curChar == '\t' or self.curChar == '\r':
            self.nextChar()
		
    # Skip comments in the code.
    def skipComment(self):
        pass

    # ANG BIDA SA LEXER
    # Return the next token.
    def getToken(self):
        self.skipWhitespace() # REMEMBER getToken IS CALLED AFTER A RECENT getToken CALL WHERE GI KAON NIYA TANANG CHAR AFTER A CERTAIN TOKEN, THUS A NEXT getToken CALL IS UNCHARTED

        token = None
        
    # NEWLINE HANDLER
        if self.curChar == '\n':
            self.curLine += 1
            self.curCol = 0
            token = Token(self.curChar, TokenType.NEWLINE)

    # End-of-file HANDLER
        elif self.curChar == '\0':
            token = Token('', TokenType.EOF)

    # OPERATOR HANDLER
        # Check the first character of this token to see if we can decide what it is.
        # If it is a multiple character operator (e.g., !=), number, identifier, or keyword then we will process the rest.
        
        elif self.curChar == '=':
            token = Token(self.curChar, TokenType.EQ)
        elif self.curChar == '+':
            token = Token(self.curChar, TokenType.PLUS)
        elif self.curChar == '-':
            token = Token(self.curChar, TokenType.MINUS)
        elif self.curChar == '*':
            token = Token(self.curChar, TokenType.ASTERISK)
        elif self.curChar == '/':
            token = Token(self.curChar, TokenType.SLASH)
        

    # NUBER HANDLER
        elif self.curChar.isdigit():
            # Leading character is a digit, so this must be a number.
            # Get all consecutive digits and decimal if there is one.
            startPos = self.curPos
            while self.peek().isdigit():
                self.nextChar()
            if self.peek() == '.': # Decimal!
                self.nextChar()

                # Must have at least one digit after decimal.
                if not self.peek().isdigit(): 
                    # Error!
                    self.abort("Illegal character in number.")
                while self.peek().isdigit():
                    self.nextChar()

            tokText = self.source[startPos : self.curPos + 1] # Get the substring.
            token = Token(tokText, TokenType.NUMBER)
        
    # IDENTIFIER HANDLER
        elif self.curChar.isalpha(): # IF IT IS ALPHANUMERIC
            # Leading character is a letter, so this must be an identifier or a keyword.
            # Get all consecutive alpha numeric characters.
            startPos = self.curPos
            while self.peek().isalnum():
                self.nextChar()

            # Check if the token is in the list of keywords.
            tokText = self.source[startPos : self.curPos + 1] # Get the substring.
            keyword = Token.checkIfKeyword(tokText)
            if keyword == None: # Identifier
                token = Token(tokText, TokenType.IDENT)
            else:   # Keyword
                token = Token(tokText, keyword)

    # UNKNOWN TOKEN HANDLING!
        else:
            # MESSAGE FORMAT:
            #   Unknown token!
            #   Starting character [INT CODE] is 97 as "a"
            self.abort("Unknown token! \nStarting character [INT CODE] is " +str(ord(self.curChar))  +" as \"" +self.curChar +"\"" )
        
        self.nextChar()
        return token

# THIS CLASS' MAIN ROLE IS TO STRUCTURE THE TOKEN, CONTAINING TOKEN TEXT AND THE TYPE OF TOKEN.
class Token:   
    def __init__(self, tokenText, tokenKind):
        self.text = tokenText   # The token's actual text. Used for identifiers, strings, and numbers.
        self.kind = tokenKind   # The TokenType that this token is classified as.
        
    @staticmethod # STATIC PARA CALLABLE SIYA BISAG WALAY BUHATAY OG INSTANCE ANI NGA CLASS
    def checkIfKeyword(tokenText):
        for kind in TokenType:
            # Relies on all keyword enum values being 1XX.
            if kind.name == tokenText and kind.value >= 100 and kind.value < 200:
                return kind
        return None

# THIS CLASS' MAIN ROLE IS TO CLASSIFY THE TOKEN, WHERE ALL RESERVED WORD ARE DEFINED HERE
# MAG SABOT SA GURO TAS RESERVED WORD GAMITON SA ATO LANGUAGE
class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    STRING = 3

	# Keywords.
    START = 101
    STOP = 102
    INT = 103
    PRINT = 104
    # LABEL = 101
	# GOTO = 102
	# PRINT = 103
	# INPUT = 104
	# LET = 105
	# IF = 106
	# THEN = 107
	# ENDIF = 108
	# WHILE = 109
	# REPEAT = 110
	# ENDWHILE = 111

	# Operators.
    EQ = 201  
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    SLASH = 205
    EQEQ = 206
    NOTEQ = 207
    LT = 208
    LTEQ = 209
    GT = 210
    GTEQ = 211



