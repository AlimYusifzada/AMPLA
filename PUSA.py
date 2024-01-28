#!/usr/bin/env python3
import os
import threading as trd
import xlwt
import PySimpleGUI as pg
from tkinter import filedialog
from ampla import *
from pins_def import *

about = '''
    AMPL Logic Compare Tool
    (c) 2020-2023, Alim Yusifzada
    reddit: u/Crazy1Dunmer
    gmail: yusifzaj@gmail.com

    This program is distributed in the hope 
    that it will be useful,but WITHOUT ANY WARRANTY.

    Buttons color code: Blue - working function
                        Orange - experimental

    This program is used to compare pairs of 
    .AAX .AA .BA or .BAX files, 
    using other formats may result in runtime errors. 
    Possible combinations:    AAX<->AAX; AAX<->AA; AA<->AA
                            BAX<->BAX; BA<->BAX; BA<->BA

    Code files can be from different source, 
    i.e. can have one extracted from FCB and the other from ONB.

    Once **select before and after directories** button is pressed 
    you will be asked to select the directories 
    contains source code you wish to compare. 
    XLS files (reports) will be generated in the 'after' directory.

    check box "generate line2line" is off by default. 
    if you set it on, excel report will be expanded 
    with additional tab contains line to line code representation. 
    this option is not recommended

    if database is splitted in several files 
    they will be combined together. 
    same option is true for logic files.

    XLS files crated individually for each pair and contain two tabs. 
    Comparison report and "line to line"
    
    Comparison performed by logic blocks (not line to line), 
    so AMPL code parsing performed before comapison.

    The program try to understand and compare 
    some elements like numeric constants as numbers, 
    i.e. D=2.3e-3 and D=0.0023 treated as no difference.
    however you will be warned in the report

    If XLS file name ends with *DIF* 
    it means, descrepancies found and logged
'''

myico='aaxcmp.ico'
waitico='aaxcmpwait.gif'
rev = 'pusa caspica'
ftypes = [("AA/AAX files", "*.aa*"), 
          ("AA/AAX files", "*.AA*"),
          ("BA/BAX files", "*.ba*"),
          ("BA/BAX files", "*.BA*")]

project=Proj('dummy')
line2line_status=False
excel_max=65530

#----------------------------------XLS report----------------------------------
def fcompare(win:pg.Window):
    '''compare folders
    '''
    dibefore = filedialog.askdirectory(title="select BEFORE source directory")
    diafter = filedialog.askdirectory(title="select AFTER source directory")
    if diafter==dibefore or dibefore=='' or diafter=='':
        return
    for dib in Path(dibefore).iterdir():
        if dib.is_file() and (str(dib)[-2:].upper()=="BX" or str(dib)[-2:].upper()=="AX" or str(dib)[-2:].upper()=="BA" or str(dib)[-2:].upper()=="AA") : # check aax and aa files
            bf=os.path.basename(dib)
            bfile=bf[:bf.index('.')] # get just file name (before)
            for dia in Path(diafter).iterdir():
                if dia.is_file() and (str(dib)[-2:].upper()=="BX" or str(dia)[-2:].upper()=="AX" or str(dib)[-2:].upper()=="BA" or str(dia)[-2:].upper()=="AA"): #look for the same file
                    bf=os.path.basename(dia)
                    afile=bf[:bf.index('.')] # get just file name (after)
                    if bfile.lower()==afile.lower(): # compare if files matched
                        win['-infotxt-'].update('\nPLEASE WAIT... processing: %s'%bfile)
                        win.Refresh()
                        trd.Thread(name=bfile,target=genXLSreport(str(dib),str(dia))).start()
    win['-infotxt-'].update('DONE! - check results at\n%s'%diafter)

def genXLSreport(dir_before,dir_after):
    '''
    generate XLS spreadsheet for each pair
    '''
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
    
    if line2line_status:
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
# ------------------------- prepare -----------------------------------
    if line2line_status:
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
# -------------------------- compare -----------------------------------
    if line2line_status:
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
            if lcnt>excel_max: break
                #description line
            codepage_compare.write(lcnt, desc_col, fB.GetBlock(blk).Description)
            if blk in fA.Blocks: # check blk in After for Description 
                codepage_compare.write(
                    lcnt, desc_col+col_offs, fA.GetBlock(blk).Description)
            lcnt += 1
            if lcnt>excel_max: break
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
                        lcnt, pinv_col+col_offs, 'PIN NOT FOUND',headstyle)
                    codepage_compare.write(lcnt, stat_col, NEQ, diffstyle)
                lcnt += 1
                if lcnt>excel_max: break
            lcnt += 2
            if lcnt>excel_max: break

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
                if lcnt>excel_max: break
                codepage_compare.write(
                    lcnt, desc_col+col_offs*2, fA.GetBlock(blk).Description)
                lcnt += 1
                if lcnt>excel_max: break
                for pin in fA.GetBlock(blk).GetPins():
                    codepage_compare.write(lcnt, pins_col+col_offs*2, pin)
                    codepage_compare.write(
                        lcnt, pinv_col+col_offs*2, fA.GetBlock(blk).Pins[pin],pinstyle)
                    lcnt += 1
                    if lcnt>excel_max: break
            else:  # alignment with existing code
                lcnt+=max(len(fA.GetBlock(blk).GetPins()),len(fB.GetBlock(blk).GetPins()))+4
                if lcnt>excel_max: break
