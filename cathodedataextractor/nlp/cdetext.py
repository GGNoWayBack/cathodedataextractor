# coding=utf-8
"""
Text-based model.
"""
from chemdataextractor.doc.text import Span, Sentence, Text
from chemdataextractor.nlp.tag import POS_TAG_TYPE, NER_TAG_TYPE
from chemdataextractor.nlp.new_cem import CemTagger, BertFinetunedCRFCemTagger

from .modi_cde_nlp import ModiBertWordTokenizer

# Whether to use GPU
CemTagger.taggers[2] = BertFinetunedCRFCemTagger(gpu_id=-1)
cem_tagger = CemTagger()


class LText(Text):
    """
    A lighter weight Text based on chemdataextractor (Text) without abbreviation_detector, lexicon and PosTagger.

    A passage of text, comprising one or more sentences.
    """
    lexicon = None
    abbreviation_detector = None
    word_tokenizer = ModiBertWordTokenizer()
    taggers = [cem_tagger]

    def _sentences_from_spans(self, spans):
        sents = []
        for span in spans:
            sent = LSentence(
                text=self.text[span[0]:span[1]],
                start=span[0],
                end=span[1],
                word_tokenizer=self.word_tokenizer,
                abbreviation_detector=self.abbreviation_detector,
                pos_tagger=self.pos_tagger,
                ner_tagger=self.ner_tagger,
                document=self.document,
                models=self.models,
                taggers=self.taggers
            )
            sents.append(sent)
        return sents


class LSentence(Sentence):
    lexicon = None
    abbreviation_detector = None
    taggers = [cem_tagger]

    def _tokens_for_spans(self, spans):
        toks = [LRichToken(
            text=self.text[span[0]:span[1]],
            start=span[0] + self.start,
            end=span[1] + self.start,
            sentence=self
        ) for span in spans]
        return toks


class LToken(Span):
    def __init__(self, text, start, end):
        super().__init__(text, start, end)


class LRichToken(LToken):

    def __init__(self, text, start, end, sentence):
        super().__init__(text, start, end)
        self.sentence = sentence
        self._tags = {}

    @classmethod
    def _from_token(cls, token, sentence):
        rich_token = cls(text=token.text,
                         start=token.start,
                         end=token.end,
                         sentence=sentence)
        return rich_token

    @property
    def legacy_pos_tag(self):

        return self[NER_TAG_TYPE]

    def __getitem__(self, key):
        if key == 0:
            return self.text
        elif key == 1:
            return self.legacy_pos_tag
        elif isinstance(key, str):
            return self.__getattr__(key)
        else:
            raise IndexError("Key" + str(key) + " is out of bounds for this token.")

    def __getattr__(self, name):
        if name in self._tags.keys():
            return self._tags[name]
        else:
            self.sentence._assign_tags(name)
            if name not in self._tags.keys():
                raise AttributeError(
                    name + " is not a supported tag type for the sentence: " + str(self.sentence) + str(
                        self.sentence.taggers) + str(type(self.sentence))
                    + str(self._tags) + str(self))
            return self._tags[name]
