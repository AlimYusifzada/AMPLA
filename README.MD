**AMPLA** is **Python3** implementation for **AMPL** code compare/analysis.
Read source **AMPL** code from **AAX** files.
Each logic block represents by an object and could be compared with the other one.

**py** files: **ampla.py** and **aaxcmp.py** should be in the same directory. 
If you run it without options simple **GUI** will be activated.

To run from **MS Windows** command line:
> ...\your_directory_at_mswindows>python3 aaxcmp.py FileA.aax FileB.aax {keys}

To run from **Linux** terminal:
> .../your_directory_at_linux$./aaxcmp.py FileA.aax FileB.axx {keys}

>**keys**
> - **-i** compare logic blocs
> - **-l** compare line by line
> - **-s** print some statistics
> - **-h** print this help
> - **-rTAG_NAME** cross reference of the TAG_NAME at FileA.aax and FileB.aax NOTE:spaces are not applicable, case sensitive
> - **-v** search for unconnected, void pins

position of the *keys* in command line, determine sequence of the output data
**AAX** files names location in the command line are not fixed but both should be present
