# coding=utf-8
from text2chem.chemical_data import default_abbreviations
from text2chem.core.formula_processing import FormulaProcessing


class DefaultProcessing:
    
    def __init__(self, regex_parser):
        self.__re = regex_parser
        self.__fp = FormulaProcessing(regex_parser)

    def process_string(self, material_string, chemical_structure):

        data = {}
        if not chemical_structure.composition:
            data = self.__fp.process_formula(material_string)
            if data["elements"]:
                data["composition"] = [{"formula": data["formula"],
                                        "amount": "1",
                                        "elements": data["elements"],
                                        "species": data["species"]}]

        else:
            composition = []
            oxygen_def = chemical_structure.oxygen_deficiency
            phase = chemical_structure.phase
            elements_x = {}
            amounts_x = {}

            for compound in chemical_structure.composition:
                formula = compound.formula
                amount = compound.amount
                formula = default_abbreviations.get(formula, formula)
                data = self.__fp.process_formula(formula)
                if not data["elements"]:
                    composition = []
                    amounts_x = {}
                    elements_x = {}
                    break
                new_compound = {"formula": data["formula"],
                                "amount": amount,
                                "elements": data["elements"],
                                "species": data["species"]}
                composition.append(new_compound)
                if not data["oxygen_deficiency"]:
                    data["oxygen_deficiency"] = oxygen_def
                if not data["phase"]:
                    data["phase"] = phase

                elements_x.update(data["elements_x"])
                amounts_x.update(data["amounts_x"])

            data["composition"] = composition
            data["amounts_x"] = amounts_x
            data["elements_x"] = elements_x

        self.update_chemical_structure(data, chemical_structure)

        return material_string, chemical_structure

    @staticmethod
    def update_chemical_structure(data, chem_structure):
        chem_structure.material_formula = data.get("material_formula", chem_structure.material_formula)
        chem_structure.material_name = data.get("material_name", chem_structure.material_name)

        chem_structure.additives = data.get("additives", chem_structure.additives)
        chem_structure.phase = data.get("phase", chem_structure.phase)
        chem_structure.oxygen_deficiency = data.get("oxygen_deficiency", chem_structure.oxygen_deficiency)

        chem_structure.amounts_x = data.get("amounts_x", chem_structure.amounts_x)
        chem_structure.elements_x = data.get("elements_x", chem_structure.elements_x)

        chem_structure.composition = [c for c in data.get("composition", chem_structure.composition)]
