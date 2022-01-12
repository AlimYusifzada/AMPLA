all scripts need xlwt module

---------------------------------

**ampla.py** is functions set for **AMPL** code compare/analysis implemented in **Python**

* ampla.py - set of the classes and functions to read and compare AA,AAX, BA, BAX code
* aaxcmp.py - gui module. run it to have simple interface

python code below as example to compare aa and aax files

from ampla import *

aa_before = AA('source_code_before.aa')

aa_after = AAX('source_code_after.aax')

print(aa_before.compare(aa_after))

--------------------------------------------------

**netband.py** to create spreadsheet from lst files

dir ...\*.mrimg /s /tc >created.lst

dir ...\*.mrimg /s /tw >accessed.lst

--------------------------------------------------

**duapt.py** to create spreadsheet report from LG files
