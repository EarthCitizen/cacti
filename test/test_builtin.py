import pytest
from cacti.builtin import *

class TestTypeDefinition:
    def test_type_is_self(self):
        type_def = TypeDefinition('TypeDefinition')
        assert type_def.type == type_def
        
    def test_name(self):
        type_def = TypeDefinition('Number')
        assert type_def.name == 'Number'
        
    def test_to_string(self):
        type_def = TypeDefinition('Number')
        assert type_def.to_string() == "<TypeDefinition 'Number'>"
        
    def test_add_method_get_method(self):
        method = PyMethod('convert_to_hex', lambda: 'AABBCCDD')
        type_def = TypeDefinition('Number')
        type_def.add_method(method)
        assert type_def.get_method('convert_to_hex') == method
        
    def test_has_method_true(self):
        method = PyMethod('convert_to_hex', lambda: 'AABBCCDD')
        type_def = TypeDefinition('Number')
        type_def.add_method(method)
        assert type_def.has_method('convert_to_hex') == True
        
    def test_has_method_false(self):
        type_def = TypeDefinition('Number')
        assert type_def.has_method('convert_to_hex') == False
    
    def test_type_of_type(self):
        type_def = TypeDefinition('Number')
        type_inst = type_def.type
        actual = [type_inst.__class__, type_inst.name]
        expected = [TypeDefinition, 'TypeDefinition']
        assert actual == expected
        
    def test_super_of_type(self):
        type_def = TypeDefinition('Number')
        type_super = type_def.super
        actual = [type_super.__class__, type_super.type.name]
        expected = [Object, 'Object']
        assert actual == expected
    

class TestObject:
    def test_no_super(self):
        number_type_def = TypeDefinition('Object')
        number_object = Object(number_type_def, None)
        assert number_object.super == None
    
    def test_super(self):
        object_type_def = TypeDefinition('Object')
        number_type_def = TypeDefinition('Number')
        object_inst = Object(object_type_def, None)
        number_inst = Object(number_type_def, object_inst)
        assert number_inst.super.type.name == 'Object'
        
    def test_call_method(self):
        object_method = PyMethod('convert_to_hex', lambda target: 'AABBCCDD')
        object_type_def = TypeDefinition('Object')
        object_type_def.add_method(object_method)
        
        object_inst = Object(object_type_def, None)
        
        actual = object_inst.call_method('convert_to_hex')
        
        assert actual == 'AABBCCDD'
        
    def test_call_method_calls_super(self):
        object_to_string_method = PyMethod('to_string', lambda target: target.to_string())
        object_type_def = TypeDefinition('Object')
        object_type_def.add_method(object_to_string_method)
        
        number_type_def = TypeDefinition('Number')
        
        object_inst = Object(object_type_def, None)
        number_inst = Object(number_type_def, object_inst)
        
        actual = number_inst.call_method('to_string')
        
        assert actual == '<Number>'
        
    def test_call_method_override(self):
        object_to_string_method = PyMethod('to_string', lambda target: target.to_string())
        object_type_def = TypeDefinition('Object')
        object_type_def.add_method(object_to_string_method)
        
        number_to_string_method = PyMethod('to_string', lambda target: '12345')
        number_type_def = TypeDefinition('Number')
        number_type_def.add_method(number_to_string_method)
        
        object_inst = Object(object_type_def, None)
        number_inst = Object(number_type_def, object_inst)
        
        actual = number_inst.call_method('to_string')
        
        assert actual == '12345'
        
    def test_type(self):
        number_type_def = TypeDefinition('Number')
        number_inst = Object(number_type_def, None)
        actual = [number_inst.type.__class__, number_inst.type.name]
        expected = [TypeDefinition, 'Number']
        assert actual == expected
    
    def test_to_string(self):
        number_type_def = TypeDefinition('Object')
        number_object = Object(number_type_def, None)
        assert number_object.to_string() == '<Object>'
        
        
    