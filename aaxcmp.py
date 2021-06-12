#!/usr/bin/env python3
import os
from tkinter import Frame,Label, Button, Entry, Text, Tk
from tkinter import filedialog
from tkinter import scrolledtext as STX
from tkinter import PhotoImage
from ampla import *

rev='0.A'

file1=''
file2=''
wwidth=50
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
        root.title('GUI rev:%s AMPLA rev:%s'%(rev,ampla_rev))
        Label(text='file BEFORE:').grid(row=rowBefore,column=3,sticky='E'+'W')
        Label(text='file AFTER:').grid(row=rowAfter,column=3,sticky='E'+'W')
## OUTPUT
        self.cmpOutput=STX.ScrolledText(root)
        self.cmpOutput.grid(row=rowOUTPUT,column=0,sticky='N'+'S'+'w'+'E',columnspan=11)
## ENTRIES
## AAX file entry - BEFORE
        self.FBefore=Entry(root,width=wwidth)
        self.FBefore.grid(row=rowBefore,column=5,columnspan=5,sticky='W'+'E')
## AAX file entry - AFTER
        self.FAfter=Entry(root,width=wwidth)
        self.FAfter.grid(row=rowAfter,column=5,columnspan=5,sticky='W'+'E')
## TAG NAME entry - cross reference
        self.TagEdit=Entry(root)
        self.TagEdit.grid(row=rowBefore,column=1,columnspan=2,sticky='W'+'E')
## BUTTONS
## button ABOUT
        #Button(root,image=PhotoImage(file='eyes.png'),text='').grid(row=rowBUTTONS,column=0)
## button CROSS REFERENCE
        self.voidBTN=Button(root,text='X-reference search',command=self.vpins).grid(row=rowBUTTONS,column=1)
## button view in notepad
        self.cleanBTN=Button(root,text='Edit',command=self.opentxt).grid(row=rowBUTTONS,column=8)
## button COMPARE
        self.cmpBTN=Button(root,text='Compare',command=self.icompare).grid(row=rowBUTTONS,column=7)
## button BROWSE
        self.AAXbrowseBTN=Button(root,text='Select',command=self.aaxbrowse).grid(row=rowBUTTONS,column=6)

    def aaxbrowse(self):
        self.FBefore.delete(0,len(self.FBefore.get()))
        self.FAfter.delete(0,len(self.FAfter.get()))
        self.FBefore.insert(0, filedialog.askopenfilename(initialdir =  "~",
                            title = "Select file BEFORE",
                            filetypes =[("BA files","*.ba"),("BAX files","*.bax"),("AA files","*.aa"),("AAX files","*.aax"),("all files","*.*")] )
                            )
        self.FAfter.insert(0, filedialog.askopenfilename(initialdir =  "~",
                            title = "Select file AFTER",
                            filetypes =[("BA files","*.ba"),("BAX files","*.bax"),("AA files","*.aa"),("AAX files","*.aax"),("all files","*.*")] )
                            )

    def opentxt(self):
        os.startfile(self.FBefore.get())
        os.startfile(self.FAfter.get())

    def icompare(self):

        extB=self.FBefore.get()[-3:].upper()
        extA=self.FAfter.get()[-3:].upper()

        if extB=='.AA':
            fA=AA(self.FBefore.get())
        elif extB=='AAX':
            fA=AAX(self.FBefore.get())
        elif extB=='BAX':
            fA=BAX(self.FBefore.get())
        elif extB=='.BA':
            fA=BA(self.FBefore.get())

        if extA=='.AA':
            fB=AA(self.FAfter.get())
        elif extA=='AAX':
            fB=AAX(self.FAfter.get())
        elif extA=='BAX':
            fB=BAX(self.FAfter.get())
        elif extA=='.BA':
            fB=BA(self.FAfter.get())

        self.cmpOutput.insert('0.0',str(fA.compare(fB)))
        self.cmpOutput.insert('0.0','\n\tDISCREPANCIES REPORT \n%s\nand\n%s\n'%(fA.fName,fB.fName))

    def vpins(self):
        if self.isAAX():
            fA=AAX(self.FBefore.get())
            fB=AAX(self.FAfter.get())
        elif self.isAA():
            fA=AA(self.FBefore.get())
            fB=AA(self.FAfter.get())
        else:
            fA=BAX(self.FBefore.get())
            fB=BAX(self.FAfter.get())

        s=str('\n\t%s at %s\n'%(self.TagEdit.get(),fA.fName))
        if len(s)>0:
            for cradd in fA.cref(self.TagEdit.get()):
                s+=str(fA.Blocks[cradd[:cradd.index(':')]])
            s+=str('\n\t%s at %s\n'%(self.TagEdit.get(),fB.fName))
            for cradd in fB.cref(self.TagEdit.get()):
                s+=str(fB.Blocks[cradd[:cradd.index(':')]])
            self.cmpOutput.insert('0.0',s)


print('\nGUI rev: %s, AMPLA rev: %s\n Copyright (c) 2020, Alim Yusifzada\n AMPL logic (aax/bax files) compare tool'%(rev,ampla_rev))
print('\nMany thanks to Stuart Redman, \n\tfor the help in testing, debugging and fixing issues')
print('Thanks a lot to Baku ABB Team for the ideas to improve the tool. \n\tYou are always so helpful')

Disclaimer='''
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
'''

print(Disclaimer)
print('Please feel free contact me: yusifzaj@gmail.com \nwith suggestions and troubleshooting\n...')

mainwin=Tk()
mainGUI(mainwin)
mainwin.grid_rowconfigure(rowOUTPUT,weight=1)
mainwin.grid_columnconfigure(0,weight=1)
mainwin.mainloop()
