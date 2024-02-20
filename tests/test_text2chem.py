# coding=utf-8
import json
import os
import unittest
from tests.resources import TEST_PATH
from text2chem.regex_parser import RegExParser
from text2chem.parser_pipeline import ParserPipelineBuilder
from text2chem.preprocessing_tools.additives_processing import AdditivesProcessing
from text2chem.preprocessing_tools.chemical_name_processing import ChemicalNameProcessing
from text2chem.preprocessing_tools.mixture_processing import MixtureProcessing
from text2chem.preprocessing_tools.phase_processing import PhaseProcessing
from text2chem.postprocessing_tools.substitute_additives import SubstituteAdditives


mp = ParserPipelineBuilder() \
    .add_preprocessing(AdditivesProcessing) \
    .add_preprocessing(ChemicalNameProcessing) \
    .add_preprocessing(PhaseProcessing) \
    .add_preprocessing(MixtureProcessing)\
    .add_postprocessing(SubstituteAdditives)\
    .set_regex_parser(RegExParser)\
    .build()


class TestText2chem(unittest.TestCase):

    @staticmethod
    def return_data(testdata):
        for idx, data in enumerate(testdata):
            chem_name = data["material"]
            output = data["parser_output"][0]
            result = mp.parse(chem_name).to_dict()
            yield output, result

    def test_formulas(self):
        """
        test formulas
        """
        testdata = json.loads(open(os.path.join(TEST_PATH, "formulas.json"), encoding="utf8").read())
        for output, result in self.return_data(testdata):
            self.assertEqual(output, result)

    def test_additives(self):
        """
        test additives
        """
        testdata = json.loads(open(os.path.join(TEST_PATH, "additives.json"), encoding="utf8").read())
        for output, result in self.return_data(testdata):
            self.assertEqual(output, result)

    def test_chemical_names(self):
        """
        test chemical names
        """
        testdata = json.loads(open(os.path.join(TEST_PATH, "chemical_names.json"), encoding="utf8").read())
        for output, result in self.return_data(testdata):
            self.assertEqual(output, result)

    def test_mixtures(self):
        """
        test mixtures: alloys, solid solutions, composites
        """
        testdata = json.loads(open(os.path.join(TEST_PATH, "mixtures.json"), encoding="utf8").read())
        for output, result in self.return_data(testdata):
            self.assertEqual(output, result)

    def test_phases(self):
        """
        test phases
        """
        testdata = json.loads(open(os.path.join(TEST_PATH, "phases.json"), encoding="utf8").read())
        for output, result in self.return_data(testdata):
            self.assertEqual(output, result)

    def test_all(self):
        """
        comprehensive test
        """
        testdata = json.loads(open(os.path.join(TEST_PATH, "comprehensive.json"), encoding="utf-8").read())
        for output, result in self.return_data(testdata):
            self.assertEqual(output, result)
