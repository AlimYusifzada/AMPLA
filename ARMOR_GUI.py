#!/usr/bin/env python3
import os
from tkinter import Frame, Label, Button, Entry, Text, Tk
from tkinter import filedialog, Menu
from tkinter import scrolledtext as STX
from tkinter import PhotoImage
from ampla import *
import logins 
import netband
import duapt
import xlwt
import datetime as dt

rev = 'Stormy CA' 

file1 = ''
file2 = ''
wwidth = 50
options = ()
files = ()
ftypes = [("AA files", "*.aa"), ("AAX files", "*.aax"),
          ("AA files", "*.AA"), ("AAX files", "*.AAX"),
          ("BA files", "*.ba"), ("BAX files", "*.bax"),
          ("BA files", "*.BA"), ("BAX files", "*.BAX"),
          ("TXT files","*.txt"),("all files", "*.*")]


rowINFO = 0
rowBUTTONS = 1
rowBefore = 2
rowAfter = 3
rowOUTPUT = 4


class mainGUI:

    def __init__(self, root):
        self.root = root
        self.dir_before="~"
        self.dir_after="~"
# Menu
        self.MMenu = Menu(root)
        self.FMenu = Menu(root)
        self.FMenu.add_command(label="select...", command=self.aaxbrowse)
        self.FMenu.add_command(label="compare", command=self.icompare)
        self.FMenu.add_command(label="generate report",command=self.genXLSreport)
        self.FMenu.add_command(label="x-reference", command=self.vpins)
        self.FMenu.add_command(label="open in editor", command=self.opentxt)

        self.TMenu = Menu(root)
        self.TMenu.add_command(label="convert to TXT...", command=self.convert)
        self.TMenu.add_command(label="calculate DUAP timing from LG...", command=self.duaptiming)
        self.TMenu.add_command(label="network bandwidth calculation...", command=self.netbandwidth)
        self.TMenu.add_command(label="get explicit logins...", command=self.get_explicit_logins)

        self.MMenu.add_cascade(label="BEFORE/AFTER", menu=self.FMenu)
        self.MMenu.add_cascade(label="TOOLSET", menu=self.TMenu)

        # self.root.configure(menu=self.MMenu)

