# coding=utf-8
"""
Some dependency rules for cycle number, capacity and retention.
"""

import regex as re
from bisect import bisect_left, bisect_right
from .regex_pattern import charge_discharge_pattern, cycle_ca_pattern


def cycle_retentions(sentence, cycle, retention, retention_l):
    n_cycle = [_ for _ in cycle if _ != 1]
    c_l = len(n_cycle)
    if c_l == 1:
        if retention_l == 2 and re.search(r'from[ \d.%]+to[ \d.]*%', sentence):
            return list(zip(n_cycle, retention[-1:]))
        return list(zip(n_cycle * retention_l, retention))
    else:
        if c_l >= retention_l:
            if n_cycle[0] < n_cycle[1]:
                return list(zip(n_cycle[-retention_l:], retention))
            return list(zip(n_cycle[:retention_l], retention))
        return list(zip(n_cycle, retention))


def cycle_capacities(sentence, cycle, c_l, capacity, capacity_l, cycle_retention):
    cr_len = len(cycle_retention) if cycle_retention else 0

    cycle_distance, cycle = list(zip(*(cycle)))
    capacity_distance, capacity = list(zip(*(capacity)))

    rate_capability = True if 'rate capability' in sentence else False

    # In general, the capacity retention rate may contain both the rate and the cycling performance
    if rate_capability:
        return list(zip(cycle[:1], capacity))

    if c_l == 1:
        if any(re_.search(sentence) for re_ in cycle_ca_pattern):
            return list(zip(cycle * capacity_l, capacity))
        if capacity_l == 1:
            res3 = re.search(r'\b(\d[\d.]++)\s?mAhg-1 (?>after|for) (\d+)\s?cycle(?:s)?', sentence)
            if re.search(r'\d\s?%( even)? after \d+\s?cycle', sentence):
                return list(zip((1, ), capacity)) if capacity[0] > 100 else list(zip(cycle, capacity))
            elif res3:
                return [(eval(res3.group(2)), eval(res3.group(1)))]
            if cr_len > 0:
                return list(zip(cycle, capacity)) if any(i in sentence for i in
                                                         ['measure', 'obtain', 'keep', 'remain', 'decrease', 'decline', 'maintain',
                                                          'decayed']) else list(zip((1, ), capacity))
            return list(zip(cycle, capacity))

        if re.search(r'from (?:an initial )?\d[\d. ]+(?:mAhg-1 )?to \d[\d. ]+mAhg-1', sentence):
            # from 127.2 to 34.6 mAhg-1 after 100 cycles
            return list(zip((1, ) + cycle, capacity))

        c_dis_ca = re.search(charge_discharge_pattern, sentence)  # Charge and discharge capacity
        if c_dis_ca:  # Charge and discharge interleaving
            new_capacity = capacity[1::2] if c_dis_ca.group().startswith('c') else capacity[::2]
            return list(zip(cycle * (capacity_l//2), new_capacity))

        discharge = sentence.find('discharge')
        if discharge > -1:
            charge = sentence.find('charge', 0, discharge)
            if charge > -1:
                return list(zip(cycle * (capacity_l//2), capacity[capacity_l//2:]))
            elif sentence.find('charge', discharge+9) > -1:
                return list(zip(cycle * (capacity_l//2), capacity[:capacity_l//2]))

        return list(zip((1, ) * (capacity_l - c_l) + cycle, capacity)) if cr_len == 1 else list(
            zip(cycle * capacity_l, capacity))
    elif c_l == 2:
        if 1 in cycle:
            if capacity_l == 1 and re.search(r'\b\d[ \d.]+mAhg-1 after \d+\s?cycle(?:s)?',  # Excluded first circle
                                             sentence):
                return list(zip([_ for _ in cycle if _ != 1], capacity))

            # Minimum character distance
            ind_left = 0
            cycle_ca = []
            for i in range(capacity_l):
                ind_left = bisect_left(cycle_distance, capacity_distance[i], lo=ind_left, hi=c_l)
                if ind_left == c_l:
                    cycle_ca.append((cycle[-1], capacity[i]))
                elif ind_left == 0:
                    cycle_ca.append((cycle[0], capacity[i]))
                elif cycle_distance[ind_left] + cycle_distance[ind_left-1] <= 2*capacity_distance[i]:
                    cycle_ca.append((cycle[ind_left], capacity[i]))
                else:
                    cycle_ca.append((cycle[ind_left-1], capacity[i]))
            if cycle_ca:
                return cycle_ca

            return list(zip(cycle, capacity)) if cr_len == 1 else list(zip((1, ) * capacity_l, capacity))

        if 2 * cr_len == capacity_l:
            return list(zip(cycle[:1] * cr_len + cycle[-1:] * cr_len, capacity))  # from 0.2 to 10 C

        if re.search(charge_discharge_pattern, sentence):  # Charge and discharge capacity
            return list(zip(cycle[:1] * capacity_l, capacity))
    elif re.search(charge_discharge_pattern, sentence) and capacity_l == 2 * c_l:
        new_c = []
        for i in cycle:
            new_c += [i] * 2
        return list(zip(new_c, capacity))
    if cycle[0] == 1 and capacity[0] < 100:
        return list(zip(cycle[-capacity_l:], capacity))
    if c_l > 2 and cycle[-1] == 1 and (capacity_l > c_l):
        return list(zip(cycle + (1, ) * (capacity_l - c_l), capacity))
    return list(zip(cycle, capacity))
