from pyparsing import *
from functools import reduce
import cacti.runtime as rntm
import cacti.builtin as bltn
import cacti.ast as ast

__all__ = ['parse_file', 'parse_string']


block = Forward()
statement = Forward()
value_expression = Forward()
function_statement = Forward()
value_operand = Forward()

keyword_function = Keyword('function').suppress()
keyword_var = Keyword('var').suppress()
keyword_val = Keyword('val').suppress()

ident_word = lambda: Word('_' + alphas, bodyChars='_' + alphanums)

open_curl = Literal("{").suppress()
close_curl = Literal("}").suppress()
open_paren = Literal("(").suppress()
close_paren = Literal(")").suppress()
assignment_operator = Literal("=").suppress()
statement_end = (Literal(";") ^ LineEnd() ^ StringEnd()).suppress()

ident = ident_word()

value_integer = Word(nums)
def value_integer_action(s, loc, toks):
    return ast.ValueExpression(bltn.make_integer(int(toks[0])))
value_integer.setParseAction(value_integer_action)

value_string = QuotedString('"', escChar='\\')
def value_string_action(s, loc, toks):
    return ast.ValueExpression(bltn.make_string(str(toks[0])))
value_string.setParseAction(value_string_action)

value_literal = value_integer ^ value_string

value_reference = ident_word()
def value_reference_action(s, loc, toks):
    return ast.ReferenceExpression(toks[0])
value_reference.setParseAction(value_reference_action)


value_reference_call = value_reference + open_paren + Group(Optional(delimitedList(value_expression))) + close_paren
def value_reference_call_action(s, loc, toks):
    return ast.OperationExpression(toks[0], '()', *toks[1])
value_reference_call.setParseAction(value_reference_call_action)

value_operand <<= (value_literal ^ value_reference ^ value_reference_call ^ function_statement)

def value_operators_action(s, loc, toks):
    operation = toks[0][1]
    operands = toks[0][0::2]
    expr = reduce(lambda o1, o2: ast.OperationExpression(o1, operation, o2), operands)
    return expr

value_operators = [
    ("*", 2, opAssoc.LEFT, value_operators_action),
    ("/", 2, opAssoc.LEFT, value_operators_action),
    ("+", 2, opAssoc.LEFT, value_operators_action),
    ("-", 2, opAssoc.LEFT, value_operators_action)
]

value_expression <<= infixNotation(value_operand, value_operators)

value_expression_statement = value_expression + statement_end

### VAL

val_statement = keyword_val + ident + assignment_operator + value_expression + statement_end
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

var_statement_dec = keyword_var + ident + assignment_operator + value_expression + statement_end
var_statement_dec.setParseAction(var_statement_action)

var_statement_dec_asgn = keyword_var + ident + statement_end
var_statement_dec_asgn.setParseAction(var_statement_action)

### ASSIGNMENT

assignment_statement = ident + assignment_operator + value_expression + statement_end
def assignment_statement_action(s, loc, toks):
    return ast.AssignmentStatement(toks[0], toks[1])
assignment_statement.setParseAction(assignment_statement_action)


### STATEMENT

statement <<= value_expression_statement ^ val_statement ^ var_statement_dec ^ var_statement_dec_asgn ^ assignment_statement ^ function_statement
def statement_action(s, loc, tok):
    return tok[0]
statement.setParseAction(statement_action)


### FUNCTION

function_statement <<= keyword_function + Optional(ident) + open_paren + Group(Optional(delimitedList(ident))) + close_paren + open_curl + block + close_curl + statement_end
def function_statement_action(s, loc, toks):
    print("TOKS: " + str(toks))
    print(*toks[1])
    return ast.FunctionDeclarationStatement(toks[0], toks[2], *toks[1])
function_statement.setParseAction(function_statement_action)

### BLOCK

block <<= ZeroOrMore(statement)
def block_action(s, loc, tok):
    return ast.Block(*tok)
block.setParseAction(block_action)

def parse_string(string):
    return value_expression.parseString(string, parseAll=True)[0]

def parse_file(file):
    return block.parseFile(file, parseAll=True)[0]
