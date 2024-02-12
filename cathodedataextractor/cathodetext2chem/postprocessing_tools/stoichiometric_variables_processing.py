# coding=utf-8
from text2chem.postprocessing_tools.stoichiometric_variables_processing import StoichiometricVariablesProcessing


class CathodeStoichiometricVariablesProcessing(StoichiometricVariablesProcessing):

    def __get_values_from_sentence(self, var, sentence):
        """
        find numeric values of var in sentence
        :param var: <str> variable name
        :param sentence: <str> sentence to look for
        :return: <dict>: max_value: upper limit
                        min_value: lower limit
                        values: <list> of <float> numeric values
        """
        values = {"values": [],
                  "max_value": None,
                  "min_value": None}

        """
        considering 4 cases of mentioning the values of variable in the text
        1. list of discrete values
        2. range x = ... - ...
        3. range ... < x < ...
        4. x from ... to ...
        """
        regs = [(var + self._re.re_stoichiometric_values, "discrete"),
                (var + self._re.re_stoichiometric_range_hyphen, "range"),
                (self._re.re_stoichiometric_range_lhs + var + self._re.re_stoichiometric_range_rhs, "range"),
                (var + self._re.re_stoichiometric_range_ft, "range")]

        for r, m in regs:
            if values["values"] == [] and values["max_value"] is None:
                r_res = re.findall(r, sentence.replace(" - ", "-").replace(";", " ;"))
                values = self.__get_values(r_res, m)

        return values



