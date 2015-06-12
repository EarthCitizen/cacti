from pyparsing import *

ParserElement.enablePackrat()

from functools import reduce
import cacti.runtime as rntm
import cacti.lang as lang
import cacti.builtin as bltn
import cacti.ast as ast
import cacti.exceptions as excp

__all__ = ['parse_file', 'parse_string']

_reserved_keywords_ = [
    'and',
    'block',
    'class', 'closure',
    'else',
    'false', 'for', 'function',
    'id', 'if', 'in', 'is',
    'method',
    'not', 'nothing',
    'operation', 'or',
    'procedure',
    'return', 'self', 'super',
    'trait', 'true', 'type',
    'var', 'val'
    ]

_operators_ = [
    '*', '/', '+', '-', '//', '%', '**',
    '*=', '/=', '+=', '-=', '//=', '%=', '**=',
    '++', '--',
    '->',
    '=',
    '==', '<=', '<', '>=', '>', '$'
    '!', '<<', '>>', '&', '|',
    '!=', '<<=', '>>=', '&=', '|='
    ]

def _get_source_info(s, loc):
    return '{}:{}: {}'.format(str(lineno(loc, s)), str(col(loc, s)), line(loc, s).strip())

def _add_source_line(s, loc, expr):
    expr.source = line(loc, s)
    return expr

def _process_prop_call_expr(operands):
    def list_reduction(a, b):
        if isinstance(b, str):
            return ast.PropertyExpression(a, b)
        else:
            return ast.OperationExpression(a, '()', *b)
    return reduce(list_reduction, operands)

identifier = Word('_' + alphas, bodyChars='_' + alphanums)

object_identifier = identifier.copy()
def object_identifier_action(s, loc, toks):
    if toks[0] in _reserved_keywords_:
        raise SyntaxError("'{}' is a reserved keyword: {}".format(toks[0], _get_source_info(s, loc)))
object_identifier.setParseAction(object_identifier_action)

block = Forward()
callable_block = Forward()
closure = Forward()
function = Forward()
klass = Forward()
value = Forward()
super = Forward()

open_curl = Literal("{").suppress()
close_curl = Literal("}").suppress()
open_paren = Literal("(").suppress()
close_paren = Literal(")").suppress()
optional_param_names = Group(Optional(delimitedList(identifier)))
def optional_param_names_action(s, loc, toks):
    param_names = list(toks[0])
    if param_names:
        repeat_params = [e for e in [[x, param_names.count(x)] for x in set(param_names)] if e[1] > 1]
        if repeat_params:
            m = map(lambda e: "{0}: {1}".format(*e), repeat_params)
            raise SyntaxError("Repeated parameters: " + ", ".join(sorted(m)))
optional_param_names.setParseAction(optional_param_names_action)
optional_param_values = Group(Optional(delimitedList(value)))

keyword_class = Keyword('class').suppress()
keyword_closure = Keyword('closure').suppress()
keyword_function = Keyword('function').suppress()
keyword_method = Keyword('method').suppress()
keyword_property = Keyword('property').suppress()
keyword_return = Keyword('return').suppress()
keyword_super = Keyword('super')
keyword_var = Keyword('var').suppress()
keyword_val = Keyword('val').suppress()
assignment_operator = Literal("=").suppress()
call_operator = open_paren + optional_param_values + close_paren
property_operator = Literal('.').suppress() + identifier
comment = (Literal('#') + restOfLine).suppress()
statement_end = (LineEnd().suppress() | Literal(";").suppress() | StringEnd().suppress() | comment | FollowedBy(Literal('}')))

super = keyword_super + Optional(call_operator | property_operator)
def super_action(s, loc, toks):
    if 1 == len(toks):
        #raise excp.SyntaxError(s, loc, "Invalid use of 'super'")
        # pyparsing is swallowing custom exceptions
        raise SyntaxError("Invalid use of 'super'")
    toks[0] = ast.ReferenceExpression(toks[0])
    return _add_source_line(s, loc, _process_prop_call_expr(toks))
super.setParseAction(super_action)

reference = identifier.copy()
def reference_action(s, loc, toks):
    return _add_source_line(s, loc, ast.ReferenceExpression(toks[0]))
reference.setParseAction(reference_action)

integer = Word(nums).setResultsName('value')
def integer_action(s, loc, toks):
    return _add_source_line(s, loc, ast.ValueExpression(bltn.make_integer(int(toks.value))))
integer.setParseAction(integer_action)

string = QuotedString('"', escChar='\\').setResultsName('value')
def string_action(s, loc, toks):
    return _add_source_line(s, loc, ast.ValueExpression(bltn.make_string(str(toks.value))))
string.setParseAction(string_action)



def binary_operation_action(s, loc, toks):
    operation = toks[0][1]
    operands = toks[0][0::2]
    expr = reduce(lambda o1, o2: ast.OperationExpression(o1, operation, o2), operands)
    return _add_source_line(s, loc, expr)

def call_property_operation_action(s, loc, toks):
    return _add_source_line(s, loc, _process_prop_call_expr(toks[0]))
    
