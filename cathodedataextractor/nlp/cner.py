# coding=utf-8
"""
This module provides a class for assisted chemical named entity recognition (CNER) and post-processing.
"""
import logging
from typing import Tuple, Union
from string import digits
from collections import OrderedDict
from functools import lru_cache

from pymatgen.core.periodic_table import _pt_data
from pymatgen.core.composition import Composition

from chemdataextractor.text import word_shape, like_number, QUOTES

from cathodedataextractor.cathodetext2chem import (
    CathodeParserPipelineBuilder,
    CathodeRegExParser
)

from text2chem.preprocessing_tools.chemical_name_processing import ChemicalNameProcessing
from text2chem.postprocessing_tools.element_variables_processing import ElementVariablesProcessing
from text2chem.postprocessing_tools.stoichiometric_variables_processing import StoichiometricVariablesProcessing

from ..parse import *
from ..utils import if_num_dot, any_func

log = logging.getLogger(__name__)
mp = CathodeParserPipelineBuilder() \
    .add_preprocessing(ChemicalNameProcessing) \
    .add_postprocessing(ElementVariablesProcessing) \
    .add_postprocessing(StoichiometricVariablesProcessing) \
    .set_regex_parser(CathodeRegExParser) \
    .build()


class CNer:
    """
    Post-processing of CNER with domain knowledge rules.
    """

    def __init__(self, tm_limit: bool = False, prompt_element: str = 'Na'):
        """

        Args:
            tm_limit (bool): Whether to limit the inclusion of transition metal elements.
            prompt_element (str): Battery type, e.g. 'Na', 'Li', etc.

        """
        self.tm_limit = tm_limit
        self.prompt_element = prompt_element

    @lru_cache(None)
    def normalized_compound_formula(self, cem: str) -> str:
        """
        Normalized treatment of inorganic chemical formulas.

        Sorting of elements, removal of redundant brackets, Spaces and valences,
        supplementary information boundary correction, fraction conversion to decimals, etc.
        """
        if not cem or '|' in cem:  # Na|Na2/3Mn1/3Fe1/3Ni1/3O2
            return cem

        def normalize(text):
            for quote in QUOTES:  # Convert all apostrophes, quotes, accents, primes to single ascii apostrophe
                text = text.replace(quote, "'")
            # Convert all brackets to regular parentheses
            for ob in {'[', '{', '&lt;'}:
                text = text.replace(ob, '(')
            for cb in {']', '}', '&gt;'}:
                text = text.replace(cb, ')')
            return text.replace("'", '').replace('\n', '').replace('--', '-').replace('(<CR>)', '')

        cem = normalize(cem)

        # Match the most informative bracket at the end and normalize accordingly
        bracket_index, _st = end_parentheses(cem)
        if bracket_index:
            # Na0.67Ni0.28Mn0.67Y0.05O2 (NMY-5 , (NNM) (NNM2)
            cem = cem[:bracket_index]

        # Remove valence
        def remove_valence(cem, sign='+', start=0):
            idx = cem.find(sign, start)
            if idx == 0:
                return remove_valence(cem, start=start+1)
            if idx == -1:
                oxygen_idx = cem.find("O", start)
                while oxygen_idx > -1:
                    valence_l = valence_r = None
                    for i in range(oxygen_idx + 1, len(cem)):
                        if valence_l is None and cem[i].isdigit():  # 1
                            valence_l = i
                        elif cem[i] == "-":  # 2
                            valence_r = i
                        elif cem[i] == " ":  # 1 2 3
                            continue
                        elif valence_r is not None and cem[i].isdigit():  # 3
                            valence_r = i
                            break
                        else:
                            valence_r = None
                            break
                    if valence_l and valence_r:
                        cem = cem[:valence_l] + cem[valence_r:]
                    oxygen_idx = cem.find("O", oxygen_idx + 1)
                return cem
            window = cem[idx - 1: idx + 2]
            if window[-1] in VAR:
                return remove_valence(cem, start=idx + 2)
            elif window[0].isdigit():
                return remove_valence(cem[:idx - 1] + cem[idx + 1:], start=idx - 1)
            else:
                return remove_valence(cem[:idx] + cem[idx + 1:], start=idx)

        cem = remove_valence(cem)

        def final_processing(cem):
            elem_with_valence = ELEMENT_VALENCE.search(cem)

            elem_with_valence2 = ELEMENT_VALENCE2.search(cem)

            if elem_with_valence:
                return final_processing(cem.replace(elem_with_valence.group(2), '', 1).replace('  ', ' '))
            elif elem_with_valence2:
                return final_processing(cem.replace(elem_with_valence2.group(1), '', 1).replace('  ', ' '))
            else:
                # Na0.8(Li0.33Mn0.67-xTix)O2withx=0.1, Na0.67Ni0.33Mn0.67-xSnxO2||Na (x=0, 0.01, 0.03 and 0.05)
                if not any_func(cem, ['with', 'of', '%']):
                    if 'H2O' not in cem:  # Hydrate
                        cem = cem.replace('·', '.').replace('•', '.')
                    else:  # Ni(NO3)2 · 6H2O
                        return cem.replace(' ', '')

                    if self.prompt_element in cem:
                        cem = cem.replace('Oxygen-', '').replace('oxides', '').replace('oxide', '').replace(' ', ''). \
                            replace('Air-', '').replace('Oxy-', '')
                        # cell structure, exclude 'P2/O3-'
                        if not re.search(r'\d/(?!O|P)[A-Za-z]|@|//', cem):
                            try:
                                cem = self.iupac_formula(cem)
                            except Exception as e:
                                log.info('%s  %s', cem, e)

                    elif any_func(cem, METAL_TYPES["transition_me_4"]):
                        cem = cem.replace(' ', '')
                return cem

        return final_processing(cem) + (' ' + _st if _st else '')

    @lru_cache(None)
    def prompt_tag(self, cem: str, normalize=False) -> str:
        """
        Further classification of chemical entities.

        Return:
            A prompt tag.
        """
        cem = self.chem_backbone(cem).split(',')[0]
        if cem in set(ELEMENTS):
            return 'element'
        elif cem in ELEMENTS_NAMES_UL:
            return 'element_name'
        elif cem in POLYATOMIC_IONS:
            return 'polyatomic_ions'
        elif cem in SIMPLE_COMPOUND:
            return 'simple'
        elif self.is_word(cem):
            return 'other'
        if len(cem) == 1 or cem.endswith(('/', '+', '-')) or if_num_dot(cem) \
                or re.match(r'[+a-z:]', cem) or re.search(r'[:@|]|[+]{0,1}/', cem):  # Na+/Na
            return 'other'
        pattern = re.compile(r'[SP]\d\d')
        un_chem_abbreviation = re.compile(r'[IJE]')

        def __generalized_elements(cem: str):
            element = {}
            try:
                result = self.chem_parse(cem, sort=False)
                element = result['composition'][0]['elements'] if result['composition'] else {}
            except Exception as e:
                # Nae).(Vf).(Naf).
                log.info('%s: %s', cem, e.__str__().encode('gbk', 'ignore').decode('gbk'))
            return element

        if normalize:
            cem = self.normalized_compound_formula(cem)
        shape = word_shape(cem)
        likely_abb = any_func(shape, ABB_SHAPE)
        if not likely_abb and (shape.startswith('d') or 'b.b' in shape):
            return 'other'
        elif 'Xx-Xx-Xx' in shape:  # Nax(Cu-Fe-Mn)O2
            return 'irregular_shape'
        parse_ = self.is_compound_formula(cem)
        if not likely_abb and parse_ and parse_[1]:
            # NaCoMnO   NaMnNiCuFeTiOF
            if len([i for i in parse_[1] if i in TRANSITION_ME]) >= 2 and parse_[0] == ''.join(
                    parse_[1]):
                return 'is_likely_abbreviation'
            # 'Na/Li/Ni/Mn/Co'
            elif not set(cem.split('/')).difference(ELEMENTS):
                return 'synthetic'
            elif all(len(i) <= 2 for i in cem.split('-')):
                return 'irregular_shape'
            elif '/' not in cem:
                return 'synthetic'
            else:
                return 'other'
        elif un_chem_abbreviation.search(cem):
            return 'other'
        elif any_func(cem, SOLVENT_NAMES):
            return 'solvent_names'
        elif any_func(cem, RAW_MATERIAL):
            return 'raw_material'
        elif cem in APPARATUS:
            return 'apparatus'
        elif cem in OTHER or any_func(cem, OTHER_IN) or pattern.match(cem):
            return 'other'

        if not likely_abb:
            try:
                _elements = [element.value for element in Composition(cem).elements]
                # Transition metal raw materials
                intersection_tme = set(_elements).intersection(self.TMB)
                # C H O
                cho = set(_elements).difference(set(AC))
                if not cho and len(_elements) == 3:
                    return 'solvent'
                # oxides, the raw material contributes only one key element
                elif (len(_elements) == 2 or len(intersection_tme) == 1) and 'O' in _elements:
                    return 'raw_material'
                elif len(intersection_tme) > 1 and self.prompt_element not in _elements:
                    return 'raw_material'
            except (ValueError, AttributeError, KeyError):
                ele_result = {}
                if self.prompt_element in cem and not likely_abb:
                    ele_result = __generalized_elements(cem)
                    if len(ele_result) > 2 and 'O' in ele_result:
                        if 'M' in ele_result:
                            return 'ElementVariables'
                        elif 'TM' in ele_result:
                            return 'ElementVariables_TM'
                    else:
                        return 'is_likely_abbreviation'
                # Na/Na
                if 'Xx*Xx' in shape:
                    return 'other'
                elif self.prompt_element in cem or self.prompt_element[0] in cem:
                    if not ele_result or likely_abb:
                        return 'is_likely_abbreviation'
                    else:
                        return 'raw_material'
        return 'is_likely_abbreviation' if likely_abb or shape in ['XX', 'Xd.d'] and not any_func(cem, ['=',
                                                                                                         ',']) else 'other'

    @staticmethod
    def is_word(string, threshold_value=4):
        def check(string_block):
            continue_count = 0
            for s in string_block:
                if s.islower():
                    continue_count += 1
                else:
                    continue_count = 0
                if continue_count == threshold_value:
                    return True
            return False
        return all(check(_) for _ in string.split("-"))

    @lru_cache(None)
    def is_compound_formula(self, cem: str, normalize: bool = False) -> Union[bool, Tuple[str, list]]:
        """
        Preliminary judgement of compounds.

        After removing some special symbols, pymatgen is used to initially determine the structure of
        a valid chemical formula and return the elemental composition.

        Args:
            cem (str): Input chemical entity.
            normalize (bool): Whether normalized is required.

        Returns:
            (cem, [Elemental composition, ... ]) If the processed string is a simple formula else False.
        """
        phase, cem = self.separate_phase(cem)
        if self.prompt_element in cem:
            _cem = self.normalized_compound_formula(cem) if normalize else cem

            if '%' in _cem:  # 84.6 % Na2/3Mn5/6O2   15.4 % Na2/3MnO2
                _cem = list(filter(lambda x: not like_number(x), _cem.split(' % ')))[0]
            if ' (' in _cem:
                _cem = _cem.split(' ', 1)[0]

            if self.separate_phase(_cem)[0]:
                _cem = self.separate_phase(_cem)[1]
            try:
                remove_ = 'xyz-+/·δ'
                for remove in remove_:
                    _cem = _cem.replace(remove, '')
                ind = _cem.find(')')
                if ind > -1 and not _cem[ind: ind + 2].endswith(tuple(digits)):  # Na0.70Ni0.20Cu0.15Mn(0.65-x)TixO2
                    _cem = _cem.replace('(', '').replace(')', '')
                # 'Na0.67(Ni0.3Mn0.5Fe0.2)0.95Zr0.05O2'
                comp = Composition(_cem)
                if not comp.elements:
                    return False
                if not any(c != 1 for c in comp.to_reduced_dict.values()):  # NaCrCHF Not a chemical formula
                    return False

                def _elements():
                    return (element.value for element in comp.elements)

                # Determining the presence or absence of transition metals
                if not self.tm_limit or set(_elements()).intersection(set(TRANSITION_ME)):  # intersection_tme
                    if phase:
                        phase += '-'
                    return phase + cem, list(_elements())
                return False
            except (ValueError, AttributeError):
                if phase:
                    phase += '-'
                return (phase + cem, []) if '□' in _cem else False
        return False

    @lru_cache(None)
    def chem_parse(self, cem: str, sort=True):
        # 'NaMgx(Ni1/3Fe1/3Mn1/3)1-xO2(x = 0, 0.02, and 0.05)'
        parsed = mp.parse(cem).to_dict()
        if sort and parsed['composition']:
            parsed['composition'][0]['elements'] = OrderedDict(sorted(parsed['composition'][0]['elements'].items(),
                                                                      key=lambda s: _pt_data[s[0]]['IUPAC ordering'])
                                                               )
        return parsed

    @lru_cache(None)
    def chem_backbone(self, cem: str) -> str:
        """
        Removal of phase symbols and closing brackets in chemical entities.

        """
        cem = self.separate_phase(cem)[1]
        idx = end_parentheses(cem)[0]
        return cem[:idx].rstrip() if idx else cem

    """
    Similar to PHASE PROCESSING by: Olga Kononova
    """

    @lru_cache(None)
    def separate_phase(self, formula: str) -> Tuple[str, str]:
        """
        Separate phase symbol part from formula.

        Arg:
            formula (str): material string

        Returns:
            phase symbol(s) (str) and rest of the formula (str)
        """
        phase = ""
        start = 0
        for m in re_phase_prefix.finditer(formula):
            phase = m.group(1)
            start = m.end() - 1

        return phase, formula[start:]

    """
    -------------------------
    Similar to Pymatgen Development Team
    -------------------------
    """

    @lru_cache(None)
    def iupac_formula(self, cem: str) -> str:
        """
        Returns:
            a formula string, with elements sorted by the iupac electronegativity ordering
            defined in Table VI of "Nomenclature of Inorganic Chemistry (IUPAC Recommendations 2005)".
            This ordering effectively follows the groups and rows of the periodic table, except
            the Lanthanides, Actanides and hydrogen. Polyanions are still determined
            based on the true electronegativity of the elements.
        """

        if any_func(cem, ['x', 'y', 'z']):  # Exclude chemical formulas with variables
            return cem
        pre, _cem = self.separate_phase(cem)
        parse = self.chem_parse(_cem)['composition']
        if parse:
            sym_amt = parse[0]['elements']
            facter = 3 if sym_amt.get('O', None) == '6' else 1
        else:
            return cem
        formula = [s + self.formula_double_format(eval(sym_amt[s]) / facter, position=2) for s in sym_amt]
        return pre + '-' + "".join(formula) if pre else "".join(formula)

    @staticmethod
    def formula_double_format(afloat, ignore_ones=True, tol=1e-8, position=8):
        """
        This function is used to make pretty formulas by formatting the amounts.

        Args:
            afloat (float): a float.
            ignore_ones (bool): if true, floats of 1 are ignored.
            tol (float): Tolerance to round to nearest int. i.e. 2.0000000001 -> 2.
            position (int): Number of bits retained.

        Returns:
            A string representation of the float for formulas.
        """
        if ignore_ones and afloat == 1:
            return ""
        if abs(afloat - int(afloat)) < tol:
            return str(int(afloat))
        return str(round(afloat, position))
