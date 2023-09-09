# coding=utf-8
import regex as re
import sympy as smp
from text2chem.constants import NUMBERS_STR, GREEK_CHARS, COMPARE_SIGNS, DEFICIENCY_CHARS, SIGNS
from text2chem.chemical_data import list_of_elements, list_of_elements_1, list_of_elements_2


class RegExParser:
    def __init__(self):
        self._list_of_elements = list_of_elements
        self._list_of_elements_1 = list_of_elements_1
        self._list_of_elements_2 = list_of_elements_2
        self._greek_symbols = "".join(GREEK_CHARS)
        self._comparing_symbols = "".join(COMPARE_SIGNS)
        self._doping_terms = {"activated", "modified", "stabilized", "doped", "added"}

    """
    PHASE PROCESSING
    """

    def separate_phase(self, formula):
        """
        separate phase symbol part from formula
        :param formula: material string
        :return: phase symbol(s) and rest of the formula
        """
        # 2023.6.8  r"^([A-Za-z" + self._greek_symbols + r"][0-9]{0,1})\-[A-Z]\.*" -------->
        # r"^([A-Za-z" + ''.join(self._greek_symbols) + r"][0-9]{0,1}|Air|Oxy|[/PO\d and-]+)\-[A-Z]\.*"
        re_phase_prefix = r"^([A-Za-z" + ''.join(self._greek_symbols) + r"][0-9]{0,1}|Air|Oxy|[/PO\d and-]+)\-[A-Z]\.*"
        phase = ""
        start = 0
        for m in re.finditer(re_phase_prefix, formula):
            phase = m.group(1)
            start = m.end() - 1

        return phase, formula[start:]

    """
    FORMULA PROCESSING
    """

    def separate_oxygen_deficiency(self, formula):
        """
        separate oxygen deficiency from formula
        :param formula:
        :return:
        """
        # 2023.3.25
        re_signs = "[" + re.escape("".join(DEFICIENCY_CHARS)) + "]"
        # re_signs = "[" + "".join(DEFICIENCY_CHARS) + "]".replace("+", "\+").replace("-", "\-")
        re_oxy_def = r"O[0-9]*([±\+\-∓]{1})[a-z" + self._greek_symbols + r"]{1}[0-9]*$"

        formula_upd = formula
        oxy_def = ""
        oxy_def_sym = ""

        if len(formula) < 3:
            return formula_upd, oxy_def, oxy_def_sym

        if formula[-2:] in list_of_elements_2:
            return formula_upd, oxy_def, oxy_def_sym

        for m in re.finditer(re_oxy_def, formula_upd.rstrip(")")):
            end = formula_upd[m.start():m.end()]
            splt = re.split(re_signs, end)
            oxy_def_sym = splt[-1]
            oxy_def = m.group(1)
            formula_upd = formula_upd[:m.start()] + formula_upd[m.start():].replace(end, splt[0])

        if oxy_def_sym not in SIGNS and oxy_def_sym == formula_upd.rstrip(")")[-1]:
            oxy_def_sym = "±"

        return formula_upd, oxy_def, oxy_def_sym

    @staticmethod
    def make_fraction_convertion(formula):
        """
        converting fractions a(b+x)/c into (a/c*b+a/c*x) in formula
        :param formula:
        :return:
        """
        re_a = r"([0-9\.]*)"
        re_b = r"(\([0-9\.]*)"
        re_x = r"([a-z]*)"
        re_s = r"([\-\+]+)"
        re_d = r"([0-9\.]*)"
        re_y = r"([a-z]+\))"
        re_c = r"(?=[/]*([0-9\.]*))"
        re_formula_fraction = r"(" + re_a + re_b + re_x + re_s + re_d + re_y + re_c + r")"
        formula_upd = formula
        for m in re.finditer(re_formula_fraction, formula_upd):
            expr_old = m.group(1) + "/" + m.group(8) if m.group(8) != "" else m.group(1)
            a = m.group(2).strip(")(") if m.group(2).strip(")(") != '' else '1'
            b = m.group(3).strip(")(") if m.group(3).strip(')(') != '' else '1'
            x = m.group(4).strip(")(") if m.group(4).strip(")(") != '' else '1'
            s = m.group(5).strip(")(") if m.group(5).strip(")(") != '' else '+'
            d = m.group(6).strip(")(") if m.group(6).strip(")(") != '' else '1'
            y = m.group(7).strip(")(") if m.group(7).strip(")(") != '' else '1'
            c = m.group(8).strip(")(") if m.group(8).strip(")(") != '' else '1'
            expr_str = a + '/' + c + '*' + b + '*' + x + s + a + '/' + c + '*' + d + "*" + y
            expr = str(smp.simplify(expr_str)).strip()
            if expr[0] == '-':
                s_expr = re.split(r"\+", expr)
                expr = s_expr[1] + s_expr[0]
            expr_new = expr.strip().replace(" ", "")
            formula_upd = formula_upd.replace(expr_old, expr_new.strip(), 1)

        return re.sub(r"\s{1,}", "", formula_upd)

    @staticmethod
    def convert_weird_syntax(formula):
        """
        check and convert for any weird syntax (A,B)zElxEly...
        replacing with MzElxEly... and M = [A, B]
        :param formula:
        :return:
        """
        re_weird_syntax = r"(\([A-Za-z\s]+[\/,\s]+[A-Za-z]+\))"
        variables = []
        for m in re.finditer(re_weird_syntax, formula):
            variables = re.split(r"[\/,]", m.group(0).strip('()'))
            formula = formula.replace(m.group(0), "M", 1)
        return formula, variables

    """
    ADDITIVES PROCESSING
    """

    @staticmethod
    def separate_additives_fraction(formula):
        """
        separate fractions: e.g. (K0.16Na0.84)0.5Bi4.5Ti4O15+xwt.% CeO2 -> (K0.16Na0.84)0.5Bi4.5Ti4O15 and CeO2
        :param formula:
        :return:
        """
        parts = []
        additives = []
        re_additive_fraction = r"[\-\+:·]{0,1}\s*[0-9x\.]*\s*[vmolwt\s]*\%"
        if "%" in formula:
            formula = formula.replace(".%", "%")
            parts = re.split(re_additive_fraction, formula)

        if len(parts) > 1:
            formula = parts[0].strip(" -+")
            additives = [d.strip() for d in parts[1:] if d != ""]

        additives = [a.strip(" ") for s in additives for a in re.split(r"[\s,\-/]|and", s) if a.strip(" ") != ""]
        return formula, additives

    def separate_doped_with(self, formula):
        """
        split "material doped with element(s)" into material and elements
        :param formula:
        :return:
        """
        additives = []
        for r in self._doping_terms:
            parts = [w for w in re.split(r + " with", formula) if w != ""]
            if len(parts) > 1:
                formula = parts[0].strip(" -+")
                additives.append(parts[1].strip())

        additives = [a.strip(" ") for s in additives for a in re.split(r"[\s,\-/]|and", s) if a.strip(" ") != ""]
        return formula, additives

    def separate_element_doped(self, formula):
        """
        split "element(s)-doped material" into element(s) and material
        :param formula:
        :return:
        """
        additives = []
        for r in self._doping_terms:
            parts = [w for w in re.split(r"(.*)[-\s]{1}" + r + " (.*)", formula) if w != ""]
            if len(parts) > 1:
                formula = parts.pop()
                additives.extend(parts)

        additives = [a.strip(" ") for s in additives for a in re.split(r"[\s,\-/]|and", s) if a.strip(" ") != ""]
        return formula, additives

    def separate_elements_colon_formula(self, formula):
        """
        separate element(s) before/after formula: e.g. Ba5Si8O21:0.02Eu2+,xDy3+ -> Ba5Si8O21 and Eu and Dy
        :param formula:
        :return:
        """
        additives = []
        for part_ in formula.split(":"):
            part_ = part_.strip(" ")

            part = part_
            if any(e in part for e in self._list_of_elements_2):
                for e in list_of_elements_2:
                    part = part.replace(e, "&&")

            if all(e.strip("zyx,. " + NUMBERS_STR) in self._list_of_elements_1 | {"R", "&&"}
                   for e in re.split(r"[\s,/]", part) if e != ""):
                additives.append(part_.strip(" "))
            else:
                formula = part_.strip(" ")

        additives = [a.strip(" ") for s in additives for a in re.split(r"[\s,\-/]|and", s) if a.strip(" ") != ""]
        return formula, additives

    """
    MIXTURE PROCESSING
    """

    def split_mixture(self, formula):
        """
        split (x)compound1-(y)compound2-(z)compound2 into  [(compound1, x), (compound2, y), (compound2, z)]
        :param formula:
        :return:
        """
        re_split_mixture = r"(?<=[0-9\)])[\-⋅·∙\∗](?=[\(0-9](?!x))|" + \
                           r"(?<=[A-Z])[\-⋅·∙\∗](?=[\(0-9])|" + \
                           r"(?<=[A-Z\)])[\-⋅·∙\∗](?=[A-Z])|" + \
                           r"(?<=[0-9\)])[\-⋅·∙\∗](?=[A-Z])" + \
                           "".join([r"|(?<=" + e + r")[\-⋅·∙\∗](?=[\(0-9A-Z])" for e in self._list_of_elements]) + \
                           r"|[-·]([nx0-9\.]H2O)"
        re_split_mixture_refine = r"(?<=[A-Z\)])[\-·∙\∗⋅](?=[xyz])|(?<=O[0-9\)]+)[\-·∙\∗⋅](?=[xyz])"

        compounds = [p for p in re.split(re_split_mixture, formula) if p]
        if len(compounds) > 1:
            compounds = [p for part in compounds for p in re.split(re_split_mixture_refine, part)]

        if any(m.strip("0987654321") in self._list_of_elements for m in compounds[:-1]):
            compounds = ["".join([p + "-" for p in compounds]).rstrip("-")]

        """
        merge oxygen element if it gets split by mistake
        """
        merged_parts = [compounds[0]]
        for m in compounds[1:]:
            if re.findall("[A-Z]", m) == ["O"]:
                to_merge = merged_parts.pop() + "-" + m
                merged_parts.append(to_merge)
            else:
                merged_parts.append(m)

        return merged_parts

    @staticmethod
    def split_mixture_fractions(formula):
        """
        split (N-x-y)compound1+(x)compound2+(y)compound3 into [(compound1, N-x-y), (compound2, x), (compound2, y)]
        :param formula:
        :return:
        """
        re_split_prefix = r"(^\(1\-[xyz][-xyz]*\))|(^\(100\-[xyz][\-xyz]*\))"
        re_separators = r"(.*)[\-\+·∙\∗⋅]"

        compounds = []
        pref = [s for s in re.split(re_split_prefix, formula) if s]
        if len(pref) > 1:
            compound_temp = pref.pop()
            amount = pref.pop()
            variables = re.findall("[a-z]", amount)
            for v in variables:
                formula = formula.replace("(" + v + ")", v)
            compounds = []
            while variables:
                v = variables.pop()
                parts = re.findall(re_separators + v + "(.*)$", compound_temp)
                if parts:
                    compounds.append((parts[0][1], v))
                    compound_temp = parts[0][0]
            compounds.append((compound_temp, amount.strip("()")))

        return [c for c in reversed(compounds)]

    """
    PUBCHECM PROCESSING
    """

    @staticmethod
    def is_chemical_term(material_string):
        return re.findall("[a-z]{4,}", material_string) != []

    """
    ADDITIVES SUBSTITUTION
    """

    @staticmethod
    def get_additives_coefficient(additive):
        """
        find any stoichiometric coefficient next to the additive and split the list of additives
        e.g. 0.05Eu -> 0.05 and Eu
        :param additive: List
        :return:
        """
        r = r"^[x0-9\.]+|[x0-9\.]+$"
        coeff = re.findall(r, additive)
        element = [s for s in re.split(r, additive) if s != ""][0]
        return element, coeff

    @staticmethod
    def additive_symbolic_substitution(elements, coeff):
        """
        create symbolic expression of substition of additive into total composition
        :param elements: Compound.elements
        :param coeff:
        :return:
        """
        expr = "".join(["(" + v + ")+" for e, v in elements.items()]).rstrip("+")
        coeff = coeff[0] if not re.match("^[0]+[1-9]", coeff[0]) else "0." + coeff[0][1:]
        expr = expr + "+(" + coeff + ")"

        return expr, coeff

    """
    ELEMENTS VARIABLES PROCESSING
    """

    def get_elements_from_sentence(self, var, sentence):
        """
        find elements values for var in the sentence
        :param var: <str> variable name
        :param sentence: <str> sentence to look for
        :return: <list> of <str> found values
        """
        # 2022.11.29  r"\s*[=:]{1}\s*([A-Za-z0-9\+,\s]+)" ----> r"\s*[=:]{1}\s*([A-Za-z0-9\+,/\s]+)"
        re_elements_values = r"\s*[=:]{1}\s*([A-Za-z0-9\+,/\s]+)"

        # 2023.7.4
        values = re.findall(var + re_elements_values, sentence)
        # values = [c.rstrip(NUMBERS_STR) for v in values for c in re.split(r"[,/\s]", v)
        #           if c.rstrip(NUMBERS_STR) in self._list_of_elements]
        # return list(set(values))  # Set deduplication ignores text continuity.

        fvalues = []
        for v in values:  # 2022.11.29   r"[,\s]" -----> r"[,/\s]"
            for c in re.split(r"[,/\s]", v):
                c = c.rstrip(NUMBERS_STR)
                if c not in fvalues and c in self._list_of_elements:
                    fvalues.append(c)
        return fvalues

    """
    formula processing: finding stoichiometric variables
    """

    @property
    def re_variables(self):
        return r"[a-z" + self._greek_symbols + r"]"

    """
    STOICHIOMETRIC VARIABLES PROCESSING
    """

    @property
    def re_stoichiometric_values(self):
        return r"\s*=\s*([-]{0,1}[0-9\.\,/and\s]+)[\s\)\]\,]"

    @property
    def re_stoichiometric_range_lhs(self):
        return r"([0-9\.\s]*)\s*[<≤⩽]{0,1}\s*"

    @property
    def re_stoichiometric_range_rhs(self):
        return r"\s*[<≤⩽>]{1}\s*([0-9\.\s]+)[\s\)\]\.\,]"

    @property
    def re_stoichiometric_range_hyphen(self):
        return r"\s*=\s*([0-9\.]+)\s*[-–]\s*([0-9\.\s]+)[\s\)\]\,m\%]"

    @property
    def re_stoichiometric_range_ft(self):
        return r"[a-z\s]*from\s([0-9\./]+)\sto\s([0-9\./]+)"


"""
stoichiometric variables
"""
# re_variables = r"[a-z" + "".join(C.GREEK_CHARS) + r"]"

"""
acronyms dictionary
"""
re_capitals_no_O = "[A-NP-Z]"
