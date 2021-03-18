#!/usr/bin/env python3
import os
from tkinter import Frame,Label, Button, Entry, Text, Tk
from tkinter import filedialog
from tkinter import scrolledtext as STX
from ampla import *

rev='0.9'

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
        root.title('ABAX GUI rev:%s ampla_rev:%s'%(rev,ampla_rev))
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
## button CROSS REFERENCE
        self.voidBTN=Button(root,text='X-reference search',command=self.vpins).grid(row=rowBUTTONS,column=1)
## button view in notepad
        self.cleanBTN=Button(root,text='Edit files',command=self.opentxt).grid(row=rowBUTTONS,column=8)
## button COMPARE
        self.cmpBTN=Button(root,text='COMPARE',command=self.icompare).grid(row=rowBUTTONS,column=7)
## button BROWSE
        self.AAXbrowseBTN=Button(root,text='Select AAX',command=self.aaxbrowse).grid(row=rowBUTTONS,column=5)
        self.BAXbrowseBTN=Button(root,text='Select BAX',command=self.baxbrowse).grid(row=rowBUTTONS,column=6)

    def isAAX(self):
        ext=self.FBefore.get()[-3:]
        if ext.upper()=='AAX':
            return True
        else:
            return False

    def aaxbrowse(self):
        self.FBefore.delete(0,len(self.FBefore.get()))
        self.FAfter.delete(0,len(self.FAfter.get()))
        self.FBefore.insert(0, filedialog.askopenfilename(initialdir =  "~",
                            title = "Select AAX file BEFORE",
                            filetypes =[("AAX files","*.aax"),("AAX files","*.AAX"),("all files","*.*")] )
                            )
        self.FAfter.insert(0, filedialog.askopenfilename(initialdir =  "~",
                            title = "Select AAX file AFTER",
                            filetypes =[("AAX files","*.aax"),("AAX files","*.AAX"),("all files","*.*")] )
                            )

    def baxbrowse(self):
        self.FBefore.delete(0,len(self.FBefore.get()))
        self.FAfter.delete(0,len(self.FAfter.get()))
        self.FBefore.insert(0, filedialog.askopenfilename(initialdir =  "~",
                            title = "Select BAX file BEFORE",
                            filetypes =[("BAX files","*.bax"),("BAX files","*.BAX"),("all files","*.*")] )
                            )
        self.FAfter.insert(0, filedialog.askopenfilename(initialdir =  "~",
                            title = "Select BAX file AFTER",
                            filetypes =[("BAX files","*.bax"),("BAX files","*.BAX"),("all files","*.*")] )
                            )

    def opentxt(self):
        os.startfile(self.FBefore.get())
        os.startfile(self.FAfter.get())

    def icompare(self):
        if self.isAAX():
            fA=AAX(self.FBefore.get())
            fB=AAX(self.FAfter.get())
        else:
            fA=BAX(self.FBefore.get())
            fB=BAX(self.FAfter.get())
        self.cmpOutput.insert('0.0',str(fA.compare(fB)))
        self.cmpOutput.insert('0.0','\n\tDISCREPANCIES REPORT \n%s\nand\n%s\n'%(fA.fName,fB.fName))

    def vpins(self):
        if self.isAAX():
            fA=AAX(self.FBefore.get())
            fB=AAX(self.FAfter.get())
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


print('aaxcmp rev:%s, ampla_rev:%s, Baku ABB, Mar/2020, Alim Yusifzada, AMPL logic (aax/bax files) compare tool'%(rev,ampla_rev))
print('Many thanks to Stuart Redman, for the help in debugging and fixing issues')
mainwin=Tk()
mainGUI(mainwin)
mainwin.grid_rowconfigure(rowOUTPUT,weight=1)
mainwin.grid_columnconfigure(0,weight=1)
mainwin.mainloop()
