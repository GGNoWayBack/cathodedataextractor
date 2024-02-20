# -*- coding: utf-8 -*-
import unittest
from cathodedataextractor.text import BatteriesTextProcessor
from cathodedataextractor.nlp import AbbreviationDetection


class TestAbbreviationDetection(unittest.TestCase):

    def test_abbr(self):
        exams = [("... Na[(Mn0.4Fe0.3Ni0.3)1−xTix]O2 (x = 0, MFN) ...", [('MFN', 'NaMn0.4Fe0.3Ni0.3O2')]),

                 ("... Na0.6MnO2, Na0.6Mn0.95Fe0.05O2, ... marked as MFT0, MF5, ...",
                  [('MFT0', 'Na0.6MnO2'), ('MF5', 'Na0.6Mn0.95Fe0.05O2')]),

                 ("... O3-NaNi0.45Mn0.3Ti0.2M0.05O2 (M=Nb/Mo/Cr, "
                  "abbreviated as NMTNb, NMTMo and NMTCr, respectively) ..., ",
                  [('NMTNb', 'O3-NaTi0.2Nb0.05Mn0.3Ni0.45O2.0'),
                   ('NMTMo', 'O3-NaTi0.2Mo0.05Mn0.3Ni0.45O2.0'),
                   ('NMTCr', 'O3-NaTi0.2Cr0.05Mn0.3Ni0.45O2.0')]),

                 ("... Na0.67Ni0.31Mn0.67Y0.02O2 (NMY2) ...", [('NMY2', 'Na0.67Y0.02Mn0.67Ni0.31O2')]),

                 ("Na0.67Ni0.23Mg0.1Mn0.67O2 ... (denoted as NNMMO-MP)", [('NNMMO-MP', 'Na0.67Mg0.1Mn0.67Ni0.23O2')]),

                 ("... h-NM, h-NMC and h-NMC2 are identified as Na0.66MnO2, "
                  "Na0.65Mn0.9Cu0.1O2 and Na0.63Mn0.8Cu0.2O2, ...", [('h-NM', 'Na0.66MnO2'),
                                                                     ('h-NMC', 'Na0.65Mn0.9Cu0.1O2'),
                                                                     ('h-NMC2', 'Na0.63Mn0.8Cu0.2O2')]),

                 ("... Na0.67Ni0.33Mn0.67O2 (NM)", [('NM', 'Na0.67Mn0.67Ni0.33O2')]),

                 ("(Na2/3Ni1/3Mn2/3O2, P2-NNMO) ", [('P2-NNMO', 'Na0.67Mn0.67Ni0.33O2')]),

                 ("... (tetragonal Na3V2(PO4)2O2F, abbreviated as NVPOF) ... ", [('NVPOF', 'Na3V2P2O10F')]),

                 ("... Na0.67MnO2, tunnel compound of Na0.44MnO2 and pure ..., "
                  "i.e. Na0.6Fe0.02Mn0.98O2 and Na0.6Fe0.06Mn0.94O2 ... "
                  "denoted as T-NM, L-NM, LT-NM, LT-NFM2 and L-NFM6, respectively.", [('T-NM', 'Na0.67MnO2'),
                                                                                      ('L-NM', 'Na0.44MnO2'),
                                                                                      ('LT-NM', 'Na0.6Mn0.98Fe0.02O2'),
                                                                                      ('LT-NFM2',
                                                                                       'Na0.6Mn0.94Fe0.06O2')]),

                 ("... Na3V2P3O12 and Na3V2P2O8F3 (NVPF) <CR>.", [('NVPF', 'Na3V2P2O8F3')])

                 ]
        for exam in exams:
            bp = BatteriesTextProcessor(exam[0], special_normal=True)
            abbr = AbbreviationDetection()
            self.assertEqual(abbr(' '.join(bp.processed_text)).new_abbreviation, exam[1])
