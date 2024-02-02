# coding=utf-8
import text2chem.core.formula_parser as tcf
from text2chem.core.formula_parser import (
    re, defaultdict, OrderedDict,
    list_of_elements, list_of_elements_1,
    VACANCIES, GREEK_CHARS, simplify
)


def parse_formula(formula, regex_parser):
    formula = formula.replace(" ", "")
    """
    separate phase, e.g. g-ABC
    """
    phase, formula = regex_parser.separate_phase(formula)

    """
    separate oxygen deficiency
    """
    formula, oxygen_deficiency, oxygen_deficiency_sym = regex_parser.separate_oxygen_deficiency(formula)

    """
    converting fractions a(b+x)/c into (a/c*b+a/c*x)
    """
    formula = regex_parser.make_fraction_convertion(formula)

    """
    check for any weird syntax (A,B)zElxEly...
    replacing with MzElxEly... and M = [A, B]
    """
    elements_x = defaultdict(str)
    stoichiometry_x = defaultdict(str)
    formula, variables = regex_parser.convert_weird_syntax(formula)
    if variables:
        elements_x["M"] = variables

    composition = __get_composition(formula)

    return dict(formula=formula,
                composition=composition,
                oxygen_deficiency=oxygen_deficiency,
                oxygen_deficiency_sym=oxygen_deficiency_sym,
                phase=phase,
                amounts_x={x: v for x, v in stoichiometry_x.items()},
                elements_x={e: v for e, v in elements_x.items()})


def __get_composition(init_formula):
    """

    :param init_formula:
    :return:
    """
    """
    if more than 4 repeating lowercase letters encountered then it is not chemical formula
    """
    if re.findall("[a-z]{4,}", init_formula):
        return OrderedDict()

    formula_dict = OrderedDict()
    formula_dict = __parse_parentheses(init_formula, "1", formula_dict)

    """
    refinement of non-variable values
    """
    incorrect = []
    for el, amt in formula_dict.items():
        formula_dict[el] = simplify(amt)
        if any(len(c) > 1 for c in re.findall("[A-Za-z]+", formula_dict[el])):
            incorrect.append(el)

    for el in incorrect:
        del formula_dict[el]

    return formula_dict


def __parse_parentheses(init_formula, init_factor, curr_dict):
    re_in_parentheses = r"\(((?>[^\(\)]+|(?R))*)\)\s*([-*\.\da-z\+/]*)"
    for m in re.finditer(re_in_parentheses, init_formula):
        factor = m.group(2) if m.group(2) != "" else "1"
        factor = simplify("(" + str(init_factor) + ")*(" + str(factor) + ")")
        unit_sym_dict = __parse_parentheses(m.group(1), factor, curr_dict)
        init_formula = init_formula.replace(m.group(0), "") if unit_sym_dict else init_formula.replace(m.group(0),
                                                                                                       m.group(1))

    unit_sym_dict = __get_sym_dict(init_formula, init_factor)
    for el, amt in unit_sym_dict.items():
        if el in curr_dict:
            if len(curr_dict[el]) != 0:
                curr_dict[el] = "(" + str(curr_dict[el]) + ")" + "+" + "(" + str(amt) + ")"
            else:
                curr_dict[el] = amt
        else:
            curr_dict[el] = amt

    return curr_dict


def __get_sym_dict(f, factor):
    re_sym_dict = r"([A-Z□]{1}[a-z]{0,1})\s*([\-\*\.\da-z" + "".join(GREEK_CHARS) + r"\+\/]*)"
    sym_dict = OrderedDict()

    def get_code_value(code, iterator):
        code_mapping = {"01": (iterator.group(1), iterator.group(2)),
                        "11": (iterator.group(1), iterator.group(2)),
                        "10": (iterator.group(1)[0], iterator.group(1)[1:] + iterator.group(2)),
                        "00": (iterator.group(1)[0], iterator.group(1)[1:] + iterator.group(2))}
        return code_mapping[code]

    for m in re.finditer(re_sym_dict, f):
        """
        checking for correct elements names
        """
        el_bin = "{0}{1}".format(str(int(m.group(1)[0] in list_of_elements_1 | {"M"} | VACANCIES)),
                                 str(int(m.group(1) in list_of_elements | {"Ln", "M"} | VACANCIES)))
        el, amt = get_code_value(el_bin, m)
        if amt.strip() == "":
            amt = "1"
        if el in sym_dict:
            sym_dict[el] = "(" + sym_dict[el] + ")" + "+" + "(" + amt + ")" + "*" + "(" + str(factor) + ")"
        else:
            sym_dict[el] = "(" + amt + ")" + "*" + "(" + str(factor) + ")"
        f = f.replace(m.group(), "", 1)
    if f.strip():
        return OrderedDict()

    """
    refinement of non-variable values
    """
    try:
        for el, amt in sym_dict.items():
            sym_dict[el] = simplify(amt)
    except:
        sym_dict = OrderedDict()
    return sym_dict


tcf.parse_formula = parse_formula
