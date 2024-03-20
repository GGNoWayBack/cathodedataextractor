# -*- coding: utf-8 -*-
import unittest
from tests.resources import TEST_PATH
from cathodedataextractor.parse import PARAGRAPH_SEPARATOR
from cathodedataextractor.text import TagClassificationPar2Text


class TestTagClassificationPar2Text(unittest.TestCase):

    def test_fulltext(self):
        tcp = TagClassificationPar2Text()
        tcp.fulltext(f"{TEST_PATH}/10.1016$$j.ensm.2023.102952.xml")

        res = "Moreover, it was revealed the average discharge voltages of P2-Na0.67[Cu0.2Co0.2Mn0.6]O2 and P2-Na0.67" \
              "[Cu0.2Mn0.8]O2 at 10 mA g−1 were ∼3.17 V and ∼2.99 V, respectively. Interestingly, the difference of " \
              "the average discharge voltage between them was more remarkable at higher current densities. <FIG>a-b " \
              "show the discharge profiles of P2-Na0.67[Cu0.2Co0.2Mn0.6]O2 and P2-Na0.67[Cu0.2Mn0.8]O2 at the " \
              "various current densities after the charging process at 10 mA g−1. The average discharge voltages of " \
              "P2-Na0.67[Cu0.2Co0.2Mn0.6]O2 and P2-Na0.67[Cu0.2Mn0.8]O2 are arranged in <FIG>c. We confirmed the " \
              "difference of the average discharge voltages between them gets larger and larger with increase of " \
              "the discharge current density. Even at 1000 mA g−1, especially, the difference was as much as 0.36 V. " \
              "Moreover, the discharge capacity of P2-Na0.67[Cu0.2Co0.2Mn0.6]O2 was ∼102 mAh g−1 at 1000 mA g−1, " \
              "which is larger than that of P2-Na0.67[Cu0.2Mn0.8]O2 (∼92 mAh g−1) at the same conditions. Conducting " \
              "repetitive experiments at different current densities to measure the power-capability also showed " \
              "similar results. In the case of P2-Na0.67[Cu0.2Mn0.8]O2, the specific discharge capacity was 92.15 " \
              "mAh g−1 at the current density of 1000 mA g−1, which is just 67.75% of the capacity measured at 10 mA " \
              "g−1. On the other hand, in the case of P2-Na0.67[Cu0.2Co0.2Mn0.6]O2, the discharge capacities at 10 " \
              "and 1000 mA g−1 were 133.16 and 102.70 mAh g−1, respectively, which indicates the capacity retention " \
              "of 77.12% at 1000 mA g−1 compared to the capacity at 10 mA g−1. (Fig. S7a-b)"

        self.assertEqual(tcp.partial_text.split(PARAGRAPH_SEPARATOR)[7], res)

