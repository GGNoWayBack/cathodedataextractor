# -*- coding: utf-8 -*-
"""
Reader classes that read a file and produce a ChemDataExtractor Document object.

"""
from .acs import AcsHtmlReader
from .cssp import CsspHtmlReader
from .elsevier import ElsevierXmlReader
from .markup import HtmlReader, XmlReader
from .pdf import PdfReader
from .plaintext import PlainTextReader
from .rsc import RscHtmlReader
from .nlm import NlmXmlReader
from .uspto import UsptoXmlReader
from .springer_jats import SpringerJatsReader


DEFAULT_READERS = [
    AcsHtmlReader(),
    RscHtmlReader(),
    NlmXmlReader(),
    UsptoXmlReader(),
    CsspHtmlReader(),
    ElsevierXmlReader(),
    XmlReader(),
    HtmlReader(),
    PdfReader(),
    PlainTextReader(),
    SpringerJatsReader(),
]
