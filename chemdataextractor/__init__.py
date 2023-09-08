# -*- coding: utf-8 -*-
"""

"""

import logging

__title__ = 'ChemDataExtractor'
__version__ = '2.1.2'
__author__ = 'Matt Swain, Callum Court, Edward Beard, Juraj Mavracic and Taketomo Isazawa'
__email__ = 'm.swain@me.com, cc889@cam.ac.uk, ejb207@cam.ac.uk, jm2111@cam.ac.uk, ti250@cam.ac.uk'
__license__ = 'MIT'
__copyright__ = 'Copyright 2019 Matt Swain and contributors'

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

logging.basicConfig(
    level=logging.INFO,
    format=u'%(levelname)-10s in %(filename)-20s--> %(message)s',
    filename='log.txt', filemode='w'
)

from .doc.document import Document
