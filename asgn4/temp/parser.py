#!/usr/bin/python
import ply.lex as lex
import sys
import ply.yacc as yacc
from lexer import tokens
import SymbolTable
import ThreeAddressCode
import logging
import sys
from copy import deepcopy
nonterminals=[]
output=[]
countg = 0
revoutput=[]
finalout=[]

stackend = []
stackbegin =[]

##
## Call this whenever array is on right hand side of =
##
def ResolveRHSArray(d):
    if( 'isArrayAccess' in d.keys() and d['isArrayAccess']):
        dst1 = ST.getTemp()
        TAC.emit(dst1,d['place']+"["+d['index_place']+"]", '','=')
        d['place'] =dst1
        d['isArrayAccess'] =False
        del d['index_place']
    return d



def p_CompilationUnit(p):
    '''CompilationUnit : ProgramFile
    '''


def p_ProgramFile(p):
    ''' ProgramFile : Importstatements TypeDeclarationOptSemi
                | Importstatements
                | TypeDeclarationOptSemi
    '''


def p_Importstatements(p):
    '''Importstatements : Importstatement
                    | Importstatements Importstatement
    '''

def p_Importstatement(p):
    '''Importstatement : KEYIMPORT QualifiedName Semicolons
                    | KEYIMPORT QualifiedName SEPDOT OPMULTIPLY Semicolons
    '''


def p_QualifiedName(p):
    '''QualifiedName : Identifier
                | QualifiedName SEPDOT Identifier
    '''
    if(len(p)==2):
        p[0] = {
            'idVal' : p[1],
            'isnotjustname' : False
        }
    else:
        p[0]={
            'idVal' : p[1]['idVal']+"."+p[3]
        }


def p_Semicolons(p):
    '''Semicolons : SEPSEMICOLON
                | Semicolons SEPSEMICOLON
    '''

def p_TypeSpecifier(p):
    '''TypeSpecifier : TypeName
            | TypeName Dims
    '''
    if(len(p)==2):
        p[0]={
            'type': p[1].upper()
            }
        return
    else:
        p[0]={
            'type' : p[1].upper(),
            'dim'  : p[2]
            }


#don't know what is Dims
def p_TypeName(p):
    '''TypeName : PrimitiveType
            | QualifiedName
    '''
    p[0]=p[1]['idVal']

def p_PrimitiveType(p):
    '''PrimitiveType : KEYBOOLEAN
                | KEYCHAR
                | KEYDOUBLE
                | KEYBYTE
                | KEYSHORT
                | KEYINT
                | KEYLONG
                | KEYVOID
                | KEYFLOAT
                | KEYSTRING
    '''
    #it is idenname because in the case of struct, we are passing the type as iden name through qualified type
    p[0]={
            'idVal' :p[1]
        }

def p_ClassNameList(p):
    '''ClassNameList : QualifiedName
                 | ClassNameList SEPCOMMA QualifiedName
    '''


def p_TypeDeclarationOptSemi(p):
    '''TypeDeclarationOptSemi : TypeDeclaration
                    | TypeDeclaration Semicolons
    '''

def p_TypeDeclaration(p):
    '''TypeDeclaration : ClassHeader SEPLEFTPARAN FieldDeclarations SEPRIGHTPARAN
                    | ClassHeader SEPLEFTPARAN SEPRIGHTPARAN
    '''

def p_ClassHeader(p):
    '''ClassHeader : Modifiers ClassWord Identifier
                | ClassWord Identifier
    '''

def p_ClassWord(p):
    '''ClassWord : KEYCLASS'''

def p_FieldDeclarations(p):
    '''FieldDeclarations : FieldDeclarationOptSemi
                    | FieldDeclarations FieldDeclarationOptSemi
    '''

def p_FieldDeclarationOptSemi(p):
    '''FieldDeclarationOptSemi : FieldDeclaration
                               | FieldDeclaration Semicolons
    '''

def p_FieldDeclaration(p):
    '''FieldDeclaration : FieldVariableDeclaration SEPSEMICOLON
                        | MethodDeclaration
                        | ConstructorDeclaration
                        | StaticInitializer
                        | NonStaticInitializer
                        | TypeDeclaration
    '''

def p_FieldVariableDeclaration(p):
    '''FieldVariableDeclaration : Modifiers TypeSpecifier VariableDeclarators
                                | TypeSpecifier VariableDeclarators
    '''
    if(len(p)==3):
        for i in p[2]:
            if(p[1]['type']=='SCANNER'):
                p[1]['type']='INT'
            ST.variableAdd(i, i, p[1]['type'])
    else:
        TAC.error("We are not supporting Modifiers to Primitive Datatypes")

def p_VariableDeclarators(p):
    '''VariableDeclarators : VariableDeclarator
                            | VariableDeclarators SEPCOMMA VariableDeclarator
    '''
    if(len(p)==2):
        p[0]=p[1]
        return
    p[0]=p[1]+p[3]


def p_VariableDeclarator(p):
    ''' VariableDeclarator : DeclaratorName
                            | DeclaratorName OPEQUAL VariableInitializer
    '''
    if(len(p)==2):
        p[0]=p[1]
        return

    if(type(p[3])!=type({})):
        return
    if( 'isarray' in p[3].keys() and p[3]['isarray']):
        TAC.emit('declare',p[1][0],p[3]['place'],p[3]['type'])
        p[0]=p[1]
    else:
        TAC.emit(p[1][0],p[3]['place'],'',p[2])
        p[0] = p[1]


