# coding=utf-8
import unittest
from collections import OrderedDict

from text2chem.core.formula_parser import __parse_parentheses as parse_parentheses
from text2chem.regex_parser import RegExParser

parser = RegExParser()


class TestParser(unittest.TestCase):

    def test_regex_parser_make_fraction_convertion_case1(self):
        self.assertEqual(parser.make_fraction_convertion(
            'Na2/3Ni(3/10-x)MgxMn7/10O2'), 'Na2/3Ni3/10-xMgxMn7/10O2'
        )

    def test_regex_parser_make_fraction_convertion_case2(self):
        self.assertEqual(parser.make_fraction_convertion(
            '(Cu1/3Nb2/3)1/4Ti(3/4-x)ZrxO2'), '(Cu1/3Nb2/3)1/4Ti3/4-xZrxO2'
        )

    def test_regex_parser_make_fraction_convertion_case3(self):
        self.assertEqual(parser.make_fraction_convertion(
            '(Cu1/3Nb2/3)(1/4-y)Ti(3/4-x)Zr(x+y)O2'), '(Cu1/3Nb2/3)1/4-yTi3/4-xZrx+yO2'
        )

    def test_regex_parser_make_fraction_convertion_case4(self):
        self.assertEqual(parser.make_fraction_convertion(
            '(Cu1/3Nb2/3)(1/4-y-x)Ti(3/4-x)Zr(2x+y)O2'), '(Cu1/3Nb2/3)(1/4-y-x)Ti3/4-xZr2*x+yO2'
        )

    def test_core_formula_parser__parse_parentheses_case1(self):
        formula_dict = OrderedDict()
        formula_dict, _ = parse_parentheses('Ti(OCH(CH3)2)4', "1", formula_dict)
        self.assertEqual(formula_dict, {'C': '(8)+(4)', 'H': '(24)+(4)', 'O': '4', 'Ti': '1'})

    def test_core_formula_parser__parse_parentheses_case2(self):
        formula_dict = OrderedDict()
        formula_dict, _ = parse_parentheses('Na2/3Ni3/10-xMgxMn7/10O2', "1", formula_dict)
        self.assertEqual(formula_dict, {'Na': '0.667', 'Ni': '0.3-x', 'Mg': 'x', 'Mn': '0.7', 'O': '2'})

    def test_core_formula_parser__parse_parentheses_case3(self):
        formula_dict = OrderedDict()
        formula_dict, _ = parse_parentheses('(Cu1/3Nb2/3)1/4Ti3/4-xZrxO2', "1", formula_dict)
        self.assertEqual(formula_dict, {'Cu': '0.083', 'Nb': '0.167', 'O': '2', 'Ti': '0.75-x', 'Zr': 'x'})

    def test_core_formula_parser__parse_parentheses_case4(self):
        formula_dict = OrderedDict()
        formula_dict, _ = parse_parentheses('(Cu1/3Nb2/3)1/4-yTi3/4-xZr(x+y)O2', "1", formula_dict)
        self.assertEqual(formula_dict, {'Cu': '0.0833-0.333*y', 'Nb': '0.167-0.667*y', 'Ti': '0.75-x', 'Zr': 'x+y', 'O': '2'})

    def test_core_formula_parser__parse_parentheses_case5(self):
        formula_dict = OrderedDict()
        formula_dict, _ = parse_parentheses('(Cu1/3Nb2/3)(1/4-y-x)Ti3/4-xZr2*x+yO2', "1", formula_dict)
        self.assertEqual(formula_dict, {'Cu': '0.0833-0.333*x-0.333*y', 'Nb': '0.167-0.667*x-0.667*y', 'Ti': '0.75-x', 'Zr': '2*x+y', 'O': '2'})
