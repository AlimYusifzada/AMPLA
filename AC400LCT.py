#!/usr/bin/env python3
import os
import threading as trd
from tkinter import Label, Entry, Tk  # ,Frame,Button,Text
from tkinter import filedialog, Menu
from tkinter import scrolledtext as STX
from pathlib import Path
from tkinter import messagebox
# from tkinter import PhotoImage  
from ampla import *
import logins
import netband
import duapt
import xlwt
import datetime as dt


rev = 'PUSA'

file1 = ''
file2 = ''
wwidth = 50
options = ()
files = ()
ftypes = [("AA/AAX files", "*.aa*"), 
          ("AA/AAX files", "*.AA*"),
          ("BA/BAX files", "*.ba*"),
          ("BA/BAX files", "*.BA*"),
          ("TXT files", "*.txt"), ("all files", "*.*")]


rowINFO = 0
rowBUTTONS = 1
rowBefore = 2
rowAfter = 3
rowOUTPUT = 4


class mainGUI:

    def __init__(self, root):
        self.root = root
        self.dir_before = "~"
        self.dir_after = "~"
# Menu
        self.MMenu = Menu(root)
        self.FMenu = Menu(root)
        self.FMenu.add_command(label="files", command=self.aaxbrowse)
        self.FMenu.add_command(label="directories",command=self.fcompare)
        self.FMenu.add_command(label="compare again", command=self.compareSelected)
        self.FMenu.add_command(label="generate xls report",
                               command=self.genXLSreport)
        self.FMenu.add_command(label="x-reference", command=self.vpins)
        self.FMenu.add_command(label="about", command=self.about)

        self.TMenu = Menu(root)
        self.TMenu.add_command(
            label="unpack AA/BA...", command=self.convert)
        self.TMenu.add_command(
            label="calculate DUAP timing from LG...", command=self.duaptiming)
        self.TMenu.add_command(
            label="network bandwidth calculation...", command=self.netbandwidth)
        self.TMenu.add_command(label="get failed logins...",
                               command=self.get_explicit_logins)

        self.MMenu.add_cascade(label="before<>after", menu=self.FMenu)
        self.MMenu.add_cascade(label="tools", menu=self.TMenu)

        # self.root.configure(menu=self.MMenu)

