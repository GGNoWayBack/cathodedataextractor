# -*- coding: utf-8 -*-
"""
Parser for finding Categories

:codeauthor: Callum Court (cc889@cam.ac.uk)
"""
import logging

from .actions import merge
from .elements import R
log = logging.getLogger(__name__)


def construct_category_element(category):
    """
    Construct an element for detecting categories.

    :param Category category: The Category to look for.
    :rtype: BaseParserElement or None
    """
    category_regex = '^'
    if not category or not category.category_dict:
        return None
    # Handle all the units
    for element in category.category_dict:
        category_regex += '(' + element.pattern + ')|'
    category_regex = category_regex[:-1]
    category_regex += '$'
    return (R(pattern=category_regex))('raw_value').add_action(merge)

