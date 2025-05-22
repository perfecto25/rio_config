#!/bin/env python3


import json
import sys
import pytest
import os
from os.path import dirname, join, abspath
from loguru import logger


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


# def test_int_singleline_list_return():
#     """ test for basic int inside single line list """
#     output = result["spaceballs"]["yogurt"][0]
#     assert output == "355"

# def test_int_multiline_list_return():
#     """test for basic int inside a multiline list """
#     output = result['spaceballs']['lucky numbers'][1]
#     assert output == 20951

# def test_fake_int_return():
#     """test a fake int (string)"""
#     #output = result['spaceballs']['actors'][2]
#     #assert output == '26'
#     output = result["spaceballs"]["fake_year"]
#     assert output == '1999'

# def test_fake_int_list_return():
#     """test a fake int inside a list (string)"""
#     output = result['spaceballs']['lucky numbers'][2]
#     assert output == '200'

# def test_list_return():
#     """test for basic list return"""
#     output = result['spaceballs']['characters']
#     assert output == ['Lonestar', 'Barf', 'Druish Princess', 'Dark Helmet']


# def test_multiline_list_return():
#     """ tests for list definition spanning multiple lines """


# def test_same_parent_key_in_separate_cfg_block():
#     """
#     test getting value for an existing parent key in a different configuration block

#     [key1]
#     subkey1 = val1

#     [key1]
#     subkey2 = val2

#     """
#     output = result['spaceballs']['power']
#     assert output == 'the Schwartz'


# def test_multiline_string():
#     """test for getting correct contents of multi-line strings"""
#     output = result['spaceballs']['comments']
#     assert output == "this is one funny, no! very... funny movie!!!"


# def test_subkey_values():
#     """
#     test subkey values

#     [key.subkey]
#     subkey2 = val
#     """
#     output = result['spaceballs']['vehicles']
#     assert output == 'Winnebago'
#     output = result['spaceballs']['car']
#     assert output == 'Mercedes'


# def test_deep_nested_single_value_hash():
#     """ deep nested hash with a single value """
#     output = result['this']['is']['a']['very']['nested']['subkey']
#     assert output == 'value1'

# def test_deep_nested_key_val_hash():
#     """ deep nested hash key val"""

#     output = result['this']['is']['also']['a']['very']['nested']['subkey']['value']
#     assert output == 'some other value'

# def test_boolean_values():
#     """
#     test return of bools: true, false True, False

#     """
#     output = result['spaceballs']['real_bool_true']
#     assert output == True

#     output = result['spaceballs']['fake_bool_true']
#     assert output == 'true'

#     output = result['spaceballs']['fake_bool_false']
#     assert output == 'false'

# def test_string_with_single_quote_troika():
#     """string with ''' """
#     output = result['complex']['string']
#     assert output == "this is a '''complex''' string"

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