# LABELS & PICTURES
        root.title('LCT rev:%s AMPLA rev:%s' % (rev, ampla_rev))
        root.config(menu=self.MMenu)
        Label(text='X-REF:').grid(row=rowBefore, column=0, sticky='E')
        Label(text='file BEFORE:').grid(row=rowBefore, column=3, sticky='W')
        Label(text='file  AFTER:').grid(row=rowAfter, column=3, sticky='W')
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
        self.compareSelected()

    # def opentxt(self):
    #     os.startfile(self.FBefore.get())
    #     os.startfile(self.FAfter.get())

    def compareSelected(self):
        self.dir_before = self.FBefore.get()
        self.dir_after = self.FAfter.get()
        self.icompare()

    def fcompare(self):
        '''compare folders
        '''
        dibefore = filedialog.askdirectory(title="select directory with BEFORE")
        diafter = filedialog.askdirectory(title="select directory with AFTER")
        messagebox.showinfo("PLEASE WAIT","Long procedure ahead.\nPlease wait till it finish")
        for dib in Path(dibefore).iterdir():
            if dib.is_file() and (str(dib)[-2:].upper()=="AX" or str(dib)[-2:].upper()=="AA") : # check aax and aa files
                bf=os.path.basename(dib)
                bfile=bf[:bf.index('.')] # get just file name (before)
                self.dir_before=str(dib) # save full path
                for dia in Path(diafter).iterdir():
                    if dia.is_file() and (str(dia)[-2:].upper()=="AX" or str(dia)[-2:].upper()=="AA"): #look for the same file
                        bf=os.path.basename(dia)
                        afile=bf[:bf.index('.')] # get just file name (after)
                        self.dir_after=str(dia) # safe full path
                        if bfile.lower()==afile.lower(): # compare if files matched
                            # trd.Thread(name=bfile,target=self.icompare()).start()  # compare using saved full path
                            trd.Thread(name=bfile,target=self.genXLSreport()).start()

    def icompare(self):
        datetimenow = str(dt.datetime.now())[:-7]
        self.cmpOutput.insert('0.0', '\n\t'+datetimenow+'\n'*3)
        extB = self.dir_before[-3:].upper()
        extA = self.dir_after[-3:].upper()

        if extB == '.AA':
            fB = AA(self.dir_before)
        elif extB == 'AAX':
            fB = AAX(self.dir_before)
        elif extB == 'BAX':
            fB = BAX(self.dir_before)
        elif extB == '.BA':
            fB = BA(self.dir_before)
        else:
            return

        if extA == '.AA':
            fA = AA(self.dir_after)
        elif extA == 'AAX':
            fA = AAX(self.dir_after)
        elif extA == 'BAX':
            fA = BAX(self.dir_after)
        elif extA == '.BA':
            fA = BA(self.dir_after)
        else:
            return

        self.cmpOutput.insert('0.0', '\n\t >>> END OF REPORT <<<')
        self.cmpOutput.insert('0.0', str(fB.compare(fA)))
        self.cmpOutput.insert(
            '0.0', '\n\tBEFORE\n%s\n\n\tAFTER\n%s\n' % (fB.fName, fA.fName))
        self.cmpOutput.insert('0.0','\n\t<<< DIFFERENTIAL ANALYSIS REPORT >>>\n')

    def vpins(self):
        datetimenow = str(dt.datetime.now())[:-7]
        self.cmpOutput.insert('0.0', '\n\t'+datetimenow+'\n'*3)
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
        s = str('\n\tLooking for %s at %s\n' % (self.TagEdit.get(), fB.fName))
        if len(s) > 0:
            for cradd in fB.xRef(self.TagEdit.get()):
                s += str(fB.Blocks[cradd[:cradd.index(':')]])
            s += str('\n\t%s at %s\n' % (self.TagEdit.get(), fA.fName))
            for cradd in fA.xRef(self.TagEdit.get()):
                s += str(fA.Blocks[cradd[:cradd.index(':')]])
            self.cmpOutput.insert('0.0', s)
        self.cmpOutput.insert('0.0', '\n\n\t >>> X_REFERENCE REPORT <<<')

    def convert(self):
        datetimenow = str(dt.datetime.now())[:-7]
        self.cmpOutput.insert('0.0', '\n\t'+datetimenow+'\n'*3)
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
        messagebox.showinfo("convert","\n\n\tSuccesfully converted to %s.txt"%afile)

    def genXLSreport(self):
        datetimenow = str(dt.datetime.now())[:-7]
        self.cmpOutput.insert('0.0', '\n\t'+datetimenow+'\n'*3)
        extB = self.dir_before[-3:].upper()
        extA = self.dir_after[-3:].upper()
        # xlsrepname=self.dir_after

        if extB == '.AA':
            fB = AA(self.dir_before)
        elif extB == 'AAX':
            fB = AAX(self.dir_before)
        elif extB == 'BAX':
            fB = BAX(self.dir_before)
        elif extB == '.BA':
            fB = BA(self.dir_before)
        else:
            return

        if extA == '.AA':
            fA = AA(self.dir_after)
        elif extA == 'AAX':
            fA = AAX(self.dir_after)
        elif extA == 'BAX':
            fA = BAX(self.dir_after)
        elif extA == '.BA':
            fA = BA(self.dir_after)
        else:
            return

        xlsreport = xlwt.Workbook(encoding='ascii')

        addrstyle = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                                'font: colour black, bold False;')
        diffstyle = xlwt.easyxf('pattern: pattern solid, fore_colour red;'
                                'font: colour black, bold True;')
        headstyle = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;'
                                'font: colour black, bold True;')
        pinstyle = xlwt.easyxf('pattern: pattern solid, fore_colour white;'
                                'font: colour blue, bold False;')
        pinstyle.alignment.wrap=1
        addrstyle.alignment.horz=addrstyle.alignment.HORZ_LEFT
        pinstyle.alignment.horz=pinstyle.alignment.HORZ_LEFT
        diffstyle.alignment.horz=diffstyle.alignment.HORZ_CENTER
        headstyle.alignment.horz=headstyle.alignment.HORZ_CENTER

        cmppage = xlsreport.add_sheet(
            'report', cell_overwrite_ok=False)
        codepage_compare = xlsreport.add_sheet(
            'line2line', cell_overwrite_ok=False)

        stat_line = 1
        col_offs = 4
        addr_col = 0
        pins_col = 1
        name_col = 1
        pinv_col = 2
        extr_col = 2
        stat_col = 3
        desc_col = 0

        lcnt = 0

        codepage_compare.col(addr_col).width = 6000
        codepage_compare.col(pinv_col).width = 7500

        codepage_compare.col(stat_col).width = 3000

        codepage_compare.col(addr_col+col_offs).width = 6000
        codepage_compare.col(pinv_col+col_offs).width = 7500

        codepage_compare.col(addr_col+col_offs*2-1).width=6000 #message

        codepage_compare.col(addr_col+col_offs*2).width=6000 
        codepage_compare.col(pinv_col+col_offs*2).width=7500

        codepage_compare.write(lcnt, addr_col, 'Address', headstyle)  # 0
        codepage_compare.write(lcnt, pins_col, 'Pin', headstyle)  # 1
        codepage_compare.write(lcnt, pinv_col, 'Value', headstyle)  # 2
        codepage_compare.write(lcnt, stat_col, 'Status', headstyle)  # 3

        codepage_compare.write(lcnt, addr_col+col_offs,
                               'Address', headstyle)  # 0
        codepage_compare.write(lcnt, pins_col+col_offs, 'Pin', headstyle)  # 1
        codepage_compare.write(lcnt, pinv_col+col_offs,
                               'Value', headstyle)  # 2
