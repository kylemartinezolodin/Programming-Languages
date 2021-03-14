import sys, enum

# THIS CLASS' MAIN ROLE IS TO TOKENIZE THE SOURCE CODE OF THE CUSTOM LANGUAGE
class Lexer:
    def __init__(self, input):
        self.source = input + '\n' # Source code to lex as a string. Append a newline to simplify lexing/parsing the last token/statement.
        self.curChar = ''   # Current character in the string.
        self.curPos = -1    # Current position in the string.

        # FOR COMPILATION ABORT PURPOSES
        self.curLine = 1 
        self.curCol = 0

        # DURING INITIALIZATION 
        self.nextChar()

    # Process the next character.
    def nextChar(self):
        self.curPos += 1
        self.curCol += 1 
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
        sys.exit("Lexical error @ line " +str(self.curLine) +", col " +str(self.curCol) +"\n" + message)
		
    # Skip whitespace except newlines, which we will use to indicate the end of a statement.
    def skipWhitespace(self):
        while self.curChar == ' ' or self.curChar == '\t' or self.curChar == '\r':
            self.nextChar()
		
    # Skip comments in the code.
    def skipComment(self):
        pass
    
    def peekToken(self):
        # SAVE CURRENT VALUES OF EACH PROPERTIES
        revertChar = self.curChar
        revertPos = self.curPos
        revertCol = self.curCol
        revertLine = self.curLine

        peekedToken = self.getToken()

        # REVERT PROPERTIES  
        self.curChar = revertChar
        self.curPos = revertPos
        self.curCol = revertCol
        self.curLine = revertLine

        return peekedToken

    # ANG BIDA SA LEXER
    # Return the next token.
    def getToken(self):
        self.skipWhitespace() # REMEMBER getToken IS CALLED AFTER A RECENT getToken CALL WHERE GI KAON NIYA TANANG CHAR AFTER A CERTAIN TOKEN, THUS A NEXT getToken CALL IS UNCHARTED

        token = None
        
    # NEWLINE HANDLER
        if self.curChar == '\n':
            self.curLine += 1
            self.curCol = 1
            token = self.tokenize('\n')

    # End-of-file HANDLER
        elif self.curChar == '\0':
            token = self.tokenize(self.curChar)

    # COMMA HANDLING!
        elif self.curChar == ',':
            token = self.tokenize(',')


    # OPERATOR HANDLER
        # Check the first character of this token to see if we can decide what it is.
        # If it is a multiple character operator (e.g., !=), number, identifier, or keyword then we will process the rest.
        
        elif self.curChar == '=':
            if self.peek() == '=':
                self.nextChar()
                token = self.tokenize("==")
            else:
                token = self.tokenize("=")
        elif self.curChar == '<':
            if self.peek() == '>':
                self.nextChar()
                token = self.tokenize("<>")
            elif self.peek() == '=':
                token = self.tokenize("<=")
            else:
                token = self.tokenize("<")
        elif self.curChar == '>':
                token = self.tokenize(">")
        elif self.curChar == '>=':
                token = self.tokenize(">=")
        elif self.curChar == '+':
            token = self.tokenize("+")
        elif self.curChar == '-':
            token = self.tokenize("-")
        elif self.curChar == '*':
            token = self.tokenize("*")
        elif self.curChar == '/':
            token = self.tokenize("/")
        elif self.curChar == '(':
            token = self.tokenize("(")
        elif self.curChar == ')':
            token = self.tokenize(")")
        elif self.curChar == '%':
            token = self.tokenize("%")

    # DOUBLE APPOSTROPHE HANDLER
        elif self.curChar == '"':
            startPos = self.curPos
            self.nextChar()
            # LOOP THRU UNTILL THE NEXT UNESCAPED DOUBLE APOSTROPHE OR NEWLINE
            while self.peek() != '\n':
                if self.curChar == '\0':
                    self.abort("Expecting closing double appostrophe [\"] ")
                
                elif self.curChar == '\"':
                    if self.source[self.curPos - 1] != "[" and self.source[self.curPos + 1] != "]": # IF UNESCAPED
                        break

                self.nextChar()

            if self.curChar == '\n': # ERROR SINCE WE STOPPED AT NEWLINE INSTEAD OF A UNESCAPED DOUBLE APPOSTROPHE
                self.abort("Expecting closing double appostrophe [\"] ")


            tokText = self.source[startPos : self.curPos + 1] # WHY self.curPos + 1, WHY NOT self.curPos FOR THE END SLICE INDEX? WE NEED TO KEEP THE self.curChar WITHIN THE TOKEN BEACUSE A self.nextChar() WILL BE CALLED BEFORE THE RETURN STATEMENT OF THIS FUNCTION
            token = self.tokenize(tokText)

    # CHARACTER INPUT HANDLER
        elif self.curChar == '\'':
            tokText = self.source[startPos: self.curPos + 2] # Get the substring.
            self.nextChar() # AFTER THE CALL WE EXPECT A CHARACTER 
            self.nextChar() # AFTER THE CALL WE EXPECT SINGLE APOSTROPHE
            
            token = self.tokenize(tokText)

    # OUTPUT(PRINT) CONCATENATION
        elif self.curChar == '&':
            token = self.tokenize("&")

    # NUMBER HANDLER
        elif self.curChar.isdigit():
            # Leading character is a digit, so this must be a number.
            # Get all consecutive digits and decimal if there is one.
            startPos = self.curPos
            hasAlreadyFoundDecimal = False
            while self.peek().isdigit() or self.peek() == '.':
                if self.curChar == ".":
                    if hasAlreadyFoundDecimal:
                        self.abort("Invalid numerical value: " +self.source[startPos : self.curPos] +", multiple decimal point")
                    else:
                        hasFoundDecimal = True

                if self.peek().isalpha():
                    self.abort("Invalid numerical value: " +self.source[startPos : self.curPos] +"")

                self.nextChar()
                
            tokText = self.source[startPos : self.curPos+1]  # WHY self.curPos + 1, WHY NOT self.curPos FOR THE END SLICE INDEX? WE NEED TO KEEP THE self.curChar WITHIN THE TOKEN BEACUSE A self.nextChar() WILL BE CALLED BEFORE THE RETURN STATEMENT OF THIS FUNCTION
            token = self.tokenize(tokText)

    # IDENTIFIER/KEYWORD/LOGICAL HANDLER
        elif self.curChar.isalpha(): # IF IT IS ALPHANUMERIC
            # LEADING CHARACTER IS A LETTER, SO THIS MUST BE AN IDENTIFIER, A KEYWORD, OR SOME BOOLEAN VALUE(IE TRUE/FALSE)/OPERATOR.

            # GET ALL CONSECUTIVE ALPHA NUMERIC CHARACTERS.
            startPos = self.curPos
            while self.peek().isalnum() or self.peek() == ":":
                self.nextChar()
            
            # Check if the token is in the list of keywords.
            tokText = self.source[startPos : self.curPos+1] # WHY self.curPos+1 ? WHY NOT self.curPos ? WE NEED TO KEEP THE CURSOR WITHIN THE TOKEN BECUASE A self.nextChar() WILL BE INVOKED BEFORE THIS FUNCITON WILL RETURN A TOKEN 
            token = self.tokenize(tokText)
         
        
    # AN UNKNOWN TOKEN STARTING CHARACTER
        else:
            # MESSAGE FORMAT:
            #   Unknown token!
            #   Starting character [INT CODE] is 97 as "a"
            self.abort("Unknown starting letter! \nStarting character [INT CODE] is " +str(ord(self.curChar))  +" as \"" +self.curChar +"\"" )
        
    # IF TOKEN KIND IS None THEN IT IS UNRECOGNIZED
        if token.kind == None:
            self.abort("Unknown token: \"" +str(token.text) +"\"" )

        self.nextChar() # REMOVE THE CURSOR FROM THE LAST CHARACTER OF THE CURRENT TOKEN
        return token




    def tokenize(self, text):
        token = None

    # NEWLINE HANDLER
        if text == '\n':
            token = Token(text, TokenType.NEWLINE)

    # End-of-file HANDLER
        elif text == '\0':
            token = Token('', TokenType.EOF)

    # COMMA HANDLING!
        elif text == ',':
            token = Token(',', TokenType.COMMA)


    # OPERATOR HANDLER
        # Check the first character of this token to see if we can decide what it is.
        # If it is a multiple character operator (e.g., !=), number, identifier, or keyword then we will process the rest.

        # ASSIGNMENT OPERATOR
        elif text == '=':
            token = Token("=", TokenType.EQUAL)

        # ARITHMETIC OPERATOR
        elif text == '+':
            token = Token("+", TokenType.PLUS)
        elif text == '-':
            token = Token("-", TokenType.MINUS)
        elif text == '*':
            token = Token("*", TokenType.ASTERISK)
        elif text == '/':
            token = Token("/", TokenType.SLASH)
        elif self.curChar == '%':
            token = Token(self.curChar, TokenType.MOD)

        # PARENTHESIS
        elif text == '(':
            token = Token("(", TokenType.PARAN_OPEN)
        elif text == ')':
            token = Token(")", TokenType.PARAN_CLOSE)

        # RELATIONAL OPERATOR
        elif text == '==':
            token = Token("==", TokenType.EEQUAL)
        elif text == '<>':
            token = Token("<>", TokenType.NEQUAL)
        elif text == '>':
            token = Token(">", TokenType.GREATER)
        elif self.curChar == '>=':
            token = Token(self.curChar, TokenType.GEQUAL)
        elif text == '<':
            token = Token(self.curChar, TokenType.LESSER)
        elif self.curChar == '<=':
            token = Token(self.curChar, TokenType.LEQUAL)

    # DOUBLE APPOSTROPHE HANDLER
        elif text[0] == '"':
            
        # BOOLEAN HANDLER
            if text == "\"TRUE\"":
                token = Token("1", TokenType.TRUE)
            elif text == "\"FALSE\"":
                self.nextChar()
                token = Token("0", TokenType.FALSE)

        # STRING/CHARACTER ESCAPE HANDLER
            else:
            # SPECIAL-CHARACTER PROCESSING
                i = 0
                while i < (len(text)):

                    # POUND-SIGN TO NEWLINE PROCESSING
                    if text[i] == '#':
                        # PYTHON TERNARY OPERATOR SYNTAX: someVar = [on_true] if [expression] else [on_false] 
                        leftNeigbhorChar = "" if i-1 < 0 else text[i-1]
                        rightNeigbhorChar = "" if i+1 < len(text) else text[i+1] 

                        if leftNeigbhorChar != "[" and rightNeigbhorChar != "]":
                            text = text.replace(leftNeigbhorChar +"#" +rightNeigbhorChar, leftNeigbhorChar +"\n" +rightNeigbhorChar, 1)
                            
                    i+=1 #INCREMENT, THER IS NO ++/-- IN PYTHON
            
            # CHARACTER ESCAPE PROCESSING
                text = text.replace("[#]", "#") # POUND-SIGN ESCAPE
                text = text.replace("[[]", "[") # OPENING BRACKET ESCAPE
                text = text.replace("[]]", "]") # CLOSING BRACKET ESCAPE
                text = text.replace("[\"]", "\"") # DOUBLE APOSTROPHE ESCAPE

                text = text[1:len(text) - 1] # REMOVE THE DOUBLE APOSTROPHE
                token = Token(text, TokenType.STRING)
                # Error!
                # self.abort("Boolean value must be true or false only.")

    # CHARACTER INPUT HANDLER
        elif text[0] == '\'':
            
            if text[2] == '\'' or len(text) > 3: # Error!
                token = Token(text, None) # UNRECOGNIZED TOKEN
            else: 
                token = Token(text, TokenType.LITERAL_CHAR)

    # OUTPUT(PRINT) CONCATENATION
        elif text == '&':
            token = Token(text, TokenType.STR_CONCAT)

    # NUMBER HANDLER
        elif text[0].isdigit(): # Leading character is a digit, so this must be a number.
            
            # Get all consecutive digits until it encounters not digits such as decimal-point.
            i = 0
            while i < len(text):
                if text[i].isdigit():
                    i += 1

            if i < len(text):
                if text[i] == '.': # Decimal!
                    # Must have at least one digit after decimal.
                    while i < len(text):
                        if not text[i+1].isdigit(): # Error!
                            token = Token(text, None) # UNRECOGNIZED TOKEN
                            break

                    token = Token(text, TokenType.FNUMBER)
            else:
                token = Token(text, TokenType.INUMBER)

    # IDENTIFIER/KEYWORD/LOGICAL HANDLER
        elif text[0].isalpha(): # IF IT IS ALPHANUMERIC

            # SPECIAL KEYWORDS
            if text.count(":"):
                if text == "OUTPUT:":
                    token = Token(text, TokenType.OUTPUT)
                elif text == "INPUT:":
                    token = Token(text, TokenType.INPUT)
                else: # Error!
                    token = Token(text, None) # UNRECOGNIZED TOKEN
            
            else:
                keyword = Token.checkIfKeyword(text)
                if keyword == None: # IF IT IS NOT RECOGNIZED AS KEYWORD THEN IT COULD BE AN IDENTIFIER
                    token = Token(text, TokenType.IDENT)

                else: # A KEYWORD
                    token = Token(text, keyword)            
        
    # UNKNOWN TOKEN HANDLING!
        else:
            # MESSAGE FORMAT:
            #   Unknown token!
            #   Starting character [INT CODE] is 97 as "a"
            self.abort("Unknown token! \nStarting character [INT CODE] is " +str(ord(self.curChar))  +" as \"" +self.curChar +"\"" )
        
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
            if tokenText == kind.name and kind.value >= 100 and kind.value < 200:
                return kind
        return None


