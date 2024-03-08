# coding=utf-8
"""
Some priori patterns and prompt words
"""
import regex as re

BACKSLASH_REPLACEMENT = PARAGRAPH_SEPARATOR = '$$'

ATTRIBUTE_PROMPT = ['voltage', 'mAhg-1', 'V', 'capacit', 'mAg-1', 'C', 'Ag-1', 'mAg-1']

VAR = {'x', 'y', 'z', 'δ'}

ELEMENTS = ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K",
            "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br", "Kr",
            "Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn", "Sb", "Te", "I",
            "Xe", "Cs", "Ba", "La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb",
            "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg", "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr",
            "Ra", "Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr", "Rf",
            "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn", "Nh", "Fl", "Mc", "Lv", "Ts", "Og", "Uue"]

ELEMENT_VALENCE = re.compile(r"(" + r"|".join(ELEMENTS) + r")\s*(\(([Ii]?[Vv]?[Ii]{0,2})\))")
ELEMENT_VALENCE2 = re.compile(r"(\([1-9]\))\s*(" + r"|".join(ELEMENTS) + r")")

ELEMENT_NAMES = ["hydrogen", "helium", "lithium", "beryllium", "boron", "carbon", "nitrogen", "oxygen", "fluorine",
                 "neon", "sodium", "magnesium", "aluminium", "silicon", "phosphorus", "sulfur", "chlorine", "argon",
                 "potassium", "calcium", "scandium", "titanium", "vanadium", "chromium", "manganese", "iron",
                 "cobalt", "nickel", "copper", "zinc", "gallium", "germanium", "arsenic", "selenium", "bromine",
                 "krypton", "rubidium", "strontium", "yttrium", "zirconium", "niobium", "molybdenum", "technetium",
                 "ruthenium", "rhodium", "palladium", "silver", "cadmium", "indium", "tin", "antimony", "tellurium",
                 "iodine", "xenon", "cesium", "barium", "lanthanum", "cerium", "praseodymium", "neodymium",
                 "promethium", "samarium", "europium", "gadolinium", "terbium", "dysprosium", "holmium", "erbium",
                 "thulium", "ytterbium", "lutetium", "hafnium", "tantalum", "tungsten", "rhenium", "osmium",
                 "iridium", "platinum", "gold", "mercury", "thallium", "lead", "bismuth", "polonium", "astatine",
                 "radon", "francium", "radium", "actinium", "thorium", "protactinium", "uranium", "neptunium",
                 "plutonium", "americium", "curium", "berkelium", "californium", "einsteinium", "fermium",
                 "mendelevium", "nobelium", "lawrencium", "rutherfordium", "dubnium", "seaborgium", "bohrium",
                 "hassium", "meitnerium", "darmstadtium", "roentgenium", "copernicium", "nihonium", "flerovium",
                 "moscovium", "livermorium", "tennessine", "oganesson", "ununennium"]

ELEMENTS_NAMES_UL = set(ELEMENT_NAMES + [en.capitalize() for en in ELEMENT_NAMES])
ELEMENT_NAMES_VALENCE = re.compile(r"(" + r"|".join(
    ELEMENT_NAMES + [en.capitalize() for en in ELEMENT_NAMES]) + r")\s*(\(([Ii]?[Vv]?[Ii]{0,2})\))")

