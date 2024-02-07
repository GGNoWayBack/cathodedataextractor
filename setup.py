# coding=utf-8
import os
from setuptools import find_packages, setup

long_description = open('README.md', encoding="utf8").read()

setup(
    name='cathodedataextractor',
    version='0.0.1',
    description='A document-level information extraction pipeline for layered cathode materials for sodium-ion batteries.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='text-mining information-extraction nlp battery-information',
    author='Yuxiao Gou',
    author_email='gouyx@mail2.sysu.edu.cn',
    url='https://github.com/GGNoWayBack/cathodedataextractor',
    install_requires=[
        'word2number',
        'text2chem==0.0.2',
        'chemdataextractor2==2.2.2',
        'pdfminer.six >=20160614, <=20221105 ; python_version < "3.8"'
    ],
    license='MIT',
    packages=find_packages(),
    platforms=["all"],
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering',
        'Topic :: Text Processing',
    ],
)
