
This program is used to compare pairs of .AAX .AA .BA or .BAX files, using other formats may result in runtime errors. 
Possible combinations (AAX<->AAX; AAX<->AA; AA<->AA; BAX<->BAX; BA<->BAX; BA<->BA)							
	
>Code files can be from different source, i.e. can have one extracted from FCB and the other from ONB.

Once **select before and after directories** button is pressed you will be asked to select the directories contains source code you wish to compare. XLS files will be generated in the 'after' directory.
>dialog window caption will guide you wich directory it's asking for
>
>check box "generate line2line" is off by default. if you set it on, excel report will be expanded with additional tab contains line to line code representation. this option is not recommended
>program automatically detect BA/BAX/AA/AAX files
>
>if database source is splitted in several files they will be combined together. same option is true for logic source files.

XLS files crated individually for each pair and contain two tabs. Comparison report and "line to line"
Please note that "line to line" is not genue line to line due to... see next line.

> Comarison performed by logic blocks (not line to line), so AMPL code parsing performed before comapison.

The program try to read and compare numeric constants as numbers, i.e. D=2.3e-3 and D=0.0023 are the same and will not be detected as differnce

If XLS file name ends with *DIF* it means, descrepancies found and logged

New revision (PUSA) has some experimental funtionality wich do not affect comparison tool

Requirements for people who are using source code instead of compiled version 
* use Python3.
* *ampla.py* is a core file contains all functions for parsing and code compare.
* External libs to install to run PUSA.PY: tkinter, xlwt, datetime, pysimplegui
* Other files: netband.py, duapt.py (not revelant for comparison and can be used separately)
---
**ampla.py** are **Python 3** functions set for **AMPL** code compare/analysis

**AMPL** Advant Master Piece Language is an ABB Ltd company product for AC400 series controllers 

python example to compare **.AA** and **.AAX** files shown below:

>from ampla import *
>
>aa_before = AA('source_code_before.aa')
>
>aa_after = AAX('source_code_after.aax')
>
>print(aa_before.compare(aa_after))

---

**netband.py** to calculate network bandwidth

command below run from the terminal to collect data
>dir ...\*.mrimg /s /tc >1.lst
>
>dir ...\*.mrimg /s /tw >2.lst

mrimg files are images of the hosts collected at NAS and used to calculate network broadband
>file 1.lst contains date and time of the files were created
>
>file 2.lst contains date and time of the files last time accessed(written)
---
**duapt.py** to create spreadsheet report from LG files>LG files need to be created with ONB contains start and finish time of the dump

