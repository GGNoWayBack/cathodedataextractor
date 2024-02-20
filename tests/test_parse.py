# -*- coding: utf-8 -*-
import unittest
from cathodedataextractor.parse import end_parentheses, relation_extraction


class TestParse(unittest.TestCase):

    def test_end_parentheses(self):
        cems = [
            ('Na3Mn1-xCrxTi(PO4)3 (x=0.01, 0.03, 0.05, 0.07, 0.10, 0.12, 0.15)',
             (20, '(x=0.01, 0.03, 0.05, 0.07, 0.10, 0.12, 0.15)')),
            ('Nax(Cu-Fe-Mn)O2', (None, None)),
            ('NaFexCr1-X(SO4)2', (None, None)),
            ('Na0.6Li0.6(Mn0.72Ni0.18Co0.10)O2', (None, None)),
            ('P2-Na0.59Mn0.85Co0.1(Ti2V)0.05O2', (None, None)),
            ('Na3Fe2PO4(P2O7', (None, None)),
            ('Na0.71Co1-xZnxO2(0 ≤ x ≤ 0.02)', (16, "(0 ≤ x ≤ 0.02)")),
            (
                'Na0.71Co1-xZnxO2(0 ≤ x ≤ 0.02, ... sdf()sff (...) sfsf)',
                (16, "(0 ≤ x ≤ 0.02, ... sdf()sff (...) sfsf)")),
            ('Na0.67Ni0.28Mn0.67Y0.05O2 (NMY-5', (26, "(NMY-5")),
            ('Na0.67Ni0.33Mn0.67O2 (NNM)', (21, "(NNM)")),
            ('O3-NaBxMn1-xO2 (x=0, 0.05, 0.1, 0.15, 0.25) oxides', (15, "(x=0, 0.05, 0.1, 0.15, 0.25) oxides")),
            ('NaFexCr1-X(SO4)2 ((dsfjs)dsfd', (17, "((dsfjs)dsfd")),
            ('Na0.66Li0.18Mn0.71Co0.08Ni0.21O2(<FIG>)', (32, "(<FIG>)")),
        ]
        for cem in cems:
            self.assertEqual(end_parentheses(cem[0]), cem[1])

    def test_PropertyParse(self):
        pp = relation_extraction.PropertyParse()
        self.assertEqual(pp.parse_stoichiometric_variables('Na0.8(Li0.33Mn0.67-xTix)O2',
                                                           'XPS spectra of Mn 2p and Ti 2p for Na0.8(Li0.33Mn0.67-xTix)O2 '
                                                           'electrodes are used to validate this speculation. The ratio of '
                                                           'Mn3+ to Mn4+ in the x=0 and x=0.1 electrodes was 0.48:0.52 and '
                                                           '0.23:0.77 calculated by fitting Mn 2p spectra, respectively [47,48]. '),
                         ('Na0.8(Li0.33Mn0.67-xTix)O2 (x=0 and x=0.1 )', 'x'))