# --------------------------COMPARE SHEET-----------------------------------
        lcnt = stat_line # lines counter
        for blk in fB.Blocks:  # check blocks in Before
            codepage_compare.write(
                lcnt, addr_col, fB.GetBlock(blk).Address, addrstyle)
            codepage_compare.write(
                lcnt, name_col, fB.GetBlock(blk).Name, addrstyle)
            codepage_compare.write(
                lcnt, extr_col, fB.GetBlock(blk).Extra, addrstyle)
            
            if blk in fA.Blocks: # if blk in After
                codepage_compare.write(
                    lcnt, addr_col+col_offs, fA.GetBlock(blk).Address, addrstyle)
                codepage_compare.write(
                    lcnt, name_col+col_offs, fA.GetBlock(blk).Name, addrstyle)
                codepage_compare.write(
                    lcnt, extr_col+col_offs, fA.GetBlock(blk).Extra, addrstyle)
                if fB.GetBlock(blk) != fA.GetBlock(blk): # blocks are not equal
                    codepage_compare.write(lcnt, stat_col, NEQ, diffstyle)
            else: # blk not in After
                codepage_compare.write(
                    lcnt, addr_col+col_offs, fB.GetBlock(blk).Address, addrstyle)
                codepage_compare.write(
                    lcnt, name_col+col_offs, fB.GetBlock(blk).Name, addrstyle)
                codepage_compare.write(
                    lcnt, extr_col+col_offs, 'STATEMENT NOT FOUND',headstyle)
                codepage_compare.write(lcnt, stat_col, NEQ, diffstyle)
            lcnt += 1
            #description line
            codepage_compare.write(lcnt, desc_col, fB.GetBlock(blk).Description)
            if blk in fA.Blocks: # check blk in After for Description 
                codepage_compare.write(
                    lcnt, desc_col+col_offs, fA.GetBlock(blk).Description)
            lcnt += 1
            # list PINs------------------------------------

            pins_before=fB.GetBlock(blk).GetPins()
            if blk in fA.Blocks:
                pins=fA.GetBlock(blk).GetPins()
            if len(pins_before)>=len(pins): #get keys(pins) from bigger block
                pins=pins_before

            for pin in pins:# iterate through the pins and compare
                codepage_compare.write(lcnt, pins_col, pin)
                codepage_compare.write(
                    lcnt, pinv_col, fB.GetBlock(blk).GetPin(pin),pinstyle)
                # check pin  in After --------------------------------
                if blk in fA.Blocks and pin in fA.GetBlock(blk).GetPins():
                    codepage_compare.write(lcnt, pins_col+col_offs, pin)
                    codepage_compare.write(
                        lcnt, pinv_col+col_offs, fA.GetBlock(blk).GetPin(pin),pinstyle)
                    if fA.GetBlock(blk).GetPin(pin) != fB.GetBlock(blk).GetPin(pin):
                        codepage_compare.write(lcnt, stat_col, NEQ, diffstyle)
                # check pin not in After ---------------------------------
                if blk in fA.Blocks and pin not in fA.GetBlock(blk).GetPins():
                    codepage_compare.write(lcnt, pins_col+col_offs, pin)
                    codepage_compare.write(
                        lcnt, pinv_col+col_offs, 'PIN DISCONNECTED',headstyle)
                    codepage_compare.write(lcnt, stat_col, NEQ, diffstyle)
                lcnt += 1
            lcnt += 2

        lcnt = stat_line
        for blk in fA.Blocks:  # check blocks in After
            if blk not in fB.Blocks:  # new block found
                codepage_compare.write(
                    lcnt, addr_col+col_offs*2-1, 'NEW STATEMENT',headstyle)
                codepage_compare.write(
                    lcnt, addr_col+col_offs*2, fA.GetBlock(blk).Address,addrstyle)
                codepage_compare.write(
                    lcnt, name_col+col_offs*2, fA.GetBlock(blk).Name,addrstyle)
                codepage_compare.write(
                    lcnt, extr_col+col_offs*2, fA.GetBlock(blk).Extra,addrstyle)
                lcnt += 1
                codepage_compare.write(
                    lcnt, desc_col+col_offs*2, fA.GetBlock(blk).Description)
                lcnt += 1
                for pin in fA.GetBlock(blk).GetPins():
                    codepage_compare.write(lcnt, pins_col+col_offs*2, pin)
                    codepage_compare.write(
                        lcnt, pinv_col+col_offs*2, fA.GetBlock(blk).Pins[pin],pinstyle)
                    lcnt += 1
            else:  # alignment with existing code
                lcnt+=max(len(fA.GetBlock(blk).GetPins()),len(fB.GetBlock(blk).GetPins()))+4

        report = fB.compare(fA)
        lcnt = stat_line
        wcnt = 0
        s = ''
        cmppage.col(0).width = 10000
        cmppage.col(1).width = 25000
        cmppage.col(2).width = 5000
        for l in report:
            style=addrstyle
            if NEQ in s:
                style=headstyle
            style.alignment.horz=style.alignment.HORZ_LEFT
            if l == '\n':
                cmppage.write(lcnt, wcnt, s,style)
                lcnt += 1
                wcnt = 0
                s = ''
            elif l == '\t':
                cmppage.write(lcnt, wcnt, s,style)
                wcnt += 1
                s = ''
            s += l
        xlsreport.save(self.dir_after+""+'.xls') #+datetimenow[-9:].replace(':', '')
        self.cmpOutput.insert(
            '0.0', "\nreport created for\t%s.xls" % self.dir_after)


    '''
    duaptiming to be moved out as separate script with available/editable code
    '''
    def duaptiming(self):
        datetimenow = str(dt.datetime.now())[:-7]
        # self.cmpOutput.insert('0.0', '\n\t'+datetimenow+'\n'*3)
        messagebox.showinfo("", duapt.duapthelp)
        filesdir = filedialog.askdirectory()
        duapt.duaptreport(str(filesdir))
        messagebox.showinfo("",
                              '''
        DUAP Timing spreadsheet generated,
        look for Duap_Timing.xls at the selected directory
        ''')
        pass

    '''
    netbandwidth to be moved out as separate script with available/editable code
    '''
    def netbandwidth(self):
        datetimenow = str(dt.datetime.now())[:-7]
        messagebox.showinfo("", netband.netbandhelp)
        filesdir = filedialog.askdirectory()
        self.cmpOutput.insert('0.0', '\n\t'+datetimenow+'\n'*3)
        self.cmpOutput.insert('0.0', netband.netbandcalc(str(filesdir)))
        pass

        '''
    duaptiming to be moved out as separate script with available/editable code
    '''
    
    '''
    failed logins to be moved out as separate script with available/editable code
    '''
    def get_explicit_logins(self):
        messagebox.showinfo("",
                              '''
            run @ domain controller
            wevtutil qe Security | find /i "4648</EventID" >explicit_logins.txt
            or
            wevtutil qe Security | find /i "4625</EventID" >failed_logins.txt
            ''')
        logsf = filedialog.askopenfilename(initialdir=self.dir_before,
                                           title="Select log file",
                                           filetypes=ftypes)
        if len(logsf) > 0:
            self.cmpOutput.insert('0.0', logins.get_logins(logsf))
    
   
    def about(self):
        self.cmpOutput.insert('0.0',Disclaimer)
        self.cmpOutput.insert('0.0',ABBlogo)
