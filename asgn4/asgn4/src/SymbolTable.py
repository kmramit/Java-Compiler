import sys
class SymbolTable:

    def __init__(self):
        self.SymbolTable = {
                'main' : {
                    'name' : 'main',
                    'identifiers' : {},
                    'type' : 'main',
                    'parent' : None,
                    }
                }
        self.currScope = 'main'
        self.tNo = -1
        self.scopeNo = -1

    def newScope(self):
        scope = self.newScopeName()
        self.SymbolTable[scope] = {
                'name' : scope,
                'identifiers' : {},
                'type' : 'scope',
                'parent' : self.currScope,
                }
        self.currScope = scope

    def endScope(self):
        self.currScope = self.SymbolTable[self.currScope]['parent']

    def variableAdd(self, idVal, place, idType, idSize = 4):
        if idSize == 4:
            idSize = self.getSize(idType)
        scope = self.getScope(idVal)
        if scope != self.currScope:
            sc = str(self.currScope)+'_'+place
            self.SymbolTable[self.currScope]['identifiers'][idVal] = {
                    'place' : sc,
                    'type' : idType,
                    'size' : idSize
                    }
        else:
            sys.exit('Variable '+idVal+" is already initialised in this scope")
        print(self.SymbolTable[self.currScope]['identifiers'])

    def variableSearch(self, idVal):
        scope = self.getScope(idVal)
        # print(scope)
        if(scope == None):
            return False
        else:
            return scope

    def getAttr(self, idVal, Name):
        scope = self.getScope(idVal)
        if scope != None:
            return  self.SymbolTable[scope]['identifiers'][idVal].get(Name)
        else:
            return None

    def addAttr(self, idVal, Name, Val):
        scope = self.getScope(idVal)
        if scope != None:
            self.SymbolTable[self.getScope(idVal)]['identifiers'][idVal][Name] = Val
            return True
            # print("Success")
        else:
            #print("Fail")
            return False

    def getSize(self, typeExpr):
        if typeExpr in ['INT', 'BOOL', 'FLOAT', 'CHAR', 'VOID' ]:
            return 4

    def getScope(self, idVal):
        scope = self.currScope
        while self.SymbolTable[scope]['type'] not in ['main']:
            if idVal in self.SymbolTable[scope]['identifiers']:
                return scope
            scope = self.SymbolTable[scope]['parent']

        if idVal in self.SymbolTable[scope]['identifiers']:
            return scope
        return None

    def getTemp(self):
        self.tNo += 1
        newTemp = "t"+str(self.tNo) 
        return newTemp

    def newScopeName(self):
        self.scopeNo += 1
        newScope = "s"+str(self.scopeNo) 
        return newScope


