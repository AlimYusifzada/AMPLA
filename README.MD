**AMPLA** is **Python3** for **AMPL** code compare/analysis

* ampla.py - set of the classes and functions to read and compare AA,AAX, BA, BAX code
* aaxcmp.py - gui module. run it to have simple interface

* simple example below:

from ampla import *

aa_before=AA('source_code_before.aa')  
aa_after=AA('source_code_after.aa')

print(aa.before.compare(aa_after))

