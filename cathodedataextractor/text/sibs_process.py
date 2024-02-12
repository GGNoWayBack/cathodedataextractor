# coding=utf-8
from string import punctuation, digits
from typing import List
# from chemdataextractor.doc.text import Span, Text, Sentence
from chemdataextractor.text.normalize import chem_normalize
from pymatgen.core.composition import Composition

from ..nlp import LText, CNer
from ..parse import *
from ..utils import any_func

reference_symbols = punctuation + digits


class BatteriesTextProcessor:
    """
    Batteries Science Text Processing Tools.
    """
    ner = CNer()

    def __init__(self, text: str = '', normalize: bool = True, special_normal: bool = False):
        """

        Args:
            text (str): Input text string.
            normalize (bool): Whether normalization is needed. Only for chemical formula. Defaults to True.
            special_normal (bool): Whether more specific normalization is needed. Defaults to False.
        """
        self.preprocessed_text = ''

        if normalize:
            self.processed_text = self.final_processed_text(text, special_normal=special_normal)
        else:
            self.processed_text = text

    def final_processed_text(self, text, special_normal=True) -> List[str, ]:
        """

        Returns:
            A list of strings where each element corresponds to a processed sentence.
        """
        text = self.remove_unprintable_chars(text)

        text = chem_normalize.normalize(text)  # Chemical text normalization
        if special_normal:
            self.preprocessed_text = self.replace_sub(text)
        else:
            self.preprocessed_text = text

        par_total = []
        for par in self.preprocessed_text.split(PARAGRAPH_SEPARATOR):
            cde = LText(par)

            new_text = []
            for sentence in cde.sentences:
                new_text.append(self.text_process(sentence.text, sentence.cems, sentence.start))
            par_total.append(' '.join(new_text).replace('\n', '').replace('  ', ''))
        return par_total

    @staticmethod
    def replace_sub(text):
        """
        Normalised texts include the harmonisation of symbols, etc.
        """

        for rep in REPLACE:
            text = text.replace(rep[0], rep[1])

        for su in SUB:
            text = re.sub(su[0], su[1], text)

        elem_name_with_valence = ELEMENT_NAMES_VALENCE.finditer(text, re.I)
        for _ in elem_name_with_valence:
            text = text.replace(_.group(2), '', 1)

        return text

    def text_process(self, text: str, cem: list, s_start: int) -> str:

        """
        The main thing here is to clean the text to return the normalized chemical formula expression
        """
        new_text = []
        if len(cem) == 1:
            start, end = cem[0].start - s_start, cem[0].end - s_start
            normalized_cem = self.ner.normalized_compound_formula(cem[0].text)
            new_text.extend([text[: start], normalized_cem, text[end:]])
            return ''.join(new_text)
        elif len(cem) > 1:
            # offset = before = 0
            before = 0
            for num, ce in enumerate(cem):
                # start, end = ce.start + offset, ce.end + offset
                start, end = ce.start - s_start, ce.end - s_start
                normalized_cem = self.ner.normalized_compound_formula(ce.text)
                new_text.extend([text[before: start], normalized_cem, text[end: cem[num + 1].start - s_start]]
                                if num + 1 < len(cem) else [text[before: start], normalized_cem + text[end:]])
                # offset += ce.length - len(normalized_cem)
                before = cem[num + 1].start - s_start if num + 1 < len(cem) else end
            return ''.join(new_text)
        return text

    @staticmethod
    def remove_unprintable_chars(s: str) -> str:

        """
        Remove all invisible characters
        """
        return ''.join(x for x in s if x.isprintable() or x == '\n')