# ------------------------------------------------------------------------------

Disclaimer = '''
    AC400 Logic Compare Tool
    (c) 2020-2023, Alim Yusifzada
    reddit: u/Crazy1Dunmer
    mastodon: Crazy1Dunmer@alim@mas.to
    gmail: yusifzaj@gmail.com

    This program is distributed in the hope 
    that it will be useful,but WITHOUT ANY WARRANTY.
'''
ABBlogo='''             
                ]@@@ ]@@@L        @@@@@@@  @@@@@m    ]@@@@@@L [@@@@b            
               ,@@@@ ]@@@@w       @@@@@@@  @@@@@@@   ]@@@@@@L [@@@@@@           
               @@@@@ ]@@@@@       @@@@@@@  @@@@@@@   ]@@@@@@L [@@@@@@           
              @@@@@@ ]@@@@@@      @@@@@@@  @@@@@@`   ]@@@@@@L [@@@@@[           
             g@@@@@@ ]@@@@@@m     @@@@@@@  @@@@@,    ]@@@@@@L [@@@@w            
          
            #@@@@@@@ ]@@@@@@@@    @@@@@@@  @@@@@@@@m ]@@@@@@L [@@@@@@@@         
           g@@@@@@@@ ]@@@@@@@@b   @@@@@@@  @@@@@@@@[ ]@@@@@@L [@@@@@@@@         
          ]@@@@@NM** '***$@@@@@g  @@@@@@@  @@@@@@@@F ]@@@@@@L [@@@@@@@P         
         g@@@@@[         ']@@@@@L @@@@@@@  @@@@@@@"  ]@@@@@@L [@@@@@@M          
         M@@@@@`          '@@@@@H @@@@@@@  @@@@*`    ]@@@@@@` *@@@@"            
'''

print(ABBlogo)
print(Disclaimer)

mainwin = Tk()
mainGUI(mainwin)
mainwin.grid_rowconfigure(rowOUTPUT, weight=1)
mainwin.grid_columnconfigure(0, weight=1)
mainwin.mainloop()