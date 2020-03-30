#!/usr/bin/env python3

from block import *
import sys
import difflib as dif
from tkinter import Frame,Label, Button, Entry, Text, Tk
from tkinter import scrolledtext as STX
##from txtcolour import *


file1=''
file2=''
wwidth=120
options=()


class mainGUI:

    def __init__(self,root):
        self.root=root

        Label(text='gui interface for aaxcmp rev0.2 Mar/2020').grid(row=0,column=1,sticky='E')
        Label(text='AAX file before:').grid(row=1,column=0,sticky='E')
        self.FBefore=Entry(root,width=wwidth)
        self.FBefore.grid(row=1,column=1,sticky='W')
        Label(text='AAX file after:').grid(row=2,column=0,sticky='E')
        self.FAfter=Entry(root,width=wwidth)
        self.FAfter.grid(row=2,column=1,sticky='W')

        self.cmpBTN=Button(root,text='COMPARE',command=self.icompare).grid(row=3,column=0,sticky='N')
        self.cmpOutput=STX.ScrolledText(root,width=wwidth)
        self.cmpOutput.grid(row=3,column=1)

    def icompare(self):
        fA=aax(self.FBefore.get())
        fB=aax(self.FAfter.get())
        self.cmpOutput.insert('1.0',str(fA.cmp(fB)))



def aaxgui():
    mainwin=Tk()
    win=mainGUI(mainwin)
    win.title='aaxcmp with GUI rev0.2'
    mainwin.mainloop()
    pass



def help():
    print('\naaxcmp [file1.aax] [file2.aax] <options>\n')
    print('options could be:')
    print(' -i compare logic blocs ;)')
    print(' -l compare line by line ;)')
##    print(' -L compare line by line with selected conflicts (use in terminal)')
##    print(' -s print some statistics (dont use - in development)')
##    print(' -w start GUI (dont use - in development)')
    print(' -h print this help')

    print('\n ;) report friendly option\n')
    print('position of the options keys in command line, determine the sequence of the output')
    print('AAX files names location in the command line are not fixed but both should be present')
    return

print('Mar/2020, Baku ABB, AY, AMPL logic (aax files) compare tool')

if len(sys.argv)<3:
    help()
    aaxgui()
    sys.exit(0)

for arg in sys.argv[1:]:
    if arg[0]=='-' and len(arg)==2: # options
        if arg not in options:
            options=options+(arg,)
    elif file1=='' and len(arg)>3 and arg[-3:].lower()=='aax':
        file1=arg
    elif file2=='' and len(arg)>3 and arg[-3:].lower()=='aax':
        file2=arg

if file1=='' or file2=='':
    print('\ncant find both files in arguments\n')
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
##    if op=='-L':
##        d=dif.Differ()
##        cmpres=d.compare(fileOne.lines,fileTwo.lines)
##        for i in cmpres:
##            if i[0]=='-' or i[0]=='+' or i[0]=='?':
##                print(CSELECTED+i+CEND,end='')
##            else:
##                print(i,end='')
    if op=='-l':
        d=dif.Differ()
        cmpres=d.compare(fileOne.Lines,fileTwo.Lines)
        print('\n line by line comparision legend\n')
        print('\n If line started with [space] the line is equal in both files')
        print('\n If line started with [-] the line  exist in the first file only')
        print('\n If line started with [+] the line exist in the second file only')
        print('\n If line started with [?] the line does not exist in both files\n')
        for i in cmpres:
                print(i,end='')
    if op=='-h':
        help()

