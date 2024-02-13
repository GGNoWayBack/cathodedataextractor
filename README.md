# CathodeDataExtractor

------------

[![Supported Python versions](https://img.shields.io/badge/python-3.6%20%7C%203.7-blue.svg)](https://www.python.org/downloads/) [![GitHub LICENSE](https://img.shields.io/github/license/GGNoWayBack/cathodedataextractor.svg)](https://github.com/GGNoWayBack/cathodedataextractor/blob/main/LICENSE)  [![PyPI version](https://badge.fury.io/py/cathodedataextractor.svg)](https://badge.fury.io/py/cathodedataextractor)  
`Cathodedataextractor` is a lightweight document-level information extraction pipeline that can automatically extract
comprehensive properties related to synthesis parameters, cycling and rate performance of cathode materials from the
literature of layered cathode materials for sodium-ion batteries.

## Installation

------------

`pip install cathodedataextractor`

## Features

------------
- It is built on open-source libraries: [pymatgen], [text2chem], and [ChemDataExtractor v2] with some modifications.
- [BatterySciBERT-uncased Multi-Label text classification] model for filtering documents. 
- Automated comprehensive data extraction pipeline for cathode materials.
- Paragraph Multi-Class classification algorithms for documents (HTML/XML) from the [RSC] and [Elsevier].
- A normalised entity handling process is provided.
- An effective chemical abbreviation detection module.
- Heuristic multi-level relation extraction algorithm for electrochemical properties.

In addition, the pipeline is also suitable for string sequence text extraction.

## Quick start

------------
#### Extract from documents

```python
from glob import iglob
from cathodedataextractor.information_extraction_pipe import Pipeline

pipline = Pipeline()
for document in iglob('*ml'):
    extraction_results = pipline.extract(document)
```
> 

#### Extract from string

```python
from cathodedataextractor.information_extraction_pipe import Pipeline

extraction_results = Pipeline.from_string(
    'Apart from the conventional cationic redox of transition metals, '
    'both Na-deficit and Na-excess materials have showcased the ability '
    'to exploit oxygen redox activity as O2–/O2n– for a charge '
    'compensation mechanism. To realize cathodes with enhanced energy '
    'density, a technique like the incorporation of alkali metal ions '
    'into transition metal layers has been adopted. Recent work by Boisse '
    '(13) et al. displayed the impact of honeycomb cation ordering of '
    'a highly stabilized intermediate phase for a Na2RuO3 cathode material '
    'in instigating the anionic redox activity and providing a capacity '
    'of 180 mAh g–1 at 0.2C with a capacity retention of 89% for over '
    '50 cycles. More devoted efforts to realize the utmost potential '
    'of anionic redox ought to be carried out in the future.')
```
> 

## Issues?

------------
You can either report an issue on GitHub or contact me directly. 
Try [gouyx@mail2.sysu.edu.cn](mailto:gouyx@mail2.sysu.edu.cn).











[pymatgen]: https://pymatgen.org

[text2chem]: https://github.com/CederGroupHub/text2chem

[ChemDataExtractor v2]: https://github.com/CambridgeMolecularEngineering/chemdataextractor2

[RSC]: https://pubs.rsc.org/

[Elsevier]: https://www.elsevier.com/

[BatterySciBERT-uncased Multi-Label text classification]: https://huggingface.co/NoWayBack/batteryscibert-uncased-abstract-mtc