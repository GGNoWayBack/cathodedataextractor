# coding=utf-8
"""
Relation extraction
"""
from copy import deepcopy
from typing import Tuple
from collections import defaultdict, OrderedDict
from functools import lru_cache

import regex as re

from chemdataextractor.doc.text import Sentence

from . import (
    end_parentheses,
    t_c_pattern, global_voltage,
    cycle_rate_capacity, coulomb_efficiency_assert, current_define_pattern
)

from .crc_relation import cycle_retentions, cycle_capacities

from ..utils import if_num_dot, any_func
from ..nlp import CNer, LText, AbbreviationDetection, units_tokenizer

tokenizer = units_tokenizer


class PropertyParse:
    """
    Paragraph analysis.
    """

    ner = CNer()
    csie = AbbreviationDetection()

    pro_list = {'mAhg-1', '%', 'V', 'C', 'mAg-1', 'cycle', 'cycles', '°C', 'h'}

    def __init__(self, doi=None, year=None, abb_names=None, stoichiometric_variable=None):

        self.doi = doi
        self.year = year

        self.abb_names = abb_names
        self.stoichiometric_variable = stoichiometric_variable

        self.temperature = []
        self.time = []

        self.current_define = defaultdict(int)  # Global record, one element (dictionary) in a record.
        self.current = []
        self.voltage = []
        self.v_record = False

        self.sent_id = 0
        self._temperature = None
        self._time = None

        self.results = []
        self.property_dict = []

    def experimental_extraction(self, obj: LText):
        """
        Experimental paragraph relation extraction.
        """
        for sentence in obj.sentences:
            _text = sentence.text
            if '°C' not in _text:
                continue
            # Temperature-time binary pairs.
            t_ls, h_ls, pre_ = [], [], None
            for t_or_c in t_c_pattern.finditer(_text):

                for pro, str_ in t_or_c.groupdict().items():
                    if str_ is None:
                        continue
                    catch_property = pro
                    num_ls = (float(tok) for tok in tokenizer.tokenize(str_) if if_num_dot(tok))
                    if pro == 'H':
                        h_ls.extend(num_ls)
                    else:
                        t_ls.extend(num_ls)
                    if pre_ and pre_ != catch_property and t_ls and h_ls:
                        t_len, h_len = len(t_ls), len(h_ls)

                        if t_len > h_len:
                            h_ls.extend([h_ls.pop()] * (t_len - h_len + 1))
                        else:
                            t_ls.extend([t_ls.pop()] * (h_len - t_len + 1))
                        self.temperature.extend(t_ls)
                        self.time.extend(h_ls)
                        t_ls, h_ls = [], []
                        pre_ = None
                    else:
                        pre_ = catch_property
        self._exp_results()

    def _exp_results(self):

        # The position corresponding to the maximum temperature.
        if self.temperature:
            if len(self.temperature) == len(self.time):
                max_ = max(self.temperature)
                ind_ = self.temperature.index(max_)
                self._temperature = max_
                self._time = self.time[ind_]

    def property_extraction(self, paragraph: LText):
        """
        Electrochemical property extraction.
        """
        sentences_ = paragraph.sentences
        self.v_record = False
        for ind_n, sentence in enumerate(sentences_):
            property_dict = {}
            _text = sentence.text

            self._voltage(_text, idx=ind_n)  # Collect voltage intervals globally.

            for cm in current_define_pattern.findall(_text):  # Global search current definition.
                c, m = list(map(lambda x: float(x.strip()), cm))
                if c > m:
                    self.current_define[round(c / m, 3)] += 1
                else:
                    self.current_define[round(m / c, 3)] += 1

            property_dict['sentence'] = _text

            if any(_ in _text for _ in ['mAhg-1', '%']):  # First filter out paragraphs with properties.

                property_dict['S_id'] = ind_n

                def extract_cner(property_dict):
                    # Extraction of chemical entities.
                    if sentence.cems:
                        property_dict_name = property_dict.setdefault('name', [])

                        c_ner = (cem.text.split(' ', 1)[0] for cem in sentence.cems if
                                 self.ner.prompt_tag(cem.text)
                                 in ['is_likely_abbreviation', 'synthetic'])

                        for c_ in c_ner:
                            if c_ not in property_dict_name:
                                property_dict_name.append(c_)

                # Cycling performance and rate performance related property extraction.
                for _key in cycle_rate_capacity:
                    max100 = True if _key == 'retention: %' else False
                    if max100 and not coulomb_efficiency_assert.search(_text) \
                            and any_func(_text, ('capacity', 'capability')):
                        # If no word for coulomb efficiency is found, it defaults to retention rate,
                        # noting that comparisons may exist such as % higher.
                        prop = re.finditer(
                            r'(?<![.@/])\b\d\d[\d .,avtoisnd/]*%(?!\b)\s?(?!wt|substitution|Ni|Mn|Sb|higher)',
                            _text)
                    elif _key.startswith('ca'):  # theoretical capacity
                        find_theoretical_ca = _text.find('theoretical capacity')
                        if find_theoretical_ca > -1:
                            prop = list(cycle_rate_capacity[_key].finditer(_text))
                            if prop and prop[0].start() > find_theoretical_ca:
                                prop.pop(0)
                        else:
                            prop = cycle_rate_capacity[_key].finditer(_text)
                    else:
                        prop = cycle_rate_capacity[_key].finditer(_text)

                    if _key == 'cycle':
                        property_dict_key = property_dict.setdefault(_key, [])
                        for _re in prop:
                            search_ls = tokenizer.tokenize(_re.group())
                            for _token in search_ls:
                                if _token.isdigit():
                                    property_dict_key.append((_re.start(), eval(_token)))
                                elif _token in ['initial', 'first']:
                                    property_dict_key.append((_re.start(), 1))
                        if not property_dict_key:
                            del property_dict[_key]
                    else:
                        for _re in prop:
                            diff_unit = self.pro_list - {_key.split(': ')[1], }
                            property_dict_key = property_dict.setdefault(_key, [])
                            search_ls = tokenizer.tokenize(_re.group())
                            ind, search_ls_len = 0, len(search_ls)
                            while ind < search_ls_len:
                                # The judgement is a generalised value and should not be greater
                                # than 100 and non-negative for values before.
                                _token = search_ls[ind]
                                if if_num_dot(_token):
                                    try:
                                        if ind + 1 == search_ls_len:
                                            if 'fraction' in _re.groupdict():
                                                property_dict_key.append(round(1 / eval(_token), 3))
                                            break
                                        elif max100 and 5 < eval(_token) <= 100 \
                                                and search_ls[ind + 1] not in diff_unit:
                                            if re.search(r'(lost|lose|loss|expense)(?! per cycle)',
                                                         _text[:_re.start()]) and eval(_token) < 50:
                                                property_dict_key.append(round(100 - eval(_token), 3))
                                            else:
                                                property_dict_key.append(eval(_token))
                                        elif not max100 and search_ls[ind + 1] not in diff_unit:
                                            if _key.endswith(' C'):
                                                property_dict_key.append(eval(_token))
                                            elif _key.endswith('Ag-1'):
                                                property_dict_key.append(eval(_token))
                                            elif _key.endswith(' mAhg-1'):
                                                if eval(_token) > 10:
                                                    property_dict_key.append((_re.start(), eval(_token)))
                                            elif eval(_token) > 1:
                                                property_dict_key.append(eval(_token))
                                    except Exception as e:
                                        print(_token, e)
                                elif _key == 'current: C' and property_dict_key \
                                        and _token == '/' and ind + 1 < search_ls_len and search_ls[ind + 1].isdigit():
                                    property_dict_key[-1] = round(property_dict_key[-1] / eval(search_ls[ind + 1]), 3)
                                    ind += 1
                                elif _token in ['CE', 'ICE']:  # Exit when you run into coulomb efficiency.
                                    break
                                ind += 1

                # Ensure that the recorded data must have attributes extracted.
                if 'cycle' in property_dict:
                    # Cycling performance.
                    if property_dict.get('retention: %', None) or property_dict.get('capacity: mAhg-1', None):
                        property_dict['Category'] = 'Cycling performance'
                        extract_cner(property_dict)
                        self.property_dict.append(property_dict)
                elif property_dict.get('capacity: mAhg-1', None) \
                        and (property_dict.get('current: mAg-1', None)
                             or property_dict.get('current: C', None) or property_dict.get('current: Ag-1', None)):
                    # Rate performance.
                    property_dict['Category'] = 'Rate performance'
                    extract_cner(property_dict)
                    self.property_dict.append(property_dict)
                # TODO: What if the sentence describes both rate and cycling performance.

        self.property_relation_extraction(sentences_)

    def property_relation_extraction(self, sentences_: LText):
        """
        Rate and cycling performance property relation extraction.
        """

        def entity_lookup(sentence):
            newfind = []
            for token in sentence.replace('//', ' // ').split(' '):
                token = token.strip('(,.;)')
                if self.ner.prompt_tag(token) in {'is_likely_abbreviation', 'synthetic'}:
                    newfind.append(token)
            return newfind

        extra_sent_id, prename = -2, []  # Sentences with no chemical formulae extracted.
        for pro in self.property_dict:
            cycle = pro.get('cycle', [])
            capacity = pro.get('capacity: mAhg-1', [])
            retention = pro.get('retention: %', [])
            currentC = pro.get('current: C', [])
            currentM = pro.get('current: mAg-1', [])
            currentA = pro.get('current: Ag-1', [])

            # respectively.
            if any_func(pro['sentence'], ('while', 'respectively', 'compared')) or not pro.get('name', []):
                newfind = entity_lookup(pro['sentence'])
                pro['name'] = newfind

            chemname = pro.get('name', [])
            # cycling.
            chem_l, c_l, capacity_l, retention_l = len(chemname), len(cycle), len(capacity), len(retention)
            cycle_capacity, cycle_retention = [], []
            # rate.
            retention_current, capacity_current = [], []
            # current.
            current_final = {}
            current_final_len = 0
            currentC_len, currentM_len, currentA_len = len(currentC), len(currentM), len(currentA)

            # Preferred to collect mAg-1, Ag-1 rather than C.
            if currentM_len > currentC_len:
                current_final['Current: mAg-1'] = currentM
                current_final_len = currentM_len
            elif currentA_len > currentC_len:
                current_final['Current: Ag-1'] = currentA
                current_final_len = currentA_len
            elif currentM_len:
                current_final['Current: mAg-1'] = currentM
                current_final_len = currentM_len
            elif currentA_len:
                current_final['Current: Ag-1'] = currentA
                current_final_len = currentA_len
            elif currentC_len:
                current_final['Current: C'] = currentC
                current_final_len = currentC_len

            current_unit, curr = list(current_final.items())[0] if current_final else ('', [])

            self.sent_id = pro['S_id']

            # The first step: key binary relationship matching.
            if pro['Category'].startswith('C'):  # Cycling performance extraction.
                if not c_l:
                    continue
                if retention and capacity:
                    cycle_retention = cycle_retentions(pro['sentence'], list(zip(*cycle))[1], retention, retention_l)
                    cycle_capacity = cycle_capacities(pro['sentence'], cycle, c_l, capacity, capacity_l,
                                                      cycle_retention)
                elif capacity:
                    cycle_capacity = cycle_capacities(pro['sentence'], cycle, c_l, capacity, capacity_l,
                                                      None)
                elif retention:
                    cycle_retention = cycle_retentions(pro['sentence'], list(zip(*cycle))[1], retention, retention_l)
            else:  # Rate performance extraction.
                capacity = list(zip(*capacity))[1]
                if current_final:
                    if capacity:
                        if current_final_len == 1:
                            capacity_current = list(zip(capacity, curr * capacity_l))
                        else:
                            if re.search(r'from[\d. ]+to[\d. ]*C\b', pro['sentence']):
                                continue
                            elif chem_l > 1 and (current_final_len < capacity_l) \
                                    and capacity_l // chem_l == current_final_len:
                                capacity_current = list(zip(capacity, curr * chem_l))
                            else:
                                capacity_current = list(zip(capacity, curr))
                    elif retention:  # TODO: Does rate performance need to take this into account?
                        if current_final_len == 1:
                            retention_current = list(zip(retention, curr * retention_l))
                        else:
                            retention_current = list(zip(retention, curr))

            voltage = self._v_result()

            def _backtrack_synthetic(chemname, sentences_, pro, extra_sent_id, prename) -> Tuple[list, int]:
                """
                Backtrack to the previous entity of the matching entity record and update
                the entity of the sentence where it is currently located.
                Returns:
                    synthetic (list): Finalised entity.
                    extra_sent_id (int): The number of the sentence in which the entity is located.
                """
                synthetic = []
                if chemname:
                    if chem_l == 1:
                        if any_func(pro['name'][0], {'x', 'y', 'z'}):
                            synthetic = self.stoichiometric_variables2synthetic(pro['name'][0],
                                                                                pro['sentence'])
                        else:
                            synthetic.append(pro['name'][0])
                        if synthetic:
                            extra_sent_id = pro['S_id']
                    else:
                        extra_sent_id = pro['S_id']
                        synthetic = [che for che in chemname if not any_func(che, {'x', 'y', 'z'})]

                else:
                    if pro['S_id'] in [extra_sent_id + 1, 0]:
                        synthetic = prename

                        extra_sent_id = pro['S_id']
                        return synthetic, extra_sent_id

                    count, Variable_ = 0, {}
                    for s in sentences_[pro['S_id'] - 1::-1]:

                        if self.stoichiometric_variable and count == 0:
                            Variable_.update(self.stoichiometric_xyz_pattern(s.text))
                        # TODO: How to determine the number of entities to find？
                        name = self._chem_detection_above(s)
                        count += 1
                        if any_func(name[1], {'x', 'y', 'z'}):

                            if Variable_:

                                Variable_str = ' (' + ' '.join(
                                    [var + '=' + value for var, value in Variable_.items()]) + ')'
                                end = end_parentheses(name[1])[0]
                                _name = name[1][:end] + Variable_str if end else name[1] + Variable_str
                                synthetic = self.csie.parse_chem_formulas_variables(_name)[0]
                            else:
                                synthetic = self.stoichiometric_variables2synthetic(name[1], s.text)

                        else:
                            synthetic = [name[1]] if name[1] else []

                        if synthetic:
                            extra_sent_id = pro['S_id'] - 1 - count
                            break
                return synthetic, extra_sent_id

            synthetic, extra_sent_id = _backtrack_synthetic(chemname,
                                                            sentences_, pro,
                                                            extra_sent_id, prename)

            # Consider carefully the organisational pattern of the final data.
            if not synthetic or not synthetic[0]:
                continue

            # The next step: heuristic rules.
            name_l = len(synthetic)
            if pro['Category'].startswith('C'):
                cc_l, cr_l = len(cycle_capacity), len(cycle_retention)
                max_l = cc_l  # The highest number of properties to be matched.
                if cc_l < cr_l:
                    max_l = cr_l
                    cycle_capacity.extend([()] * (cr_l - cc_l))
                else:
                    cycle_retention.extend([()] * (cc_l - cr_l))

                # Compare the length of the extracted data to assert the need to append entities forward.
                if name_l < capacity_l == c_l == retention_l:
                    s_ = sentences_[extra_sent_id - 1].text
                    new_find_name = prename or [new_name for new_name in entity_lookup(s_) if new_name not in synthetic]
                    synthetic = new_find_name + synthetic if re.search(r'increas',
                                                                       pro['sentence']) else synthetic + new_find_name
                    name_l = len(synthetic)

                if name_l == 1:  # Only one entity is extracted based on the number of properties
                    # speculating that it may contain more than one.
                    re_name = self._find_full_name(synthetic[0])
                    if not re_name[1]:
                        continue
                    if current_final_len == 1:
                        for combination in zip(curr * max_l, cycle_capacity, cycle_retention):
                            self._formatting_writes(pro, current_unit, re_name, combination[0],
                                                    [combination[1], ], [combination[2], ],
                                                    voltage)
                    elif current_final_len > 1:
                        for combination in zip(curr, cycle_capacity, cycle_retention):
                            self._formatting_writes(pro, current_unit, re_name, combination[0],
                                                    [combination[1], ], [combination[2], ],
                                                    voltage)
                    else:
                        for combination in zip(cycle_capacity, cycle_retention):
                            self._formatting_writes(pro, current_unit, re_name, [],
                                                    [combination[0], ], [combination[1], ],
                                                    voltage)

                else:
                    if current_final_len == 1:
                        batch = max_l // name_l or 1
                        if voltage is None:
                            voltage_split = False
                        else:
                            voltage_split = len(voltage) == name_l and isinstance(voltage[0], list)

                        start, re_name = 0, self._find_full_name(synthetic[0])
                        for idx, combination in enumerate(zip(curr * max_l, cycle_capacity, cycle_retention)):
                            if idx > 0 and idx % batch == 0:
                                start += 1
                                if start >= name_l:
                                    break
                                re_name = self._find_full_name(synthetic[start])

                            self._formatting_writes(pro, current_unit, re_name, combination[0],
                                                    [combination[1], ], [combination[2], ],
                                                    voltage[idx % batch] if voltage_split else voltage)

                    elif current_final_len > 1:
                        for combination in zip(curr, cycle_capacity, cycle_retention, synthetic):
                            re_name = self._find_full_name(combination[3])
                            self._formatting_writes(pro, current_unit, re_name, combination[0],
                                                    [combination[1], ], [combination[2], ],
                                                    voltage)

                    else:
                        for combination in zip(cycle_capacity, cycle_retention, synthetic):
                            re_name = self._find_full_name(combination[2])
                            self._formatting_writes(pro, current_unit, re_name, [],
                                                    [combination[0], ], [combination[1], ],
                                                    voltage)
            else:
                if capacity_current:
                    description = 'Capacity'
                    rate_capability = capacity_current

                else:
                    description = 'Retention'
                    rate_capability = retention_current

                def rate_capability_split(synthetic, rate_capability, check=True):
                    s_l = len(synthetic)
                    if not s_l:
                        return
                    rate_l = len(rate_capability)
                    if s_l == 1 or not check:
                        if s_l == 2 and rate_l == 1 and re.search(r'both', pro['sentence']):
                            for syn in synthetic:
                                rate_capability_split([syn], rate_capability)
                        else:
                            re_name = self._find_full_name(synthetic[0])
                            for combination in rate_capability:
                                if description == 'Capacity':
                                    _ = self._formatting_writes(pro, current_unit, re_name, combination[1],
                                                                [combination[0]], [],
                                                                voltage)
                                else:
                                    _ = self._formatting_writes(pro, current_unit, re_name, combination[1],
                                                                [], [combination[0]],
                                                                voltage)

                    else:
                        # Iterate to find subscripts with duplicate property records.
                        if description == 'Capacity':
                            curr_, num_name_choice, pre_split = set(), 0, -1
                            for split_id, rate_ in enumerate(rate_capability):
                                if rate_[1] in curr_:
                                    if num_name_choice == name_l:
                                        break
                                    rate_capability_split([synthetic[num_name_choice]],
                                                          rate_capability[
                                                          0 if pre_split == -1 else pre_split: split_id])
                                    pre_split = split_id
                                    num_name_choice += 1
                                curr_.add(rate_[1])

                            if pre_split >= 0:
                                if (pre_split < rate_l):
                                    if num_name_choice == name_l:
                                        rate_capability_split([synthetic[num_name_choice - 1]],
                                                              rate_capability[pre_split:])
                                    else:
                                        rate_capability_split([synthetic[num_name_choice]],
                                                              rate_capability[pre_split:])
                            else:
                                rate_capability_split([synthetic[num_name_choice]], rate_capability)

                rate_capability_split(synthetic, rate_capability, current_final_len != 1)
            if synthetic:
                prename = synthetic

        self.property_dict.clear()

    def _formatting_writes(self, pro, current_unit, re_name: tuple, current, cycle_capacity, cycle_retention, voltage):
        """
        Data recording.
        """

        def _v(voltage):
            # Multiple voltage intervals are folded into a lower bound minimum voltage
            # and an upper bound maximum voltage.
            if voltage and isinstance(voltage[0], list):
                v_ = [10, 0]
                for g in voltage:
                    v_[0] = min(v_[0], g[0])
                    v_[1] = max(v_[1], g[1] if g[1] < 10 else 0)
                voltage = v_
            return voltage

        def _new_write():
            new_cycle_capacity, new_cycle_retention = [_ for _ in cycle_capacity if _], [_ for _ in cycle_retention if
                                                                                         _]
            _result = self._final_results(abb=re_name[0],
                                          cem=re_name[1],
                                          category=pro['Category'],
                                          current=current,
                                          current_unit=current_unit,
                                          cycle_capacity=new_cycle_capacity,
                                          cycle_retention=new_cycle_retention,
                                          voltage=_v(voltage))
            if _result:
                self.results.append(_result)
                return True

        if re_name[1]:
            # Remove duplicate data and overwrite on top of the original record.
            phase, name = self.ner.separate_phase(re_name[1])
            Write = True
            for results in self.results:
                phase_r, name_r = self.ner.separate_phase(results['Name'])
                name_same = (not (phase_r or phase) or (phase_r == phase)) and name == name_r
                if not name_same:  # Only the same name has the possibility of removal.
                    continue
                results_f, pro_f = results['Category'][0], pro['Category'][0]
                if results_f != pro_f:
                    continue
                if results_f == 'C':
                    if results['Cycle_capacity: mAhg-1'] == cycle_capacity or \
                            results['Cycle_retention: %'] == cycle_retention:
                        if results.get('Cycle_retention: %', None) is None:
                            results['Cycle_retention: %'] = cycle_retention if cycle_retention[0] else None
                        if results.get('Cycle_capacity: mAhg-1', None) is None:
                            results['Cycle_capacity: mAhg-1'] = cycle_capacity if cycle_capacity[0] else None
                        if current_unit:
                            results.setdefault(current_unit, current)
                        if results.get('Voltage_range: V', None) is None:
                            results['Voltage_range: V'] = _v(voltage)
                        Write = False
                        break
                else:
                    if results['Capacity'] == cycle_capacity:
                        if current_unit:
                            results.setdefault(current_unit, current)
                        if results.get('Voltage_range: V', None) is None:
                            results['Voltage_range: V'] = _v(voltage)
                        Write = False
                        break
            if Write:
                return _new_write()

    def _final_results(self, cem, abb, cycle_capacity, category, current, current_unit, cycle_retention, voltage):
        """
        The properties that the data contains.
        """

        try:
            composition = self.ner.chem_parse(cem.replace('-δ', ''))['composition'][0]['elements']
        except (KeyError, IndexError, SyntaxError, ValueError):
            print(cem, self.doi, sep='>' * 20)
            return None

        result_dic = dict()

        result_dic['Category'] = category
        if current_unit:
            result_dic[current_unit] = current
        if category == 'Rate performance':
            result_dic['Capacity'] = cycle_capacity[0] if cycle_capacity else None
            result_dic['Retention'] = cycle_retention[0] if cycle_retention else None
        else:
            result_dic['Cycle_capacity: mAhg-1'] = cycle_capacity if cycle_capacity else None
            result_dic['Cycle_retention: %'] = cycle_retention if cycle_retention else None

        result_dic['Doi'] = self.doi
        result_dic['Year'] = self.year
        result_dic['Abbreviation'] = abb if abb else None
        result_dic['Name'] = cem
        result_dic['Sintering temperature'] = self._temperature
        result_dic['Sintering time'] = self._time

        result_dic['Voltage_range: V'] = voltage
        result_dic['Elements'] = composition

        return result_dic

    def _voltage(self, full_text_par, idx=0):

        voltage_ = defaultdict(list)
        _voltage = []
        for voltage in global_voltage.findall(full_text_par):

            v_num = [float(word) for word in voltage if if_num_dot(word)]
            if v_num and len(v_num) == 2:
                v_num.sort()

                if (v_num[-1] - v_num[0] - 1 >= 0) and v_num[-1] < 5:
                    _voltage.append(v_num)

        if _voltage:
            voltage_[idx].extend(_voltage)
            if self.v_record and self.voltage:
                self.voltage[-1].update(OrderedDict(voltage_))
            else:
                self.voltage.append(OrderedDict(voltage_))
            self.v_record = True

    def _v_result(self):
        def v_selection(items):
            result = []
            cur = items[-1]
            if self.v_record:
                for key in reversed(cur):
                    if key <= self.sent_id:
                        result = cur[key] if len(cur[key]) > 1 else cur[key][0]
                        break
                else:
                    if len(items) > 1:
                        _new = deepcopy(items[-2])
                        item = _new.popitem()
                        result = item[1] if len(item[1]) > 1 else item[1][0]
            else:
                _new = deepcopy(cur)
                item = _new.popitem()
                result = item[1] if len(item[1]) > 1 else item[1][0]
            return result

        voltage = []
        # If there is an extraction in this paragraph then find the nearest sentence to 
        # the property extraction that has a voltage extraction, 
        # otherwise select the last recorded message of the previous paragraph.

        if self.voltage and self.voltage[-1]:
            voltage = v_selection(self.voltage)
        return voltage if voltage else None

    @staticmethod
    def parse_stoichiometric_variables(cem: str, sentence: str):
        """
        Parsing potential entities.

        If the recognised chemical formula contains (x, y, z) then go to the field and look for x/y/z = ... .
        """

        variables, res_v = ['x', 'y', 'z'], ''
        cem_end, _st = end_parentheses(cem)
        cem = cem[:cem_end].rstrip() if cem_end else cem
        for _, variable in enumerate(variables):
            if variable in cem:
                res_v = variables[_]
                break
        if res_v:
            stoichiometric_values = res_v + r"\s*=\s*([-]{0,1}[0-9\.\,/and\sxyz=]+)[\s\)\]\,]"
            res_str = re.search(stoichiometric_values, sentence)
            return (cem + ' (' + res_str.group().rstrip(';:)') + ')', res_v) if res_str else (False, res_v)
        return False, res_v

    def stoichiometric_variables2synthetic(self, cem: str, sentence: str):
        """
        Possible values of stoichiometric variables of chemical formulas are analyzed in combination with sentences.
        """
        chem = self.parse_stoichiometric_variables(cem, sentence)
        synthetic = []
        if chem[0]:
            synthetic = self.csie.parse_chem_formulas_variables(chem[0])[0]
        else:
            for _ in self.stoichiometric_variable:
                if cem == _ or self.ner.separate_phase(cem) == self.ner.separate_phase(_):
                    _format = _ + f' ({chem[1]}=' + ','.join([str(st) for st in self.stoichiometric_variable[_]]) + ')'
                    synthetic = self.csie.parse_chem_formulas_variables(_format)[0]
                    break
        return synthetic

    @lru_cache(None)
    def _find_full_name(self, cem: str):
        """
        Look up the full name of the abbreviation
        """
        is_abb = self.ner.prompt_tag(cem)
        cem_phase, cem_str = self.ner.separate_phase(re.sub(r'[iboh]-', '', cem))
        for abb in self.abb_names:
            abb_name_phase = self.ner.separate_phase(re.sub(r'[iboh]-', '', abb[0]))[0] or \
                             self.ner.separate_phase(abb[1])[0]
            _abb = self.ner.separate_phase(abb[0])[1]
            _name = self.ner.separate_phase(abb[1])[1]
            phase = cem_phase or abb_name_phase
            if cem_phase == abb_name_phase or (cem_phase or abb_name_phase):
                if cem_str in [_abb, _name] or (
                        is_abb == 'is_likely_abbreviation' and self._is_same_abb(cem_str, _abb)):
                    return (_abb, phase + '-' + _name) if abb_name_phase else (_abb, _name)
        else:
            return ('', cem) if is_abb == 'synthetic' else ('', '')

    @staticmethod
    def _is_same_abb(a: str, b: str) -> bool:
        """
        Blurring the order of abbreviated words in an article and clerical errors.
        For example, consider only the case of full abbreviations: NaNMF equals NaNFM.
        """
        count = defaultdict(int)
        if a.isalpha() and b.isalpha() and len(a) == len(b):
            for i, j in zip(a, b):
                if i != j:
                    count[i] += 1
                    count[j] -= 1
            return all(v == 0 for v in count.values())
        return False

    @staticmethod
    def stoichiometric_xyz_pattern(sentence: str):
        dic = {}
        pattern = re.compile(r'(\b[Xxyz]\b)\s*=([0-9\.,and\s%]+)')
        for _iter in pattern.finditer(sentence):
            new_ = []
            _iter_group1 = _iter.group(1).replace('X', 'x')
            v_str = tokenizer.tokenize(_iter.group(2))
            if _iter.group(2).find('%') != -1:
                for ind, tok in enumerate(v_str):
                    if ind < len(v_str) - 1 and if_num_dot(tok) \
                            and v_str[ind + 1] == '%' and str(float(tok) / 100) not in new_:
                        new_.append(str(float(tok) / 100))
            else:
                for ind, tok in enumerate(v_str):
                    if if_num_dot(tok) and float(tok) < 10 and tok not in new_ and tok.startswith('0'):
                        if tok[:2] == '0.':
                            new_.append(tok)
                        else:
                            new_.append('0.' + tok[2:])

            if _iter_group1 not in dic:
                dic[_iter_group1] = (' ' + ', '.join(new_)) if new_ else ''
            else:
                dic[_iter_group1] += (', ' + ', '.join(new_)) if new_ else ''
        return dic

    def _chem_detection_above(self, sentence: Sentence):
        """
        Detect chemical formulae in sentences as a rule.
        """

        bat_ner = [_.text.split(' ', 1)[0] if _.text.count(' ') <= 1 else _.text.rsplit(' ', 1)[-1] for _ in
                   sentence.cems if self.ner.prompt_tag(_.text)
                   in ['synthetic', 'is_likely_abbreviation']] if sentence.cems else ''
        if not bat_ner:
            for token in sentence.text.split(' '):
                if self.ner.prompt_tag(token) == 'is_likely_abbreviation':
                    return self._find_full_name(token)
        elif bat_ner:
            cem = bat_ner[0]
            return self._find_full_name(cem)
        return '', ''