def p_VariableInitializer(p):
    '''VariableInitializer : Expression
                            | SEPLEFTPARAN SEPRIGHTPARAN
                            | SEPLEFTPARAN ArrayInitializers SEPRIGHTPARAN
    '''
    if(len(p)==2):
        p[0]=p[1]
        return


def p_ArrayInitializers(p):
    '''ArrayInitializers : VariableInitializer
                            | ArrayInitializers SEPCOMMA VariableInitializer
                            | ArrayInitializers SEPCOMMA
    '''


def p_MethodDeclaration(p):
    '''MethodDeclaration : Modifiers TypeSpecifier MethodDeclarator MethodBody FMark2
                        | Modifiers TypeSpecifier MethodDeclarator Throws MethodBody FMark3
                        | TypeSpecifier MethodDeclarator Throws MethodBody FMark3
                        | TypeSpecifier MethodDeclarator MethodBody FMark2
    '''


def p_FMark2(p):
    '''FMark2 : '''
    TAC.emit('ret','','','')
    TAC.emit('label',p[-2][0],'','')

def p_FMark3(p):
    '''FMark3 : '''
    TAC.emit('ret','','','')
    TAC.emit('label',p[-3][0],'','')

def p_Throws(p):
    '''Throws : KEYTHROWS ClassNameList
    '''

def p_MethodDeclarator(p):
    '''MethodDeclarator : DeclaratorName SEPLEFTBRACE ParameterList SEPRIGHTBRACE
                    | DeclaratorName SEPLEFTBRACE SEPRIGHTBRACE
                    | MethodDeclarator OP_DIM
    '''
    if(len(p)>3):
        l1 = TAC.newLabel()
        TAC.emit('func','','','')
        p[0]=[l1]
        stackbegin.append(p[1])
        stackend.append(l1)
        TAC.emit('label',p[1][0],'','')


def p_ParameterList(p):
    '''ParameterList : Parameter
                    | ParameterList SEPCOMMA Parameter
    '''

def p_Parameter(p):
    '''Parameter : TypeSpecifier DeclaratorName
       '''

def p_DeclaratorName(p):
    '''DeclaratorName : Identifier
                    | DeclaratorName OP_DIM
    '''
    if(len(p)==2):
        p[0]=[p[1]]
        return
# def p_Throws(p):
#     '''Throws : THROWS ClassNameList'''

def p_MethodBody(p):
    '''MethodBody : Block
                | SEPSEMICOLON
    '''

def p_ConstructorDeclaration(p):
    '''ConstructorDeclaration : Modifiers ConstructorDeclarator Block
                        | ConstructorDeclarator Block
    '''

def p_ConstructorDeclarator(p):
    '''ConstructorDeclarator : Identifier SEPLEFTBRACE ParameterList SEPRIGHTBRACE
                            | Identifier SEPLEFTBRACE SEPRIGHTBRACE
    '''


def p_StaticInitializer(p):
    '''StaticInitializer : KEYSTATIC Block
    '''


def p_NonStaticInitializer(p):
    '''NonStaticInitializer : Block
    '''




##############################################################################################3
def p_Modifiers(p):
    '''Modifiers : Modifier
                | Modifiers Modifier
    '''

def p_Modifier(p):
    '''Modifier : KEYPUBLIC
                | KEYPROTECTED
                | KEYPRIVATE
                | KEYSTATIC
                | KEYFINAL
    '''

def p_Block(p):
    '''Block : SEPLEFTPARAN BMark1 LocalVariableDeclarationsAndStatements BMark2 SEPRIGHTPARAN
            | SEPLEFTPARAN SEPRIGHTPARAN
    '''
def p_BMark1(p):
    '''BMark1 : '''
    ST.newScope()

def p_BMark2(p):
    '''BMark2 : '''
    ST.endScope()

def p_LocalVariableDeclarationsAndStatements(p):
    '''LocalVariableDeclarationsAndStatements : LocalVariableDeclarationOrStatement
                        | LocalVariableDeclarationsAndStatements LocalVariableDeclarationOrStatement
    '''
    if(len(p)==2):
        p[0] = p[1]
        return
def p_LocalVariableDeclarationOrStatement(p):
    '''LocalVariableDeclarationOrStatement : LocalVariableDeclarationStatement
                                | Statement
    '''
    if(len(p)==2):
        p[0] = p[1]
        return

def p_LocalVariableDeclarationStatement(p):
    '''LocalVariableDeclarationStatement : TypeSpecifier VariableDeclarators  SEPSEMICOLON
    '''
    #Since VariableDecalrators is a list of variable
    # paramlen = len(VariableDeclarators)
    # print(p[2])
    for i in p[2]:
        if(p[1]['type']=='SCANNER'):
            p[1]['type']='INT'
        ST.variableAdd(i, i, p[1]['type'])


def p_Statement(p):
    '''Statement : EmptyStatement
                | ExpressionStatement SEPSEMICOLON
                | LabelStatement
                | SelectionStatement
                | IterationStatement
                | JumpStatement
                | GuardingStatement
                | Block
    '''

def p_EmptyStatement(p):
    ''' EmptyStatement : SEPSEMICOLON
    '''

def p_LabelStatement(p):
    ''' LabelStatement : Identifier SEPCOLON
                | KEYCASE ConstantExpression SEPCOLON
                | KEYDEFAULT SEPCOLON
    '''

def p_ExpressionStatement(p):
    '''ExpressionStatement : Expression
    '''
    p[0] = p[1]

# IF else ........................
precedence = (
    ('right', 'THAN', 'KEYELSE'),
)

