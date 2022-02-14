Requirements to run ARMOR_GUI:

Python3

External lib to instal: os,tkinter, xlwt, datetime

Other files: ampla.py, netband.py, duapt.py

---------------------------------

**ampla.py** is functions set for **AMPL** code compare/analysis implemented in **Python**

python code below as example to compare aa and aax files

from ampla import *

aa_before = AA('source_code_before.aa')

aa_after = AAX('source_code_after.aax')

print(aa_before.compare(aa_after))

--------------------------------------------------

**netband.py** to create spreadsheet from lst files

possible to run from the terminal

dir ...\*.mrimg /s /tc >created.lst

dir ...\*.mrimg /s /tw >accessed.lst

--------------------------------------------------

**duapt.py** to create spreadsheet report from LG files

possible to run from the terminal
