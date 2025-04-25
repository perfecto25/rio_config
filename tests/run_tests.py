#!/bin/env python3


from flex_markup import Flex
import json
import sys
import pytest
from os.path import dirname, join, abspath

# import repo version of dictor, not pip-installed version
sys.path.insert(0, abspath(join(dirname(__file__), "..")))
flex = Flex()
try:
    result = flex.parse_file('data.flx')

except Exception as error:
    raise Exception(error)


def test_string_return():
    """test for basic string return"""
    output = result['spaceballs']['title']
    assert output == "spaceballs"


def test_int_return():
    """test for basic int return"""
    output = result['spaceballs']['year']
    assert output == 1987


def test_list_return():
    """test for basic list return"""
    output = result['spaceballs']['characters']
    assert output == ['Lonestar', 'Barf', 'Druish Princess', 'Dark Helmet']


def test_multiline_list_return():
    """ tests for list definition spanning multiple lines """


def test_same_parent_key_in_separate_cfg_block():
    """
    test getting value for an existing parent key in a different configuration block

    [key1]
    subkey1 = val1

    [key1]
    subkey2 = val2

    """
    output = result['spaceballs']['power']
    assert output == 'the Schwartz'


def test_multiline_string():
    """test for getting correct contents of multi-line strings"""
    output = result['spaceballs']['comments']
    assert output == "this is one funny, no! very... funny movie!!!"


def test_subkey_values():
    """
    test subkey values

    [key.subkey]
    subkey2 = val
    """
    output = result['spaceballs']['vehicles']
    assert output == 'Winnebago'


# def test_simple_dict():
#     """test for value in a dictionary"""
#     result = dictor(BASIC, "robocop.year")
#     assert result == 1989


# def test_non_existent_value():
#     """test a non existent key search"""
#     result = dictor(BASIC, "non.existent.value")
#     assert result is None

#     result = dictor({"lastname": "Doe"}, "foo.lastname")
#     assert result is None


# def test_zero_value():
#     """test a Zero value - should return 0"""
#     result = dictor(BASIC, "terminator.2.terminator 3.year", checknone=True)
#     assert result == 0

# print(json.dumps(result, ensure_ascii=False))