def p_SelectionStatement(p):
    '''SelectionStatement : KEYIF SEPLEFTBRACE Expression SEPRIGHTBRACE IfMark1 Statement IfMark2 %prec THAN
                        | KEYIF SEPLEFTBRACE Expression SEPRIGHTBRACE IfMark1 Statement KEYELSE IfMark4 Statement IfMark5
    '''
def p_IfMark1(p):
    '''IfMark1 : '''
    l1 = TAC.newLabel()
    l2 = TAC.newLabel()
    # need to handle p[-2].place big work..
    TAC.emit('ifgoto',p[-2]['place'],'eq 0', l2)
    TAC.emit('goto',l1, '', '')
    TAC.emit('label',l1, '', '')
    ST.newScope()
    p[0]=[l1,l2]

def p_IfMark2(p):
    '''IfMark2 : '''
    ST.endScope()
    TAC.emit('label',p[-2][1], '', '')


def p_IfMark4(p):
    '''IfMark4 : '''
    l3 = TAC.newLabel()
    TAC.emit('goto',l3,'','')
    TAC.emit('label',p[-3][1],'','')
    p[0]=[l3]

def p_IfMark5(p):
    '''IfMark5 : '''
    ST.endScope()
    TAC.emit('label',p[-2][0],'','')


# IF else end here .................


# Iteration statements start here ..................
def p_IterationStatement(p):
    '''IterationStatement : KEYWHILE WhMark1 SEPLEFTBRACE Expression SEPRIGHTBRACE WhMark2 Statement WhMark3
                        | KEYFOR FoMark0 SEPLEFTBRACE ForInt FoMark1 ForExpr ForIncr SEPRIGHTBRACE FoMark2 Statement FoMark3
                        | KEYFOR FoMark0 SEPLEFTBRACE ForInt FoMark1 ForExpr SEPRIGHTBRACE FoMark4 Statement FoMark5
    '''
def p_WhMark1(p):
    '''WhMark1 : '''
    l1 = TAC.newLabel()
    l2 = TAC.newLabel()
    l3 = TAC.newLabel()
    stackbegin.append(l1)
    stackend.append(l3)
    ST.newScope()
    TAC.emit('label',l1,'','')
    p[0]=[l1,l2,l3]

def p_WhMark2(p):
    '''WhMark2 : '''
    TAC.emit('ifgoto',p[-2]['place'],'eq 0', p[-4][2])
    TAC.emit('goto',p[-4][1],'','')
    TAC.emit('label',p[-4][1],'','')

def p_WhMark3(p):
    '''WhMark3 : '''
    TAC.emit('goto',p[-6][0],'','')
    TAC.emit('label',p[-6][2],'','')
    ST.newScope()
    stackbegin.pop()
    stackend.pop()

def p_FoMark0(p):
    '''FoMark0 : '''
    ST.newScope()

def p_FoMark1(p):
    '''FoMark1 : '''
    l1 = TAC.newLabel()
    l2 = TAC.newLabel()
    l3 = TAC.newLabel()
    stackbegin.append(l1)
    stackend.append(l3)
    TAC.emit('label',l1,'','')
    p[0]=[l1,l2,l3]

def p_FoMark2(p):
    '''FoMark2 : '''
    TAC.emit('ifgoto',p[-3]['place'],'eq 0', p[-4][2])
    TAC.emit('goto',p[-4][1],'','')
    TAC.emit('label',p[-4][1],'','')

def p_FoMark4(p):
    '''FoMark4 : '''
    TAC.emit('ifgoto',p[-2]['place'],'eq 0', p[-3][2])
    TAC.emit('goto',p[-3][1],'','')
    TAC.emit('label',p[-3][1],'','')

def p_FoMark3(p):
    '''FoMark3 : '''
    TAC.emit('goto',p[-6][0],'','')
    TAC.emit('label',p[-6][2],'','')
    ST.endScope()
    stackbegin.pop()
    stackend.pop()

def p_FoMark5(p):
    '''FoMark5 : '''
    TAC.emit('goto',p[-5][0],'','')
    TAC.emit('label',p[-5][2],'','')
    ST.endScope()
    stackbegin.pop()
    stackend.pop()

def p_ForInt(p):
    '''ForInt : ExpressionStatements SEPSEMICOLON
            | LocalVariableDeclarationStatement
            | SEPSEMICOLON
    '''

def p_ForExpr(p):
    '''ForExpr : Expression SEPSEMICOLON
            | SEPSEMICOLON
    '''
    if(len(p)>2):
        p[0]=p[1]
        return
    else:
        newPlace =ST.getTemp()
        TAC.emit(newPlace,'1','','=')
        p[0] = {
            'place' : newPlace,
            'type' : 'INT'
        }

def p_ForIncr(p):
    '''ForIncr : ExpressionStatements
    '''


# Iteration Statements end here......


def p_ExpressionStatements(p):
    '''ExpressionStatements : ExpressionStatement
                    | ExpressionStatements SEPCOMMA ExpressionStatement
    '''

def p_JumpStatement(p):
    '''JumpStatement : KEYBREAK Identifier SEPSEMICOLON
                | KEYBREAK SEPSEMICOLON
                | KEYCONTINUE Identifier SEPSEMICOLON
                | KEYCONTINUE SEPSEMICOLON
                | KEYRETURN Expression SEPSEMICOLON
                | KEYRETURN  SEPSEMICOLON
                | KEYTHROW Expression SEPSEMICOLON
    '''
    if(len(p)==3 and p[1]=='break'):
        TAC.emit('goto',stackend[-1],'','')
        return
    if(len(p)==3 and p[1]=='continue'):
        TAC.emit('goto',stackbegin[-1],'','')
        return
    if(len(p)==3 and p[1]=='return'):
        TAC.emit('ret','','','')
        return


