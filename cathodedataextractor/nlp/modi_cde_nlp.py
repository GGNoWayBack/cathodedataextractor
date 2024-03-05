# -*- coding: utf-8 -*-
"""Some modifications have been made to ChemDataExtractor v2"""
from chemdataextractor.nlp import cem
"""
nlp/cem
"""
# Split on plus surrounded by any letter or number provided no brackets
change_cem = cem.SPECIALS.index('^([^\(\)]+\w)\+(\w[^\(\)]+)$')
cem.SPECIALS[change_cem] = '^([^()]+ \w)\+([^xyx][^()]+)'

"""
nlp/tokenize
"""
import regex as re
from chemdataextractor.nlp.tokenize import regex_span_tokenize, ChemWordTokenizer, BertWordTokenizer

MODI_SPLIT = ChemWordTokenizer.SPLIT[:]
MODI_SPLIT[ChemWordTokenizer.SPLIT.index('°')] = '°(?!C)'


class ModiChemWordTokenizer(ChemWordTokenizer):
    SPLIT = MODI_SPLIT  # \u00b0 Degrees

    def handle_additional_regex(self, s, span, nextspan, additional_regex):
        text = s[span[0]:span[1]]
        if not additional_regex:
            return None
        for regex in additional_regex:
            split_text = regex.search(text)
            if not split_text:
                continue
            groups = split_text.groupdict()
            groups = {_: groups[_] for _ in groups if groups[_] is not None}
            groupindex = split_text.re.groupindex
            for group_name, group in groups.items():
                if group is None:
                    continue
                regs = split_text.regs[groupindex[group_name]]
                index = regs[0]
                group_length = len(groups)
                if 'split' in group_name and group_length != 0:
                    return self._split_span(span, index, regs[1] - regs[0]) if group_length > 1 \
                        else self._split_span(span, index, 0)

    def span_tokenize(self, s, additional_regex=None):
        """"""
        # First get spans by splitting on all whitespace
        # Includes: \u0020 \u00A0 \u1680 \u180E \u2000 \u2001 \u2002 \u2003 \u2004 \u2005 \u2006 \u2007 \u2008 \u2009
        # \u200A \u202F \u205F \u3000
        spans = [(left, right) for left, right in regex_span_tokenize(s, '\s+') if not left == right]
        i = 0
        # Recursively split spans according to rules
        while i < len(spans):
            subspans = self._subspan(s, spans[i], spans[i + 1] if i + 1 < len(spans) else None, additional_regex)
            subspans = [subspan for subspan in subspans if subspan[1] - subspan[0] > 0]
            spans[i:i + 1] = subspans
            if len(subspans) == 1:
                i += 1
        return spans


class ModiBertWordTokenizer(BertWordTokenizer):

    def span_tokenize_bert(self, s, additional_regex=None):
        output = self.tokenizer.encode(str(s))
        offsets = output.offsets[1: -1]
        given_tokens = output.tokens[1: -1]
        current_span = (0, 0)
        spans = []
        i = 0
        zipped = [el for el in zip(offsets, given_tokens)]

        while i < len(zipped):
            offset, token = zipped[i]

            # If symbol is in do_not_split and it's part of a word, i.e. it's not surrounded
            # by whitespace, then don't split it
            if (s[offset[0]: offset[1]] in self.do_not_split_if_in_num and offset[0] == current_span[1]
                    and i < len(zipped) - 1 and zipped[i + 1][0][0] == offset[1]
                    and re.match("\d+$", s[zipped[i + 1][0][0]: zipped[i + 1][0][1]])):
                i += 1
                offset, token = zipped[i]
                current_span = (current_span[0], offset[1])
            # If symbol is in do_not_split and it's part of a word, i.e. it's not surrounded
            # by whitespace, then don't split it
            elif (s[offset[0]: offset[1]] in self.do_not_split and offset[0] == current_span[1]
                  and i < len(zipped) - 1 and zipped[i + 1][0][0] == offset[1]):
                i += 1
                offset, token = zipped[i]
                current_span = (current_span[0], offset[1])
            # Prevent splitting of negative numbers, but allow splitting of ranges such as 0.5-1.0
            # and cases like 5-Bromo-6-Penda...
            elif (s[offset[0]: offset[1]] == "-"
                  and i < len(zipped) - 1 and zipped[i + 1][0][0] == offset[1]
                  and re.match(r"\d+$", s[zipped[i + 1][0][0]: zipped[i + 1][0][1]])
                  and (i == 0
                       or not (zipped[i - 1][0][1] == offset[0]
                               and re.match(r"\d+$", s[zipped[i - 1][0][0]: zipped[i - 1][0][1]])))
                  and (i >= len(zipped) - 2
                       or not (zipped[i + 2][0][0] == zipped[i + 1][0][1]
                               and s[zipped[i + 2][0][0]: zipped[i + 2][0][1]] == "-"))):
                i += 1
                if current_span != (0, 0):
                    spans.append(current_span)
                current_span = offset
                offset, token = zipped[i]
                current_span = (current_span[0], offset[1])
            # If the token is a subword, as defined by BERT, then merge it with the previous token
            elif len(token) > 2 and token[:2] == "##":
                current_span = (current_span[0], offset[1])
            # Otherwise, split it
            else:
                if current_span != (0, 0):
                    spans.append(current_span)
                current_span = offset
            i += 1

        spans.append(current_span)

        # Perform additional tokenisation as required by the additional regex
        if additional_regex is not None:
            i = 0
            while i < len(spans):
                subspans = self.handle_additional_regex(s, spans[i], spans[i + 1] if i + 1 < len(spans) else None,
                                                        additional_regex)
                if subspans is not None:
                    spans[i:i + 1] = [subspan for subspan in subspans if subspan[1] - subspan[0] > 0]
                i += 1

        return spans
