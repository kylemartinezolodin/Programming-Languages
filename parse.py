import sys
from lexer import *
from symbolTable import *

# Parser keeps track of current token and checks if the code matches to the grammar of CFPL <3.
# WIP REMINDER:
# - AFTER THE TRIGGER(THIS COULD BE ANYTHING LIKE KEYWORD, LOGICAL OPERATOR, ETC.) QUICKLY CALL self.nextToken(), BECUASE WE WANT TO HAVE A UNIORM POST-TRIGGER APPROARCH, AT THE TIME THIS WAS WRITTEN ONLY varstmnt1(), [expression() & family funcs] AND reassignment_Statment() IS CONFIRMED TO FOLLOW
# - AFTER PROCESSING CALL self.nextToken(), TO MAKE THE FUNCTIONS UNIFORM
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        
        # FOR PARSER CURRENT LINE AND COLUMN
        self.curLine = None 
        self.curCol = None

        # FOR ABORT PURPOSES
        self.prevLine = None
        self.prevCol = None

        self.variables = list()    # Variables declared so far.

        self.curToken = None
        self.nextToken()

        # FOR VARIABLE ASSIGNMENT #BAG-OH NI
        self.symbol_table = SymbolTable(self)
        self.tempSymbol = None
        self.symbo_name = ""
        self.symbo_type = None
        self.symbo_value = None

        self.debug = False

    # USE THIS FOR DEBUGGING PURPOSE PRINTS, THIS IS WILL HELP IMMIDEATELY REMOVING DEBUG PRINTS
    def debugPrint(self, message):
        if self.debug:
            print(message)

    # Return true if current token matches. This helps parser decide which grammar rule to apply given the current token or the next one.
    def checkToken(self, kind):
        return kind == self.curToken.kind

    # Return true if next token matches. This helps parser decide which grammar rule to apply given the current token or the next one.
    def checkPeek(self, kind):
        return kind == self.lexer.peekToken().kind

    # Try to match current token. If not, error. Advances the current token.
    def match(self, kind):
        if not self.checkToken(kind):
            self.abort("Expected " + kind.name + ", got " + self.curToken.kind.name)
        self.nextToken()
    
    # ANG BIDA SA PARSER (UNTA)
    def matchCurrent_Token(self, kind, errorMessage = ""):
        if not self.checkToken(kind):
            if errorMessage == "":
                self.abort("Expecting " + kind.name + ", got " + self.curToken.kind.name)
            else:
                self.abort(errorMessage)

    # Advances the current token.
    def nextToken(self):
        # FOR ABORT PURPOSES
        self.prevLine = self.curLine
        self.prevCol = self.curCol

        # LEXER MUST BE AHEAD THAN PARSER
        self.curToken = self.lexer.getToken()
        self.curLine = self.lexer.curLine
        self.curCol = self.lexer.curCol

    def abort(self, message):
        sys.exit("Parsing error @ line " +str(self.prevLine) +", col " +str(self.prevCol) +"\n" + message)

    # program ::= {statement}
    def program(self):
        self.debugPrint("PROGRAM")

        # Since some newlines are requ,ired in our grammar, need to skip the excess.
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        # Parse all the statements in the program. Will continue to call statement until there is nothing left.
        while not self.checkToken(TokenType.EOF):
            self.statement()
            
        if self.debug:
            print("PARSER: DEBUG PROPERTY IS SET TO TRUE, SET TO FALSE TO DISABLE UNESSACARY PRINTS")
        else:
           print("PARSER: DEBUG PROPERTY IS SET TO FALSE, SET TO TRUE TO PRINT DEBUG OUTPUT MARKERS") 

    # statement ::= "OUTPUT:" (expression | string) nl
    def statement(self):
        # Check the first token to see what kind of statement this is.

        # "OUTPUT" (expression | string)
        if self.checkToken(TokenType.OUTPUT):
            self.debugPrint("OUTPUT-STATEMENT")
            self.nextToken()

            concatDeclared = True # WE SHOULD INITIALIZE TO LET IT PASS THROUGH THE FIRST PRINT
            # ITERATIVE 
            while not self.checkToken(TokenType.NEWLINE):
                if concatDeclared:
                    if self.checkToken(TokenType.STRING):
                        # Simple string.
                        print(self.curToken.text[1:-1], end="") # REMOVE THE FIRST AND LAST DOUBLE APPOSTHROPHES
                        self.nextToken()

                    else:
                        # Expect an expression.
                        output = self.expression()
                        if type(output) == str: # IF THE OUPUT WILL BE A STRING OR CHAR
                            output = output[1:-1] # REMOVE THE FIRST AND LAST CHARACTER WHICH IS LIKELY SOME APPOSTHROPHES
                        print(output, end="")
                        # value = self.expression()
                        # tempToken = self.curToken
                        # if value == None: # NONE SYMBOLS WILL BE OUPUTED AS "null"
                        #     if tempToken == TokenType.INT:
                        #         value = 0
                        #     elif tempToken == TokenType.FLOAT:
                        #         value = 0.0
                        #     elif tempToken == TokenType.CHAR or tempToken == TokenType.STRING:
                        #         value = "\0"
                        #     elif tempToken == TokenType.BOOL:
                        #         value = "FALSE"
                        # print(value, end="")

                    concatDeclared = False # TURN OFF TO REQUIRE THE CONCATANATION

                else:
                    if self.checkToken(TokenType.STR_CONCAT): # IF CONCATENATION IS HAS BEEN READ, ALLOW NEXT TOKEN TO BE PRINTED
                        concatDeclared = True
                        self.nextToken()
                    else: # ELSE THROW ERROR
                        self.abort("Expecting concatenation [&]")
            print("\n", end="") # AESTHETIC DEBUGGUNG PURPOSES, I DELETE NYA NI 

                    
        # "VAR" ident "=" (number | char | boolean | {expression} | ident) AS (INT | FLOAT | CHAR | BOOL)
        elif self.checkToken(TokenType.VAR):
            self.debugPrint("VAR-STATEMENT")
            self.symbo_name = ""
            self.symbo_type = None
            self.symbo_value = None
            # self.varstmt()

            self.nextToken()
            self.varstmt1()
        
        elif self.checkToken(TokenType.INPUT):
            self.debugPrint("INPUT-STATEMENT")
            self.symbo_name = ""
            self.symbo_type = None
            self.symbo_value = None
            self.inputstmt()
        
        elif self.checkToken(TokenType.WHILE):
        # WHILE v1.2
            self.debugPrint("WHILE-STATEMENT")
            # CURRENT TOKEN BEFORE self.nextToken(): "WHILE" KEYWORD  
            self.nextToken() # AFTER THIS CALL, WE SHOULD EXPECT OPEN PARENTHESIS FOR THE CFPL WHILE LOOP

            
            self.matchCurrent_Token(TokenType.PARAN_OPEN) # EXPECT A OPENING PARENTHESIS
            self.nextToken() # AFTER THIS CALL, WE SHOULD EXPECT AN BOOLEAN EXPRESSION FOR THE CFPL WHILE LOOP
            
            # REMEMBER THE CURRENT POSITION OF THE LEXER CURSOR, THIS WILL SERVE AS THE RESTORE-POINT/CHECKPOINT
            tempStartRepiPosMarker = self.lexer.curPos # MINUS ONE BECAUSE THE LEXER INITIALIZATION WILL MOVE THE CURSOR BY ONE CHAR, FIX THIS
            tempStartRepiColMarker = self.lexer.curCol
            tempStartRepiLineMarker = self.lexer.curLine

            # REMEMBER THE CURRENT ATTRIBUTES OF THE PARSER, THIS WILL SERVE AS THE RESTORE-POINT/CHECKPOINT
            tempParsercurToken = self.curToken

            # LOOP THRU THE WHOLE STATEMENT INSIDE CFPL WHILE, UNTIL THE "STOP" HAS BEEN READ, WHILE LOOP IS WIERDLY WRITTEN BECAUSE WE NEED IT NEED TO READ THE CLOSING PARENTHESIS BEFORE BREAK(A MAKESHIFT DO WHILE), FIX THIS
            while True:
                whileExpression = self.expression()
                self.matchCurrent_Token(TokenType.PARAN_CLOSE) # REQUIRE CLSING PARENTHESIS
                self.nextToken() # AFTER THE CALL WE EXPECT NEWLINES
                
                self.nl() # HELPS US LOOP THRU NEWLINES

                
                self.matchCurrent_Token(TokenType.START) # REQUIRE START KEYWORD
                self.nextToken() # AFTER THE CALL WE EXPECT STATEMENTS INSIDE THE CFPL LOOP

                if whileExpression == True:
                    # LOOP THRU STATEMENTS INSIDE THE CFPL LOOP UNTIL STOP KEYWORD
                    while not self.checkToken(TokenType.STOP):
                        self.nl() # HELPS US LOOP THRU NEWLINES
                        if self.checkToken(TokenType.EOF):
                            self.abort("No STOP keyword in WHILE STATEMENT")
                        self.statement() # EXECUTE THE STATEMENT IN THE LINE 
                    
                    # USE THE RESTORE-POINT/CHECKPOINT FOR LEXER
                    self.lexer.curChar = self.lexer.source[tempStartRepiPosMarker]
                    self.lexer.curPos = tempStartRepiPosMarker
                    self.lexer.curCol = tempStartRepiColMarker
                    self.lexer.curLine = tempStartRepiLineMarker

                    self.curToken = tempParsercurToken

                    self.debugPrint("REPEAT")

                else: # IF BOOLEANN EXPRESSION IN CFPLE IS FALSE
                    # AFTER THE WHILE-LOOP ABOVE, WE ARE ASSUMING THE LEXER TO BE POINTING AT THE CONDITION FOR THE CFPL WHILE-LOOP
                    startStopStack = ["START"]
                    while len(startStopStack) != 0:
                        if self.checkToken(TokenType.START): # PUSH "START" KEYWORD
                            startStopStack.append("START")
                        elif self.checkToken(TokenType.STOP): # POP "START" KEYWORD
                            startStopStack.remove("START")
                        elif self.checkToken(TokenType.EOF):
                            self.abort("No STOP keyword in WHILE STATEMENT")
                        
                        self.nextToken()
                    self.nextToken() # AFTER THE WHILE-LOOP ABOVE, WE ARE ASSUMING THE LEXER TO BE POINTING AT THE "STOP" KEYWORD FOR THE CFPL WHILE-LOOP, THUS WE SHOULD CALL self.nextToken() 
                    
                    break # EXIT THE INFINITE LOOP

        elif self.checkToken(TokenType.IDENT):
            self.debugPrint("REASSIGNMENT-STATEMENT")
            identifier = Symbol(self.curToken.text)
            self.nextToken() # TOKEN BEFORE THE CALL: SOME DECLARED VARIABLE, AFTER THIS CALL WE SHOULD EXPECT A TokenType.EQUAL

            if self.symbol_table.doesNotExist(identifier.identity):
                self.abort("Variable \"" +self.curToken.text +"\" undeclared!")

            identifier = self.symbol_table.lookup(identifier.identity)
            identifier.value = self.reassign_Statment()
            
            # self.reassign_Statment()

        elif self.checkToken(TokenType.ASTERISK):
            self.debugPrint("COMMENT STATEMENT")
            self.lexer.skipComment() # SKIPS CHARACTERS UNTIL NEWLINE CHARACTER
            # AFTER THE self.lexer.skipComment() WE EXPECT THE LEXER POINTING A NEWLINE CHARACTER 
            self.nextToken() # CURRENTLY self.curToken IS STILL TokenType.ASTERISK, CALLING self.nextToken() WILL UPDATE self.curToken
            
            # while not self.checkToken(TokenType.NEWLINE):
            #     self.nextToken()

        elif self.checkToken(TokenType.IF) or self.checkToken(TokenType.ELIF) or self.checkToken(TokenType.ELSE):
            # HELPER FUNCTION TO SKIP FUNCTION UNTIL NEWLINE
            def skipStatement():
                while not self.checkToken(TokenType.NEWLINE):
                    self.nextToken()
                self.nl()

            hasIfStatement = False # FLAGS IF IT HAS READ A IF STATEMENT
            hasAlreadySelectedCondition = False # FLAGS IF A CONDITION HAS ALREADY ACCEPTED, THIS WILL HELP IGNORE THE REMAINING CONDITION
            if self.checkToken(TokenType.IF):
                self.debugPrint("IF-STATEMENT")
                self.nextToken()

                hasIfStatement = True

                self.matchCurrent_Token(TokenType.PARAN_OPEN) # EXPECT A OPENING PARENTHESIS
                self.nextToken() # AFTER THIS CALL, WE SHOULD EXPECT AN BOOLEAN EXPRESSION FOR THE IF STATEMENT
                boolExpression = self.expression()
                self.matchCurrent_Token(TokenType.PARAN_CLOSE) # REQUIRE CLSING PARENTHESIS
                self.nextToken() # AFTER THE CALL WE EXPECT NEWLINES
                
                self.nl() # HELPS US LOOP THRU NEWLINES

                self.matchCurrent_Token(TokenType.START) # REQUIRE START KEYWORD
                self.nextToken() # AFTER THE CALL WE EXPECT STATEMENTS INSIDE THE CFPL IF STATEMENT
            
                # LOOP THRU STATEMENTS INSIDE THE CFPL IF STATEMENT UNTIL STOP KEYWORD
                while not self.checkToken(TokenType.STOP):
                    self.nl() # HELPS US LOOP THRU NEWLINES
                    if self.checkToken(TokenType.EOF):
                        self.abort("No STOP keyword in IF STATEMENT")

                    if boolExpression == True:    
                        self.statement() # EXECUTE THE STATEMENT IN THE LINE
                    else:
                        skipStatement() # IGNORE STATEMENT UNTIL NEWLINE
                if boolExpression == True:    
                    hasAlreadySelectedCondition = True 
                self.nextToken() # AFTER THE CALL WE EXPECT NEWLINES

                self.nl() # HELPS US LOOP THRU NEWLINES

            while self.checkToken(TokenType.ELIF):
                if not hasIfStatement:
                    self.abort("ELIF should only come after IF statement")
                self.debugPrint("ELIF-STATEMENT")
                self.nextToken()

                self.matchCurrent_Token(TokenType.PARAN_OPEN) # EXPECT A OPENING PARENTHESIS
                self.nextToken() # AFTER THIS CALL, WE SHOULD EXPECT AN BOOLEAN EXPRESSION FOR THE IF STATEMENT
                boolExpression = self.expression()
                self.matchCurrent_Token(TokenType.PARAN_CLOSE) # REQUIRE CLSING PARENTHESIS
                self.nextToken() # AFTER THE CALL WE EXPECT NEWLINES
                
                self.nl() # HELPS US LOOP THRU NEWLINES

                self.matchCurrent_Token(TokenType.START) # REQUIRE START KEYWORD
                self.nextToken() # AFTER THE CALL WE EXPECT STATEMENTS INSIDE THE CFPL IF STATEMENT

                
                # LOOP THRU STATEMENTS INSIDE THE CFPL IF STATEMENT UNTIL STOP KEYWORD
                while not self.checkToken(TokenType.STOP):
                    self.nl() # HELPS US LOOP THRU NEWLINES
                    if self.checkToken(TokenType.EOF):
                        self.abort("No STOP keyword in IF STATEMENT")

                    if boolExpression == True and hasAlreadySelectedCondition == False:    
                        self.statement() # EXECUTE THE STATEMENT IN THE LINE
                    else:
                        skipStatement() # IGNORE STATEMENT UNTIL NEWLINE

                if boolExpression == True and hasAlreadySelectedCondition == False:    
                    hasAlreadySelectedCondition = True 
                self.nextToken() # AFTER THE CALL WE EXPECT NEWLINES

                self.nl() # HELPS US LOOP THRU NEWLINES

            if self.checkToken(TokenType.ELSE):
                if not hasIfStatement:
                    self.abort("ELSE should only come after IF statement or ELIF statement")
                self.debugPrint("ELSE-STATEMENT")
                self.nextToken()

                self.nl() # HELPS US LOOP THRU NEWLINES

                self.matchCurrent_Token(TokenType.START) # REQUIRE START KEYWORD
                self.nextToken() # AFTER THE CALL WE EXPECT STATEMENTS INSIDE THE CFPL IF STATEMENT
                
                # LOOP THRU STATEMENTS INSIDE THE CFPL IF STATEMENT UNTIL STOP KEYWORD
                while not self.checkToken(TokenType.STOP):
                    self.nl() # HELPS US LOOP THRU NEWLINES
                    if self.checkToken(TokenType.EOF):
                        self.abort("No STOP keyword in IF STATEMENT")

                    if hasAlreadySelectedCondition == False:    
                        self.statement() # EXECUTE THE STATEMENT IN THE LINE
                    else:
                        skipStatement() # IGNORE STATEMENT UNTIL NEWLINE
                self.nextToken()
            
       # This is not a valid statement. Error!
        else:
            self.abort("Invalid statement at " + self.curToken.text + " tokenType=" + self.curToken.kind.name)

        # Newline.
        self.nl() #BAG-OH NI

    def reassign_Statment(self):
        self.matchCurrent_Token(TokenType.EQUAL)
        self.nextToken()  # TOKEN BEFORE THE CALL: "=", AFTER THIS CALL WE SHOULD EXPECT A EXPRESSION OR IDENTIFIER WHICH CAN BE DETERMINED BY self.expression()

        if self.checkToken(TokenType.IDENT) and self.checkPeek(TokenType.EQUAL):
            identifier = Symbol(self.curToken.text)
            if self.symbol_table.doesNotExist(identifier.identity):
                self.abort("Variable \"" +self.curToken.text +"\" undeclared!")

            self.nextToken()  # TOKEN BEFORE THE CALL: IDENTIFIER, AFTER THIS CALL WE SHOULD EXPECT A TokenType.EQUAL
            reassignedValue = self.reassign_Statment()
            self.symbol_table.update(identifier.identity, reassignedValue)
            return reassignedValue

        reassignedValue = self.expression() # self.expression() ALREADY CALLS self.nextToken(), SO NO NEED TO CALL FOR THIS FUNCTION

        return reassignedValue

    # "INPUT" function
    def inputstmt(self):
        #self.symbo_value = None
        # typeNum = 0 #0 if int, 1 if float for error handling later
        self.debugPrint("inputstmt()")
        self.nextToken()
        self.symbo_value = None
        
        #  Check if identifier exists in symbol table. If not, declare it.

        if self.checkToken(TokenType.IDENT): #ierase later
            self.debugPrint("<IDENT> = " + self.curToken.text)

            if self.symbol_table.doesNotExist(self.curToken.text):
                # Error!
                self.abort("Variable " + self.curToken.text + " not found")
            else: 
                self.symbo_name = self.curToken.text
            self.nextToken()
        else:
            # Error!
                self.abort("No variable assigned!")

        if self.checkToken(TokenType.EQUAL):
            #print(self.curToken.text)
            self.nextToken()
            
            if self.checkToken(TokenType.LITERAL_CHAR):
                self.symbo_value = self.curToken.text
                self.symbol_table.update(self.symbo_name, self.symbo_value)
                #print(self.symbo_name + "=")
                #print(self.symbo_value)
                self.nextToken()

            elif self.checkToken(TokenType.STRING):
                self.symbo_value = self.curToken.text
                self.symbol_table.update(self.symbo_name, self.symbo_value)
                #print(self.symbo_name + "=")
                #print(self.symbo_value)
                self.nextToken()

            elif self.checkToken(TokenType.IDENT):
                #print(self.curToken.text)
                if type(self.symbol_table.lookup(self.curToken.text).value) == str:
                    self.symbo_value = self.curToken.text
                    self.symbol_table.update(self.symbo_name, self.symbo_value)
                    self.nextToken()
                else:
                    #print("hello")
                    self.symbo_value = self.expression()
                    #print(self.symbo_value)
                    self.symbol_table.update(self.symbo_name, self.symbo_value)    
            else:
                #print(self.curToken.text)
                self.symbo_value = self.expression()
                #print(self.symbo_name)
                #print(self.symbo_value)
                self.symbol_table.update(self.symbo_name, self.symbo_value)
                #print(self.symbo_name + "=") 
                #print(self.symbo_value)

        if self.checkToken(TokenType.COMMA):
            print("COMMA")
            self.varstmt()
    
    # "VAR" function
    def varstmt(self):
        #self.symbo_value = None
        # typeNum = 0 #0 if int, 1 if float for error handling later
        self.debugPrint("varstmt()")
        self.nextToken() # AFTER THIS CALL WE SHOULD EXPECT A UNDECLARED IDENTIFIER

        self.symbo_value = None
        askey = 0
        #  Check if identifier exists in symbol table. If not, declare it.
        
        if self.checkToken(TokenType.IDENT): #ierase later
            self.debugPrint("<IDENT> = " + self.curToken.text)
            if self.curToken.text not in self.variables:
                self.variables.append(self.curToken.text)
                self.symbo_name = self.curToken.text

            else:
                # Error!
                self.abort("Already declared variable! " + self.curToken.text)

            self.nextToken()
        else:
            # Error!
                self.abort("No variable declared!")

        if self.checkToken(TokenType.EQUAL):
            self.nextToken()

            if self.checkToken(TokenType.LITERAL_CHAR):
                self.symbo_value = self.curToken.text
                symbol = Symbol(self.symbo_name, None, self.symbo_value) #BAG-OH NI
                self.symbol_table.insert(symbol)
                #print(self.symbo_name + "=")
                #print(self.symbo_value)
                self.nextToken()

            elif self.checkToken(TokenType.STRING):
                self.symbo_value = self.curToken.text
                symbol = Symbol(self.symbo_name, None, self.symbo_value) #BAG-OH NI
                self.symbol_table.insert(symbol)
                #print(self.symbo_name + "=")
                #print(self.symbo_value)
                self.nextToken()
            
            elif self.checkToken(TokenType.IDENT):
                if type(self.symbol_table.lookup(self.curToken.text).value) == str:
                    self.symbo_value = self.symbol_table.lookup(self.curToken.text).value
                    symbol = Symbol(self.symbo_name, None, self.symbo_value) #BAG-OH NI
                    self.symbol_table.insert(symbol)
                    self.nextToken()
                    
                else:
                    self.symbo_value = self.expression()
                    self.symbol_table.update(self.symbo_name, self.symbo_value)

            else:
                self.symbo_value = self.expression()
                symbol = Symbol(self.symbo_name, None, self.symbo_value) #BAG-OH NI
                self.symbol_table.insert(symbol)
                #print(self.symbo_name + "=") 
                #print(self.symbo_value)

        if self.checkToken(TokenType.COMMA):
            print("COMMA")
            self.varstmt()
        
        if self.checkToken(TokenType.AS): #ierase later
            print("AS")
            self.match(TokenType.AS)              

            if self.checkToken(TokenType.INT):
                print("INT")
                self.nextToken()
                self.symbo_type = TokenType.INT

            elif self.checkToken(TokenType.FLOAT):
                print("FLOAT")
                self.nextToken()
                self.symbo_type = TokenType.FLOAT

            elif self.checkToken(TokenType.CHAR):
                print("CHAR")
                self.symbo_type = TokenType.CHAR
                self.nextToken()    

            elif self.checkToken(TokenType.BOOL):
                print("BOOL")
                self.symbo_type = TokenType.BOOL
                self.nextToken()
            
        else:
            # Error!
            if self.checkToken(TokenType.NEWLINE):
                pass
            elif self.checkToken(TokenType.EOF): 
                pass
            elif self.symbo_type == None:
            # Error!
                self.abort("No AS keyword!")
            else:
                self.abort("Invalid statement at " + self.curToken.text + " (" + self.curToken.kind.name + ")")

        if self.symbo_type == None:
            # Error!
                self.abort("No datatype declared to a variable!")

        if self.variables:
            pop = self.variables.pop()
            if not self.symbol_table.doesNotExist(pop):
                if self.errorhandling(self.symbol_table.lookup(pop).value) == 1:
                    self.symbol_table.setdatatype(pop, self.symbo_type)
                else:
                    # Error
                    self.abort("Variable type and value do not coincide!" + self.curToken.text)    
            else:
                symbol = Symbol(pop, self.symbo_type, None) #BAG-OH NI
                self.symbol_table.insert(symbol) 
                #value = None
    
    # "VAR" FUNCTION, THIS FUNCTION ASSUMES IT READING TOKEN AFTER THE "VAR" STATEMENT, THUS  SHOULD NO LONGER ACCEPT ANOTHER VAR KEYWORD
    def varstmt1(self): # var-statment := VAR [<UNDECLRED_IDENT> | <UNDECLRED_IDENT> = <VALUE_MATCHIN_TYPE>]  {[, <UNDECLRED_IDENT> |, <UNDECLRED_IDENT> = <VALUE_MATCHIN_TYPE>]} AS <TYPE>
        self.debugPrint("varstmt1()")

        self.matchCurrent_Token(TokenType.IDENT) # EXPECTS AN UNDELARED IDENTIFIER

        tempSymbol = None # A TEMPORARY HOLDER FOR A UNCDECLARED DECLARED CFPL VARIABLE

        # IDENTIFIER EXISTENCE CHECK
        if self.symbol_table.doesNotExist(self.curToken.text): 
            self.debugPrint("Identifier \"" +self.curToken.text +"\"")

            tempSymbol = Symbol(self.curToken.text)
            self.symbol_table.insert(tempSymbol)
            tempSymbol = self.symbol_table.lookup(tempSymbol.identity)

            self.nextToken()
        else:
            # Error!
            self.abort("Variable already declared! " + self.curToken.text)
        
        # AFTER THE EXISTENCE CHECK WE CAN EXPECT AN EQUALS
        if self.checkToken(TokenType.EQUAL):
            self.nextToken() # TOKEN BEFORE THE CALL: "=", AFTER THIS CALL WE SHOULD EXPECT A VALUE FOR THE DECLARED VARIABLE
        
        # APPROARCH v1.1
            tempSymbol.value = self.expression()

        # APPROARCH v1
            # if self.checkToken(TokenType.LITERAL_CHAR) or self.checkToken(TokenType.STRING):
            #     tempSymbol.value = str(self.curToken.text)
            #     self.nextToken() 
            # else: # FOR VALUES THAT IS NOT A CHAR OR STRING, VERY LIKELY TO BE AN EXPRESSION
            #     tempSymbol.value = self.expression()


        # AFTER THE EXISTENCE CHECK WE CAN ALSO EXPECT A COMMA OR "AS" KEYWORD
        if self.checkToken(TokenType.COMMA):
            self.nextToken()

            # tempSymbol = self.symbol_table.lookup(tempSymbol.identity)
            identType = self.varstmt1() 
            tempSymbol.dataType = identType

            return identType

        elif self.checkToken(TokenType.AS):
            self.nextToken()

            # ALLOWED DATA TYPES FOR THE CFPL
            if self.checkToken(TokenType.STRING) or self.checkToken(TokenType.CHAR) or self.checkToken(TokenType.INT) or self.checkToken(TokenType.FLOAT) or self.checkToken(TokenType.BOOL):
                identType = self.curToken.kind
                tempSymbol.dataType = identType
                self.nextToken()
                return identType
            else:
                self.abort("Expecting Data-Type definition [CHAR | INT | FLOAT | BOOL], got " +self.curToken.kind.name)
        
        else: # ERROR 
            self.abort("Expecting \",\" [COMMA] | \"AS\" keyword, got " +self.curToken.kind.name)


    # expression ::= term {( "-" | "+" ) | term}  #BAG-OH NI #WTF FIX THIS
    def expression(self):
        self.debugPrint("expression()")

        left = self.term()

        if self.checkToken(TokenType.OR) or  self.checkToken(TokenType.AND):
            while self.checkToken(TokenType.OR) or  self.checkToken(TokenType.AND):
                operatorToken = self.curToken # WE EXPECT self.curToken TO BE A BOOLEAN KEYWORD 
                self.nextToken()

                right = self.term()
                # WE ONLY EXPECT BOOLEAN VALUE
                if type(left) == str or type(right) == str:
                    self.abort("A CHAR/STRING isn't supposed to be used for boolean operation")
                elif type(left) != bool or type(right) != bool:
                    self.abort("A NUMERIC value isn't supposed to be used for boolean operation")
                
                if operatorToken.kind == TokenType.OR: 
                    left = left or right
                elif operatorToken.kind == TokenType.AND:
                    left = left and right
                else:
                    self.abort("Expecting BOOLEAN [AND/OR] keywords in the expression")


        # 0 OR MORE ARITHMETIC OR LOGICAL EXPRESSION
        else:
            while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS) or self.checkToken(TokenType.EEQUAL) or self.checkToken(TokenType.NEQUAL) or self.checkToken(TokenType.GEQUAL) or self.checkToken(TokenType.GREATER) or self.checkToken(TokenType.LEQUAL) or self.checkToken(TokenType.LESSER):
                operatorToken = self.curToken # WE EXPECT self.curToken TO BE A ARITHMETIC OR LOGICAL OPERATOR 
                self.nextToken()

                right = self.term()
                # WE ONLY EXPECT NUMERICAL VALUE
                if type(left) == str or type(right) == str:
                    self.abort("A CHAR/STRING isn't supposed to be used for arithmethic or relational operation")
                elif type(left) == bool or type(right) == bool:
                    self.abort("A BOOLEAN isn't supposed to be used for arithmethic or relational operation")

                # WE EXECUTE OPERATION BASED ON THE PREVIOUS TOKEN WE ASSUMED TO BE AN OPERATOR
                # ARITHMETHIC
                if operatorToken.kind == TokenType.PLUS: 
                    left += right
                elif operatorToken.kind == TokenType.MINUS:
                    left -= right
                    
                # RELATIONAL
                elif operatorToken.kind == TokenType.EEQUAL:
                    left = left == right
                elif operatorToken.kind == TokenType.NEQUAL:
                    left = left != right
                elif operatorToken.kind == TokenType.GEQUAL:
                    left = left >= right
                elif operatorToken.kind == TokenType.GREATER:
                    left = left > right
                elif operatorToken.kind == TokenType.LEQUAL:
                    left = left <= right
                elif operatorToken.kind == TokenType.LESSER:
                    left = left < right
                else:
                    self.abort("Expecting ARITHMETIC [+/-] operators or RELATIONAL [==/<>/>=/>/<=/<] operators in the expression")

        return left
        
    # term ::= unary {( "/" | "*" ) unary}
    def term(self):
        self.debugPrint("term()")

        left = self.unary()

        # Can have 0 or more *// and expressions.
        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH) or self.checkToken(TokenType.MOD):
            operatorToken = self.curToken # WE EXPECT self.curToken TO BE A LOGICAL OPERATOR 
            self.nextToken()

            right = self.unary()
            # CHECKS IF THE VALUES ARE CONSISTENLY NUMERICAL
            if type(left) == bool or type(right) == bool: 
                self.abort("A BOOLEAN isn't supposed to be used for numerical operation")
            elif type(left) == str or type(right) == str:
                self.abort("A CHAR/STRING isn't supposed to be used for numerical operation")
                
            # WE EXECUTE OPERATION BASED ON THE PREVIOUS TOKEN WE ASSUMED TO BE AN OPERATOR
            if operatorToken.kind == TokenType.ASTERISK:
                left *= right
            elif operatorToken.kind == TokenType.SLASH:
                left /= right
            elif operatorToken.kind == TokenType.MOD:
                left %= right
        return left

    # unary ::= ("+" | "-") (<numrical_primary>|<expression>)) | ("NOT") (<boolean_primary>|<expression>)) 
    def unary(self):
        self.debugPrint("unary()")
        result = None

        sign = 1
        hasReadNotKeyword = False # A FLAG IF THE "NOT" KEYWORD HAS BEEN READ
        # OPTIONAL UNARRY/PREFFIX [ + | - | NOT ]
        if self.checkToken(TokenType.PLUS):
            self.nextToken()
        elif self.checkToken(TokenType.MINUS):
            sign = -1
            self.nextToken()
        elif self.checkToken(TokenType.NOT):
            hasReadNotKeyword = True
            self.nextToken()

        # IF IT READS A PRENTHESIS IT LIKELY TO BE AN EXPRESSION        
        if self.checkToken(TokenType.PARAN_OPEN):
            self.debugPrint("OPEN-PARAN")
            self.nextToken()
            result = self.expression()
            self.matchCurrent_Token(TokenType.PARAN_CLOSE)
            self.debugPrint("CLOSE-PARAN")
            self.nextToken()
        else:
            result = self.primary()

        if type(result) == str: # IF VALUE IS SOME STRING
            if hasReadNotKeyword:
                self.abort("Cannot negate CHAR/STRING,, NOT operator is used in BOOLEAN values")
            elif sign == -1:
                self.abort("Cannot negate CHAR/STRING, Unary \"-\" [NEGATION] operator is used in numerical values")

        elif hasReadNotKeyword: # IF NOT KEYWORD WAS PRESSENT 
            result = not result
        elif sign == -1: # IF UNARY "-" [NEGATION] OPERATOR WAS PRESSENT
            result = sign * result
        return result
        
    def primary(self): #BAG-OH NI
        value = None

        if self.checkToken(TokenType.INUMBER): 
            value = int(self.curToken.text)

        elif self.checkToken(TokenType.FNUMBER):
            value = float(self.curToken.text)

        elif self.checkToken(TokenType.LITERAL_CHAR):
            value = self.curToken.text

        elif self.checkToken(TokenType.STRING):
            value = self.curToken.text
        
        elif self.checkToken(TokenType.IDENT): 
            value = self.symbol_table.lookup(self.curToken.text).value
            
        elif self.checkToken(TokenType.TRUE): # IF CURRENT TOKEN IS A KEYWORD "TRUE"
            value = True
        elif self.checkToken(TokenType.FALSE): # IF CURRENT TOKEN IS A KEYWORD "FALSE"
            value = False
        else:
            self.abort("Unexpected " +self.curToken.text +" token, expecting numerical or logical value")
        # elif self.curToken.text != '=':
        #     # Error!
        #     self.abort("Unexpected " +self.curToken.text +" token, expecting numerical or logical value")

        
        self.debugPrint("PRIMARY (" +str(value) +")")
        self.nextToken()
        return value

    def nl(self):
        self.debugPrint("nl()")
		
        # Require at least one newline.
        # self.match(TokenType.NEWLINE)
        # But we will allow extra newlines too, of course.
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
        
    def expression1(self):
        print("<EXPRESSION>")
        value = None
        if self.checkToken(TokenType.IDENT):
            if self.symbol_table.lookup(self.curToken.text).value == None:
                if self.checkPeek(TokenType.EQUAL):
                    self.multiequal()
                    return self.symbo_value
                else:
                    value = 0
            else:
                value = str(self.symbol_table.lookup(self.curToken.text).value)
            exp = str(value)
        else:            
            exp = self.curToken.text
        #print(exp)
        self.nextToken()
        
        while not self.checkToken(TokenType.AS):
            if self.checkToken(TokenType.INT) or self.checkToken(TokenType.FLOAT) or self.checkToken(TokenType.BOOL) or self.checkToken(TokenType.CHAR):
                break
            elif self.checkToken(TokenType.NEWLINE):
                break
            elif self.checkToken(TokenType.EOF):
                break
            elif self.checkToken(TokenType.COMMA):
                break
            elif self.checkToken(TokenType.IDENT):
                value = self.symbol_table.lookup(self.curToken.text).value
            else: 
                value = self.curToken.text
            exp += str(value)
            self.nextToken()
        
        #print(exp)
        #print(eval(exp))
        if(eval(exp) != None):
            value = eval(exp)
            
        return eval(exp)
    
    def multiequal(self):
        print("MULTIEQUAL")
        variables = list()
        variables.append(self.curToken.text)
        self.nextToken() 
        #a = b = c = d = 5
        
        while not self.checkToken(TokenType.NEWLINE):
            if self.checkToken(TokenType.PARAN) or self.checkToken(TokenType.INUMBER) or self.checkToken(TokenType.FNUMBER):
                self.symbo_value = self.expression()
                break
            elif self.checkToken(TokenType.IDENT):
                variables.append(self.curToken.text)
            self.nextToken()
        
        while variables:
            pop = variables.pop()
            print(pop)
            self.symbol_table.update(pop, self.symbo_value)

        self.nextToken()
        return self.symbo_value
    
    def booleval(self,exp):
        print("CONDITION")
        value = None
        templex = Lexer(exp)
        token = templex.getToken()
        exp = ""
        while token.kind != TokenType.EOF:
            if token.kind == TokenType.IDENT:
                value = str(self.symbol_table.lookup(token.text).value)
                exp += str(value)
            else:            
                exp += token.text
            token = templex.getToken()
        #print(exp)
        try:
            print(eval(exp))
            if eval(exp) == True or eval(exp) == False:
                return eval(exp) 
        except:
            print("Invalid condition in WHILE! Bool expression/s are required.")

    def errorhandling(self, value):
        flag = 0

        #print(self.symbo_type)
        #print(type(self.symbo_value))
       

        if self.symbo_value == None:
            flag = 1

        elif self.symbo_type == TokenType.INT and type(value) == int:
            flag = 1

        elif self.symbo_type == TokenType.FLOAT and type(value) == float:
            flag = 1

        elif self.symbo_type == TokenType.FLOAT and type(value) == int:
            flag = 1    
            self.symbo_value = float(value)

        elif self.symbo_type == TokenType.CHAR:
            if value == '\0':
                flag = 1
            elif type(value) == str:
                if len(value) == 1:
                    flag = 1

        elif self.symbo_type == TokenType.BOOL:
            if type(value) == str or type(value) == bool:
                flag = 1

        return flag
