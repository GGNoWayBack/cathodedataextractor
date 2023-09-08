# coding=utf-8
import regex as re
from collections import OrderedDict

import text2chem.chemical_data as cd
from text2chem.constants import VACANCIES, LATIN_CAPITAL
from text2chem.core.formula_parser import parse_formula


class FormulaProcessing:
    def __init__(self, regex_parser):
        self.__re = regex_parser

    def process_formula(self, formula):
        """
        :param regex_parser:
        :param formula: str
        :return: chemical_structure
        """
        for s, r in cd.species_acronyms.items():
            formula = formula.replace(s, r)
        """
        build dictionary of elements and stoichiometries
        """
        formula_data = parse_formula(formula, self.__re)

        """
        looking for variables in elements and stoichiometry
        """
        for el, amt in formula_data["composition"].items():
            if el not in cd.list_of_elements | formula_data["elements_x"].keys() | VACANCIES:
                formula_data["elements_x"][el] = []
            for var in re.findall(self.__re.re_variables, amt):
                formula_data["amounts_x"][var] = {}

        formula, \
        elements, \
        elements_x, \
        stoichiometry_x, \
        oxygen_deficiency = self.__refine_variables(formula_data["formula"],
                                                    formula_data["composition"],
                                                    formula_data["elements_x"],
                                                    formula_data["amounts_x"],
                                                    formula_data["oxygen_deficiency"],
                                                    formula_data["oxygen_deficiency_sym"])

        if self.__is_acronym(formula, elements, elements_x) or self.__has_negative_composition(elements):
            return dict(formula=formula,
                        elements=OrderedDict(),
                        species=OrderedDict(),
                        oxygen_deficiency="",
                        phase="",
                        amounts_x={},
                        elements_x={})

        species = self.get_species(formula) if len(elements) > 2 or formula == "H2O" else elements

        return dict(formula=formula,
                    elements=elements,
                    species=species,
                    oxygen_deficiency=oxygen_deficiency,
                    phase=formula_data["phase"],
                    amounts_x={x: v for x, v in stoichiometry_x.items()},
                    elements_x={e: v for e, v in elements_x.items()})

    def get_species(self, formula):
        species_in_material, species_indexs, species_dict = OrderedDict(), OrderedDict(), OrderedDict()
        material_formula = formula
        i = 0
        for species in cd.species:
            while species in material_formula:
                material_formula = material_formula.replace(species, "specie" + str(i) + "_")
                species_in_material["specie" + str(i) + "_"] = species
                i += 1

        if not species_in_material:
            return OrderedDict()

        for species in cd.number_to_alphabet_dict:
            while species in material_formula:
                material_formula = material_formula.replace(species, cd.number_to_alphabet_dict[species])
                species_indexs[cd.number_to_alphabet_dict[species]] = species_in_material[species]
        species_info = parse_formula(material_formula, self.__re)["composition"]
        for species_index in species_info:
            species_dict[species_indexs[species_index]] = species_info[species_index]
        return species_dict

    @staticmethod
    def __refine_variables(formula, composition, elements_vars, stoichiometry_vars, oxy_def, oxy_def_sym):
        """
        :return:
        """
        """
        combining [RE, AE, TM] into one variable
        """
        rename_variables = [("R", "E"), ("A", "E"), ("T", "M")]
        for v1, v2 in rename_variables:
            if v1 in elements_vars and v2 in elements_vars and v1 + v2 in formula:
                elements_vars[v1 + v2] = []
                del elements_vars[v2]
                del elements_vars[v1]
                composition[v1 + v2] = composition[v2]
                del composition[v1]
                del composition[v2]

        """
        correction for Me variable
        """
        if "M" in elements_vars and "e" in stoichiometry_vars:
            elements_vars["Me"] = []
            del elements_vars["M"]
            del stoichiometry_vars["e"]
            c = composition["M"][1:]
            composition["Me"] = c if c != "" else "1.0"
            del composition["M"]

        """
        remove oxygen deficiency from variables
        """
        if not oxy_def and oxy_def_sym in stoichiometry_vars:
            oxy_def = None
        variables = [v for v in stoichiometry_vars.keys()
                     if [e for e, s in composition.items() if v in s] == ["O"]]
        oxy_def = chr(177) if len(variables) > 0 else oxy_def
        for var in variables:
            del stoichiometry_vars[var]
            composition["O"] = "1" if composition["O"] == var else composition["O"].replace(var, "").strip()
            formula = formula.replace(var, "")
        return formula, composition, elements_vars, stoichiometry_vars, oxy_def

    @staticmethod
    def __is_acronym(formula, composition, variables):

        if formula in cd.ions:
            return False

        if any(ion in formula and len(ion) > 1 for ion in cd.ions):
            return False

        if len(composition) == 2 and variables:
            return True

        capital_letters = LATIN_CAPITAL - set(cd.list_of_elements_1) - {"M", "L"}
        if [r for c in capital_letters for r in re.findall(c + "[A-Z0-9\-]", formula)] \
                and all(w not in formula for w in ["RE", "OAC", "TM", "ME"]):
            return True

        if all(e.isupper() and s in ["1.0", "1"] for e, s in composition.items()):
            return True

        elements_x = [el for el in variables.keys() if len(el) == 1 and el.isupper()]
        if len(elements_x) > 1:
            return True

        if all(c.isupper() for c in formula) and any(c not in cd.list_of_elements_1 for c in formula):
            return True

        if re.findall("[A-Z]{3,}", formula) != [] and \
            all(w not in formula for w in ["CH", "COO", "OH", "NH"] + [a for a in cd.default_abbreviations.keys()]):
            return True

        if "PV" == formula[0:2]:
            return True

        return False

    @staticmethod
    def __has_negative_composition(composition):

        flag = False
        try:
            flag = any(float(amt) < 0 for el, amt in composition.items())
        except:
            pass

        return flag
