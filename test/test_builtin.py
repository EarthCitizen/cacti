import pytest

from cacti.ast import *
from cacti.builtin import *
from cacti.lang import *

#def test_output(capsys):
#    print("Hello")
#    out, err = capsys.readouterr()
#    assert "Hello\n" == out

@pytest.mark.usefixtures('set_up_env')    
class TestPrint:
    def test_sends_output_to_stdout(self, capsys):
        fn = OperationExpression(ReferenceExpression('print'), '()', ValueExpression(make_string("Hello World!")))
        fn()
        out, err = capsys.readouterr()
        assert "Hello World!\n" == out
    
    def test_calls_string_operation(self, capsys):
        class CustomStringOperation(ObjectDefinition):
            def to_string(self):
                return "This is the custom string"
        fn = OperationExpression(ReferenceExpression('print'), '()', ValueExpression(CustomStringOperation(None)))
        fn()
        out, err = capsys.readouterr()
        assert "This is the custom string\n" == out
        