def p_GuardingStatement(p):
    '''GuardingStatement : KEYTRY Block Finally
                        | KEYTRY Block Catches
                        | KEYTRY Block Catches Finally
    '''

def p_Catches(p):
    '''Catches : Catch
            | Catches Catch
    '''

def p_Catch(p):
    '''Catch : CatchHeader Block
    '''

def p_CatchHeader(p):
    '''CatchHeader : KEYCATCH SEPLEFTBRACE TypeSpecifier Identifier SEPRIGHTBRACE
                | KEYCATCH SEPLEFTBRACE TypeSpecifier SEPRIGHTBRACE
    '''

def p_Finally(p):
    '''Finally : KEYFINALLY Block
    '''

def p_PrimaryExpression(p):
    '''PrimaryExpression : QualifiedName
                    | NotJustName
    '''
    p[0] = {
        'place' : 'undefined',
        'type' : 'TYPE_ERROR'
    }
    if(p[1]['isnotjustname']==False):
        if ST.variableSearch(p[1]['idVal']) :
            p[0]['place'] = ST.getAttr(p[1]['idVal'],'place')
            p[0]['type'] = ST.getAttr(p[1]['idVal'],'type')
        else:
            TAC.error('Error : undefined variable '+p[1]['idVal']+' is used.')
    else:
        p[0]=p[1]['val']



def p_NotJustName(p):
    '''NotJustName : SpecialName
                | NewAllocationExpression
                | ComplexPrimary
    '''
    p[0]={
        'isnotjustname' : True,
        'val' : p[1],
    }
    # print(p[0])
    # p[1]
    #
def p_ComplexPrimary(p):
    '''ComplexPrimary : SEPLEFTBRACE Expression SEPRIGHTBRACE
            | ComplexPrimaryNoParenthesis
    '''
    if(len(p)>2):
        p[0]=p[2]
        return
    p[0]=p[1]

def p_ComplexPrimaryNoParenthesis(p):
    '''ComplexPrimaryNoParenthesis : BooleanLiteral
                            | IntLiteral
                            | FlLiteral
                            | ChLiteral
                            | StLiteral
                            | ArrayAccess
                            | FieldAccess
                            | MethodCall
    '''
    p[0]=p[1]

def p_IntLiteral(p):
    '''IntLiteral : IntegerLiteral
    '''
    p[0] = {
        'type' : 'INT',
        'place' : p[1]
    }
def p_FlLiteral(p):
    '''FlLiteral : FloatingLiteral
    '''
    p[0] = {
        'type' : 'FLOAT',
        'place' : p[1]
    }
def p_ChLiteral(p):
    '''ChLiteral : CharacterLiteral
    '''
    p[0] = {
        'type' : 'CHAR',
        'place' : p[1]
    }
def p_StLiteral(p):
    '''StLiteral : StringLiteral
    '''
    p[0] = {
        'type' : 'STRING',
        'place' : p[1]
    }

def p_ArrayAccess(p):
    '''ArrayAccess : QualifiedName SEPLEFTSQBR Expression SEPRIGHTSQBR
                | ComplexPrimary SEPLEFTSQBR Expression SEPRIGHTSQBR
    '''
    p[0]= p[1]
    p[0]['isArrayAccess'] = True;
    p[0]['type'] = ST.getAttr(p[0]['idVal'],'type')
    p[0]['place'] = ST.getAttr(p[0]['idVal'],'place')
    p[0]['index_place'] = p[3]['place']
    del p[0]['idVal']

def p_FieldAcess(p):
    '''FieldAccess : NotJustName SEPDOT Identifier
            | RealPostfixExpression SEPDOT Identifier
            | QualifiedName SEPDOT KEYTHIS
            | QualifiedName SEPDOT KEYCLASS
            | PrimitiveType SEPDOT KEYCLASS
    '''

def p_MethodCall(p):
    ''' MethodCall : MethodAccess SEPLEFTBRACE ArgumentList SEPRIGHTBRACE
            | MethodAccess SEPLEFTBRACE SEPRIGHTBRACE
    '''
    x = p[1]['idVal'].split('.')
    if(p[1]['idVal']=='System.out.println'):
        TAC.emit('print',p[3]['place'],'','')
        p[0]=p[1]
    elif(x[len(x)-1]=='nextInt'):
        p[0]=p[1]
        p[0]['input'] = 'True'
    else:
        TAC.emit('call',p[1]['idVal'],'','')
        p[0]=p[1]



def p_MethodAccess(p):
    ''' MethodAccess : ComplexPrimaryNoParenthesis
                | SpecialName
                | QualifiedName
    '''
    p[0]=p[1]

def p_SpecialName(p):
    '''SpecialName : KEYTHIS
    '''

def p_ArgumentList(p):
    '''ArgumentList : Expression
            | ArgumentList SEPCOMMA Expression
    '''
    if(len(p)==2):
        p[0] = p[1]
        return

def p_NewAllocationExpression(p):
    '''NewAllocationExpression : PlainNewAllocationExpression
                    | QualifiedName SEPDOT PlainNewAllocationExpression
    '''
    if(len(p)==2):
        p[0]=p[1]
        return
    p[0]=p[3]