## LABELS & PICTURES
        root.title('GUI:%s AMPLA:%s'%(rev,ampla_rev))
        root.config(menu=self.MMenu)
        Label(text='X-REF:').grid(row=rowBefore, column=0, sticky='E')
        Label(text='BEFORE:').grid(row=rowBefore, column=3, sticky='W')
        Label(text='AFTER:').grid(row=rowAfter, column=3, sticky='W')
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

        self.FBefore.insert(0, filedialog.askopenfilename(initialdir=self.dir_before,
                            title="Select original file",
                            filetypes=ftypes)
                            )
        self.FAfter.insert(0, filedialog.askopenfilename(initialdir=self.dir_after,
                                                         title="Select modified file",
                                                         filetypes=ftypes)
                           )

        self.dir_before=self.FBefore.get()
        self.dir_after=self.FAfter.get()

        self.icompare()

    def opentxt(self):
        os.startfile(self.FBefore.get())
        os.startfile(self.FAfter.get())

    def icompare(self):
        datetimenow=str(dt.datetime.now())[:-7]
        self.cmpOutput.insert('0.0','\n\t'+datetimenow+'\n'*3)
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

        self.cmpOutput.insert('0.0', '\n\t >>> END OF REPORT <<<')
        self.cmpOutput.insert('0.0', str(fB.compare(fA)))
        self.cmpOutput.insert(
            '0.0', '\n\n\t >>> DISCREPANCIES REPORT <<<\n%s\nand\n%s\n' % (fB.fName, fA.fName))

    def vpins(self):
        datetimenow=str(dt.datetime.now())[:-7]
        self.cmpOutput.insert('0.0','\n\t'+datetimenow+'\n'*3)
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

        self.cmpOutput.insert('0.0', "\n\t >>> END OF REPORT <<<")
        s = str('\n\t%s at %s\n' % (self.TagEdit.get(), fB.fName))
        if len(s) > 0:
            for cradd in fB.xRef(self.TagEdit.get()):
                s += str(fB.Blocks[cradd[:cradd.index(':')]])
            s += str('\n\t%s at %s\n' % (self.TagEdit.get(), fA.fName))
            for cradd in fA.xRef(self.TagEdit.get()):
                s += str(fA.Blocks[cradd[:cradd.index(':')]])
            self.cmpOutput.insert('0.0', s)
        self.cmpOutput.insert('0.0', '\n\n\t >>> X_REFERENCE REPORT <<<')

    def convert(self):
        datetimenow=str(dt.datetime.now())[:-7]
        self.cmpOutput.insert('0.0','\n\t'+datetimenow+'\n'*3)
        afile = filedialog.askopenfilename(initialdir="~",
                                           title="Select AA or BA file",
                                           filetypes=ftypes)
        ext = afile[-3:].upper()
        if ext == '.AA':
            f = AA(afile)
        elif ext == '.BA':
            f = BA(afile)
        else:
            return
        f.Write()
        self.cmpOutput.insert(
            '0.0', "\n\n\tSuccesfully converted to %s.txt " % afile)

    def genXLSreport(self):
        datetimenow=str(dt.datetime.now())[:-7]
        self.cmpOutput.insert('0.0','\n\t'+datetimenow+'\n'*3)
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

        xlsreport=xlwt.Workbook(encoding='ascii')
        
        addrstyle = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                              'font: colour blue, bold True;')        
        diffstyle = xlwt.easyxf('pattern: pattern solid, fore_colour red;'
                              'font: colour black, bold True;')
        headstyle = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;'
                              'font: colour black, bold True;')

        cmppage=xlsreport.add_sheet('Discrepancy Report',cell_overwrite_ok=False)
        codepage_compare=xlsreport.add_sheet('Compare',cell_overwrite_ok=False)

        stat_line=1
        col_offs=4
        addr_col=0
        pins_col=1
        name_col=1
        pinv_col=2
        extr_col=2
        stat_col=3
        desc_col=0
        lcnt=0

        codepage_compare.col(addr_col).width=5000
        codepage_compare.col(pinv_col).width=5000
        codepage_compare.col(addr_col+col_offs).width=5000
        codepage_compare.col(pinv_col+col_offs).width=5000
        codepage_compare.col(stat_col).width=10000

        codepage_compare.write(lcnt,addr_col,'Address',headstyle) # 0
        codepage_compare.write(lcnt,pins_col,'Pin',headstyle) # 1
        codepage_compare.write(lcnt,pinv_col,'Value',headstyle) # 2
        codepage_compare.write(lcnt,stat_col,'Status',headstyle) # 3

        codepage_compare.write(lcnt,addr_col+col_offs,'Address',headstyle) # 0
        codepage_compare.write(lcnt,pins_col+col_offs,'Pin',headstyle) # 1
        codepage_compare.write(lcnt,pinv_col+col_offs,'Value',headstyle) # 2
