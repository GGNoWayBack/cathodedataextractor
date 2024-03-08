# coding=utf-8
from text2chem.regex_parser import (
    re, smp,
    list_of_elements_2,
    DEFICIENCY_CHARS, SIGNS, NUMBERS_STR,
    RegExParser
)


class CathodeRegExParser(RegExParser):

    def separate_phase(self, formula):
        """
        separate phase symbol part from formula
        :param formula: material string
        :return: phase symbol(s) and rest of the formula
        """
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
        re_signs = "[" + re.escape("".join(DEFICIENCY_CHARS)) + "]"
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
        re_a = r"([0-9.]*)"
        re_b = r"(\([0-9./]*)"
        re_x = r"([a-z]*)"
        re_s = r"([-+]+)"
        re_d = r"([0-9./]*)"
        re_y = r"([a-z]+\))"
        re_c = r"(?=[/]*([0-9.]*))"
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

    def get_elements_from_sentence(self, var, sentence):
        """
        find elements values for var in the sentence
        :param var: <str> variable name
        :param sentence: <str> sentence to look for
        :return: <list> of <str> found values
        """
        re_elements_values = r"\s*[=:]{1}\s*([A-Za-z0-9\+,/\s]+)"
        values = re.findall(var + re_elements_values, sentence)

        fvalues = []
        for v in values:
            for c in re.split(r"[,/\s]", v):
                c = c.rstrip(NUMBERS_STR)
                if c not in fvalues and c in self._list_of_elements:
                    fvalues.append(c)
        return fvalues

    @property
    def re_stoichiometric_values(self):
        return r"\s*=\s*([-]{0,1}[0-9.,/and\s]+)[\s)\],;]"
