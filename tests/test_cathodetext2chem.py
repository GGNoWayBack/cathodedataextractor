# coding=utf-8
import json
import os
import unittest

from cathodedataextractor.cathodetext2chem import (
    CathodeParserPipelineBuilder,
    CathodeRegExParser
)
from tests.resources import TEST_PATH
from text2chem.preprocessing_tools.additives_processing import AdditivesProcessing
from text2chem.preprocessing_tools.chemical_name_processing import ChemicalNameProcessing
from text2chem.preprocessing_tools.phase_processing import PhaseProcessing
from text2chem.preprocessing_tools.mixture_processing import MixtureProcessing
from text2chem.postprocessing_tools.substitute_additives import SubstituteAdditives
from text2chem.postprocessing_tools.element_variables_processing import ElementVariablesProcessing
from text2chem.postprocessing_tools.stoichiometric_variables_processing import StoichiometricVariablesProcessing

mp = CathodeParserPipelineBuilder() \
    .add_preprocessing(AdditivesProcessing) \
    .add_preprocessing(ChemicalNameProcessing) \
    .add_preprocessing(PhaseProcessing) \
    .add_preprocessing(MixtureProcessing) \
    .add_postprocessing(SubstituteAdditives) \
    .add_postprocessing(ElementVariablesProcessing) \
    .add_postprocessing(StoichiometricVariablesProcessing) \
    .set_regex_parser(CathodeRegExParser) \
    .build()


class TestCathodeText2chem(unittest.TestCase):
    @staticmethod
    def return_data(testdata):
        for idx, data in enumerate(testdata):
            chem_name = data["material"]
            output = data["parser_output"]
            result = mp.parse(chem_name).to_dict()
            yield output, result

    def test(self):
        testdata = json.loads(open(os.path.join(TEST_PATH, "cathode.json")).read())
        for output, result in self.return_data(testdata):
            self.assertEqual(output, result)