def p_PlainNewAllocationExpression(p):
    '''PlainNewAllocationExpression :  ArrayAllocationExpression
                        | ClassAllocationExpression
                        | ArrayAllocationExpression SEPLEFTPARAN SEPRIGHTPARAN
                        | ClassAllocationExpression SEPLEFTPARAN SEPRIGHTPARAN
                        | ArrayAllocationExpression SEPLEFTPARAN ArrayInitializers SEPRIGHTPARAN
                        | ClassAllocationExpression SEPLEFTPARAN FieldDeclarations SEPRIGHTPARAN
    '''
    if(len(p)==2):
        p[0]=p[1]
    p[0]=p[1]

def p_ClassAllocationExpression(p):
    '''ClassAllocationExpression : KEYNEW TypeName SEPLEFTBRACE ArgumentList SEPRIGHTBRACE
                        | KEYNEW TypeName SEPLEFTBRACE SEPRIGHTBRACE
    '''
    p[0]=p[2]

def p_ArrayAllocationExpression(p):
    '''ArrayAllocationExpression : KEYNEW TypeName DimExprs Dims
                            | KEYNEW TypeName DimExprs
                            | KEYNEW TypeName Dims
    '''
    #Doing just 2nd rule i.e 1D array
    if(len(p)==4):
        # TAC.emit('declare',p[2],p[3][1:-1])
        p[0]={
            'type' : p[2].upper(),
            'place'  : p[3]['place'],
            'isarray' : True
        }
        # print p[0]['len']


def p_DimExprs(p):
    '''DimExprs : DimExpr
                | DimExprs DimExpr
    '''
    if(len(p)==2):
        p[0]=p[1]
        return

def p_DimExpr(p):
    '''DimExpr : SEPLEFTSQBR Expression SEPRIGHTSQBR
    '''
    if(p[2]['type']=='INT'):
        p[0]=p[2]
    else:
        TAC.error("Error : Array declaration needs an integer size = "+p[2]['place'])

def p_Dims(p):
    '''Dims : OP_DIM
            | Dims OP_DIM
    '''
    if(len(p)==2):
        p[0]=1
        return
    else:
        p[0]=1+p[1]
        return

def p_PostfixExpression(p):
    '''PostfixExpression : PrimaryExpression
                    | RealPostfixExpression
    '''
    p[0] = p[1]

def p_RealPostfixExpression(p):
    '''RealPostfixExpression : PostfixExpression OPINCREMENT
                    | PostfixExpression OPDECREMENT
    '''
    if(p[1]['type']=='INT'):
        if(p[2][0]=='+'):
            TAC.emit(p[1]['place'],p[1]['place'],'1','+')
        else:
            TAC.emit(p[1]['place'],p[1]['place'],'1','-')
        p[0] = {
            'place' : p[1]['place'],
            'type' : 'INT'
        }
    else:
        TAC.error("Error: increment operator can be used only with integer")

def p_UnaryExpression(p):
    '''UnaryExpression : OPINCREMENT UnaryExpression
                | OPDECREMENT UnaryExpression
                | ArithmeticUnaryOperator CastExpression
                | LogicalUnaryExpression
    '''
    if(len(p)==2):
        p[0] = p[1]
        return


def p_LogicalUnaryExpression(p):
    '''LogicalUnaryExpression : PostfixExpression
                        | LogicalUnaryOperator UnaryExpression
    '''
    if(len(p)==2):
        p[0] = p[1]
        return

def p_LogicalUnaryOperator(p):
    '''LogicalUnaryOperator : OPTILDE
                         | OPNOT
    '''
    p[0] = p[1]

def p_ArithmeticUnaryOperator(p):
    '''ArithmeticUnaryOperator : OPPLUS
                            | OPMINUS
    '''
    p[0] = p[1]

def p_CastExpression(p) :
    ''' CastExpression : UnaryExpression
                | SEPLEFTBRACE PrimitiveTypeExpression SEPRIGHTBRACE CastExpression
                | SEPLEFTBRACE ClassTypeExpression SEPRIGHTBRACE CastExpression
                | SEPLEFTBRACE Expression SEPRIGHTBRACE LogicalUnaryExpression
    '''
    if(len(p)==2):
        p[0] = p[1]
        return


def p_PrimitiveTypeExpression(p):
    '''PrimitiveTypeExpression : PrimitiveType
                    | PrimitiveType Dims
    '''

def p_ClassTypeExpression(p):
    '''ClassTypeExpression : QualifiedName Dims
    '''

def p_MultiplicativeExpression(p):
    '''MultiplicativeExpression : CastExpression
                    | MultiplicativeExpression OPMULTIPLY CastExpression
                    | MultiplicativeExpression OPDIVIDE CastExpression
                    | MultiplicativeExpression OPMOD CastExpression
    '''
    if(len(p)==2):
        p[0] = p[1]
        return
    newPlace = ST.getTemp()
    p[0] = {
        'place' : newPlace,
        'type' : 'TYPE_ERROR'
    }
    if p[1]['type']=='TYPE_ERROR' or p[3]['type']=='TYPE_ERROR':
        return
    if p[2] == '*':
        if p[1]['type'] == 'INT' and p[3]['type'] == 'INT' :
            p[3] =ResolveRHSArray(p[3])
            p[1] =ResolveRHSArray(p[1])
            TAC.emit(newPlace,p[1]['place'],p[3]['place'],p[2])
            p[0]['type'] = 'INT'
        else:
            TAC.error('Error: Type is not compatible'+p[1]['place']+','+p[3]['place']+'.')
    elif p[2] == '/' :
        if p[1]['type'] == 'INT' and p[3]['type'] == 'INT' :
            p[3] =ResolveRHSArray(p[3])
            p[1] =ResolveRHSArray(p[1])
            TAC.emit(newPlace,p[1]['place'],p[3]['place'],p[2])
            p[0]['type'] = 'INT'
        else:
            TAC.error('Error: Type is not compatible'+p[1]['place']+','+p[3]['place']+'.')
    elif p[2] == '%':
        if p[1]['type'] == 'INT' and p[3]['type'] == 'INT' :
            p[3] =ResolveRHSArray(p[3])
            p[1] =ResolveRHSArray(p[1])
            TAC.emit(newPlace,p[1]['place'],p[3]['place'],p[2])
            p[0]['type'] = 'INT'
        else:
            TAC.error('Error: Type is not compatible'+p[1]['place']+','+p[3]['place']+'.')