# THIS CLASS' MAIN ROLE IS TO CLASSIFY THE TOKEN, WHERE ALL RESERVED WORDS ARE DEFINED HERE
class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    INUMBER = 1  # INT NUMBER
    FNUMBER = 2  # FLOAT NUMBER  
    IDENT = 3
    STRING = 4
    COMMA = 5
    LITERAL_CHAR = 6   # INPUT CHAR
    TRUE = 7
    FALSE = 8


	# Keywords.
    START = 101
    STOP = 102
    INT = 103
    PRINT = 104
    VAR = 105
    AS = 106
    OUTPUT = 107
    FLOAT = 108
    BOOL = 109
    CHAR = 110
    INPUT = 111
    WHILE = 112
    # LABEL = 101
	# GOTO = 102
	# PRINT = 103
	# INPUT = 104
	# LET = 105
	# IF = 106
	# THEN = 107
	# ENDIF = 108
	# REPEAT = 110
	# ENDWHILE = 111

	# Operators.
    NOT = 198 # RECOGNIZE AS KEYWORD ALSO
    OR = 199 # RECOGNIZE AS KEYWORD ALSO
    AND = 200 # RECOGNIZE AS KEYWORD ALSO
    EQUAL = 201  
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    SLASH = 205
    MOD = 206
    GEQUAL = 8
    LEQUAL = 9
    GREATER = 10
    LESSER = 11
    EEQUAL = 12
    NEQUAL = 13

    # SPECIALS
    STR_RETCAR = 301
    STR_CONCAT = 302
    STR_ESC = 303

    PARAN_OPEN = 311
    PARAN_CLOSE = 312
