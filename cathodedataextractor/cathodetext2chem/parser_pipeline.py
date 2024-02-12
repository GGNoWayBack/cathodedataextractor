# coding=utf-8
import re
from text2chem.parser_pipeline import (
    ChemicalStructure, list_of_elements, name2element, diatomic_molecules,
    ParserPipeline,
    ParserPipelineBuilder,
)
from cathodedataextractor.parse import end_parentheses


class CathodeParserPipeline(ParserPipeline):
    def parse(self, material_string):
        """
        :param material_string:
        :return: chemical structure (see chemical_structure.py)
        """
        output_structure = ChemicalStructure(material_string)

        _, _postprocessing = end_parentheses(material_string)
        _postprocessing = re.sub(r'\s?(/)\s?', r'\1', _postprocessing) if _postprocessing else _postprocessing
        material_string = material_string[:_].rstrip() if _ else material_string
        if not material_string:
            return output_structure

        """
        element-like material string
        """
        if material_string in list_of_elements:
            return output_structure.element_structure(material_string)
        if material_string in name2element:
            return output_structure.element_structure(name2element[material_string])

        """
        material string is diatomic molecule
        """
        if material_string in diatomic_molecules:
            return output_structure.diatomic_molecule_structure(material_string[0])

        """
        preprocessing steps
        """
        for p in self._preprocessings:
            material_string, output_structure = p(self._regex_parser).process_string(material_string,
                                                                                     output_structure)

        """
        default functionality: extraction of data from chemical formula
        """
        material_string, output_structure = self._default_processing.process_string(material_string,
                                                                                    output_structure)

        """
        postprocessing steps
        """
        if _postprocessing:
            for p in self._postprocessings:
                p(self._regex_parser).process_data(output_structure, [_postprocessing, ])
        output_structure.combine_formula()

        return output_structure


class CathodeParserPipelineBuilder(ParserPipelineBuilder):
    def build(self, options=None):  # -> MaterialParser
        return CathodeParserPipeline(options,
                                     self._regex_parser,
                                     self._preprocessings,
                                     self._postprocessings)
