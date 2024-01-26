	
Code files can be from different source, i.e. can have one extracted from FCB and the other from ONB.

This program is used to compare pairs of .AAX .AA .BA or .BAX files, using other formats may result in runtime errors. Possible comparisions (AAX<->AAX; AAX<->AA; BAX<->BAX; BA<->BAX)										

Once 'Compare' is pressed you will be asked to select the two directories (before and after) you wish to compare. The default search location is the same location as this program.											

A workbook will be output and saved in the 'after' directory.

XLS file crated individually for each pair and contain two tabs

if XLS file has *DIF*	in its name it means, descrepancies found and logged
    										
Requirements for people who are using source code instead of compiled version 
Python3 required!
Core file containing all funcs: *ampla.py* - you could use it in your own projects without any other libraries.
External libs to install: tkinter, xlwt, datetime
To run pusa.py required pysimplegui
Other files: netband.py, duapt.py (not revelant for comparison and can run independently)

---------------------------------
**ampla.py** are **Python 3** functions set for **AMPL** code compare/analysis

**AMPL** Advant Master Piece Language is an ABB Ltd company product for AC400 series controllers 

some examples to compare **AA** and **AAX** files shown below:

from ampla import *
aa_before = AA('source_code_before.aa')
aa_after = AAX('source_code_after.aax')
print(aa_before.compare(aa_after))

--------------------------------------------------
**netband.py** to calculate network bandwidth

command below run from the terminal to collect data

dir ...\*.mrimg /s /tc >1.lst
dir ...\*.mrimg /s /tw >2.lst

mrimg files are images of the hosts collected at NAS and used to calculate network broadband
file 1.lst contains date and time of the files were created
file 2.lst contains date and time of the files last time accessed(changed) or copy process finished
netband use the data to calculate network speed for the hosts

--------------------------------------------------
**duapt.py** to create spreadsheet report from LG files
possible to run from the terminal
LG files need to be created with ONB contains start and finish time of the dump

