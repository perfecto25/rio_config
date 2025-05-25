#!/bin/env python3


import json
import sys
import pytest
import os
from loguru import logger
from os.path import dirname, join, abspath



# import repo version of dictor, not pip-installed version
sys.path.insert(0, abspath(join(dirname(__file__), "..")))
from flex_markup import Flex

flex = Flex()
try:
    result = flex.parse_file('data2.flx')
except Exception as error:
    raise Exception(error)

logger.warning(result)

def test1_basic_key_value():
    """test for basic string return on a section key = value"""
    assert  result['test1']['name'] == "Test1"

def test2_simple_quoted_section_key():
    """test for section key being in quotes"""
    assert result['test2']['name'] == "Test 2"
    assert result['test2']['sub'] == "this is a subkey"
    assert result['test2']['sub2'] == "another subkey"

def test3_escape_character():
    """ test skipping key splitting by a dot if theres an escape char """
    output = result['test3.feature']['header.subkey']['name']
    assert output == 'escape character'

def test4_deep_nested_key_val_hash():
    """ deep nested hash key val"""
    output = result['test4']['this']['is']['a']['very']['nested']['subkey']['name']
    assert output == 'Test4'

def test5_complex_quoted_section_key():
    """ dot separated section key in quotes """
    output = result['test5.subkey.blah']['name']
    assert output == 'Test5'

def test6_int_return():
    """test for basic int return"""
    assert result['test6']['int year'] == 1986

def test6_stringified_int_return():
    """test for int as a string return"""
    assert result['test6']['string year'] == "1986"

def test7_equal_sign_in_config():
    """test for config value having equal sign"""
    assert result['test7.abc']['name'] == "this = name"
    assert result['test7.abc']['double'] == "this == double"

def test8_singleline_list_return():
    """ test for basic single line list """
    assert result["test8"]["mylist"] == ['a', 'b', 'c']

def test9_brackets_in_config_value():
    """ test for string brackets, ie fake list """
    assert result["test9"]["fakelist"] == r"[ this is a fake \ list ]"

def test10_multiline_list_return():
    """ test for multi line list """
    assert result["test10"]["mylist"] == ['a', 'b', 'c', 0, 1, "2", "3"]
    assert result["test10"]["another list"] == ['x', 'y', 'z', 2]

def test11_multiline_comment():
    """ test comments spanning multiple lines"""
    assert result["test11"]["comment1"] == "this is \na \nmultiline\ncomment\n"
    assert result["test11"]["comment2"] == "also a \nmultiline\ncomment\n"

def test12_template_usage():
    """using template variables inside a block"""
    assert result["test12"]["comment"] == "from template1"
    assert result["test12"]["templ_list"] == ["this", "list", 99]
    assert result["test12"]["new_name"] == "from template 2"

def test13_same_parent_key_in_separate_cfg_block():
    """
    test getting value for an existing parent key in a different configuration block
    2nd identical block should overwrite the 1st
    
    """
    assert result["test13"]["value"] == "xyz"

def test14_boolean_values():
    """
    test return of bools: true, false True, False

    """
    assert result['test14']['real_bool_true'] == True
    assert result['test14']['real_bool_true_2'] == True
    assert result['test14']['real_bool_false'] == False
    assert result['test14']['real_bool_false_2'] == False
    assert result['test14']['fake_bool_true'] == 'true'
    assert result['test14']['fake_bool_false'] == 'false'

def test15_subkey_values():
    """
    test subkey values

    [key.subkey]
    subkey2 = val
    """
    assert result['test15']['subkey1']['subkey2'] == 'value'
    


def test16_string_with_single_quote_troika():
    """string with ''' """
    output = result['complex']['string']
    assert output == "this is a '''complex''' string"

# def test_env_var():
#     """test @env variable"""
#     os.environ['PASSWORD'] = 'luggage12345'

#     result = flex.parse_file('data.flx')
#     output = result['spaceballs']['password'] 
#     assert output == 'luggage12345'

#     # test fallback value
#     output = result['spaceballs']['password2'] 
#     assert output == 'Spaceball#1'

# def test_template_use():
#     """ @template, @use"""
#     output = result['spaceballs']['species']
#     assert output == 'mawg'

#     # test for multiple uses of same template
#     output = result['somekey3']['tag']
#     assert output == 'my own best friend'

#     # test multiple different templates
#     output = result['somekey3']['species']
#     assert output == 'robot'


# def test_escape_character():
#     """ test skipping key splitting by a dot if theres an escape char """

#     output = result['key1']['key2.still-key2']['key3']
#     assert output == 'some value'
    

# def test_equal_sign_in_string():
#     """ test parsing key,val in string that contains = """

#     output = result['spaceballs']['drink']
#     assert output == '=perri air'
    

#  # test int to str  age = "30" << str return
# # test raising error if same key:val exists