operators = [
    ((property_operator ^ call_operator), 1, opAssoc.LEFT, call_property_operation_action),
    ("*", 2, opAssoc.LEFT, binary_operation_action),
    ("/", 2, opAssoc.LEFT, binary_operation_action),
    ("+", 2, opAssoc.LEFT, binary_operation_action),
    ("-", 2, opAssoc.LEFT, binary_operation_action)
]

operand = (super | reference | integer | string)

value <<= (infixNotation(operand, operators) ^ closure ^ function ^ klass)

value_statement = value + statement_end

### VAL

val_statement = keyword_val + object_identifier + assignment_operator + value + statement_end
def val_statement_action(s, loc, toks):
    return _add_source_line(s, loc, ast.ValDeclarationStatement(toks[0], toks[1]))
val_statement.setParseAction(val_statement_action)

### VAR

def var_statement_action(s, loc, toks):
    symbol = toks[0]
    if len(toks) == 2:
        return_value = ast.VarDeclarationStatement(symbol, toks[1])
    else:
        return_value = ast.VarDeclarationStatement(symbol, ast.ReferenceExpression('nothing'))
        
    return _add_source_line(s, loc, return_value)

var_assign = keyword_var + object_identifier + assignment_operator + value
var_no_assign = keyword_var + object_identifier

var_statement = (var_assign | var_no_assign) + statement_end
var_statement.setParseAction(var_statement_action)

### ASSIGNMENT

assign_to_operators = [
    ((property_operator ^ call_operator), 1, opAssoc.LEFT)
]

assign_to_operand = (identifier)

assign_to = infixNotation(assign_to_operand, assign_to_operators)

assignment_statement = assign_to + assignment_operator + value + statement_end
def assignment_statement_action(s, loc, toks):
    assign_target_tokens = toks[0]
    # Only one assignment identifier will be a str
    if isinstance(assign_target_tokens, str):
        assign_id = assign_target_tokens
        assign_target_expr = None
    else:
        assign_id = assign_target_tokens[-1]
        assign_target_tokens[0] = ast.ReferenceExpression(assign_target_tokens[0])
        assign_target_expr = _process_prop_call_expr(assign_target_tokens[:-1])
        
    if not isinstance(assign_id, str):
        raise SyntaxError(s, loc, 'No identifier for assignment target expression')
        
    return _add_source_line(s, loc, ast.AssignmentStatement(assign_id, toks[1], assign_target_expr))
assignment_statement.setParseAction(assignment_statement_action)

### CLOSURE

closure <<= keyword_closure + open_paren + optional_param_names + close_paren + open_curl + callable_block + close_curl
def closure_action(s, loc, toks):
    return _add_source_line(s, loc, ast.ClosureDeclarationStatement(toks[1], *toks[0]))
closure.setParseAction(closure_action)
closure_statement = closure + statement_end

### FUNCTION

function <<= keyword_function + \
                Optional(object_identifier, default=None) + \
                open_paren + optional_param_names + close_paren + \
                open_curl + callable_block + close_curl
def function_action(s, loc, toks):
    return _add_source_line(s, loc, ast.FunctionDeclarationStatement(toks[0], toks[2], *toks[1]))
function.setParseAction(function_action)
function_statement = function + statement_end

### CLASS

property_field = keyword_property + object_identifier + open_paren + identifier + close_paren
def property_field_action(s, loc, toks):
    print("TOKS: " + str(toks))
    return ast.PropertyFieldDeclaration(toks[0], toks[1])
property_field.setParseAction(property_field_action)

property_statement = property_field + statement_end

method = keyword_method + object_identifier + \
                open_paren + optional_param_names + close_paren + \
                open_curl + callable_block + close_curl
def method_action(s, loc, toks):
    return _add_source_line(s, loc, ast.MethodDefinitionDeclarationStatement(toks[0], toks[2], *toks[1]))
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

klass_content_statement = (method_statment | klass_val_statement | klass_var_statement | property_statement)

klass <<= keyword_class + object_identifier + Optional(Literal(':').suppress() + identifier, default='Object') + open_curl + Group(ZeroOrMore(klass_content_statement)) + close_curl
def klass_action(s, loc, toks):
    return _add_source_line(s, loc, ast.ClassDeclarationStatement(toks[0], toks[1], *toks[2]))
klass.setParseAction(klass_action)
klass_statement = klass + statement_end

### STATEMENT

statement = (val_statement | var_statement | value_statement | assignment_statement | comment)

### RETURN STATEMENT

return_statement = keyword_return + Optional(value) + statement_end
def return_statement_action(s, loc, toks):
    # Empty
    if not toks:
        value_expr = ast.ReferenceExpression('nothing')
    else:
        value_expr = toks[0]
    return ast.ReturnStatement(value_expr)
return_statement.setParseAction(return_statement_action)

### CALLABLE BLOCK

callable_block <<= ZeroOrMore(return_statement | statement)
def callable_block_action(s, loc, tok):
    return ast.Block(*tok)
callable_block.setParseAction(callable_block_action)

### BLOCK

block <<= ZeroOrMore(statement)
def block_action(s, loc, tok):
    return ast.Block(*tok)
block.setParseAction(block_action)

def parse_string(string):
    return value.parseString(string, parseAll=True)

def parse_file(file):
    return block.parseFile(file, parseAll=True)[0]