def p_AdditiveExpression(p):
    '''AdditiveExpression : MultiplicativeExpression
                        | AdditiveExpression OPPLUS MultiplicativeExpression
                        | AdditiveExpression OPMINUS MultiplicativeExpression
    '''
    if(len(p)==2):
        p[0] = p[1]
        return
    newPlace = ST.getTemp()
    p[0] = {
        'place' : newPlace,
        'type' : 'TYPE_ERROR'
    }
    if p[1]['type']=='TYPE_ERROR' or p[3]['type']=='TYPE_ERROR':
        return
    if p[1]['type'] == 'INT' and p[3]['type'] == 'INT' :
        p[3] =ResolveRHSArray(p[3])
        p[1] =ResolveRHSArray(p[1])
        TAC.emit(newPlace,p[1]['place'],p[3]['place'],p[2])
        p[0]['type'] = 'INT'
    else:
        TAC.error("Error: integer value is needed")


def p_ShiftExpression(p):
    '''ShiftExpression : AdditiveExpression
                    | ShiftExpression OPLEFTSHIFT AdditiveExpression
                    | ShiftExpression OPRIGHTSHIFT AdditiveExpression
                    | ShiftExpression OPLOGICALSHIFT AdditiveExpression
    '''
    if(len(p)==2):
        p[0] = p[1]
        return

def p_RelationalExpression(p):
    '''RelationalExpression : ShiftExpression
                        | RelationalExpression OPLESSER ShiftExpression
                        | RelationalExpression OPGREATER ShiftExpression
                        | RelationalExpression OPLESSEQ ShiftExpression
                        | RelationalExpression OPGREATEQ ShiftExpression
                        | RelationalExpression OPINSTANCEOF TypeSpecifier
    '''
    if(len(p)==2):
        p[0] = p[1]
        return
    l1 = TAC.newLabel()
    l2 = TAC.newLabel()
    l3 = TAC.newLabel()
    newPlace = ST.getTemp()
    p[0]={
        'place' : newPlace,
        'type' : 'TYPE_ERROR'
    }
    if p[1]['type']=='TYPE_ERROR' or p[3]['type']=='TYPE_ERROR':
        return
    if p[1]['type'] == 'INT' and p[3]['type'] == 'INT' :
        if(p[2]=='>'):
            p[3] =ResolveRHSArray(p[3])
            p[1] =ResolveRHSArray(p[1])
            TAC.emit('ifgoto',p[1]['place'],'g '+p[3]['place'],l2)
            TAC.emit('goto',l1,'','')
            TAC.emit('label',l1,'','')
            TAC.emit(newPlace,'0','','=')
            TAC.emit('goto',l3,'','')
            TAC.emit('label',l2,'','')
            TAC.emit(newPlace,'1','','=')
            TAC.emit('label',l3,'','')
            p[0]['type'] = 'INT'
        elif(p[2]=='>='):
            p[3] =ResolveRHSArray(p[3])
            p[1] =ResolveRHSArray(p[1])
            TAC.emit('ifgoto',p[1]['place'],'ge '+p[3]['place'],l2)
            TAC.emit('goto',l1,'','')
            TAC.emit('label',l1,'','')
            TAC.emit(newPlace,'0','','=')
            TAC.emit('goto',l3,'','')
            TAC.emit('label',l2,'','')
            TAC.emit(newPlace,'1','','=')
            TAC.emit('label',l3,'','')
            p[0]['type'] = 'INT'
        elif(p[2]=='<'):
            p[3] =ResolveRHSArray(p[3])
            p[1] =ResolveRHSArray(p[1])
            TAC.emit('ifgoto',p[1]['place'],'l '+p[3]['place'],l2)
            TAC.emit('goto',l1,'','')
            TAC.emit('label',l1,'','')
            TAC.emit(newPlace,'0','','=')
            TAC.emit('goto',l3,'','')
            TAC.emit('label',l2,'','')
            TAC.emit(newPlace,'1','','=')
            TAC.emit('label',l3,'','')
            p[0]['type'] = 'INT'
        elif(p[2]=='<='):
            p[3] =ResolveRHSArray(p[3])
            p[1] =ResolveRHSArray(p[1])
            TAC.emit('ifgoto',p[1]['place'],'le '+p[3]['place'],l2)
            TAC.emit('goto',l1,'','')
            TAC.emit('label',l1,'','')
            TAC.emit(newPlace,'0','','=')
            TAC.emit('goto',l3,'','')
            TAC.emit('label',l2,'','')
            TAC.emit(newPlace,'1','','=')
            TAC.emit('label',l3,'','')
            p[0]['type'] = 'INT'
    else:
        TAC.error('Error: Type is not compatible'+p[1]['place']+','+p[3]['place']+'.')

