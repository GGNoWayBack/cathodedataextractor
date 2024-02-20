# -*- coding: utf-8 -*-
import unittest

import cathodedataextractor.nlp


class TestUnitsTokenizer(unittest.TestCase):

    def test_tokenizer4units(self):
        tokenize = cathodedataextractor.nlp.units_tokenizer

        test = """
         ( ... 0.1 ... C ... ) ... within ... P2 ... - ... type ... Na0.67Mn0.7(Ni0.15Cu0.15)O2 ... micr ... 
         Na3Mn1-xCrxTi(PO4)3 ... and ... the ... mixture ... was ... heated ... up ... to ... 800 ... °C ... for 
         ... 24 ... h ... dried ... at ... 100 ... °C ... and ... then ... calcined ... at ... 400 ... °C ... for 
         ... 2 ... h ... under ... nitrogen ... atmosphere. ... dried ... in ... a ... 100 ... °C ... vacuum ... 
         oven ... for ... 12 ... h. ... for ... 4 ... h ... at ... 450 ... °C ... in ... an ... Ar ... atmosphere 
         ... to ... decompose ... the ... organic ... compound ... , ... and ... then ... for ... 7 ... h ... at 
         ... 700 ... , ... 750 ... and ... 800 ... °C ... to ... obtain ... the ... car ... 0.01 ... C ... 3.5 ... 
         - ... 4.5 ... V ... CE ... The ... intrest ... calculation ... results ... show ... that ... borophene ... 
         exhibits ... a ... superhigh ... specific ... capacity ... ( ... 1 ... , ... 218 ... mAhg-1 ... ) ... 5 
         ... Cto10 ... C ... respectively ... , ... 11 ... cyclesat ... rates ... of ... 0.1 ... , ... 0.2 ... , 
         ... 0.5 ... , ... 1 ... , ... 2 ... , ... 5 ... to ... 10 ... C ... , ... to ... be ... 149 ... , ... 139 
         ... , ... 129 ... , ... 118 ... , ... 109 ... , ... 101 ... , ... 93 ... , ... 78 ... , ... and ... ( ... 
         64 ... mAhg-1 ... ) ... at ... 0.05 ... , ... 0.1 ... , ... 0.2 ... , ... 0.3 ... , ... 0.4 ... , ... 0.5 
         ... , ... 1 ... , ... 2 ... , ... and ... 3 ... Ag-1 ... and ... 2 ... when ... it ... returned ... to ... 
         0.4 ... Ag-1 ... , ... the ... capacity ... of ... NCMO-1 ... also ... returned ... to ... 103 ... mAhg-1 
         ... , ... indicating ... the ... excellent ... reversibility ... of ... the ... material. ... It ... is 
         ... worth ... noting ... that ... even ... at ... a ... current ... density ... of ... 3 ... Ag-1 ... , 
         ... NCMO-1 ... still ... exhibited ... a ... reversible ... specific ... capacity ... of ... 64 ... mAhg-1 
         ... ; ... profiles ... ( ... 1 ... st ... , ... 25 ... , ... 50 ... , ... 75 ... , ... 100 ... , ... 125 
         ... , ... 150 ... , ... 200 ... , ... 250 ... , ... 300 ... , ... 350 ... , ... 400 ... , ... 450 ... , 
         ... and1 ... , ... 2 ... nd ... , ... 5 ... th ... , ... 10 ... th ... , ... 15 ... th ... , ... 30 ... th 
         ... , ... 50 ... th ... , ... 70 ... th ... , ... and ... 100 ... cycles ... ( ... charge ... states ... ) 
         ... ar
        """

        test_res = tokenize.tokenize(
            '(0.1C) within P2-type Na0.67Mn0.7(Ni0.15Cu0.15)O2 micr Na3Mn1-xCrxTi(PO4)3 and the mixture was heated '
            'up to 800 °C for 24h  dried at 100°C and then calcined at 400°C for 2h under nitrogen '
            'atmosphere. dried in a 100 °C vacuum oven for 12h. for 4h at 450°C in an Ar '
            'atmosphere to decompose the organic compound, and then for 7h at 700, 750 and 800°C to '
            'obtain the car 0.01C 3.5-4.5V CE The intrest calculation results show '
            'that borophene exhibits a superhigh specific capacity '
            '(1,218mAhg-1) 5Cto10C respectively, 11cyclesat rates '
            'of 0.1, 0.2, 0.5, 1, 2, 5to10C, to be 149 , 139 , 129 , '
            '118,109 , 101 , 93 , 78 , and (64 mAhg-1) at 0.05 , '
            '0.1 , 0.2 , 0.3 , 0.4 , 0.5 , 1 , 2 , and 3Ag-1and2 when '
            'it returned to 0.4Ag-1, the capacity of NCMO-1 also '
            'returned to 103 mAhg-1 , indicating the excellent '
            'reversibility of the material. It is worth noting that '
            'even at a current density of 3Ag-1, NCMO-1 still exhibited '
            'a reversible specific capacity of 64mAhg-1;'
            ' profiles (1st, 25, 50, 75, 100, 125, 150, 200, 250, 300, 350, 400, 450, and'
            '1,2nd,5th,10th,15th,30th,50th,70th, and 100 cycles (charge states) ar')
        self.assertEqual(list(map(lambda x: x.strip(), test.split(" ... "))), test_res)
