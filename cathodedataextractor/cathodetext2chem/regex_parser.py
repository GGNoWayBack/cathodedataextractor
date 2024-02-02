# coding=utf-8
from text2chem.regex_parser import (
    re,
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
