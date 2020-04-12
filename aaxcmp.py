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
wwidth=60
options=()
files=()

rowINFO=0
rowBUTTONS=1
rowBefore=2
rowAfter=3
rowOUTPUT=4

class mainGUI:

    def __init__(self,root):
        self.root=root

## LABELS & PICTURES
        root.title('AAXCMP GUI rev %s Mar/2020'%rev)
        Label(text='AAX file BEFORE:').grid(row=rowBefore,column=9,sticky='E'+'W')
        Label(text='AAX file AFTER:').grid(row=rowAfter,column=9,sticky='E'+'W')
## OUTPUT
        self.cmpOutput=STX.ScrolledText(root)
        self.cmpOutput.grid(row=rowOUTPUT,column=0,sticky='N'+'S'+'w'+'E',columnspan=11)
## ENTRIES
## AAX file entry - BEFORE
        self.FBefore=Entry(root,width=wwidth)
        self.FBefore.grid(row=rowBefore,column=10,sticky='W'+'E')
## AAX file entry - AFTER
        self.FAfter=Entry(root,width=wwidth)
        self.FAfter.grid(row=rowAfter,column=10,sticky='W'+'E')
## TAG NAME entry - cross reference
        self.TagEdit=Entry(root)
        self.TagEdit.grid(row=rowBefore,column=1,columnspan=2,sticky='W'+'E')
## BUTTONS
## button COMPARE
        self.cmpBTN=Button(root,text='COMPARE',command=self.icompare).grid(row=rowBUTTONS,column=1)
## button CROSS REFERENCE
        self.voidBTN=Button(root,text='XREFERENCE',command=self.vpins).grid(row=rowBUTTONS,column=2)

    def icompare(self):
        fA=aax(self.FBefore.get())
        fB=aax(self.FAfter.get())
        self.cmpOutput.insert('0.0','_'*wwidth)
        self.cmpOutput.insert('0.0',str(fA.cmp(fB)))
        self.cmpOutput.insert('0.0','_'*wwidth)

    def vpins(self):
        fA=aax(self.FBefore.get())
        fB=aax(self.FAfter.get())
        s=str('\n\t%s at %s\n'%(self.TagEdit.get(),fA.fName))
        for cradd in fA.CRef(self.TagEdit.get()):
            s+=str(fA.Blocks[cradd[:cradd.index(':')]])
        s+=str('\n\t%s at %s\n'%(self.TagEdit.get(),fB.fName))
        for cradd in fB.CRef(self.TagEdit.get()):
            s+=str(fB.Blocks[cradd[:cradd.index(':')]])
        self.cmpOutput.insert('0.0','_'*wwidth)
        self.cmpOutput.insert('0.0',s)
        self.cmpOutput.insert('0.0','_'*wwidth)

def aaxgui():
    mainwin=Tk()
    win=mainGUI(mainwin)
    mainwin.grid_rowconfigure(rowOUTPUT,weight=1)
    mainwin.grid_columnconfigure(0,weight=1)
    mainwin.mainloop()
    pass

def help():
    print('\n./aaxcmp.py [file1.aax] [file2.aax] <options>\n')
    print('options could be:')
    print(' -i compare logic blocs')
    print(' -l compare line by line')
    print(' -L compare line by line with conflicts selected (linux terminal only)')
    print(' -rTAG_NAME cross reference of TAG_NAME at file1.aax and file2.aax')
    print('            NOTE: spaces are not applicable')
    print(' -v search for unconnected pins')
    print(' -h print this help')
    print('position of the options keys in the command line, determine the sequence of the output')
    print('AAX files names location in the command line are not fixed but both should be present')
    return

print('\n aaxcmp,rev%s,Baku ABB,Mar/2020,AlimYusifzada,AMPL logic (aax files) compare tool'%rev)

for arg in sys.argv[1:]:
    if arg[0]=='-':
        if arg not in options:
            options+=(arg,)
    if arg[-3:].lower()=='aax':
        if arg not in files:
            files+=(arg,)

if len(files)<1 or len(options)<1:
    help()
    aaxgui()
    sys.exit(-1)
try:
    if len(files)>=2:
        fileOne=aax(files[0])
        fileTwo=aax(files[1])
except:
    sys.exit(-2)

for op in options:
    if op=='-i':
        print('\n\tBLOCKS COMPARE:\t','%s VS %s'%(fileOne.fName[-10:],fileTwo.fName[-10:]))
        print(fileOne.cmp(fileTwo))
        print('_'*wwidth)
    if op=='-s':
        print('\n\tSTAT.INFO:\t','%s and %s'%(fileOne.fName[-10:],fileTwo.fName[-10:]))
        print('File %s'%fileOne.fname)
        print(fileOne.statout())
        print('File %s'%fileTwo.fname)
        print(fileTwo.statout())
        print('_'*wwidth)
    if op=='-L':
        print('\n\tL2L COMPARE:\t','%s VS %s'%(fileOne.fName[-10:],fileTwo.fName[-10:]))
        d=dif.Differ()
        cmpres=d.compare(fileOne.Lines,fileTwo.Lines)
        for i in cmpres:
            if i[0]=='-' or i[0]=='+' or i[0]=='?':
                print(CSELECTED+i+CEND,end='')
            else:
                print(i,end='')
        print('_'*wwidth)
    if op=='-l':
        d=dif.Differ()
        cmpres=d.compare(fileOne.Lines,fileTwo.Lines)
        print('\n line by line comparision legend\n')
        print('\n If line started with [space] the line is equal in both files')
        print('\n If line started with [-] the line  exist in the first file only')
        print('\n If line started with [+] the line exist in the second file only')
        print('\n If line started with [?] the line does not exist in both files\n')
        print('\n\tL2L COMPARE:\t','%s VS %s'%(fileOne.fName[-10:],fileTwo.fName[-10:]))
        for i in cmpres:
                print(i,end='')
        print('_'*wwidth)
    if op=='-h':
        help()

    if op[:2]=='-r' and len(op[2:])>0:
        print('\n\tXREFERENCE %s at:\t'%op[2:],'%s and %s'%(fileOne.fName[-10:],fileTwo.fName[-10:]))
        print('\n\n\t%s at %s\n'%(op[2:],fileOne.fName))
        for cradd in fileOne.CRef(op[2:]):
            print(fileOne.Blocks[cradd[:cradd.index(':')]])
        print('\n\n\t%s at %s\n'%(op[2:],fileTwo.fName))
        for cradd in fileTwo.CRef(op[2:]):
            print(fileTwo.Blocks[cradd[:cradd.index(':')]])
        print('_'*wwidth)
    if op=='-v':
        print('\n\tVOID PINs at: ','%s and %s'%(fileOne.fName[-10:],fileTwo.fName[-10:]))
        print('\n\n\tUnconnected pins at %s\n'%fileOne.fName)
        for cradd in fileOne.CRef(NONE):
            print(fileOne.Blocks[cradd[:cradd.index(':')]])
        print('\n\n\tUnconnected pins at %s\n'%fileTwo.fName)
        for cradd in fileTwo.CRef(NONE):
            print(fileTwo.Blocks[cradd[:cradd.index(':')]])
        print('_'*wwidth)