#--------------------------COMPARE SHEET-----------------------------------
        lcnt=stat_line
        for blk in fB.Blocks: #check blocks in Before against After
            codepage_compare.write(lcnt,addr_col,fB.Blocks[blk].Address,addrstyle)
            codepage_compare.write(lcnt,name_col,fB.Blocks[blk].Name,addrstyle)
            codepage_compare.write(lcnt,extr_col,fB.Blocks[blk].Extra,addrstyle)
            if blk in fA.Blocks:
                codepage_compare.write(lcnt,addr_col+col_offs,fA.Blocks[blk].Address,addrstyle)
                codepage_compare.write(lcnt,name_col+col_offs,fA.Blocks[blk].Name,addrstyle)
                codepage_compare.write(lcnt,extr_col+col_offs,fA.Blocks[blk].Extra,addrstyle)
                if fB.Blocks[blk]!=fA.Blocks[blk]:
                    codepage_compare.write(lcnt,stat_col,NEQ,diffstyle)
            else:
                codepage_compare.write(lcnt,addr_col+col_offs,fB.Blocks[blk].Address,addrstyle)
                codepage_compare.write(lcnt,name_col+col_offs,fB.Blocks[blk].Name,addrstyle)
                codepage_compare.write(lcnt,extr_col+col_offs,'NOT FOUND - STATEMENT REMOVED')
                codepage_compare.write(lcnt,stat_col,NEQ,diffstyle)
            lcnt+=1
            codepage_compare.write(lcnt,desc_col,fB.Blocks[blk].Description)
            if blk in fA.Blocks:
                codepage_compare.write(lcnt,desc_col+col_offs,fA.Blocks[blk].Description)
            lcnt+=1
            for pin in fB.Blocks[blk].Pins.keys():
                codepage_compare.write(lcnt,pins_col,pin)
                codepage_compare.write(lcnt,pinv_col,fB.Blocks[blk].Pins[pin])
                if blk in fA.Blocks and pin in fA.Blocks[blk].Pins.keys():
                    codepage_compare.write(lcnt,pins_col+col_offs,pin)
                    codepage_compare.write(lcnt,pinv_col+col_offs,fA.Blocks[blk].Pins[pin])
                    if fA.Blocks[blk].Pins[pin]!=fB.Blocks[blk].Pins[pin]:
                        codepage_compare.write(lcnt,stat_col,NEQ,diffstyle)
                if blk in fA.Blocks and pin not in fA.Blocks[blk].Pins.keys():
                    codepage_compare.write(lcnt,pins_col+col_offs,pin)
                    codepage_compare.write(lcnt,pinv_col+col_offs,'NOT FOUND - PIN DISCONNECTED')
                    codepage_compare.write(lcnt,stat_col,NEQ,diffstyle)
                lcnt+=1
            lcnt+=2

        lcnt=stat_line
        for blk in fA.Blocks: #check blocks in After against Before
            if blk not in fB.Blocks: #new block
                codepage_compare.write(lcnt,addr_col+col_offs*2-1,'NEW STATEMENT')
                codepage_compare.write(lcnt,addr_col+col_offs*2,fA.Blocks[blk].Address)
                codepage_compare.write(lcnt,name_col+col_offs*2,fA.Blocks[blk].Name)
                codepage_compare.write(lcnt,extr_col+col_offs*2,fA.Blocks[blk].Extra)
                lcnt+=1
                codepage_compare.write(lcnt,desc_col+col_offs*2,fA.Blocks[blk].Description)
                lcnt+=1
                for pin in fA.Blocks[blk].Pins.keys():
                    codepage_compare.write(lcnt,pins_col+col_offs*2,pin)
                    codepage_compare.write(lcnt,pinv_col+col_offs*2,fA.Blocks[blk].Pins[pin])
                    lcnt+=1
            else: #alignment with existing code
                for pin in fA.Blocks[blk].Pins.keys():
                    lcnt+=1
                lcnt+=4

        report=fB.compare(fA)
        lcnt=stat_line
        wcnt=0
        s=''
        cmppage.col(0).width=10000
        cmppage.col(1).width=20000
        for l in report:
            if l=='\n':
                cmppage.write(lcnt,wcnt,s)
                lcnt+=1
                wcnt=0
                s=''
            elif l=='\t':
                cmppage.write(lcnt,wcnt,s)
                wcnt+=1
                s=''
            s+=l
        xlsrepname=self.FAfter.get()+datetimenow[-9:].replace(':','')+'.xls'
        xlsreport.save(xlsrepname)
        self.cmpOutput.insert(
            '0.0', "\n\t%s report created"%xlsrepname)

    def duaptiming(self):
        datetimenow=str(dt.datetime.now())[:-7]
        self.cmpOutput.insert('0.0','\n\t'+datetimenow+'\n'*3)
        self.cmpOutput.insert('0.0',duapt.duapthelp)
        filesdir=filedialog.askdirectory()
        duapt.duaptreport(str(filesdir))
        self.cmpOutput.insert('0.0',
        '''
        DUAP Timing spreadsheet generated
        Look for Duap_Timing.xls file at the selected directory
        ''')
        pass

    def netbandwidth(self):
        datetimenow=str(dt.datetime.now())[:-7]
        self.cmpOutput.insert('0.0',netband.netbandhelp)
        filesdir=filedialog.askdirectory()
        self.cmpOutput.insert('0.0','\n\t'+datetimenow+'\n'*3)
        self.cmpOutput.insert('0.0',netband.netbandcalc(str(filesdir)))
        pass

    def get_explicit_logins(self):
        self.cmpOutput.insert('0.0',
            '''
            run @ domain controller
            wevtutil qe Security | find /i "4648</EventID" >logins.txt
            ''')
        logsf= filedialog.askopenfilename(initialdir=self.dir_before,
                title="Select log file",
                filetypes=ftypes)
        if len(logsf)>0:
            self.cmpOutput.insert('0.0',logins.get_logins(logsf))
#------------------------------------------------------------------------------

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
