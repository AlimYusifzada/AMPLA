#!/usr/bin/env python3
from ampla import *
import sys
import difflib as dif
from tkinter import Frame,Label, Button, Entry, Text, Tk
from tkinter import scrolledtext as STX
##from txtcolour import *

rev='0.5'

file1=''
file2=''
wwidth=120
options=()
files=()

class mainGUI:

    def __init__(self,root):
        self.root=root

        Label(text='gui interface for aaxcmp rev %s Mar/2020'%rev).grid(row=0,column=10,sticky='E'+'W')
        Label(text='AAX file before:').grid(row=1,column=9,sticky='E'+'W')
        self.FBefore=Entry(root,width=wwidth)
        self.FBefore.grid(row=1,column=10,sticky='W'+'E')
        Label(text='AAX file after:').grid(row=2,column=9,sticky='E'+'W')
        self.FAfter=Entry(root,width=wwidth)
        self.FAfter.grid(row=2,column=10,sticky='W'+'E')
        self.TagEdit=Entry(root)
        self.TagEdit.grid(row=2,column=1,sticky='W'+'E')

        self.cmpBTN=Button(root,text='cmp',command=self.icompare).grid(row=1,column=0)
        self.voidBTN=Button(root,text='xref tag below',command=self.vpins).grid(row=1,column=1)
        self.cmpOutput=STX.ScrolledText(root)
        self.cmpOutput.grid(row=3,column=1,sticky='N'+'S'+'w'+'E',columnspan=10)

    def icompare(self):
        fA=aax(self.FBefore.get())
        fB=aax(self.FAfter.get())
        self.cmpOutput.insert('0.0',str(fA.cmp(fB)))

    def vpins(self):
        fA=aax(self.FBefore.get())
        fB=aax(self.FAfter.get())
        s=str('\n\t%s at %s\n'%(self.TagEdit.get(),fA.fName))
        for cradd in fA.CRef(self.TagEdit.get()):
            s+=str(fA.Blocks[cradd[:cradd.index(':')]])
        s+=str('\n\t%s at %s\n'%(self.TagEdit.get(),fB.fName))
        for cradd in fB.CRef(self.TagEdit.get()):
            s+=str(fB.Blocks[cradd[:cradd.index(':')]])
        self.cmpOutput.insert('0.0',s)

def aaxgui():
    mainwin=Tk()
    win=mainGUI(mainwin)
    win.title='aaxcmp with GUI rev%s'%rev
    mainwin.mainloop()
    pass

def help():
    print('\n./aaxcmp.py [file1.aax] [file2.aax] <options>\n')
    print('options could be:')
    print(' -i compare logic blocs')
    print(' -l compare line by line')
##    print(' -L compare line by conflicts selected (linux terminal tested)')
    print(' -rTAG_NAME cross reference of TAG_NAME at file1.aax and file2.aax')
    print('            NOTE: spaces are not applicable')
    print(' -v search for unconnected pins')
##    print(' -s print some statistics (dont use - in development)')
##    print(' -w start GUI (dont use - in development)')
    print(' -h print this help')
    print('position of the options keys in the command line, determine the sequence of the output')
    print('AAX files names location in the command line are not fixed but both should be present')
    return

print('\n aaxcmp,rev%s,Baku ABB,Mar/2020,AlimYusifzada,AMPL logic (aax files) compare tool'%rev)

if len(sys.argv)<2:
    help()
    aaxgui()
    sys.exit(0)

for arg in sys.argv[1:]:
    if arg[0]=='-':
        if arg not in options:
            options+=(arg,)
    if arg[-3:].lower()=='aax':
        if arg not in files:
            files+=(arg,)

if len(files)<2:
    print('\ncant find both files in arguments\n')
    help()
    sys.exit(-1)

try:
    fileOne=aax(files[0])
    fileTwo=aax(files[1])
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
##        cmpres=d.compare(fileOne.Lines,fileTwo.Lines)
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

    if op[:2]=='-r' and len(op[2:])>0:
        print('\n\t%s at %s\n'%(op[2:],fileOne.fName))
        for cradd in fileOne.CRef(op[2:]):
            print(fileOne.Blocks[cradd[:cradd.index(':')]])
        print('\n\t%s at %s\n'%(op[2:],fileTwo.fName))
        for cradd in fileTwo.CRef(op[2:]):
            print(fileTwo.Blocks[cradd[:cradd.index(':')]])

    if op=='-v':
        print('\n\tUnconnected pins at %s\n'%fileOne.fName)
        for cradd in fileOne.CRef(NONE):
            print(fileOne.Blocks[cradd[:cradd.index(':')]])
        print('\n\tUnconnected pins at %s\n'%fileTwo.fName)
        for cradd in fileTwo.CRef(NONE):
            print(fileTwo.Blocks[cradd[:cradd.index(':')]])




