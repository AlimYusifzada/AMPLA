#!/usr/bin/env python3
import os
from tkinter import Frame, Label, Button, Entry, Text, Tk
from tkinter import filedialog, Menu
from tkinter import scrolledtext as STX
from tkinter import PhotoImage
from ampla import *

rev = 'CA'  # revision style change. GUI revision indicate site/place of development

file1 = ''
file2 = ''
wwidth = 50
options = ()
files = ()
ftypes = [("AA files", "*.aa"), ("AAX files", "*.aax"),
          ("AA files", "*.AA"), ("AAX files", "*.AAX"),
          ("BA files", "*.ba"), ("BAX files", "*.bax"),
          ("BA files", "*.BA"), ("BAX files", "*.BAX"),
          ("all files", "*.*")]


rowINFO = 0
rowBUTTONS = 1
rowBefore = 2
rowAfter = 3
rowOUTPUT = 4


class mainGUI:

    def __init__(self, root):
        self.root = root

# Menu
        self.MMenu = Menu(root)

        self.FMenu = Menu(root)
        self.FMenu.add_command(label="SELECT", command=self.aaxbrowse)
        self.FMenu.add_command(label="COMPARE", command=self.icompare)
        self.FMenu.add_command(label="EDIT", command=self.opentxt)

        self.TMenu = Menu(root)
        self.TMenu.add_command(label="CONVERT to TXT", command=self.convert)
        #self.TMenu.add_command(label="SCAN FOLDER")
        self.TMenu.add_command(label="X-REFERENCE", command=self.vpins)

        self.MMenu.add_cascade(label="FILE", menu=self.FMenu)
        self.MMenu.add_cascade(label="TOOLS", menu=self.TMenu)

        # self.root.configure(menu=self.MMenu)

## LABELS & PICTURES
        root.title('GUI rev:%s AMPLA rev:%s' % (rev, ampla_rev))
        root.config(menu=self.MMenu)
        Label(text='X-REF VALUE:').grid(row=rowBefore, column=0, sticky='E')
        Label(text=' BEFORE:').grid(row=rowBefore, column=3, sticky='W')
        Label(text=' AFTER:').grid(row=rowAfter, column=3, sticky='W')
# OUTPUT
        self.cmpOutput = STX.ScrolledText(root)
        self.cmpOutput.grid(row=rowOUTPUT, column=0,
                            sticky='N'+'S'+'w'+'E', columnspan=11)
# ENTRIES
# AAX file entry - BEFORE
        self.FBefore = Entry(root, width=wwidth)
        self.FBefore.grid(row=rowBefore, column=4, sticky='W')
# AAX file entry - AFTER
        self.FAfter = Entry(root, width=wwidth)
        self.FAfter.grid(row=rowAfter, column=4, sticky='W')
# TAG NAME entry - cross reference
        self.TagEdit = Entry(root)
        self.TagEdit.grid(row=rowBefore, column=1, sticky='W')

    def aaxbrowse(self):
        self.FBefore.delete(0, len(self.FBefore.get()))
        self.FAfter.delete(0, len(self.FAfter.get()))
        self.FBefore.insert(0, filedialog.askopenfilename(initialdir="~",
                            title="Select original file",
                            filetypes=ftypes)
                            )
        self.FAfter.insert(0, filedialog.askopenfilename(initialdir="~",
                                                         title="Select modified file",
                                                         filetypes=ftypes)
                           )
        self.icompare()

    def opentxt(self):
        os.startfile(self.FBefore.get())
        os.startfile(self.FAfter.get())

    def icompare(self):
        extB = self.FBefore.get()[-3:].upper()
        extA = self.FAfter.get()[-3:].upper()

        if extB == '.AA':
            fB = AA(self.FBefore.get())
        elif extB == 'AAX':
            fB = AAX(self.FBefore.get())
        elif extB == 'BAX':
            fB = BAX(self.FBefore.get())
        elif extB == '.BA':
            fB = BA(self.FBefore.get())
        else:
            return

        if extA == '.AA':
            fA = AA(self.FAfter.get())
        elif extA == 'AAX':
            fA = AAX(self.FAfter.get())
        elif extA == 'BAX':
            fA = BAX(self.FAfter.get())
        elif extA == '.BA':
            fA = BA(self.FAfter.get())
        else:
            return

        self.cmpOutput.insert('0.0', '\n\tEND OF REPORT')
        self.cmpOutput.insert('0.0', str(fB.compare(fA)))
        self.cmpOutput.insert(
            '0.0', '\n\n\t>>> DISCREPANCIES REPORT <<<\n%s\nand\n%s\n' % (fB.fName, fA.fName))

    def vpins(self):
        extB = self.FBefore.get()[-3:].upper()
        extA = self.FAfter.get()[-3:].upper()

        if extB == '.AA':
            fB = AA(self.FBefore.get())
        elif extB == 'AAX':
            fB = AAX(self.FBefore.get())
        elif extB == 'BAX':
            fB = BAX(self.FBefore.get())
        elif extB == '.BA':
            fB = BA(self.FBefore.get())
        else:
            return

        if extA == '.AA':
            fA = AA(self.FAfter.get())
        elif extA == 'AAX':
            fA = AAX(self.FAfter.get())
        elif extA == 'BAX':
            fA = BAX(self.FAfter.get())
        elif extA == '.BA':
            fA = BA(self.FAfter.get())
        else:
            return

        self.cmpOutput.insert('0.0', "\n\tEND OF REPORT")
        s = str('\n\t%s at %s\n' % (self.TagEdit.get(), fB.fName))
        if len(s) > 0:
            for cradd in fB.cref(self.TagEdit.get()):
                s += str(fB.Blocks[cradd[:cradd.index(':')]])
            s += str('\n\t%s at %s\n' % (self.TagEdit.get(), fA.fName))
            for cradd in fA.cref(self.TagEdit.get()):
                s += str(fA.Blocks[cradd[:cradd.index(':')]])
            self.cmpOutput.insert('0.0', s)
        self.cmpOutput.insert('0.0', '\n\n\t>>> X_REFERENCE REPORT <<<')

    def convert(self):
        afile = filedialog.askopenfilename(initialdir="~",
                                           title="Select AA or BA file",
                                           filetypes=ftypes)
        ext = afile[-3:].upper()
        if ext == '.AA':
            f = AA(afile)
        elif ext == '.BA':
            f = BA(afile)
        else:
            #self.cmpOutput.insert('0.0',"\n\t Error occure while converting %s"%afile)
            return
        f.write()
        self.cmpOutput.insert(
            '0.0', "\n\n\tSuccesfully converted to %s.txt " % afile)


print('\nGUI rev: %s, AMPLA rev: %s\n Copyright (c) 2020, Alim Yusifzada\n AMPL logic (aax/bax files) compare tool' % (rev, ampla_rev))
print('\nMany thanks to Stuart Redman, \n\tfor the help in testing, debugging and fixing issues')
print('Thanks a lot to Baku ABB Team for the ideas to improve the tool. \n\tYou are always so helpful')
print('\nhttps://github.com/AlimYusifzada/AMPLA.git')

Disclaimer = '''
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
'''

print(Disclaimer)
print('Please feel free contact me: yusifzaj@gmail.com \nwith suggestions and troubleshooting\n...')
mainwin = Tk()
mainGUI(mainwin)
mainwin.grid_rowconfigure(rowOUTPUT, weight=1)
mainwin.grid_columnconfigure(0, weight=1)
mainwin.mainloop()
