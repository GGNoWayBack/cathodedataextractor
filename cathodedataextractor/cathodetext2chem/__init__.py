# coding=utf-8
import os

if os.name == "nt":
    import _locale
    _locale._gdl_bak = _locale._getdefaultlocale
    _locale._getdefaultlocale = (lambda *args: (_locale._gdl_bak()[0], 'utf8'))

from .core.formula_parser import *

from .parser_pipeline import CathodeParserPipelineBuilder
from .regex_parser import CathodeRegExParser
from .postprocessing_tools import CathodeStoichiometricVariablesProcessing
