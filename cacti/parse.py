from pyparsing import *
import cacti.runtime as rntm
import cacti.builtin as bltn
import cacti.ast as ast

__all__ = ['parse_file', 'parse_string']

keyword_var = Keyword('var')
keyword_val = Keyword('val')

ident_word = lambda: Word('_' + alphas, bodyChars='_' + alphanums)

open_paren = Suppress(Literal("("))
close_paren = Suppress(Literal(")"))
assignment_operator = Suppress(Literal("="))
statement_end = Suppress(Literal(";") ^ LineEnd()) # ^ StringEnd())

value_expression = Forward()

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

value_operand = Forward()
value_operand <<= (value_literal ^ value_reference ^ value_reference_call)

def value_operators_action(s, loc, toks):
    return ast.OperationExpression(toks[0][0], toks[0][1], toks[0][2])

value_operators = [
    ("*", 2, opAssoc.LEFT, value_operators_action),
    ("/", 2, opAssoc.LEFT, value_operators_action),
    ("+", 2, opAssoc.LEFT, value_operators_action),
    ("-", 2, opAssoc.LEFT, value_operators_action)
]

value_expression <<= infixNotation(value_operand, value_operators)

value_expression_statement = value_expression + statement_end

val_statement = Suppress(keyword_val) + ident + assignment_operator + value_expression + statement_end
def val_statement_action(s, loc, toks):
    #print("TOKS: " + str(toks))
    #return None
    return ast.ValDeclarationStatement(toks[0], toks[1])
val_statement.setParseAction(val_statement_action)

statement = value_expression_statement ^ val_statement
def statement_action(s, loc, tok):
    return tok[0]
statement.setParseAction(statement_action)

block = OneOrMore(statement)
def block_action(s, loc, tok):
    return ast.Block(*tok)
block.setParseAction(block_action)

def parse_string(string):
    return value_expression.parseString(string, parseAll=True)[0]

def parse_file(file):
    return block.parseFile(file, parseAll=True)[0]
