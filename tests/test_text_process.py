# -*- coding: utf-8 -*-
import unittest
from cathodedataextractor.text import BatteriesTextProcessor


class TestBatteriesTextProcessor(unittest.TestCase):

    def test_func1(self):
        texts = [
            (  # 0
                'We synthesized P2-Na0.67+xNi0.33Mn0.67O2 (x = 2 %, 2.5 %, 3 %, 3.5 %, 4 %) '
                'with different sodium contents by solid state method, and compared the '
                'differences in material properties under different sodium contents to '
                'determine the optimal sodium content.',

                'We synthesized P2-Na0.67+xNi0.33Mn0.67O2 (x = 2 %, 2.5 %, 3 %, 3.5 %, 4 %) '
                'with different sodium contents by solid state method, and compared the '
                'differences in material properties under different sodium contents to '
                'determine the optimal sodium content.'
            ),

            (  # 1
                'O3-type layered Na(Ni0.4Cu0.1Mn0.4Ti0.1)1-xLaxO2 (x = 0 , 0.001 , 0.003 , '
                '0.005 , termed as NMCT, NMCT-Lax , respectively), which is consistent with '
                'the data of No. 1535056 (tetragonal Na3V2(PO4)2O2F, abbreviated as NVPOF) in '
                'Inorganic Crystal Structure Database.',

                'O3-type layered Na(Ni0.4Cu0.1Mn0.4Ti0.1)1-xLaxO2 (x = 0 , 0.001 , 0.003 , '
                '0.005 , termed as NMCT, NMCT-Lax , respectively), which is consistent with '
                'the data of No. 1535056 (tetragonal Na3V2P2O10F, abbreviated as NVPOF) in '
                'Inorganic Crystal Structure Database.'
            ),

            (  # 2
                'In this work, the obtained layered O3-type NaFe9/20Cr9/20Ti1/10O2 delivered '
                'a high initial discharge capacity of 140.63 mAh g−1 compared to '
                'Na0.66Fe1/3Cr1/3Ti1/3O2 cathode material, which delivered discharge capacity '
                'of 135.5 mAh g−1[7]',

                'In this work, the obtained layered O3-NaTi0.1Cr0.45Fe0.45O2 delivered a high '
                'initial discharge capacity of 140.63 mAhg-1 compared to '
                'Na0.66Ti0.33Cr0.33Fe0.33O2 cathode material, which delivered discharge '
                'capacity of 135.5 mAhg-1[7]'),

            (  # 3
                'The compositions of h-NM, h-NMC and h-NMC2 are identified as Na0.66MnO2, '
                'Na0.65Mn0.9Cu0.1O2 and Na0.63Mn0.8Cu0.2O2, based on ICP-AES results (Table '
                'S1).',

                'The compositions of h-NM, h-NMC and h-NMC2 are identified as Na0.66MnO2, '
                'Na0.65Mn0.9Cu0.1O2 and Na0.63Mn0.8Cu0.2O2, based on ICP-AES results (Table '
                'S1).'
            ),

            (  # 4
                'An initial reversible capacity of 131.3 mAhg-1 at 0.1 C can been seen for '
                'the P2-NMNCC electrode, which maintained a retention of 86.7 % after 200 '
                'cycles with an average Coulombic efficiency of approximately 99 % . Whereas '
                'the P2-NMNC electrode only had 71.9 % initial capacity retention after 200 '
                'cycles at 0.1 C . and then drying in a vacuum at 80 °C . First, selenium '
                'powder was dispersed into 5 mg mL-1 graphite oxide (GO) solution by '
                'sonication for 10 hours, followed by a freeze-drying process of 48 hours.',

                'An initial reversible capacity of 131.3 mAhg-1 at 0.1 C can been seen for '
                'the P2-NMNCC electrode, which maintained a retention of 86.7 % after 200 '
                'cycles with an average Coulombic efficiency of approximately 99 % . Whereas '
                'the P2-NMNC electrode only had 71.9 % initial capacity retention after 200 '
                'cycles at 0.1 C . and then drying in a vacuum at 80 °C . First, selenium '
                'powder was dispersed into 5 mg mL-1 graphite oxide (GO) solution by '
                'sonication for 10 hours, followed by a freeze-drying process of 48 hours.'),

            (  # 5
                'is still over 99.5% after 10, 000 cycles which presents a high degree of the '
                'electrochemical. Density functional theory calculations and ab initio '
                'molecular dynamics simulations are performed to study the feasibility of '
                'using borophene, a newly synthesized two-dimensional sheet of boron, as an '
                'anode material for sodium-ion and sodium-O2 batteries. The theoretical '
                'capacity of borophene is found to be as high as 1,218mAhg-1 (Na0.5B).  '
                '(Li0.75B, 1,860mAhg-1),',

                'is still over 99.5% after 10, 000 cycles which presents a high degree of the '
                'electrochemical. Density functional theory calculations and ab initio '
                'molecular dynamics simulations are performed to study the feasibility of '
                'using borophene, a newly synthesized two-dimensional sheet of boron, as an '
                'anode material for sodium-ion and sodium-O2 batteries. The theoretical '
                'capacity of borophene is found to be as high as 1218mAhg-1 (Na0.5B). '
                '(Li0.75B, 1860mAhg-1),'
            ),

            (  # 6
                'The O3-type Na((Mn0.4Fe0.3Ni0.3)1-xTix)O2 (x = 0 and 0.1) powders were '
                'synthesized using a simple solid-state method. First, stoichiometric amounts '
                'of Na2CO3 (Sigma Aldrich), Mn2O3 (Sigma Aldrich), Fe2O3 (Sigma Aldrich), NiO '
                '(Sigma Aldrich), and TiO2 (Sigma Aldrich) powders were mixed using an agate '
                'mortar.',

                'The O3-Na((Mn0.4Fe0.3Ni0.3)1-xTix)O2 (x = 0 and 0.1) powders were '
                'synthesized using a simple solid-state method. First, stoichiometric amounts '
                'of Na2CO3 (Sigma Aldrich), Mn2O3 (Sigma Aldrich), Fe2O3 (Sigma Aldrich), NiO '
                '(Sigma Aldrich), and TiO2 (Sigma Aldrich) powders were mixed using an agate '
                'mortar.'
            ),

            (  # 7
                'Na0.70Ni0.20Cu0.15Mn0.65O2 (NNCM) powder was synthesized through the sol-gel '
                'route. Stoichiometric amounts of nickelacetatetetrahydrate, '
                'Copper(II)nitratetrihydrate, manganese(II)acetatetetrahydrate, and '
                'sodiumcarbonate were dissolved in distilled water and were then stirred for '
                '5 h. Appropriate amounts of citric acid & ethyleneglycol were added to the '
                'solution. The mixed solution was further stirred for another 10 h followed '
                'by heating at 100 °C to make a gel. The gel was dried at 150 °C and ground '
                'using a pestle and mortar. The resulting powder was calcinated at 550 °C for '
                '12 h and ground again. Subsequently, the ground powder was calcined at '
                'different temperatures (700 °C, 800 °C, 850 °C, and 950 °C) for 12 h in air '
                'and cooled to room temperature in the same furnace.',

                'Na0.7Mn0.65Ni0.2Cu0.15O2 (NNCM) powder was synthesized through the sol-gel '
                'route. Stoichiometric amounts of nickelacetatetetrahydrate, '
                'Coppernitratetrihydrate, manganeseacetatetetrahydrate, and sodiumcarbonate '
                'were dissolved in distilled water and were then stirred for 5 h. Appropriate '
                'amounts of citric acid & ethyleneglycol were added to the solution. The '
                'mixed solution was further stirred for another 10 h followed by heating at '
                '100 °C to make a gel. The gel was dried at 150 °C and ground using a pestle '
                'and mortar. The resulting powder was calcinated at 550 °C for 12 h and '
                'ground again. Subsequently, the ground powder was calcined at different '
                'temperatures (700 °C, 800 °C, 850 °C, and 950 °C) for 12 h in air and cooled '
                'to room temperature in the same furnace.'
            ),

            (  # 8
                'Therefore, NaNi0.45Mn0.3Ti0.2Zr0.05O2 exhibits an initial reversible '
                'capacity of 141.4\u202fmAh g−1 with a coulombic efficiency of 98.8% '
                'and remarkable capacity retention of 70% after 200 cycles at 0.05C, '
                'presenting better electrochemistry performance than the conventional '
                'NaNi0.5Mn0.5O2.',

                'Therefore, NaZr0.05Ti0.2Mn0.3Ni0.45O2 exhibits an initial reversible '
                'capacity of 141.4mAhg-1 with a coulombic efficiency of 98.8% and remarkable '
                'capacity retention of 70% after 200 cycles at 0.05C, presenting better '
                'electrochemistry performance than the conventional NaMn0.5Ni0.5O2.'
            ),

            (  # 9
                'Conversely, Na||P2-NaMN shows severe capacity loss at −40\u2009°C and '
                '920\u2009mA\u2009g−1 (Fig. 4c) and a discharge capacity retention of 77.8% '
                'after 215 cycles at RT (Supplementary Fig. 19). The rest of the composites, '
                'Na3Mn1-xCrxTi(PO4)3 (x=0.01, 0.03, 0.05, 0.07, 0.10, 0.12, 0.15), are '
                'denoted as 1%Cr-NMTP, 3%Cr-NMTP, 5%Cr-NMTP, 7%Cr-NMTP, 10%Cr-NMTP, '
                '12%Cr-NMTP, and 15%Cr-NMTP, respectively. At present, the most studied '
                'candidate materials are Na3V2P3O12 and Na3V2P2O8F3 (NVPF) <CR>. The '
                'schematic procedure for the synthesis of NaCo0.15Ni0.815Al0.035O2 via '
                'hydrothermal method (named as NCA-Hydro) is shown in Fig. S1(a). <FIG> '
                'depicts XRD patterns for Na2MgNiTeO6 (NMNTO) and Na2MgZnTeO6 (NMZTO) '
                'materials prepared via a solid-state reaction method and XRD pattern of '
                'Na2Mg2TeO6 (NMTO) is also added for comparison. Pristine P2-Na0.67MnO2 (NMO) '
                'and Mo-doped P2-Na0.67Mn1-xMoxO2 (x=0.01, 0.03 and 0.05, defined as NMMO-x '
                '(x=1, 3, 5)) were synthesized via a solid-state reaction, and pure P2 phase '
                'is obtained for x≤0.05, as shown in <FIG>. Pristine P2-Na0.67MnO2 (NMO) and '
                'Mo-doped P2-Na0.67Mn1-xMoxO2 (x = 0.01, 0.03 and 0.05, defined as NMMO-x (x '
                '= 1, 3, 5)) were synthesized via a solid-state reaction, and pure P2 phase '
                'is obtained for x ≤ 0.05, as shown in Fig. S1. All series of layer/tunnel '
                'composite materials (Na0.60Mn1-x-yFexTiyO2, x = 0, 0.05, 0.1, y = 0, 0.05, '
                '0.1, namely Na0.6MnO2, Na0.6Mn0.95Fe0.05O2, Na0.6Mn0.9Fe0.1O2, '
                'Na0.6Ti0.05Mn0.95O2, Na0.6Ti0.1Mn0.9O2, Na0.6Ti0.05Mn0.9Fe0.05O2 and '
                'Na0.6Ti0.1Mn0.8Fe0.1O2, marked as MFT0, MF5, MF10, MT5, MT10, MFT5 and '
                'MFT10) samples were synthesized by co-precipitation method and '
                'high-temperature solid-state reaction. ',

                'Conversely, Na||P2-NaMN shows severe capacity loss at -40°C and 920mAg-1 '
                '(Fig. 4c) and a discharge capacity retention of 77.8% after 215 cycles at RT '
                '(Supplementary Fig. 19). The rest of the composites, Na3Mn1-xCrxTi(PO4)3 '
                '(x=0.01, 0.03, 0.05, 0.07, 0.10, 0.12, 0.15), are denoted as 1%Cr-NMTP, '
                '3%Cr-NMTP, 5%Cr-NMTP, 7%Cr-NMTP, 10%Cr-NMTP, 12%Cr-NMTP, and 15%Cr-NMTP, '
                'respectively. At present, the most studied candidate materials are '
                'Na3V2P3O12 and Na3V2P2O8F3 (NVPF) <CR>. The schematic procedure for the '
                'synthesis of NaCo0.15Ni0.81Al0.04O2 via hydrothermal method (named as '
                'NCA-Hydro) is shown in Fig. S1(a). <FIG> depicts XRD patterns for '
                'Na0.67Mg0.33Ni0.33Te0.33O2 (NMNTO) and Na0.67Mg0.33Zn0.33Te0.33O2 (NMZTO) '
                'materials prepared via a solid-state reaction method and XRD pattern of '
                'Na0.67Mg0.67Te0.33O2 (NMTO) is also added for comparison. Pristine '
                'P2-Na0.67MnO2 (NMO) and Mo-doped P2-Na0.67Mn1-xMoxO2 (x=0.01, 0.03 and 0.05, '
                'defined as NMMO-x (x=1, 3, 5)) were synthesized via a solid-state reaction, '
                'and pure P2 phase is obtained for x≤0.05, as shown in <FIG>. Pristine '
                'P2-Na0.67MnO2 (NMO) and Mo-doped P2-Na0.67Mn1-xMoxO2 (x = 0.01, 0.03 and '
                '0.05, defined as NMMO-x (x = 1, 3, 5)) were synthesized via a solid-state '
                'reaction, and pure P2 phase is obtained for x ≤ 0.05, as shown in Fig. S1. '
                'All series of layer/tunnel composite materials (Na0.60Mn1-x-yFexTiyO2, x = '
                '0, 0.05, 0.1, y = 0, 0.05, 0.1, namely Na0.6MnO2, Na0.6Mn0.95Fe0.05O2, '
                'Na0.6Mn0.9Fe0.1O2, Na0.6Ti0.05Mn0.95O2, Na0.6Ti0.1Mn0.9O2, '
                'Na0.6Ti0.05Mn0.9Fe0.05O2 and Na0.6Ti0.1Mn0.8Fe0.1O2, marked as MFT0, MF5, '
                'MF10, MT5, MT10, MFT5 and MFT10) samples were synthesized by '
                'co-precipitation method and high-temperature solid-state reaction.'
            ),

            (  # 10
                'The rate performance of NaFe0.5 Mg0.5 O2 different current density is 158, '
                '150, 141,133,121 mAh g−1 at 50, 100, 200, 400, 800\xa0mA /g respectively. '
                '(Na2/3Ni1/3Mn2/3O2, P2-NNMO) The Na3Mn1-xCrxTi(PO4)3 (x=0, 0.01, 0.03, 0.05, '
                '0.07, 0.10, 0.12, 0.15) cathode materials series were synthesized through a '
                'feasible sol-gel method. A slight decrease in the capacity was confirmed in '
                'the Ti-substituted Na[(Mn0.4Fe0.3Ni0.3)1−xTix]O2 (for x = 0, 167 mAh g−1; x '
                '= 0.1, 151 mAh g−1 at 24 mA g−1) Nominal Na0.6(Li0.2Mn0.8)O2 with the '
                'layered P3 structure (s.g. R3m) showed XPS evidence of holes in the O-2p '
                'bands on removal of Na+ ions. A large voltage plateau at 4.1 V versus Na+/Na '
                'faded significantly over 50 cycles although the capacity in the range 20 ≤ V '
                '< 4.5 V remained unchanged. Oxidation of the O-2p bands is not reversible. '
                'At a rate of 0.5C, NMCO_750 exhibited a high gravimetric capacity of 84\xa0'
                'mA\xa0h\xa0g−1, which was higher than NMCO_650 (80\xa0mA\xa0h\xa0g−1) and '
                'NMCO_850 (77\xa0mA\xa0h\xa0g−1).',

                'The rate performance of NaMg0.5Fe0.5O2 different current density is 158, '
                '150, 141,133,121 mAhg-1 at 50, 100, 200, 400, 800mAg-1 respectively. '
                '(Na0.67Mn0.67Ni0.33O2, P2-NNMO) The Na3Mn1-xCrxTi(PO4)3 (x=0, 0.01, 0.03, '
                '0.05, 0.07, 0.10, 0.12, 0.15) cathode materials series were synthesized '
                'through a feasible sol-gel method. A slight decrease in the capacity was '
                'confirmed in the Ti-substituted Na((Mn0.4Fe0.3Ni0.3)1-xTix)O2 (for x = 0, '
                '167 mAhg-1; x = 0.1, 151 mAhg-1 at 24 mAg-1) Nominal Na0.6Li0.2Mn0.8O2 with '
                'the layered P3 structure (s.g. R3m) showed XPS evidence of holes in the O-2p '
                'bands on removal of Na+ ions. A large voltage plateau at 4.1V versus Na/Na '
                'faded significantly over 50 cycles although the capacity in the range 20 ≤ V '
                '< 4.5V remained unchanged. Oxidation of the O-2p bands is not reversible. At '
                'a rate of 0.5C, NMCO_750 exhibited a high gravimetric capacity of 84mAhg-1, '
                'which was higher than NMCO_650 (80mAhg-1) and NMCO_850 (77mAhg-1).'
            ),

            (  # 11
                'A simple sol-gel method was used to synthesize the P2-type NMNCC and NMNC '
                'cathode materials. Manganese(II)acetate tetrahydrate, nickel(II)acetate '
                'tetrahydrate, cobalt(II)acetate tetrahydrate, copper(II)acetate monohydrate '
                'and sodiumcarbonate anhydrous were dissolved into a citric acid solution '
                'with a corresponding stoichiometric ratio',

                'A simple sol-gel method was used to synthesize the P2-type NMNCC and NMNC '
                'cathode materials. Manganeseacetate tetrahydrate, nickelacetate '
                'tetrahydrate, cobaltacetate tetrahydrate, copperacetate monohydrate and '
                'sodiumcarbonate anhydrous were dissolved into a citric acid solution with a '
                'corresponding stoichiometric ratio'
            ),

            (  # 12
                'P2-Na0.67Ni0.33Mn0.67O2-yFy (y = 0 , 0.05 , 0.1 , 0.15 , abbreviated as '
                'NaNMO, NaNMOF0.05, NaNMOF0.1, NaNMOF0.15, respectively) and '
                'P2-Na0.67Ni0.33Mn0.67-xTixO1.9F0.1 (x = 0.1 , 0.2 , 0.3 , 0.4 , abbreviated '
                'as NaNMTi0.1OF, NaNMTi0.2OF, NaNMTi0.3OF, and NaNMTi0.4OF, respectively) '
                'were synthesized by solid-state reaction.',

                'P2-Na0.67Ni0.33Mn0.67O2-yFy (y = 0 , 0.05 , 0.1 , 0.15 , abbreviated as '
                'NaNMO, NaNMOF0.05, NaNMOF0.1, NaNMOF0.15, respectively) and '
                'P2-Na0.67Ni0.33Mn0.67-xTixO1.9F0.1 (x = 0.1 , 0.2 , 0.3 , 0.4 , abbreviated '
                'as NaNMTi0.1OF, NaNMTi0.2OF, NaNMTi0.3OF, and NaNMTi0.4OF, respectively) '
                'were synthesized by solid-state reaction.'
            ),

            (  # 13
                'Here we synthesized an O3-NaNi0.5-xMn0.3Ti0.2ZrxO2 (NaNMTZ , x=0.02,0.05 , '
                'NaNMTZ2, NaNMTZ5) by co-substituting NaNi0.5Mn0.5O2 (NaNM) with Ti and Zr. '
                'In this work, the influence of co-substitution of Ti and Zr on '
                'NaNi0.5Mn0.5O2 was studied.',

                'Here we synthesized an O3-NaNi0.5-xMn0.3Ti0.2ZrxO2 (NaNMTZ,x=0.02,0.05 , '
                'NaNMTZ2, NaNMTZ5) by co-substituting NaMn0.5Ni0.5O2 (NaNM) with Ti and Zr. '
                'In this work, the influence of co-substitution of Ti and Zr on '
                'NaMn0.5Ni0.5O2 was studied.'
            )

        ]

        for text in texts:
            bat = BatteriesTextProcessor(text[0], special_normal=True)
            self.assertEqual(' '.join(bat.processed_text), text[1])
