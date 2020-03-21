#!/usr/bin/env python3

from block import *
import sys
import difflib as dif
import tkinter as tk
from txtcolour import *


file1=''
file2=''
options=()

def help():
    print('\naaxcmp [file1.aax] [file2.aax] <options>\n')
    print('options could be:')
    print(' -i compare logic blocs ;)')
    print(' -l compare line by line ;)')
    print(' -L compare line by line with selected conflicts')
    print(' -s print some statistics (dont use - in development)')
    print(' -w start GUI (dont use - in development)')
    print(' -h print this help')

    print('\n;) report friendly option')
    print('position of the options keys in command line, determine the sequence of the output')
    print('AAX files names location in the command line are not fixed but both should be present')
    return

print('Mar,2020,AY AMPL logic block compare')

if len(sys.argv)<3:
    help()
    sys.exit(0)
          
for arg in sys.argv[1:]:
    if arg[0]=='-' and len(arg)==2: # option
        options=options+(arg,)
    elif file1=='':
        file1=arg
    elif file2=='':
        file2=arg

if file1=='' or file2=='':
    print('cant find files in arguments')
    help()
    sys.exit(-1)

try:
    fileOne=aax(file1)
    fileTwo=aax(file2)
except:
    sys.exit(-2)

for op in options:
    if op=='-i':
        print(fileOne.cmp(fileTwo))
    if op=='-s':
        print('File %s'%fileOne.fname)
        print(fileOne.statout())
        print('File %s'%fileTwo.fname)
        print(fileTwo.statout())
    if op=='-L':
        d=dif.Differ()
        cmpres=d.compare(fileOne.lines,fileTwo.lines)
        for i in cmpres:
            if i[0]=='-' or i[0]=='+' or i[0]=='?':
                print(CSELECTED+i+CEND,end='')
            else:
                print(i,end='')
    if op=='-l':
        d=dif.Differ()
        cmpres=d.compare(fileOne.lines,fileTwo.lines)
        print('\n line by line comparision legend\n')
        print('\n If line started with [space] the line is equal in both files')
        print('\n If line started with [-] the line  exist in the first file only')
        print('\n If line started with [+] the line exist in the second file only')
        print('\n If line started with [?] the line does not exist in both files\n')
        for i in cmpres:
                print(i,end='')
    if op=='-h':
        help()
    
