#!/bin/env python3
import sys
import os
import pytest
from loguru import logger
from os.path import dirname, join, abspath

# import repo version of Rio, not pip-installed version
sys.path.insert(0, abspath(join(dirname(__file__), "..")))

from rio_config import Rio

testfile = 'all_tests.rio'

rio = Rio()

def test0_exception_unquoted_colon_ML():
    """ unquoted strings with colons should raise an Exception """
    with pytest.raises(Exception, match="unquoted : symbol inside an Array declaration on line >>   c:"):
        result = rio.parse_file("test26.rio")





try:
    result = rio.parse_file(testfile)
except Exception as error:
    raise Exception(error)

logger.warning(result)

def test1_basic_key_value():
    """test for basic string return on a section key = value"""
    assert result['test1']['name'] == "Test1"


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
    assert result["test11"]["comment1"] == " this is \na \nmultiline\ncomment\n"
    assert result["test11"]["comment2"] == "also a \nmultiline\ncomment\n"


def test12_template_usage():
    """using template variables inside a block"""
    assert result["test12"]["comment"] == "from template 1"
    assert result["test12"]["templ_list"] == ["this", "list", 99]
    assert result["test12"]["new_name"] == "from template 2"
    with pytest.raises(KeyError):
        assert result["test12"]["@use"] == None # dont include @use as key,val



def test12a_template_reuse():
    """re-using template variables inside a block"""
    assert result["test12a"]["new_name"] == "from template 2"


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

    assert result['test16']['string'] == "this is a '''complex''' string"


def test17_env_vars():
    """test getting env vars"""
    os.environ['PASSWORD'] = 'abc123'
    result = rio.parse_file(testfile)
    assert result['test17']['password'] == "abc123"
    assert result['test17']['password with fallback'] == "xyz789"
    assert result['test17']['no var'] == None
    assert result['test17']['password2'] == 'Spaceball#1'

def test18_equal_sign_in_string():
    """ test parsing key,val in string that contains = """

    output = result['test18']['drink']
    assert output == '=perri air'

def test19_leading_spaces():
    """ test values that have leading spaces"""

    assert result['test19']['first']['with spaces'] == True
    assert result['test19']['second']['with spaces'] == True
    
def test20_simple_keyval():
    """ parent keys with only values - no sub key"""
    assert result['test20'] == "simple value"

def test21_simple_keyval_list():
    """ parent keys with only list values - no sub key"""
    assert result['test21'] == ["a", "b", "c", 1000]

def test22_simple_keyval_list_ML():
    """ parent keys with only multiline list values - no sub key"""
    assert result['test22'] == ["a", "b", "c", 1000]

def test23_simple_keyval_ML_strings():
    """ parent keys with only multiline string values - no sub key"""
    assert result['test23'] == "simple \nmultiline \ncomment\n"

def test24_values_with_colons():
    """ test for values that have : """
    assert result['test24'] == "this is a : value:"

def test25_list_values_with_colons():
    """ test for values that have : """
    assert result['test25'] == ['a', 'b:', 'c:']

def test26_ignore_comments():
    """ return data without comments on end of line """
    assert result['test26']['k1'] == "apple"
    assert result['test26']['k2'] == "banana # is # delicious ###"
    assert result['test26']['k3'] == "cherry ##"
    assert result['test26a'] == "fruit"
    assert result['test26b'] == ['a', 'b', 'c']

def test27_nested_child_subkeys():
    """ parse child subkeys with dots """
    assert result['test27']['planet']['name'] == "mars"
    assert result['test27']['planet']['color'] == "red"
    assert result['test27']['planet']['size']['miles'] == 500
    assert result['test27']['planet']['size']['km'] == 200
    assert result['test27']['key1.key2'] == "fake subkey"

def test28_float_values_in_list():
    """ list returning floats """
    assert result['test28']['vals'] == [2.0, 3.1, 567, 'apple', True, 'true', False, 'false']