def p_EqualityExpression(p):
    '''EqualityExpression : RelationalExpression
                        | EqualityExpression OPCHECKEQ RelationalExpression
                        | EqualityExpression OPNOTEQ RelationalExpression
    '''
    if(len(p)==2):
        p[0] = p[1]
        return
    l1 = TAC.newLabel()
    l2 = TAC.newLabel()
    l3 = TAC.newLabel()
    newPlace = ST.getTemp()
    p[0]={
        'place' : newPlace,
        'type' : 'TYPE_ERROR'
    }
    if p[1]['type']=='TYPE_ERROR' or p[3]['type']=='TYPE_ERROR':
        return
    if p[1]['type'] == 'INT' and p[3]['type'] == 'INT' :
        if(p[2][0]=='='):
            p[3] =ResolveRHSArray(p[3])
            p[1] =ResolveRHSArray(p[1])
            TAC.emit('ifgoto',p[1]['place'],'eq '+p[3]['place'],l2)
            TAC.emit('goto',l1,'','')
            TAC.emit('label',l1,'','')
            TAC.emit(newPlace,'0','','=')
            TAC.emit('goto',l3,'','')
            TAC.emit('label',l2,'','')
            TAC.emit(newPlace,'1','','=')
            TAC.emit('label',l3,'','')
            p[0]['type'] = 'INT'
        else:
            p[3] =ResolveRHSArray(p[3])
            p[1] =ResolveRHSArray(p[1])
            TAC.emit('ifgoto',p[1]['place'],'eq '+p[3]['place'],l2)
            TAC.emit('goto',l1,'','')
            TAC.emit('label',l1,'','')
            TAC.emit(newPlace,'1','','=')
            TAC.emit('goto',l3,'','')
            TAC.emit('label',l2,'','')
            TAC.emit(newPlace,'0','','=')
            TAC.emit('label',l3,'','')
            p[0]['type'] = 'INT'
    else:
        TAC.error('Error: Type is not compatible'+p[1]['place']+','+p[3]['place']+'.')
def p_AndExpression(p):
    '''AndExpression : EqualityExpression
                    | AndExpression OPBINAND EqualityExpression
    '''
    if(len(p)==2):
        p[0] = p[1]
        return
    newPlace = ST.getTemp()
    p[0] = {
        'place' : newPlace,
        'type' : 'TYPE_ERROR'
    }
    if p[1]['type']=='TYPE_ERROR' or p[3]['type']=='TYPE_ERROR':
        return
    if p[1]['type'] == 'INT' and p[3]['type'] == 'INT' :
        p[3] =ResolveRHSArray(p[3])
        p[1] =ResolveRHSArray(p[1])
        TAC.emit(newPlace,p[1]['place'],p[3]['place'],'and')
        p[0]['type'] = 'INT'
    else:
        TAC.error('Error: Type is not compatible'+p[1]['place']+','+p[3]['place']+'.')

def p_ExclusiveOrExpression(p):
    '''ExclusiveOrExpression : AndExpression
                    | ExclusiveOrExpression OPXOR AndExpression
    '''
    if(len(p)==2):
        p[0] = p[1]
        return
    newPlace = ST.getTemp()
    p[0] = {
        'place' : newPlace,
        'type' : 'TYPE_ERROR'
    }
    if p[1]['type']=='TYPE_ERROR' or p[3]['type']=='TYPE_ERROR':
        return
    if p[1]['type'] == 'INT' and p[3]['type'] == 'INT' :
        p[3] =ResolveRHSArray(p[3])
        p[1] =ResolveRHSArray(p[1])
        TAC.emit(newPlace,p[1]['place'],p[3]['place'],'xor')
        p[0]['type'] = 'INT'
    else:
        TAC.error('Error: Type is not compatible'+p[1]['place']+','+p[3]['place']+'.')

def p_InclusiveOrExpression(p):
    '''InclusiveOrExpression : ExclusiveOrExpression
                        | InclusiveOrExpression OPBINOR ExclusiveOrExpression
    '''
    if(len(p)==2):
        p[0] = p[1]
        return
    newPlace = ST.getTemp()
    p[0] = {
        'place' : newPlace,
        'type' : 'TYPE_ERROR'
    }
    if p[1]['type']=='TYPE_ERROR' or p[3]['type']=='TYPE_ERROR':
        return
    if p[1]['type'] == 'INT' and p[3]['type'] == 'INT' :
        p[3] =ResolveRHSArray(p[3])
        p[1] =ResolveRHSArray(p[1])
        TAC.emit(newPlace,p[1]['place'],p[3]['place'],'or')
        p[0]['type'] = 'INT'
    else:
        TAC.error('Error: Type is not compatible'+p[1]['place']+','+p[3]['place']+'.')

def p_ConditionalAndExpression(p):
    '''ConditionalAndExpression : InclusiveOrExpression
                            | ConditionalAndExpression OPAND InclusiveOrExpression
    '''
    if(len(p)==2):
        p[0] = p[1]
        return
    newPlace = ST.getTemp()
    p[0] = {
        'place' : newPlace,
        'type' : 'TYPE_ERROR'
    }
    if p[1]['type']=='TYPE_ERROR' or p[3]['type']=='TYPE_ERROR':
        p[0]=p[1]
        return
    if p[1]['type'] == 'INT' and p[3]['type'] == 'INT' :
        p[3] =ResolveRHSArray(p[3])
        p[1] =ResolveRHSArray(p[1])
        TAC.emit(newPlace,p[1]['place'],p[3]['place'],'and')
        p[0]['type'] = 'INT'
    else:
        TAC.error('Error: Type is not compatible'+p[1]['place']+','+p[3]['place']+'.')

