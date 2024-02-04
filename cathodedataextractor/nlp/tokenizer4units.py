# coding=utf-8
"""
Word tokenizer with boundary-controlled.
"""
import regex
from typing import Iterable
from .modi_cde_nlp import ModiChemWordTokenizer


class UnitsTokenizer(ModiChemWordTokenizer):
    """
    Split units, prepositions, and numerical values
    """

    units = ['V', 'mAg-1', 'Ag-1', 'mAhg-1', '°C', r'C(\b|to|and)', '%',
             r'h(?>rs|ours?h?)?\b', 'cycles?', 'nd', 'th', 'st']

    prepositions = ['to', '(within|with|in)', 'at', 'for', 'from', 'and', ',']

    units_pattern = [regex.compile(r'(?P<split1>(?<=[\d]){})'.format(unit)) for unit in units]
    pre_pattern = [regex.compile(r'(?P<split1>^({}))\d'.format('|'.join(prepositions)))]
    preposition_pattern = [regex.compile(
        r'(?P<split2>(?<=\d|{})({}))(?P<split3>\d)'.format(
            r'\b(V|mAg-1|Ag-1|mAhg-1|°C|C|%|h(?>rs|ours?h?)?|cycles?|nd|th|st)\b', preposition)) for
        preposition in prepositions]

    preposition_pattern.extend(units_pattern)
    preposition_pattern.extend(pre_pattern)

    def tokenize(self, s: str, additional_regex: Iterable = None):
        """
        Return a list of token strings from the given sentence.

        Args:
            s (str): The sentence string to tokenize.
            additional_regex : Any additional regex to further split the tokens.

        Returns:
            iter(str)
        """
        if additional_regex is None:
            additional_regex = self.preposition_pattern
        return [s[start:end] for start, end in self.span_tokenize(s, additional_regex=additional_regex)]


units_tokenizer = UnitsTokenizer()
