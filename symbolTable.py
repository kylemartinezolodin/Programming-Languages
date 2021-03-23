import sys
from lexer import TokenType

class SymbolTable:
    def __init__(self, parser):
        self.parser = parser
        self.table = list()

    def doesNotExist(self, identifier):
        for x in self.table:
            if x.identity == identifier:
                return False
        return True
    
    def lookup(self, identity):
        for x in self.table:
            if x.identity == identity:
                return x
        self.abort("Lookup Error, identifier \"" +identity +"\" does not exist")
        

    def insert(self, symb):
        if self.doesNotExist(symb):
            self.table.append(symb)
            return True
        else:
            return False

    def update(self, identifier, value):
        if self.doesNotExist(identifier):
            return None
        else:
            for x in self.table:
                if x.identity == identifier:
                    x.value = value
    
    def getdatatype(self, identifier):
        return self.lookup(identifier).dataType

    def setdatatype(self, identifier, dataType):
        self.lookup(identifier).dataType = dataType

    def abort(self, message):
        sys.exit("Symbol-Table error @ line " +str(self.parser.curLine) +", col " +str(self.parser.curCol) +"\n" + message)


class Symbol:
    def __init__(self, identity, dataType = None, value = None):
        self.identity = identity
        self._dataType = dataType
        self._value = value

    def getDataType(self):
        return self._dataType

    def setDataType(self, symboType):
        if self._value != None:
            # CHECK IF ITS IS NOT A STRING, OR DOES NOT HAVE A DOUBLE APPOSTROPHE IN THE START AND AT THE END OF THE STRING
            if symboType == TokenType.STRINGK and ( type(self._value) != str or (self._value[0] != "\"" and self._value[-1] != "\"") ):
                if type(self.value) == bool:
                    self.value = str(self.value)
                else:
                    self.abort("Value " +str(self.value) +" is not STRING, STRING values should be enclosed by double-appostrophe [\"]")

            # CHECK IF ITS IS NOT A STRING, OR STRING-LENGHT IS NOT 3, OR DOES NOT HAVE A SINGLE APPOSTROPHE IN THE START AND AT THE END
            elif symboType == TokenType.CHAR and ( type(self._value) != str or ( len(self._value) != 3 or (self._value[0] != "\'" and self._value[-1] != "\'")) ):
                self.abort("Value " +str(self.value) +" is not CHAR, CHAR values should only be a single character enclosed by single-appostrophe [\']")
            elif symboType == TokenType.INT and type(self._value) != int:
                if type(self.value) == float:
                    self.value = int(self.value)
                else:
                    self.abort("Value \"" +str(self.value) +"\" is not INT")
            elif symboType == TokenType.FLOAT and type(self._value) != float:
                if type(self.value) == int:
                    self.value = float(self.value)
                else:
                    self.abort("Value \"" +str(self.value) +"\" is not FLOAT")
            elif symboType == TokenType.BOOL and type(self._value) != bool:
                self.abort("Value \"" +str(self.value) +"\" is not BOOL")
                
        self._dataType = symboType

    dataType = property(getDataType, setDataType) # property() PYTHON BUILT FUNCTION READ MORE: https://www.geeksforgeeks.org/getter-and-setter-in-python/


    def getValue(self):
        ret = None
        if self._value == None and self._dataType != None:
            if self.dataType == TokenType.CHAR or self.dataType == TokenType.STRINGK:
                ret = "\0"
            elif self.dataType == TokenType.INT:
                ret = 0
            elif self.dataType == TokenType.FLOAT:
                ret = 0.0
            elif self.dataType == TokenType.BOOL:
                ret = False
            else:
                self.abort("Unknown dataype")
        else:
            ret = self._value
        return ret
        
    def setValue(self, val):
        if self._dataType != None:
            if type(val) == str:
                if val[0] == "\'" and (self.dataType != TokenType.CHAR or len(val) != 3):
                    self.abort("Assigned value must be a "+ str(self.dataType)[10:] +", instead of a CHAR") #IF ASSIGNED VALUE IS CHAR
                elif val[0] == "\"" and self.dataType != TokenType.STRINGK:
                    self.abort("Assigned value must be a "+ str(self.dataType)[10:]+", instead of a STRING") #IF ASSIGNED VALUE IS STRING
                # else:
                #     self._value = val[1:len(val)-1]
            elif type(val) == int and self.dataType != TokenType.INT:
                if self.dataType == TokenType.FLOAT:
                    val = float(val)
                else:
                    self.abort("Assigned value must be a "+ str(self.dataType)[10:]+", instead of an INT") #IF ASSIGNED VALUE IS INT
            elif type(val) == float and self.dataType != TokenType.FLOAT:
                if self.dataType == TokenType.INT:
                    val = int(val)
                else:
                    self.abort("Assigned value must be a "+ str(self.dataType)[10:] +", instead of a FLOAT") #IF ASSIGNED VALUE IS FLOAT
            elif type(val) == bool and self.dataType != TokenType.BOOL:
                if(self.dataType == TokenType.STRINGK):
                    val = str(val)
                else:
                    self.abort("Assigned value must be a "+ str(self.dataType)[10:] +", instead of a BOOL") #IF ASSIGNED VALUE IS BOOL

        self._value = val
        # if type(val) == str:
        #     self._value = val[1:len(val)-1] #REMOVES APPOSTROPHES FOR BOTH STRING AND CHAR
        # else:
        #     self._value = val

        # elif self._dataType == TokenType.INT:
        #     self._value = ord(val)
        # else:
        #     self._value = val

    value = property(getValue, setValue) # property() PYTHON BUILT FUNCTION READ MORE: https://www.geeksforgeeks.org/getter-and-setter-in-python/
        
    # @property # A PHTON PROPERTY-GETTER DECORATOR, READ MORE: https://www.geeksforgeeks.org/getter-and-setter-in-python/
    # def dataType(self):
    #     return self._dataType

    # @dataType.setter # A PHTON PROPERTY-SETTER DECORATOR, READ MORE: https://www.geeksforgeeks.org/getter-and-setter-in-python/
    # def dataType(self, symboType):
    #     if self._value != None:
    #         pass

    # @property  # A PHTON PROPERTY-GETTER DECORATOR, READ MORE: https://www.geeksforgeeks.org/getter-and-setter-in-python/
    # def value(self):
    #     return self._value

    # @value.setter # A PHTON PROPERTY-SETTER DECORATOR, READ MORE: https://www.geeksforgeeks.org/getter-and-setter-in-python/
    # def value(self, val):
    #     if self._value != None:
    #         pass
    
    def abort(self, message):
        sys.exit("Symbol error for \"" +self.identity +"\" identifier \n" + message)

    