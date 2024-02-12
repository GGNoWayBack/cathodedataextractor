# coding=utf-8
"""
Information extraction pipeline.
"""
import os
import csv
from pathlib import Path
from typing import List, Dict, Tuple, Union, Optional, NamedTuple

from .parse import PARAGRAPH_SEPARATOR, ATTRIBUTE_PROMPT, BACKSLASH_REPLACEMENT
from .parse.relation_extraction import PropertyParse
from .nlp import LText, AbbreviationDetection
from .text import TagClassificationPar2Text, BatteriesTextProcessor
from .relationextractpostprocessing import data_pprocess
from .util_functions import write_into_json, write_csv

__all__ = ['Pipeline']

class PipelineData(NamedTuple):
    """
    Information extraction pipeline data types.
    """
    year: int = None
    doi: str = None
    pred_labels: Optional[List[str]] = None
    introduction: Optional[str] = ''
    experiment: Optional[str] = ''
    property_text: Optional[str] = ''

    abbreviation: Union[list, List[Tuple[str, str]]] = []
    stoichiometric_variables_chem: Union[dict, Dict[str, List[int]]] = {}


PATH = Path(__file__).absolute().parent.parent


class Pipeline:

    def __init__(self, select_filename=None):
        self.select_data = {}

        if select_filename is not None:
            with open(str(PATH / f"{select_filename}"),
                      'r', encoding='utf-8') as f:  # Cached CSV files of the documents to be analyzed and their labels.
                self.select_data = {row[1].replace('/', BACKSLASH_REPLACEMENT): row[2] for row in csv.reader(f)}

    @staticmethod
    def from_string(text: str):

        bat_doc = BatteriesTextProcessor(text, special_normal=True)

        AbbreviationDetection.ner = bat_doc.ner
        abbreviation_detection = AbbreviationDetection()
        processed_text = ' '.join(bat_doc.processed_text)
        abbreviation_detection = abbreviation_detection(processed_text)

        prep_data = PipelineData(property_text=processed_text,
                                 abbreviation=abbreviation_detection.new_abbreviation,
                                 stoichiometric_variables_chem=abbreviation_detection.stoichiometric_variables_chem)

        pp: PropertyParse = Pipeline._relation_extract(prep_data)
        for j in pp.results:
            if pp.current_define:
                j['Current_define'] = pp.current_define

        final_records = []
        for orig in pp.results:
            final_records.extend(data_pprocess(orig))

        return dict(layer1=prep_data._asdict(),
                    layer2=pp.results,
                    layer3=final_records)

    def extract(self, path: str):
        """
        Note:
            The file name is named after the doi of the article where '/' is replaced by '.'.

        Args:
            path (str): Document (Xml or Html) file path.
        """

        head, tail = os.path.split(path)
        if self.select_data and tail.rsplit('.', 1)[0] not in self.select_data:
            return

        """
        Paragraph classification.
        """
        data: PipelineData = self._collect_corpus(head=head, tail=tail)

        """
        Text preprocessing and chemical supplementary information extraction (CSIE).
        """
        prep_data: PipelineData = self._preprocess_csie(data)

        """
        Named entity recognition (NER) and relation extraction.
        """
        pp: PropertyParse = self._relation_extract(prep_data)
        for j in pp.results:
            if pp.current_define:
                j['Current_define'] = pp.current_define

        final_records = []
        for orig in pp.results:
            final_records.extend(data_pprocess(orig))
        return dict(layer1=data._asdict(),
                    layer2=prep_data._asdict(),
                    layer3=pp.results,
                    layer4=final_records)

    def _collect_corpus(self, head, tail) -> PipelineData:

        TC = TagClassificationPar2Text()
        TC.get_abstract(head=head, tail=tail)

        TC.fulltext(head=head, tail=tail)

        return PipelineData(int(TC.year), TC.doi,
                            introduction=TC.introduction, experiment=TC.experiment, property_text=TC.partial_text,
                            pred_labels=self.select_data.get(TC.doi.replace("/", '.'), None))

    @staticmethod
    def _preprocess_csie(data: PipelineData) -> PipelineData:
        # preprocess
        year, doi, labels, _intro, _experi, _partial_text = data[:6]

        intro = _intro.strip(PARAGRAPH_SEPARATOR)

        num = intro.count(PARAGRAPH_SEPARATOR)
        bat_doc = BatteriesTextProcessor(_experi, special_normal=True)
        bat_full_text = BatteriesTextProcessor(intro + PARAGRAPH_SEPARATOR + _partial_text, special_normal=True)

        experi, partial_text = bat_doc.processed_text, bat_full_text.processed_text
        ltext = LText(' '.join(partial_text))
        property_par = '\n'.join([par for par in partial_text[num + 1:]
                                  if any(_ for _ in ATTRIBUTE_PROMPT if _ in par)])

        # Chemical abbreviation detection and supplementary information identification
        AbbreviationDetection.ner = bat_full_text.ner
        abbreviation_detection = AbbreviationDetection()
        abbreviation_detection = abbreviation_detection(ltext)

        return PipelineData(data.year, data.doi, data.pred_labels,
                            '\n'.join(partial_text[:num + 1]), '\n'.join(experi), property_par,
                            abbreviation_detection.new_abbreviation,
                            abbreviation_detection.stoichiometric_variables_chem)

    @staticmethod
    def _relation_extract(data: PipelineData) -> PropertyParse:

        year, doi, labels, _, exp, property_text, abb_che, stoichiometric_variable = data

        pp = PropertyParse(abb_names=abb_che,
                           doi=doi,
                           year=year,
                           stoichiometric_variable=stoichiometric_variable)
        # Experimental parameter relation extraction
        pp.experimental_extraction(LText(property_text if not exp else exp))

        # Property relation extraction
        full_text_par = property_text.split('\n')
        for full_par in full_text_par:
            pp.property_extraction(LText(full_par))
        return pp
