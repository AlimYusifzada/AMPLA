#!/usr/bin/env python3
import os
import threading as trd
import PySimpleGUI as pg
from tkinter import filedialog
import xlwt
from ampla import *

rev = 'PUSA'
ftypes = [("AA/AAX files", "*.aa*"), 
          ("AA/AAX files", "*.AA*"),
          ("BA/BAX files", "*.ba*"),
          ("BA/BAX files", "*.BA*"),
          ("TXT files", "*.txt"), ("all files", "*.*")]

mainMenuR=[
    ['Proj',
     ['Open','Search','Source','Sink']],
    ['Compare',
     ['Dir2Dir']],
    ['About',
     ['Help','Exit']],
    ]


mainMenu=pg.MenuBar(mainMenuR)
buttons=[[pg.Button('Clear Output',key='-clear'),pg.Button('Open'),pg.Button('Search'),pg.Button('Compare',key='Dir2Dir')]]
inputs=[[pg.Input('',key='-search',size=(100,0))]]

labels=[[pg.Text('',key='-info',size=(100,0))]]


mainlayout=[[mainMenu],buttons,labels,inputs]
projlayout=[[]]
pcprogs=[]


mainWin=pg.Window(title=rev+':'+ampla_rev,layout=mainlayout,resizable=False)
# projWin=pg.Window(title=rev,layout=projlayout,resizable=True)


E=None
V=None
project=Proj('dummy')

def fcompare():
    '''compare folders
    '''
    dibefore = filedialog.askdirectory(title="select directory with BEFORE")
    diafter = filedialog.askdirectory(title="select directory with AFTER")
    for dib in Path(dibefore).iterdir():
        if dib.is_file() and (str(dib)[-2:].upper()=="AX" or str(dib)[-2:].upper()=="AA") : # check aax and aa files
            bf=os.path.basename(dib)
            bfile=bf[:bf.index('.')] # get just file name (before)
            for dia in Path(diafter).iterdir():
                if dia.is_file() and (str(dia)[-2:].upper()=="AX" or str(dia)[-2:].upper()=="AA"): #look for the same file
                    bf=os.path.basename(dia)
                    afile=bf[:bf.index('.')] # get just file name (after)
                    if bfile.lower()==afile.lower(): # compare if files matched
                        trd.Thread(name=bfile,target=genXLSreport(str(dib),str(dia))).start()
                        mainWin['-info'].update(mainWin['-info'].get()+'\n...processing:%s'%bfile)
                        mainWin.Refresh()
    mainWin['-info'].update('check results at\n%s'%diafter)

def genXLSreport(dir_before,dir_after):
    extB = dir_before[-3:].upper()
    extA = dir_after[-3:].upper()

    if extB == '.AA':
        fB = AA(dir_before)
    elif extB == 'AAX':
        fB = AAX(dir_before)
    elif extB == 'BAX':
        fB = BAX(dir_before)
    elif extB == '.BA':
        fB = BA(dir_before)
    else:
        return

    if extA == '.AA':
        fA = AA(dir_after)
    elif extA == 'AAX':
        fA = AAX(dir_after)
    elif extA == 'BAX':
        fA = BAX(dir_after)
    elif extA == '.BA':
        fA = BA(dir_after)
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
    xlsreport.save(dir_after+""+'.xls') #+datetimenow[-9:].replace(':', '')


while True:
    E,V=mainWin.read()
    if E=='Dir2Dir':
        fcompare()
        pass
    if E=='-clear':
        pcs=''
        mainWin['-info'].update(pcs)
        mainWin.Refresh()
        for pc in project.SRCE.keys():
            pcs+=pc+', '
        pcs+=''
        mainWin['-info'].update(pcs)
        mainWin.Refresh() 
    if E=='Trace':
        pass
    if E=='Search':
        if len(mainWin['-search'].get())>3:
            mainWin['-info'].update('...searching...')
            mainWin.Refresh()
            sr=project.Search(mainWin['-search'].get())
            if len(sr)>0:
                mainWin['-info'].update(sr)
            else:
                mainWin['-info'].update('found nothing')

    if E=='exit' or E=='Exit' or E==pg.WIN_CLOSED:
        break
    if E=='Open':
        path=filedialog.askdirectory(title='Select SRCE directory')
        pcs=''
        mainWin['-info'].update('...downloading...')
        mainWin.Refresh()
        project.Read(path)
        for pc in project.SRCE.keys():
            pcs+=pc+', '
        pcs+=' dowloaded'
        mainWin['-info'].update(pcs)
        mainWin.Refresh()
mainWin.close()