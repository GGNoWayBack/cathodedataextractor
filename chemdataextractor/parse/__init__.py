# -*- coding: utf-8 -*-
"""
Parse text using rule-based grammars.

"""
from .actions import join, merge, strip_stop, fix_whitespace
from .elements import W, I, R, T, H
from .elements import Any, Word, Tag, IWord, Regex, Start, End, Hide, Not
from .elements import Every, And, Or, First, ZeroOrMore, OneOrMore, Optional, Group, SkipTo
from .auto import BaseAutoParser, AutoSentenceParser, AutoTableParser
from .base import BaseParser, BaseSentenceParser, BaseTableParser
