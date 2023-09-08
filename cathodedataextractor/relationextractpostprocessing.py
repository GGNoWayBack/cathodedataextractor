# coding=utf-8
"""
Post-processing of data records
"""
import os
import json
import pandas as pd
from copy import deepcopy
from .util_functions import write_into_json

_sort = {'Doi': 0, 'Year': 1, 'Name': 2, 'Abbreviation': 3, 'Sintering temperature': 4, 'Sintering time': 5,
         'Category': 6, 'Cycle': 7, 'Capacity': 8, 'Retention': 8,
         'Current: mAg-1': 9, 'Current: C': 9, 'Current: Ag-1': 9,
         'Voltage lower limit': 10, 'Voltage upper limit': 11}


def data_pprocess(data):
    binary_columns = ['Cycle_capacity: mAhg-1', 'Cycle_retention: %']
    res_json = []
    data = deepcopy(data)
    if data.get('Current_define', None) is not None:
        equal_ind = data.pop('Current_define')
        pre_current = float(max(equal_ind.keys(), key=lambda x: equal_ind[x]))

        if data.get('Current: C', None) is not None and 'Current: mAg-1' not in data:
            data['Current: mAg-1'] = round(data.pop('Current: C') * pre_current, 2)
    if data.get('Current: Ag-1', None):
        data['Current: mAg-1'] = data.pop('Current: Ag-1') * 1000
    v_ = data.pop('Voltage_range: V')
    if v_:
        data['Voltage lower limit'] = v_[0]
        data['Voltage upper limit'] = v_[1]
    else:
        data['Voltage lower limit'] = None
        data['Voltage upper limit'] = None
    if data['Category'].startswith('R'):
        if 'Retention' in data:
            data.pop('Retention')
        res_json.append(data)
    else:
        if data[binary_columns[1]] is None:
            # Capacity, cycle split if no cycle, retention extracted
            repeat = set()
            for Cycle, Capacity in data[binary_columns[0]]:
                if Cycle not in repeat:
                    new_ = deepcopy(data)
                    new_.pop('Cycle_capacity: mAhg-1')
                    new_.pop('Cycle_retention: %')
                    new_['Cycle'] = Cycle
                    new_['Capacity'] = Capacity
                    res_json.append(new_)
                repeat.add(Cycle)
        elif data[binary_columns[0]] is None:
            for Cycle, Retention in data[binary_columns[1]]:
                if Cycle > 1:
                    new_ = deepcopy(data)
                    new_.pop('Cycle_capacity: mAhg-1')
                    new_.pop('Cycle_retention: %')
                    new_['Cycle'] = Cycle
                    new_['Retention'] = Retention
                    res_json.append(new_)
                else:
                    print(data)
        else:  # If both are extracted and there is a first lap capacity.
            # Convert the retention rate to the corresponding number of cycles according to the first cycle,
            # and also save the capacity retention rate, generating two pieces of data.
            count = 0
            cca_cra = [data.pop('Cycle_capacity: mAhg-1'), data.pop('Cycle_retention: %')]
            c_c = {}
            for cycle_capacity in cca_cra[0]:
                if cycle_capacity[0] == 1:
                    count += 1
                if count > 1:
                    break
                if cycle_capacity[0] not in c_c:
                    c_c[cycle_capacity[0]] = cycle_capacity[1]
            if count == 1:
                for cycle_retention in cca_cra[1]:
                    if cycle_retention[0] not in c_c:
                        c_c[cycle_retention[0]] = round(c_c[1] * cycle_retention[1] / 100, 1)
                for Cycle, Capacity in cca_cra[0]:
                    new_ = deepcopy(data)
                    new_['Cycle'] = Cycle
                    new_['Capacity'] = Capacity
                    res_json.append(new_)
                for Cycle, Retention in cca_cra[1]:
                    new_ = deepcopy(data)
                    new_['Cycle'] = Cycle
                    new_['Retention'] = Retention
                    res_json.append(new_)
            elif count == 0:  # If the number of cycle is the same,
                # then convert to the first cycle capacity and generate three pieces of data.
                for Cycle, Capacity in cca_cra[0]:
                    new_ = deepcopy(data)
                    new_['Cycle'] = Cycle
                    new_['Capacity'] = Capacity
                    res_json.append(new_)
                for Cycle, Retention in cca_cra[1]:
                    new_ = deepcopy(data)
                    new_['Cycle'] = Cycle
                    new_['Retention'] = Retention
                    res_json.append(new_)
                if cca_cra[0][0][0] == cca_cra[1][0][0]:
                    new_capacity = round(cca_cra[0][0][1] * 100 / cca_cra[1][0][1], 1)
                    new_ = deepcopy(data)
                    new_['Cycle'] = 1
                    new_['Capacity'] = new_capacity
                    res_json.append(new_)
            else:
                res_json.append(data)
    for _, final in enumerate(res_json):
        res_json[_] = dict(sorted(final.items(), key=lambda x: _sort.get(x[0], 12)))
    return res_json
