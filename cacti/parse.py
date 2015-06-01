from pyparsing import *

ParserElement.enablePackrat()

from functools import reduce
import cacti.runtime as rntm
import cacti.lang as lang
import cacti.builtin as bltn
import cacti.ast as ast

__all__ = ['parse_file', 'parse_string']

open_curl = Literal("{").suppress()
close_curl = Literal("}").suppress()
open_paren = Literal("(").suppress()
close_paren = Literal(")").suppress()

keyword_class = Keyword('class').suppress()
keyword_closure = Keyword('closure').suppress()
keyword_function = Keyword('function').suppress()
keyword_method = Keyword('method').suppress()
keyword_var = Keyword('var').suppress()
keyword_val = Keyword('val').suppress()
assignment_operator = Literal("=").suppress()
statement_end = (LineEnd().suppress() | Literal(";").suppress() | StringEnd().suppress() | FollowedBy(Literal('}')))

block = Forward()
closure = Forward()
function = Forward()
klass = Forward()
value = Forward()

identifier = Word('_' + alphas, bodyChars='_' + alphanums)

reference = identifier.copy()
def reference_action(s, loc, toks):
    return ast.ReferenceExpression(toks[0])
reference.setParseAction(reference_action)

integer = Word(nums).setResultsName('value')
def integer_action(s, loc, toks):
    return ast.ValueExpression(bltn.make_integer(int(toks.value)))
integer.setParseAction(integer_action)

string = QuotedString('"', escChar='\\').setResultsName('value')
def string_action(s, loc, toks):
    return ast.ValueExpression(bltn.make_string(str(toks.value)))
string.setParseAction(string_action)

call_operator = open_paren + Group(Optional(delimitedList(value))) + close_paren

property_operator = Literal('.').suppress() + identifier

def binary_operation_action(s, loc, toks):
    operation = toks[0][1]
    operands = toks[0][0::2]
    expr = reduce(lambda o1, o2: ast.OperationExpression(o1, operation, o2), operands)
    return expr

def call_property_operation_action(s, loc, toks):
    operands = toks[0]
    def list_reduction(a, b):
        if isinstance(b, str):
            return ast.PropertyExpression(a, b)
        else:
            return ast.OperationExpression(a, '()', *b)
    return reduce(list_reduction, operands)
    
operators = [
    ((property_operator ^ call_operator), 1, opAssoc.LEFT, call_property_operation_action),
    ("*", 2, opAssoc.LEFT, binary_operation_action),
    ("/", 2, opAssoc.LEFT, binary_operation_action),
    ("+", 2, opAssoc.LEFT, binary_operation_action),
    ("-", 2, opAssoc.LEFT, binary_operation_action)
]

operand = (reference | integer | string)

value <<= (infixNotation(operand, operators) ^ closure ^ function ^ klass)

value_statement = value + statement_end

### VAL

val_statement = keyword_val + identifier + assignment_operator + value + statement_end
def val_statement_action(s, loc, toks):
    return ast.ValDeclarationStatement(toks[0], toks[1])
val_statement.setParseAction(val_statement_action)

### VAR

def var_statement_action(s, loc, toks):
    symbol = toks[0]
    if len(toks) == 2:
        return ast.VarDeclarationStatement(symbol, toks[1])
    else:
        return ast.VarDeclarationStatement(symbol, ast.ReferenceExpression('nothing'))

var_assign = keyword_var + identifier + assignment_operator + value
var_no_assign = keyword_var + identifier

var_statement = (var_assign | var_no_assign) + statement_end
var_statement.setParseAction(var_statement_action)

### ASSIGNMENT

assignment_statement = identifier + assignment_operator + value + statement_end
def assignment_statement_action(s, loc, toks):
    return ast.AssignmentStatement(toks[0], toks[1])
assignment_statement.setParseAction(assignment_statement_action)

### CLOSURE

closure <<= keyword_closure + open_paren + Group(Optional(delimitedList(identifier))) + close_paren + open_curl + block + close_curl
def closure_action(s, loc, toks):
    return ast.ClosureDeclarationStatement(toks[1], *toks[0])
closure.setParseAction(closure_action)
closure_statement = closure + statement_end

### FUNCTION

function <<= keyword_function + \
                Optional(identifier, default=None) + \
                open_paren + Group(Optional(delimitedList(identifier))) + close_paren + \
                open_curl + block + close_curl
def function_action(s, loc, toks):
    return ast.FunctionDeclarationStatement(toks[0], toks[2], *toks[1])
function.setParseAction(function_action)
function_statement = function + statement_end

### CLASS

method = keyword_method + identifier + \
                open_paren + Group(Optional(delimitedList(identifier))) + close_paren + \
                open_curl + block + close_curl
def method_action(s, loc, toks):
    return ast.MethodDefinitionDeclarationStatement(toks[0], toks[2], *toks[1])
method.setParseAction(method_action)

method_statment = method + statement_end

klass_val_statement = val_statement.copy()
def klass_val_statement_action(s, loc, toks):
    return lang.ValDefinition(toks[0], toks[1])
klass_val_statement.setParseAction(klass_val_statement_action)

klass_var_statement = var_statement.copy()
def klass_var_statement_action(s, loc, toks):
    symbol = toks[0]
    if len(toks) == 2:
        return lang.VarDefinition(symbol, toks[1])
    else:
        return lang.VarDefinition(symbol, ast.ReferenceExpression('nothing'))
klass_var_statement.setParseAction(klass_var_statement_action)

klass_content_statement = (method_statment | klass_val_statement | klass_var_statement)

klass <<= keyword_class + identifier + open_curl + Group(ZeroOrMore(klass_content_statement)) + close_curl
def klass_action(s, loc, toks):
    return ast.ClassDeclarationStatement(toks[0], *toks[1])
klass.setParseAction(klass_action)
klass_statement = klass + statement_end

### STATEMENT

statement = (val_statement | var_statement | value_statement | assignment_statement)

### BLOCK

block <<= ZeroOrMore(statement)
def block_action(s, loc, tok):
    return ast.Block(*tok)
block.setParseAction(block_action)

def parse_string(string):
    return value.parseString(string, parseAll=True)

def parse_file(file):
    return block.parseFile(file, parseAll=True)[0]