def p_ConditionalOrExpression(p):
    '''ConditionalOrExpression : ConditionalAndExpression
                        | ConditionalOrExpression OPOR ConditionalAndExpression
    '''
    if(len(p)==2):
        p[0] = p[1]
        return
    newPlace = ST.getTemp()
    p[0] = {
        'place' : newPlace,
        'type' : 'TYPE_ERROR'
    }
    if p[1]['type']=='TYPE_ERROR' or p[3]['type']=='TYPE_ERROR':
        return
    if p[1]['type'] == 'INT' and p[3]['type'] == 'INT' :
        p[3] =ResolveRHSArray(p[3])
        p[1] =ResolveRHSArray(p[1])
        TAC.emit(newPlace,p[1]['place'],p[3]['place'],'or')
        p[0]['type'] = 'INT'
    else:
        TAC.error('Error: Type is not compatible'+p[1]['place']+','+p[3]['place']+'.')

def p_ConditionalExpression(p):
    ''' ConditionalExpression : ConditionalOrExpression
                        | ConditionalOrExpression OPTERNARY Expression SEPCOLON ConditionalExpression
    '''
    if(len(p)==2):
        p[0] = p[1]
        return

def p_AssignmentExpression(p):
    '''AssignmentExpression : ConditionalExpression
                        | UnaryExpression AssignmentOperator AssignmentExpression
    '''
    if(len(p)==2):
        p[0] = p[1]
        return

    if(p[3]=='Scanner'):
        p[0]=p[3]
        return

    if('input' in p[3].keys() and p[3]['input']):
        dst=p[1]['place']
        if( 'isArrayAccess' in p[1].keys() and p[1]['isArrayAccess']):
            dst=p[1]['place'] + "["+p[1]['index_place'] + "]"
        TAC.emit('input',dst,'','')
        p[0] = {}
        return

    if(type(p[3])!=type({})):
        p[0]=p[3]
        return
#    print(p[3])
    if('isarray' in p[3].keys() and p[3]['isarray'] and p[2]=='='):
        TAC.emit('declare',p[1]['place'],p[3]['place'],p[3]['type'])
        return

    newPlace = ST.getTemp()
    p[0] = {
        'place' : newPlace,
        'type' : 'TYPE_ERROR',
        'isarray': False
    }
    # print(p[3])
    if('input' in p[3].keys() and p[3]['input']):
        p[0] = p[3]
        return
    if p[1]['type']=='TYPE_ERROR' or p[3]['type']=='TYPE_ERROR':
        return
    if p[1]['type'] == 'INT' and p[3]['type'] == 'INT' :
        if(p[2][0]=='='):
            # if( 'isArrayAccess' in p[1].keys() and p[1]['isArrayAccess']):
            #     dst1 = ST.getTemp()
            #     TAC.emit(dst1,p[1]['place']+"["+p[1]['index_place']+"]", '','=')
            #     p[1]['place'] =dst1
            #     p[1]['isArrayAccess'] =False
            #     del p[1]['index_place']

            p[3] = ResolveRHSArray(p[3])

            dst = p[1]['place']
            if( 'isArrayAccess' in p[1].keys() and p[1]['isArrayAccess']):
                dst=p[1]['place'] + "["+p[1]['index_place'] + "]"
            TAC.emit(dst,p[3]['place'],'',p[2])
            p[0] = p[1]
            # print(p[0])
        else:
            p[3]=ResolveRHSArray(p[3])
            # print(p[1])
            new1=p[1].copy()
            new = ResolveRHSArray(p[1])
            p[1]=new1.copy()
            # print(p[1])
            dst = p[1]['place']
            if( 'isArrayAccess' in p[1].keys() and p[1]['isArrayAccess']):
                dst=p[1]['place'] + "["+p[1]['index_place'] + "]"
            TAC.emit(newPlace,new['place'],p[3]['place'],p[2][0])
            # print("lok here=====> " +dst)
            TAC.emit(dst,newPlace,'',p[2][1])
        p[0]['type'] = 'INT'
    else:
        TAC.error('Error: Type is not compatible'+p[1]['place']+','+p[3]['place']+'.')

def p_AssignmentOperator(p):
    ''' AssignmentOperator : OPEQUAL
                        | OPMULTIPLYEQ
                        | OPDIVIDEEQ
                        | OPMODEQ
                        | OPPLUSEQ
                        | OPMINUSEQ
                        | OPLEFTSHIFTEQ
                        | OPRIGHTSHIFTEQ
                        | OPLOGICALSHIFTEQ
                        | OPBINANDEQ
                        | OPXOREQ
                        | OPBINOREQ
    '''
    p[0] = p[1]

def p_Expression(p):
    '''Expression : AssignmentExpression
    '''
    p[0] = p[1]

def p_ConstantExpression(p):
    '''ConstantExpression : ConditionalExpression
    '''
    p[0] = p[1]

def p_error(p):
    if p == None:
        print str(sys.argv[1])+" ::You missed something at the end"
    else:
        print str(sys.argv[1])+" :: Syntax error in line no " +  str(p.lineno)




yacc.yacc()
ST = SymbolTable.SymbolTable()
TAC = ThreeAddressCode.ThreeAddressCode()

s = open(sys.argv[1],'r')
data = s.read()
data+= "\n"
s.close()

#Parse it!
yacc.parse(data)
# TAC.output()
TAC.output3AC()