TRANSITION_ME = ["Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
                 "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd",
                 "Lu", "Hf", "Ta", "Re", "Os", "Ir", "Pt", "Au", "Hg",
                 "Lr", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn"]

BATTERIES = ['Na', 'Li']

BATTERIES_TML = BATTERIES + TRANSITION_ME + ['O']

TMB = set(TRANSITION_ME + ["Mg", "Al"] + BATTERIES)

AC = ['C', 'H', 'O']

INERT_GAS = ["He", "Ne", "Ar", "Kr", "Xe", "Rn"]

GAS = ["Ar", 'air', 'O2']

METAL_TYPES = {  # "non_metals": ['H', 'C', 'N', 'O', 'F', 'Cl', 'S', 'P', 'Se', 'Br', 'I'],
    "alkali_me": ['Li', 'Na', 'K', 'Rb', 'Cs'],
    "alkaline_me": ['Be', 'Ca', 'Sr', 'Ba'],
    "transition_me_4": ['Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn'],
    "transition_me_5": ['Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd'],
    "transition_me_6": ['Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg'],
    "lanthanoid": ['La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Yb', 'Lu'],
    "other_me": ['B', 'Al', 'Ga', 'In', 'Tl', 'Si', 'Ge', 'Sn', 'Pb', 'As', 'Sb', 'Bi', 'Te'],
}

POLYATOMIC_IONS = {'CO3', 'PO4', 'PO3', 'P2O7', 'NH4', 'NO3', 'NO2', 'SO4', 'SO3', 'OH', 'CN', 'SiO4'}
SIMPLE_COMPOUND = ['NaHO', 'NaCl', 'NaF', 'NaBr', 'Na2S2', 'Na2CO3']
# m_anions = ['H2PO4', 'HPO4', 'HCO3', 'HSO4', 'HSO3', 'C2O4']
# d_anions = ['CO3', 'PO4', 'PO3', 'NH4', 'NO3', 'NO2', 'SO4', 'SO3', 'OH', 'CN']
# s_anions = ['O', 'H', 'N', 'C', 'F', 'S', 'B', 'P']
# acetates = {'CH3COO', "CH3CO2"}
# ions = m_anions + d_anions + s_anions + ['Cl'] + ['Org'] + ['Ac'] + ['Elem']

SOLVENT_NAMES = ['ethanol', 'dimethylformamide', 'methyl', 'pyrrolidone']  # 溶剂

RAW_MATERIAL = ['CH3COO', 'OCH2CH3', 'OAc', 'NO', 'CO3', 'OH', 'SO4', 'NH2', 'BO3', 'NH3', 'NH4',
                'CTAB', 'transition', 'Nitrates', 'H2O']

APPARATUS = {'XRD', 'XPS', 'SEM', 'EDS', 'TEM', 'ESI', 'XAS', 'EXAFS', 'AFM', 'UV', 'XANES'}

GREEK_CHARS = {chr(i) for i in range(945, 970)}

OTHER = {'JCPDS', 'JCPSD', 'RT', 'SOC', 'ICP', 'SIB', 'DFT', 'STA', 'ICSD', 'HITACH', 'NIST', 'PAL', 'TXM', 'SXRPD',
         'PVDF', 'DFPT', 'CNTs', 'USP', 'ALD', 'PH3', 'CV', 'CS', 'PC', 'OC', 'CB', 'ND', 'TG', 'NPs',
         'Na-rich', 'Na-ion'}

OTHER_IN = ['PDF', 'No.', '↔', 'Nae', 'Fig',
            'AB',  # AB ABCABC...
            'Non',  # Non-sub
            ]

ABB_SHAPE = ['XXdd', 'XXX', 'XXd', 'XxXX', 'Xddd']

NUMBER_REGEX = r'\d++[\d. ]*+'

re_phase_prefix = re.compile(r"^([A-Za-z" + ''.join(GREEK_CHARS) + r"][0-9]{0,1}|Air|Oxy|(?=P|O)[/PO\d and-]+)\-[A-Z]\.*")

# html、xml Fig tag
fig_pattern = re.compile(r'fig', re.I)

REPLACE = [
    ('•', '·'),
    ('&lt;', '<'),
    ('&gt;', '>'),
    ('∕', '/'),
    ('~', ' ~ '),
    ('~', ' ~ '),
    ('≈', ' ≈ '),
    ('。', '. ')
]

digit = r'(\d+(\.\d+)?)'

SUB = [
    #  space correction
    (r'\b(to|and|or)(\d)', r'\1 \2'),
    (r'with×=', 'with x='),
    #  Unit unity
    (r'[\s\.·/]{0,1}'.join(list('mAhg')) + r'[-\s1]*(?<=1|g)', 'mAhg-1'),
    (r'\s?'.join(list('mAg-1')) + '|' + r'\s?'.join(list('mA/g')) + '|' + r'\s?'.join(list('mA·g-1')), 'mAg-1'),
    (r'(?<!m)' + r'[\s.·/]{0,1}'.join(list('Ag-1')), 'Ag-1'),
    (r'\s?'.join(list('◦C')) + '|' + r'℃' + '|' + r'\s?'.join(list('°C')), '°C'),
    (digit + r'[ V]+-\s?' + digit + r'\s?V\b', r'\1-\3 V'),
    (r'(?<=\d)\s?V\b(?!\.)', 'V'),
    (r'(?<=\d)\s?V\s?(?=\.)', 'V'),
    (r'cycled for (\d+) times', r'\1 cycles'),
    (r'\b([\d]+)[ ]*(?:st|rd|nd|th|times)?[ ]*(cycle(?:s)?)\b', r' \1 \2'),
    (r'( \d+)(?:th|nd|st)(?!\s?cycle)', r'\1'),
    ('((?:first|all) three cycles|first, second and third cycle)', '1, 2, and 3 cycle'),
    (r'first-?(?=\s?cycle)', '1'),
    (r'second(?=\s?cycle)', '2'),
    (r'third(?=\s?cycle)', '3'),
    (r'fiftieth\b', '50'),
    #  Scientific notation
    (r'(\d)\s?,\s?(0\d+\s?[c°])', r'\1\2'),
    (r'(?<!-|\d)(\d),(\d+\s?mA)', r'\1\2'),
    #  phase prefix
    (r'([PO][23]-)type (?=Na)', r'\1'),
    (r'\s{2,3}', ' '),

]

from word2number.w2n import american_number_system

SUB.extend((key + r"\b", str(value)) for key, value in list(american_number_system.items())[3: -4])

# Conflict Acknowledgements
c_a_pattern = re.compile(r'Acknowledgements?|References?|Conflicts?|Author', re.I)

# Experimental Characterization
characteristic_pattern = re.compile(
    '|'.join(['X-Ray', 'XRD', 'SEM', 'EDS', 'TEM', 'ESI', 'XAS', 'EXAFS', 'AFM', 'UV', 'XANES']))

# Charge and discharge
charge_discharge_pattern = re.compile(r'(?:discharge|charge)\W(?:discharge|charge)')

cycle_ca_pattern = [
    re.compile(r'\b\d[\d. ]+mAhg-1 (?:\([^()]+\) )?(?>after|for|at) (?:the )?\d+\s?cycle(s)?'
               r'|'
               r'after[ \d]+cycles (at[ .\d]+C )?(?>was|is)( only)?[ .\d]+mAhg-1'),
    re.compile(r'^(After|By|Even)[ a-z]++\d+\s?cycles'
               r'|'
               r'^Cycling'),  # Adverbial clause
    re.compile(r'% \([ \d.\w]+mAhg-1[ \d\w]+\)')  # Capacity retention rate supplementary description
]

# The closing parentheses should not be separated
end_par_not_split_pattern = re.compile(r'\((' + '|'.join(POLYATOMIC_IONS) + r')\)$')

# IGNORE_SUFFIX  -graphene
ignore_suffix_pattern = re.compile(r'(?i:-(hydro))')

add_infor_pattern = re.compile(r'\s?\(((?>[^()]|(?R))*)\)(?!\w)')

# named as marked as noted as
abb_named_pattern = re.compile('name(?:d|ly)|marked|noted|labeled|denoted|identified|referred|abbreviated')

# Temperature time
t_c_pattern = re.compile(r'(?P<T>\d{2,3}+[-/(\d, airtond)]*°C(?![\s/]*min[-1]*))'
                         r'|'
                         r'(?P<H>\b\d[-/(\d,. orand)]*h(?>rs|oursh|ours?)?\b(?! to reach))')

# Coulombic efficiencies, CE
coulomb_efficiency_assert = re.compile(r'(?i:cou?l[ou]mb(ic)? efficienc(y|ies)|efficiency)|\b(CE|ICE)\b')

global_voltage = re.compile(r'(\d[\d.]*+)\s?(?>-|to|and)\s?(\d[\d.]*+)\s?(?=V\b)')  # cutoff potentials

# 1.0C = 200 mAg-1, 17 mA g-1 (0.1 C)
current_define_pattern = re.compile(r'(?|\b(' + NUMBER_REGEX + r')C\s?=\s?(' + NUMBER_REGEX + r')\s?mAg-1\b|'  # CM
                                                                                              r'(' + NUMBER_REGEX + r')mAg-1\s?\((' + NUMBER_REGEX + r')C\s?\)|'  # MC
                                                                                                                                                     r'(' + NUMBER_REGEX + r')C\s?\((' + NUMBER_REGEX + r')\s?mAg-1\s?\))')  # CM

# Performance properties
cycle_rate_capacity = {'cycle': r'(?(DEFINE)'
                                r'(?P<FIRST>(initial|first))'
                                r'(?P<CHARGE>(charge|discharge)(\W(?3))*))'
                                r'(?<= )((\d++[\d,/ andoghscueirTtn]*? (?=cycle|(?&CHARGE) capacit))'
                                r'|(?&FIRST)'
                                r'('
                                r'|( (?&CHARGE))?( specific| reversible)? capacit(?>y|ies)(?=.+?mAhg-1)'
                                r'|[ -]*((?&CHARGE)|cycle)'
                                r'))',  # initial first
                       'capacity: mAhg-1': r'(?<!-|=)\b\d[\d.,~/ toand]*+mAhg-1',
                       'retention: %': r'(?<=\bretention.)[^%]*+%(?! higher)([^%\n](?>[^%]+|(?1))%(?! higher))*'
                                       r'|(?<=[ ~()])\d[\d.,and ]*+%[^%]+? (?=capacity|retention)',
                       'current: C': r'(?<![-.])\b(\d[/\d.,toand ]*+C\b(?!=)|(?<fraction>(?<![°@])C\s?/\s?\d+))',
                       # 1C  C/100
                       'current: mAg-1': r'(?<![-=])\b\d[\d.,~/ toand]*+mAg-1',
                       'current: Ag-1': r'(?<!-)\b\d[\d.,/ toand]*+Ag-1'
                       }
for _ in cycle_rate_capacity:
    cycle_rate_capacity[_] = re.compile(cycle_rate_capacity[_])
