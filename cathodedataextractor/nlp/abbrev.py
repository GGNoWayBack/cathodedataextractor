# coding=utf-8
"""
Abbreviation detection.
"""
import logging
from typing import List, Tuple, Union, Optional
from collections import Counter
from functools import partial, lru_cache

import regex as re
from pymatgen.core.periodic_table import _pt_data

from .cner import CNer
from .cdetext import LText
from .tokenizer4units import units_tokenizer as tokenizer

from ..parse import (
    end_parentheses,
    bracket_level,
    add_infor_pattern,
    abb_named_pattern,
    end_par_not_split_pattern,
    ignore_suffix_pattern
)
from ..utils import any_func, if_num_dot


log = logging.getLogger(__name__)


class AbbreviationDetection:
    """
    Detect abbreviation definitions
    """
    ner = CNer()

    def __init__(self):

        self._new_abbreviation_definitions = []
        self._own_abbreviation_definitions = []
        self._elements = []
        self._stoichiometric_variables = {}

    def _seq2token_ner(self, ls, keyword, num=float('inf')):
        n, start, ner = len(ls), 0, []
        while start < n and num:
            token = ls[start].strip('(,.;")')
            if self.ner.prompt_tag(token) == keyword:
                num -= 1
                ner.append(token)
            start += 1
        return ner

    def _seq2token_ners(self, ls):
        abb_ner, synthesis_ner = [], []
        for token in ls:
            token = token.strip('(,.;")')
            if self.ner.prompt_tag(token) == 'is_likely_abbreviation':
                abb_ner.append(token.split('(')[0])
            elif self.ner.prompt_tag(token) == 'synthetic' and not any_func(token, ['x', 'y', 'z']):
                synthesis_ner.append(token)
        return (abb_ner, synthesis_ner) if abb_ner and synthesis_ner else None

    def _cem_near_supp_infor(self, ner_str, after2indices, find_abbs, find_cem) -> Optional[tuple]:
        """
        Look up the abbreviations around.
        """
        try:
            end_v, vend_span = self.xyz_pattern(find_abbs.group(), deep_search=False)
            # The front and back of a chemical formula.
            (front_find_string,
             after_find_string) = (find_abbs.group()[:vend_span[0]],
                                   find_abbs.group()[vend_span[1]:]) if vend_span \
                else ('', '')
            synthetic, _variables = self.parse_chem_formulas_variables(ner_str + end_v)

            v_chem = ner_str.strip()
            # Extract chemical formulae with variables for stoichiometry.
            for _sv in self._stoichiometric_variables:
                if v_chem == _sv or self.ner.separate_phase(v_chem)[1] == \
                        self.ner.separate_phase(_sv)[1]:
                    if len(_variables) > len(self._stoichiometric_variables[_sv]):
                        self._stoichiometric_variables[_sv] = _variables
                    break
            else:
                self._stoichiometric_variables[v_chem] = _variables

            abb = []
            # 'NaNi0.4Mn0.25Ti0.3Co0.05O2-xFx' (denoted as NMTC-Fx, x=0, 0.04 , 0.08 and 0.12)
            find_v_abb, abb_v, x_value, abb = self._detect_abbreviations_variables(
                after_find_string, abb)
            if find_v_abb and len(abb) != len(synthetic):
                find_v_abb, abb_v, x_value, abb = self._detect_abbreviations_variables(
                    front_find_string, abb)
            if not find_v_abb:
                _variables = x_value if x_value else _variables
                abb = self._convert_abbreviations_variables(_variables, abb_v)
            if not abb:
                last_string = find_cem.text[after2indices + find_abbs.end():]
                namepattern = abb_named_pattern.split(last_string)
                if len(namepattern) == 2:  # Detects the field after the parentheses.
                    abb.extend(self._seq2token_ner(namepattern[-1].split(' '), 'is_likely_abbreviation'))

            return (synthetic, abb) if synthetic and abb else None
        except Exception as e:
            log.info('%s-%s-%s', ner_str, e, find_abbs.group())

    def _detect_abbreviations_variables(self, text: str, abb: list):
        tokens = map(lambda x: x.strip('(,.;")'), text.split())
        find_v_abb, abb_v, x_equal_lb, x_value = True, '', [0, 0], []
        for ind, toke in enumerate(tokens):
            if find_v_abb and self.ner.prompt_tag(toke) == 'is_likely_abbreviation':
                if self._abbreviations_variables(toke):
                    abb_v = toke
                    find_v_abb = False
                else:  # Add if no abbreviations with variables are found.
                    abb.append(toke)
            elif toke in ['x', 'y', 'z']:
                x_equal_lb[0] = ind
            elif '=' in toke:
                if toke == '=' and ind - x_equal_lb[0] == 1:
                    x_equal_lb[1] = ind
                else:
                    toke = toke.split('=')[-1]
                    x_equal_lb = [True, True]
                    if if_num_dot(toke):
                        x_value.append(eval(toke))
            elif all(x_equal_lb) and if_num_dot(toke):
                x_value.append(eval(toke))

        return find_v_abb, abb_v, x_value, abb

    @staticmethod
    def xyz_pattern(sentence: str, deep_search=True) -> Tuple[str, Tuple]:
        """
        Try to retrieve information that contains only stoichiometric variables.
        """
        pattern = re.compile(r'(\b[xyz]\b)\s*=([0-9\.,and\s%]+)(?!\w)')
        new_ = []
        sentence = sentence.replace('X', 'x')
        find_ = pattern.finditer(sentence)
        for fin in find_:
            v_str = tokenizer.tokenize(fin.group(2))
            # Handling of the presence of percentage signs.
            if fin.group(2).find('%') != -1:
                for ind, tok in enumerate(v_str):
                    if ind < len(v_str) - 1 and if_num_dot(tok) \
                            and v_str[ind + 1] == '%' and str(float(tok) / 100) not in new_:
                        new_.append(str(float(tok) / 100))
            else:
                for ind, tok in enumerate(v_str):
                    if if_num_dot(tok) and eval(tok) < 10 and tok not in new_:
                        new_.append(tok)
            if not deep_search:
                break
        return (' (' + fin.group(1) + '=' + ', '.join(new_) + ')', fin.span()) if new_ else ('', ())

    @staticmethod
    def _rectification_of_boundaries(ner_str, ner_end, s_start, find_cem):
        if end_par_not_split_pattern.search(ner_str):
            # Numbers in parentheses may be base words or entities.
            num_suffix = re.match(r'\d', find_cem[ner_end - s_start:])
            if num_suffix:
                return ner_str + num_suffix.group(), ner_end + 1
        return ner_str, ner_end

    @staticmethod
    def _contain_end_balance_parentheses(cem: str) -> Tuple[bool, Tuple]:
        result = end_parentheses(cem)
        if result[1] and bracket_level(result[1]) == 0:
            return True, result
        else:
            return False, result

    @lru_cache(None)
    def _extract_elements_list(self, cem: str):
        """
        Extract the elements that are not 'O' in the chemical formula.
        """
        try:
            self._elements = self.ner.is_compound_formula(cem)[1][:]
            self._elements.remove('O')
        except (ValueError, AttributeError, TypeError):
            return
        return self._elements

    @lru_cache(None)
    def parse_element_formulas_variables(self, var_cem: str, position=2) -> list:
        """
        Analyse the chemical formulae of the elemental variables (M, TM).
        such as O3-NaNi0.45Mn0.3Ti0.2M0.05O2 (M=Nb/Mo/Cr).

        Returns:
            synthetic (list): Chemical formulae for all determinate forms.
        """
        res_dict_m = self.ner.chem_parse(var_cem, sort=False)
        if res_dict_m['amounts_x']:
            return []
        if 'M' not in res_dict_m['elements_x']:
            return []

        facter = 3 if res_dict_m['composition'][0]['elements'].get('O', None) == '6' else 1
        m_value = res_dict_m['composition'][0]['elements'].pop('M')
        m_value = '' if eval(m_value) == 1 else str(round(eval(m_value) / facter, position))

        synthetic, syns_m = [], {}
        for iterm in res_dict_m['composition'][0]['elements'].items():
            if eval(iterm[1]) != 1:
                syns_m.update({iterm[0]: str(round(eval(iterm[1]) / facter, position))})
            else:
                syns_m.update({iterm[0]: ''})
        for m in res_dict_m['elements_x']['M']:
            syns_m.update({m: m_value})
            sort_ = sorted(syns_m.items(), key=lambda s: _pt_data[s[0]]['IUPAC ordering'])
            synthetic.append(res_dict_m['phase'] + '-' + ''.join([_[0] + _[1] for _ in sort_]))
            del syns_m[m]
        return synthetic

    @lru_cache(None)
    def parse_chem_formulas_variables(self, var_cem: str) -> Tuple[list, list]:
        """
        Analyse a chemical formula containing the variables (x,y,z) and their values
        such as Na2/3Ni1/3Co(1/3-x)Mn1/3AlxO2 (x = 0).

        Returns:
            synthetic (list): Chemical formulae for all determinate forms.
            value_list (list): Values of variables.
        """

        def _variable(res_dict, factor, dynamic):
            syns = []
            exec(dynamic)  # Dynamic definition of local variables.
            for iterm in res_dict['composition'][0]['elements'].items():
                if eval((iterm[1])) != 0:
                    if eval(iterm[1]) != 1 and eval(iterm[1]) != factor:
                        syns.append(iterm[0] + self.ner.formula_double_format(eval(iterm[1]) / factor, position=2))
                    else:
                        syns.append(iterm[0])
            return ''.join(syns)

        synthetic, _list, phase = [], [], ''
        try:
            res_dict = self.ner.chem_parse(var_cem)
            phase = res_dict['phase']
            factor = 3 if res_dict['composition'][0]['elements'].get('O', None) == '6' else 1
            if len(res_dict['amounts_x']) == 1:
                val_key = list(res_dict['amounts_x'].keys())[0]
                _list = res_dict['amounts_x'][val_key]['values']
                for num in _list:
                    synthetic.append(_variable(res_dict, factor, '{} = {}'.format(val_key, num)))
        except ValueError:
            log.info('ValueError: %s', var_cem)
        finally:
            if phase:
                synthetic = [phase + '-' + sy for sy in synthetic]
            return synthetic, _list

    def _convert_abbreviations_variables(self, variables: List[int], token: str):
        abb = []
        result = list(self._abbreviations_variables(token))
        if result[-1] in ['x', 'y', 'z']:
            for var in variables:
                if var == 0:
                    if result[0] not in abb:
                        abb.append(result[0])
                else:
                    result[-1] = str(var)
                    abb.append(''.join(result))
        else:
            for var in variables:
                result[0] = '0' if var == 0 else str(var)
                abb.append(''.join(result))
        return abb

    @staticmethod
    @lru_cache(None)
    def _abbreviations_variables(cem: str):
        """
        NMTC-Fx, NMCT-Lax, x-NMTO
        """
        # Chemical formulas are broken down into abbreviations and variables.
        pattern = {'1': r'([A-Z]+)(-?[^-xyz]*)([xyz])',
                   '2': r'([xyz])(-?)([A-Z]+)'}
        for pat in pattern:
            result = re.search(pattern[pat], cem)
            if result and pat == '1':
                return result.group(1), result.group(2).rstrip(), result.group(3)
            if result and pat == '2':
                return result.group(1), result.group(2).rstrip(), result.group(3)
        else:
            return False

    @staticmethod
    def _find_abb_both_sides(before_cem, behind_cem, right_len, sentence, searching_threshold=25):
        # Entity before and after text search.
        for i in range(min(searching_threshold, before_cem)):
            before_cem -= 1
            if sentence[before_cem] == ')':
                return
            if sentence[before_cem] == '(':
                break
        else:
            return

        for j in range(min(searching_threshold, right_len)):
            if sentence[behind_cem] == '(':
                return
            if sentence[behind_cem] == ')':
                break
            behind_cem += 1
        return sentence[before_cem + 1: behind_cem]

    def _is_new_chem_abbreviation_pairs(self, pair: tuple) -> bool:
        pair_phase = self.ner.separate_phase(pair[0])[0] or self.ner.separate_phase(pair[1])[0]
        for abb_name in self._new_abbreviation_definitions:
            abb_name_phase = self.ner.separate_phase(abb_name[0])[0] or self.ner.separate_phase(abb_name[1])[0]
            phase_same_fg = pair_phase == abb_name_phase  # Whether the phase components are the same.
            lb = self.ner.separate_phase(pair[0])[1] == self.ner.separate_phase(
                abb_name[0])[1] and self.ner.separate_phase(pair[1])[1] == self.ner.separate_phase(abb_name[1])[1]
            if lb and phase_same_fg:  # Remove duplicates.
                return False

        return True

    @lru_cache(None)
    def abb_cem_relevance(self, abb, cem, threshold_value=2):
        """
        Abbreviation and full name determination.
        """
        def each_part(abb, cem_c, threshold_value):

            abb_c = Counter(s for s in abb if s.isupper())
            n = len(abb_c)
            end_threshold_value = 0
            if abb.endswith("0"):  # MFT0, Na0.6MnO2
                end_threshold_value = 2
            for ind, abb_k in enumerate(abb_c, 1):
                if abb_k != 'O':
                    min_same = min(abb_c[abb_k], cem_c.get(abb_k, 0))
                    if min_same:
                        threshold_value -= min(abb_c[abb_k], cem_c.get(abb_k, 0))
                    else:  # The uppercase character in an abbreviation must be present in the full name,
                        # and if not must be at the end and longer than 1.
                        # ： 'FMR', 'Na0.67Mn0.5Fe0.5O2'  'NFMCu-0'  '0-NFMCu', 'NaMn0.6Fe0.4O2'
                        if (n == 1) or (threshold_value and ind + end_threshold_value < n):
                            return False

            return True if threshold_value <= 1 else False

        suffix_pattern = ignore_suffix_pattern.search(abb)
        if suffix_pattern:  # Ignore suffixes.
            abb = abb[:suffix_pattern.start()]

        p_abb, p_cem = self.ner.separate_phase(abb), self.ner.separate_phase(cem)  # Consider the phase.
        if p_abb[0] and p_cem[0] and (p_abb[0] != p_cem[0]):
            return False
        if len(abb) > len(cem) or any(i in abb for i in {'x', 'y', 'z'}):
            return False
        cem_c = Counter(s for s in p_cem[1] if s.isupper())
        func_p = partial(each_part, cem_c=cem_c, threshold_value=threshold_value)

        # Determines whether the parts spaced by '-' are satisfied.
        return any(func_p(abb) for abb in p_abb[1].split('-'))

    def __call__(self, obj: Union[LText, str]):
        if isinstance(obj, str):
            obj = LText(obj)

        for num_s, find_cem in enumerate(obj.sentences):
            s_start, s_end = find_cem.start, find_cem.end
            _cem = find_cem.cems

            break_fg = False
            s_abb, s_synthetic = [], []
            for num, _ in enumerate(_cem):
                ner_str, ner_start, ner_end = _.text, _.start, _.end
                label = self.ner.prompt_tag(ner_str)

                if label == 'is_likely_abbreviation' and ' (' in ner_str:
                    ab, sy = ner_str.split(' ', 1)
                    sy = sy.strip('() ')
                    if self.ner.prompt_tag(sy) == 'synthetic':
                        s_abb.append(ab)
                        s_synthetic.append(sy)
                    continue
                elif label not in {'synthetic', 'ElementVariables'}:
                    continue

                # Adjustment of boundaries.
                ner_str, ner_end = self._rectification_of_boundaries(ner_str, ner_end, s_start, find_cem.text)
                if self._elements:
                    self._elements.clear()
                # Customised chemical formula abbreviations.
                if self._extract_elements_list(ner_str):
                    abb_ = [element[0] for element in self._elements]
                    if (''.join(abb_), ner_str) not in self._own_abbreviation_definitions:
                        self._own_abbreviation_definitions.append((''.join(abb_), ner_str))

                # start
                abb, synthetic = [], []

                # Parentheses after judgement of identified entities.
                balance_parentheses_lb, (paren_begin, end_paren) = self._contain_end_balance_parentheses(ner_str)

                # Determine possible search locations.
                adjacent_idx = None
                if ner_end + 1 == s_end:  # Early termination.
                    if not balance_parentheses_lb:
                        break
                else:
                    if find_cem.text[ner_end + 1 - s_start] == '(':
                        adjacent_idx = ner_end + 1 - s_start
                    elif find_cem.text[ner_end - s_start] == '(':
                        adjacent_idx = ner_end - s_start

                if any_func(ner_str, ['x', 'y', 'z']):  # 1. Detection of stoichiometric variables.
                    if balance_parentheses_lb:  # 1.1 Complete supplementary information may exist in the entity，
                        sy = self.parse_chem_formulas_variables(ner_str)[0]
                        if sy:
                            res = self._seq2token_ner(find_cem.text[ner_start + paren_begin - s_start:].split(),
                                                      'is_likely_abbreviation',
                                                      len(sy))
                            if res:
                                synthetic.extend(sy)
                                abb.extend(res)

                    elif adjacent_idx is not None:  # 1.2 Identified entities do not contain supplementary information,
                        # but supplementary information may immediately follow the chemical formula.
                        # eg. Na[(Mn0.4Fe0.3Ni0.3)1−xTix]O2 (x = 0, MFN)
                        find_abbs = add_infor_pattern.match(find_cem.text[adjacent_idx:])
                        if find_abbs is None or '=' not in find_abbs.group(1):
                            continue
                        synthetic_abb = self._cem_near_supp_infor(ner_str, adjacent_idx, find_abbs, find_cem)
                        if synthetic_abb is not None:
                            abb.extend(synthetic_abb[1])
                            synthetic.extend(synthetic_abb[0])

                    elif paren_begin:  # 1.3 Entity identifies incomplete additional information
                        # (unbalanced bracketed endings), converted to 1.2 .
                        adjacent_idx = ner_start + paren_begin - s_start
                        ner_str = ner_str[:paren_begin]
                        find_abbs = add_infor_pattern.match(find_cem.text[adjacent_idx:])
                        if find_abbs is None or '=' not in find_abbs.group(1):
                            continue
                        synthetic_abb = self._cem_near_supp_infor(ner_str, adjacent_idx, find_abbs, find_cem)
                        if synthetic_abb is not None:
                            abb.extend(synthetic_abb[1])
                            synthetic.extend(synthetic_abb[0])

                    elif not paren_begin:  # 1.4 Failure to recognise proximity supplementary information,
                        # consider long distance balancing brackets and naming verbs.
                        # eg. ... Na0.6MnO2, Na0.6Mn0.95Fe0.05O2, ... marked as MFT0, MF5, ...
                        find_text = find_cem.text[ner_end - s_start:]
                        find_abbs = add_infor_pattern.search(find_text)

                        if find_abbs and '=' in find_abbs.group(1):
                            last_string = obj.sentences[num_s + 1].text if num_s < len(
                                obj.sentences) - 1 else find_abbs.group(1)
                            synthetic, _variables = self.parse_chem_formulas_variables(
                                ner_str + find_abbs.group().replace('X', 'x'))
                            namepattern = abb_named_pattern.split(last_string)
                            if len(namepattern) >= 2:
                                res = self._seq2token_ner(namepattern[-1].split(' '), 'is_likely_abbreviation')
                                if res:
                                    abb.extend(res)
                            else:
                                for token in find_abbs.group(1).split(' '):
                                    token = token.strip('(,.;")')
                                    if self.ner.prompt_tag(token) == 'is_likely_abbreviation':
                                        if self._abbreviations_variables(token):
                                            abb.extend(self._convert_abbreviations_variables(_variables, token))
                                            break
                                        else:
                                            if self.ner.prompt_tag(token) == 'is_likely_abbreviation':
                                                abb.append(token)

                        else:
                            if abb_named_pattern.search(find_text):  # Consider naming verbs.
                                pair = self._seq2token_ners(find_text.split())
                                if pair:
                                    abb.extend(pair[0])
                                    synthetic.extend(pair[1])
                                    break_fg = True

                # O3-NaNi0.45Mn0.3Ti0.2M0.05O2 (M=Nb/Mo/Cr, abbreviated as NMTNb, NMTMo and NMTCr, respectively)
                elif label == 'ElementVariables':  # 2.Elemental Variables.
                    # Placement of chemical formula endings in sentences.
                    start_find_parentheses = ner_start - s_start + paren_begin if paren_begin else ner_end - s_start
                    find_text = find_cem.text[start_find_parentheses:]
                    find_abb = add_infor_pattern.search(find_text)
                    if find_abb and '=' in find_abb.group(1):
                        res = self._seq2token_ner(find_abb.group(1).split(' '), 'is_likely_abbreviation')
                        if res:
                            abb.extend(res)
                            synthetic.extend(self.parse_element_formulas_variables(
                                find_cem.text[ner_start - s_start:start_find_parentheses] + find_abb.group()))

                # Chemical formulas with constant stoichiometry:  Na0.67Ni0.31Mn0.67Y0.02O2 (NMY2)
                else:  # 3.Chemical formula without variables.
                    # 3.1 Adjacent brackets.
                    if adjacent_idx is not None \
                            and num + 1 < len(_cem) \
                            and self._elements \
                            and _cem[num + 1].start - ner_end <= 6 \
                            and self.ner.prompt_tag(_cem[num + 1].text) == 'is_likely_abbreviation':

                        abb_ = [element[0] for element in self._elements if element[0] in _cem[num + 1].text]
                        if len(self._elements) == len(abb_) or \
                                self.abb_cem_relevance(_cem[num + 1].text, _cem[num].text):
                            abb.append(_cem[num + 1].text.strip('()').split('(')[0].rstrip())
                            synthetic.append(ner_str)

                    elif paren_begin:  # 3.2 Match the nearest balancing bracket after the chemical formula.
                        find_abb = add_infor_pattern.match(find_cem.text[ner_start + paren_begin - s_start:])
                        if find_abb:
                            res = self._seq2token_ner(find_abb.group(1).split(), 'is_likely_abbreviation')
                            if res:
                                abb.extend(res)
                                synthetic.append(ner_str[:paren_begin].rstrip())

                    # Na0.67Ni0.23Mg0.1Mn0.67O2 ... (denoted as NNMMO-MP)
                    elif not paren_begin:

                        before_cem, behind_cem, right_len = ner_start - s_start, ner_end - s_start, s_end - ner_end
                        find_text = find_cem.text[behind_cem:]
                        find_abb = add_infor_pattern.search(find_text)

                        if find_abb and '=' not in find_abb.group(1):
                            res = self._seq2token_ner(find_abb.group(1).split(), 'is_likely_abbreviation', 1)
                            if res:
                                synthetic.append(ner_str)
                                abb.extend(res)
                            else:
                                # ... h-NM, h-NMC and h-NMC2 are identified as
                                # Na0.66MnO2, Na0.65Mn0.9Cu0.1O2 and Na0.63Mn0.8Cu0.2O2, ...
                                if abb_named_pattern.search(find_cem.text):
                                    pair = self._seq2token_ners(find_cem.text.split())
                                    if pair:
                                        abb.extend(pair[0])
                                        synthetic.extend(pair[1])
                                    break_fg = True

                        # Na0.67Ni0.33Mn0.67O2 (NM). the latter abbreviated entity is not recognisable.
                        elif find_abb and find_cem.text[ner_end - s_start + 1] == '(':
                            res = self._seq2token_ner(find_abb.group(1).split(), 'is_likely_abbreviation', 1)
                            if res:
                                synthetic.append(ner_str)
                                abb.extend(res)
                        else:
                            # (tetragonal Na3V2(PO4)2O2F, abbreviated as NVPOF) (Na2/3Ni1/3Mn2/3O2, P2-NNMO)
                            ner_itself_in_parentheses = self._find_abb_both_sides(before_cem, behind_cem, right_len,
                                                                                 find_cem.text)
                            if ner_itself_in_parentheses:
                                res = self._seq2token_ner(ner_itself_in_parentheses.split(),
                                                          'is_likely_abbreviation', 1)
                                if res:
                                    synthetic.append(ner_str)
                                    abb.extend(res)
                            else:
                                # ... Na0.67MnO2, tunnel compound of Na0.44MnO2 and pure ...,
                                # i.e. Na0.6Fe0.02Mn0.98O2 and Na0.6Fe0.06Mn0.94O2 ...
                                # denoted as T-NM, L-NM, LT-NM, LT-NFM2 and L-NFM6, respectively.
                                if abb_named_pattern.search(find_cem.text):
                                    pair = self._seq2token_ners(find_cem.text.split())
                                    if pair:
                                        if pair[1] == pair[0]:
                                            break_fg = True
                                            abb.extend(pair[0])
                                            synthetic.extend(pair[1])
                                        else:
                                            abb.extend(pair[0][:len(pair[1])])
                                            synthetic.extend(pair[1])

                s_abb.extend(abb)
                s_synthetic.extend(synthetic)
                if break_fg:
                    break
                # covering the pairs of abbreviated chemical formulae relations extracted in the sentence
                # that have the same abbreviation, retaining the last extracted pair.
                # In terms of matching distance this means that the extracted relation pairs are more reliable.
                # i.e： ... Na3V2P3O12 and Na3V2P2O8F3 (NVPF) <CR>.
            for abb_cem in dict(abb_cem for abb_cem in zip(s_abb, s_synthetic)).items():
                if self.abb_cem_relevance(abb_cem[0], abb_cem[1]) and self._is_new_chem_abbreviation_pairs(abb_cem):
                    self._new_abbreviation_definitions.append(abb_cem)

        return self

    @property
    def new_abbreviation(self):
        return self._new_abbreviation_definitions

    @property
    def custom_abbreviation(self):
        return self._own_abbreviation_definitions

    @property
    def stoichiometric_variables_chem(self):
        return self._stoichiometric_variables

