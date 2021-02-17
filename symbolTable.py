import sys

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

    def abort(self, message):
        sys.exit("Symbol error @ line " +str(self.parser.curLine) +", col " +str(self.parser.curCol) +"\n" + message)


class Symbol:
    def __init__(self, identity, dataType, value):
        self.identity = identity
        self.dataType = dataType
        self.value = value

    