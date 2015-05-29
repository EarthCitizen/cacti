import logging
from pyparsing import *

# HUGE speed increase after enabling packrat
ParserElement.enablePackrat()

from functools import reduce
import cacti.runtime as rntm
import cacti.lang as lang
import cacti.builtin as bltn
import cacti.ast as ast

__all__ = ['parse_file', 'parse_string']


block = Forward()
statement = Forward()
value_expression = Forward()
closure = Forward()
function = Forward()
value_operand = Forward()

keyword_class = Keyword('class').suppress()
keyword_closure = Keyword('closure').suppress()
keyword_function = Keyword('function').suppress()
keyword_method = Keyword('method').suppress()
keyword_var = Keyword('var').suppress()
keyword_val = Keyword('val').suppress()

ident_word = lambda: Word('_' + alphas, bodyChars='_' + alphanums)

open_curl = Literal("{").suppress()
close_curl = Literal("}").suppress()
open_paren = Literal("(").suppress()
close_paren = Literal(")").suppress()
assignment_operator = Literal("=").suppress()
statement_end = (Literal(";").suppress() | LineEnd().suppress() | StringEnd().suppress() | FollowedBy(Literal('}')))

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

value_properties_of = (value_literal ^ value_reference ^ value_reference_call) + Group(OneOrMore(Literal('.').suppress() + ident))
def value_properties_of_action(s, loc, toks):
    return ast.PropertyExpression(toks[0], *toks[1])
value_properties_of.setParseAction(value_properties_of_action)

value_operand <<= (value_literal ^ value_reference ^ value_reference_call ^ value_properties_of)

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

value_expression <<= (infixNotation(value_operand, value_operators) ^ function ^ closure)

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

### CLOSURE

closure <<= keyword_closure + open_paren + Group(Optional(delimitedList(ident))) + close_paren + open_curl + block + close_curl
def closure_action(s, loc, toks):
    logging.debug(s)
    logging.debug(str(toks))
    return ast.ClosureDeclarationStatement(toks[1], *toks[0])
closure.setParseAction(closure_action)
closure_statement = closure + statement_end

### FUNCTION

function <<= keyword_function + \
                Optional(ident, default=None) + \
                open_paren + Group(Optional(delimitedList(ident))) + close_paren + \
                open_curl + block + close_curl
def function_action(s, loc, toks):
    return ast.FunctionDeclarationStatement(toks[0], toks[2], *toks[1])
function.setParseAction(function_action)
function_statement = function + statement_end

### CLASS

method = keyword_method + ident + \
                open_paren + Group(Optional(delimitedList(ident))) + close_paren + \
                open_curl + block + close_curl
def method_action(s, loc, toks):
    return ast.MethodDefinitionDeclarationStatement(toks[0], toks[2], *toks[1])
method.setParseAction(method_action)

method_statement = method + statement_end

klass = keyword_class + ident + open_curl + Group(ZeroOrMore(method_statement)) + close_curl
def klass_action(s, loc, toks):
    return ast.ClassDeclarationStatement(toks[0], *toks[1])
klass.setParseAction(klass_action)
klass_statement = klass + statement_end

### STATEMENT

statement <<= value_expression_statement ^ val_statement ^ var_statement_dec ^ var_statement_dec_asgn ^ assignment_statement ^ function_statement ^ klass_statement
def statement_action(s, loc, tok):
    return tok[0]
statement.setParseAction(statement_action)

### BLOCK

block <<= ZeroOrMore(statement)
def block_action(s, loc, tok):
    return ast.Block(*tok)
block.setParseAction(block_action)

def parse_string(string):
    return value_expression.parseString(string, parseAll=True)[0]

def parse_file(file):
    return block.parseFile(file, parseAll=True)[0]