# ========================== l2l report done =============================   

    report = fB.compare(fA) # simple text returned

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
            if lcnt>excel_max: break
            wcnt = 0
            s = ''
        elif l == '\t':
            cmppage.write(lcnt, wcnt, s,style)
            wcnt += 1
            s = ''
        s += l
    if fB.difstat:
        xlsreport.save(dir_after+'_DIF.xls') # diference found
    else:
        xlsreport.save(dir_after+'.xls') # no dif detected
#===============================================================================


#===============================================================================
#--------------------------------Main Window------------------------------------
def MainWin()->pg.Window:
    font10=('Areial',10)
    buttons=[
            [
            pg.Text('to compare AA(AAX) or BA(BAX)',font=font10),
            pg.Button('select <before> and <after> directories...',key='-compare-',font=font10),
            pg.Checkbox('generate line2line',default=False,key='-line2line-',font=font10),
            ],
            
            [
            #pg.Text('Search and tracing (experimental)'),
            pg.Button('read source files',key='-open-',font=font10,button_color='orange'),
            pg.Button('search',key='-search-',disabled=True,font=font10,button_color='orange'),
            pg.Button('show PC element',key='-browse-',disabled=True,font=font10,button_color='orange'),
            pg.Button('<= source',key='-source-',disabled=True,font=font10,button_color='orange'),
            pg.Button('sink =>',key='-sink-',disabled=True,font=font10,button_color='orange'),
            ],
            [
            pg.Button('refresh',key='-clear-',button_color='gray',font=font10),
            pg.Button('about',key='-about-',button_color='green',font=font10),  
            pg.Button('exit',key='-exit-',button_color='red',font=font10),
            ]
            ]
    inputs=[[pg.Input('',key='-searchtxt-',size=(110,0))]]
    labels=[[pg.Text('',key='-infotxt-',size=(100,0))]]
    mainlayout=[buttons,labels,inputs]
    return pg.Window(title=rev+':'+ampla_rev,layout=mainlayout,resizable=False,finalize=True,icon=myico)

def refreshGUI(W:pg.Window):
        pcs=''
        W['-infotxt-'].update(pcs)
        W.Refresh()
        for pc in project.SRCE.keys():
            pcs+=pc+', '
        pcs+=''
        if len(project.SRCE.keys())>0:
            W['-search-'].update(disabled=False)
            W['-browse-'].update(disabled=False)
            W['-sink-'].update(disabled=False)
            W['-source-'].update(disabled=False)
        else:
            W['-search-'].update(disabled=True)
            W['-browse-'].update(disabled=True)
            W['-sink-'].update(disabled=True)
            W['-source-'].update(disabled=True)
        W.Refresh() 
        
#------------------------------------------------------------------------
mainwin=MainWin()   #main window event handler starts here

while True:
    W,E,V=pg.read_all_windows()
    line2line_status=W['-line2line-'].get()
    if E=='-source-':
        sinklist=W['-searchtxt-'].get().upper().split()
        sinks=[]
        for item in sinklist:
            if project.is_pc_exist(get_addr_pin(item)[0]):
                pcname=get_PC_name(item)
                sinks.append(get_source(project.SRCE[pcname],[item,]))
        pg.ScrolledTextBox(str(sinks),title='Sinks',icon=myico)
        pass
    if E=='-sink-':
        sinklist=W['-searchtxt-'].get().upper().split()
        sinks=[]
        for item in sinklist:
            if project.is_pc_exist(get_addr_pin(item)[0]):
                pcname=get_PC_name(item)
                sinks.append(get_sink(project.SRCE[pcname],[item,]))
        pg.ScrolledTextBox(str(sinks),title='Sinks',icon=myico)
        pass
    if E=='-browse-':
        pckey=W['-searchtxt-'].get().upper()
        if pckey.find(':')>0:
            pckey=pckey[:pckey.find(':')] #cutoff pin number
        pcname=get_PC_name(pckey)
        if pcname in project.SRCE.keys():
            if pckey in project.SRCE[pcname].Blocks.keys():
                s=str(project.SRCE[pcname].Blocks[pckey])
                pg.ScrolledTextBox(s,title=pckey,icon=myico)      
    if E=='-compare-':
        fcompare(W)
        pass
    if E=='-clear-':
        refreshGUI(W)
    if E=='-search-':
        if len(W['-searchtxt-'].get())>3:
            sr=project.Search(W['-searchtxt-'].get().upper())
            if len(sr)>0:
                pg.ScrolledTextBox(sr,title=W['-searchtxt-'].get().upper(),icon=myico)
            else:
                W['-infotxt-'].update('found nothing')
    if E=='-exit-'or E==pg.WIN_CLOSED:
        break
    if E=='-open-':
        path=filedialog.askdirectory(title='Select SRCE directory')
        pcs=''
        W['-infotxt-'].update('...AMPL source code downloading...')
        W.Refresh()
        project.Read(path)
        refreshGUI(W)
    if E=='-about-':
        pg.ScrolledTextBox(rev+ampla_rev
                           ,about,
                           title='about',
                           icon=myico,
                           no_sizegrip=True,
                           no_titlebar=True)
mainwin.close()