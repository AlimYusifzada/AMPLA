Requirements 
Python3, External lib to install: tkinter, xlwt, datetime
Other files: ampla.py, netband.py, duapt.py

except ampla, netband and duapt and be run independantly

---------------------------------
**ampla.py** is functions set for **AMPL** code compare/analysis implemented in **Python**

python code below as example to compare aa and aax files

from ampla import *
aa_before = AA('source_code_before.aa')
aa_after = AAX('source_code_after.aax')
print(aa_before.compare(aa_after))

--------------------------------------------------
**netband.py** to create spreadsheet from lst files

 to run from the terminal

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

