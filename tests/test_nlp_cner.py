# -*- coding: utf-8 -*-
import unittest

from cathodedataextractor.nlp import CNer


class TestCNer(unittest.TestCase):
    ner = CNer()

    def test_normalized_compound_formula(self):

        cem_normalized_compound_formula = [
            ('Na0.67Ni0.31Mn0.67Y0.02O2(NMY-2)', 'Na0.67Y0.02Mn0.67Ni0.31O2 (NMY-2)'),
            ('Na0.67Ni0.28Mn0.67Y0.05O2(NMY-5', 'Na0.67Y0.05Mn0.67Ni0.28O2 (NMY-5'),
            ('Na0.66Li0.18Mn0.71Ni0.2Co0.08O2-δ', 'Na0.66Li0.18Mn0.71Co0.08Ni0.2O2'),
            ('Na0.66Li0.18Mn0.71Ni0.2Co0.08O2+δ', 'Na0.66Li0.18Mn0.71Co0.08Ni0.2O2'),
            ('Na0.7(Mn0.6Ni0.2Mg0.2)O2', 'Na0.7Mg0.2Mn0.6Ni0.2O2'),
            ('Na2/3MnO2', 'Na0.67MnO2'),
            ('Na9/10Cr1/2Fe1/2O2', 'Na0.9Cr0.5Fe0.5O2'),
            ('Na0.8(Li0.33Mn0.67-xTix)O2 (x = 0, 0.05, 0.1, 0.2)', 'Na0.8(Li0.33Mn0.67-xTix)O2 (x = 0, 0.05, 0.1, 0.2)'),
            ('Na0.8(Li0.33Mn0.67-xTix)O2(x = 0, 0.05, 0.1, 0.2)', 'Na0.8(Li0.33Mn0.67-xTix)O2 (x = 0, 0.05, 0.1, 0.2)'),
            ('Na2/3(Co3+0.15Mn3+0.52Mn4+0.33)O2', 'Na0.67Mn0.85Co0.15O2'),
            ('NaxMn0.6Ni0.4O2 (0.75 <x < 1)', 'NaxMn0.6Ni0.4O2 (0.75 <x < 1)'),
            ('Na0.44MnO2@NaTi2(PO4)3', 'Na0.44MnO2@NaTi2(PO4)3'),
            ('Na3Ni2Sb1 - xRuxO6(x=0, 0.1, 0.2, and 0.3)', 'Na3Ni2Sb1-xRuxO6 (x=0, 0.1, 0.2, and 0.3)'),
            ('Na3Ni2SbO6', 'NaNi0.67Sb0.33O2'),
            ('Na0.71Co1- xZnxO2', 'Na0.71Co1-xZnxO2'),
            ('Na0.71Co1-   xZnxO2', 'Na0.71Co1-xZnxO2'),
            ('O3-NaTi0.1Cr0.45Fe0.45O2-2', 'O3-NaTi0.1Cr0.45Fe0.45O2'),
            ('P2-Na0.67 (Mg2+ 0.33Ru4+ 0.67)O2- 2', 'P2-Na0.67Mg0.33Ru0.67O2'),
            ('P2-Na2/3Mg(II)1/4Mn(IV)7/12Co(III)1/6O2', 'P2-Na0.67Mg0.25Mn0.58Co0.17O2'),
            ('Na3Fe2PO4(P2O7)', 'Na3Fe2P3O11'),
            ('NaH2PO2·H2O,>99%', 'NaH2PO2·H2O,>99%'),
            ('Na3PS4(<CR>)', 'Na3PS4'),
            ('NaMg0.67Ru0.33O2 (<CR>)', 'NaMg0.67Ru0.33O2'),
            ('Na3Ni2Sb1-xRuxO6 (x=0, 0.1, 0.2, and 0.3)', 'Na3Ni2Sb1-xRuxO6 (x=0, 0.1, 0.2, and 0.3)'),
        ]

        for cem_pro in cem_normalized_compound_formula:
            self.assertEqual(self.ner.normalized_compound_formula(cem_pro[0]), cem_pro[1])

    def test_is_compound_formula(self):
        test2 = [
            ('Na0.67(Ni0.3Mn0.5Fe0.2)1-xZrxO2', ('Na0.67(Ni0.3Mn0.5Fe0.2)1-xZrxO2', ['Na', 'Ni', 'Mn', 'Fe', 'Zr', 'O'])),
            ('P2-Na0.67(Ni0.3Mn0.5Fe0.2)0.95Zr0.05O2', ('P2-Na0.67(Ni0.3Mn0.5Fe0.2)0.95Zr0.05O2', ['Na', 'Ni', 'Mn', 'Fe', 'Zr', 'O'])),
            ('NaNi0.45Mn0.4Ti0.1Co0.05O2-LiF', ('NaNi0.45Mn0.4Ti0.1Co0.05O2-LiF', ['Na', 'Ni', 'Mn', 'Ti', 'Co', 'O', 'Li', 'F'])),
            ('Na0.70Ni0.20Cu0.15Mn(0.65-x)TixO2', ('Na0.70Ni0.20Cu0.15Mn(0.65-x)TixO2', ['Na', 'Ni', 'Cu', 'Mn', 'Ti', 'O'])),
            ('Na2/3Ni1/3Co1/3Mn1/3O2', ('Na2/3Ni1/3Co1/3Mn1/3O2', ['Na', 'Ni', 'Co', 'Mn', 'O'])),
            ('Na0·667Mn0·667Ni0·333O2', ('Na0·667Mn0·667Ni0·333O2', ['Na', 'Mn', 'Ni', 'O'])),
            ('Na0.67Fe0.5-x/2Mn0.5-x/2TixO2 (x = 0, 0.01, 0.05, 0.10)', ('Na0.67Fe0.5-x/2Mn0.5-x/2TixO2 (x = 0, 0.01, 0.05, 0.10)', ['Na', 'Fe', 'Mn', 'Ti', 'O'])),
            ('Na0.71Co1-xZnxO2 (0 ≤ x ≤ 0.02)', ('Na0.71Co1-xZnxO2 (0 ≤ x ≤ 0.02)', ['Na', 'Co', 'Zn', 'O'])),
            ('P2-Na0.67+xNi0.33Mn0.67O2', ('P2-Na0.67+xNi0.33Mn0.67O2', ['Na', 'Ni', 'Mn', 'O'])),
            ('NaxMn1/3Fe1/3Ni1/3O2 (x = 2/3 and 1)', ('NaxMn1/3Fe1/3Ni1/3O2 (x = 2/3 and 1)', ['Na', 'Mn', 'Fe', 'Ni', 'O'])),
            ('MxC2O4·xH2O', False),
            ('ethanol', False),
            ('P2-NaNM', False),
            ('Na2CO3', ('Na2CO3', ['Na', 'C', 'O'])),
        ]
        for t2 in test2:
            self.assertEqual(self.ner.is_compound_formula(t2[0]), t2[1])

    def test_prompt_tag(self):
        self.assertEqual(self.ner.prompt_tag('Na2CO3'), 'simple')
        self.assertEqual(self.ner.prompt_tag('Na2CO3R'), 'raw_material')
        self.assertEqual(self.ner.prompt_tag('NaCl'), 'simple')
        self.assertEqual(self.ner.prompt_tag('NaF'), 'simple')
        self.assertEqual(self.ner.prompt_tag('NH4Cl'), 'raw_material')
        self.assertEqual(self.ner.prompt_tag('Na0·667Mn0·667Ni0·333O2'), 'synthetic')
        self.assertEqual(self.ner.prompt_tag('NM00'), 'is_likely_abbreviation')
        self.assertEqual(self.ner.prompt_tag('NCMTV'), 'is_likely_abbreviation')
        self.assertEqual(self.ner.prompt_tag('NCF'), 'is_likely_abbreviation')
        self.assertEqual(self.ner.prompt_tag('EC300J'), 'other')
        self.assertEqual(self.ner.prompt_tag('PC'), 'other')
        self.assertEqual(self.ner.prompt_tag('C4H4O6KNa·4H2O'), 'synthetic')
        self.assertEqual(self.ner.prompt_tag('PO4'), 'polyatomic_ions')
        self.assertEqual(self.ner.prompt_tag('Na-ion'), 'other')
        self.assertEqual(self.ner.prompt_tag('Na-N532'), 'is_likely_abbreviation')
        self.assertEqual(self.ner.prompt_tag('Nalgene'), 'other')
        self.assertEqual(self.ner.prompt_tag('No.166'), 'other')
        self.assertEqual(self.ner.prompt_tag('No.54-0894'), 'other')
        self.assertEqual(self.ner.prompt_tag('0-NMTO'), 'is_likely_abbreviation')
        self.assertEqual(self.ner.prompt_tag('NaMnNiCuFeTiOF'), 'is_likely_abbreviation')
        self.assertEqual(self.ner.prompt_tag('Mn-Na-Mn'), 'irregular_shape')
        self.assertEqual(self.ner.prompt_tag('P2/O3-NMT3'), 'is_likely_abbreviation')
        self.assertEqual(self.ner.prompt_tag('Ti-doped-NNMOF'), 'is_likely_abbreviation')
