#!/usr/bin/env python3

from tkinter import Label, Entry, Tk, Button
from tkinter import filedialog, Menu
from tkinter import scrolledtext as STX
from tkinter import messagebox

from ampla import *
# from pins_def import * # pins_def combined with ampla

try:
    import pyi_splash
    pyi_splash.close()
except ImportError:
    pass

rev = 'Erzurum'

file1 = ''
file2 = ''
wwidth = 80
options = ()
files = ()
ftypes = [("AA/AAX files", "*.aa*"), 
          ("AA/AAX files", "*.AA*"),
          ("BA/BAX files", "*.ba*"),
          ("BA/BAX files", "*.BA*"),
        ]

# rowButtons = 1
rowBefore = 2
rowAfter = 3
rowEntry = 4
rowOutput = 5
firstline='0.0'
project=Proj('dummy') # create empty project

class OutputWin:
    def __init__(self,text_data='',MWtitle='---') -> None:
        MW=Tk()
        MW.title(MWtitle)
        MW.grid_rowconfigure(0,weight=1)
        MW.grid_columnconfigure(0,weight=1)
        self.DataOutput=STX.ScrolledText(master=MW)
        self.DataOutput.insert(firstline,text_data)
        self.DataOutput.grid(sticky='N'+'S'+'W'+'E',row=0,column=0)
        pass

class MainGUI:

    def __init__(self, root) -> None:
        self.root = root

# Menu
        self.MMenu = Menu(root) # add main menu
        self.FMenu = Menu(root) # add drop out compare menu
        self.TMenu = Menu(root) # add tool/ menu
        self.PMenu = Menu(root) # add project menu

# before<>after menu config
        self.FMenu.add_command(label=" before<->after ", command=self.CompareSelectedFiles)
        self.FMenu.add_command(label=" files.. ", command=self.SelectAndCompare)
        self.FMenu.add_command(label=" directories.. ",command=self.CompareDirectories)

# Proj menu config
        self.PMenu.add_command(label=" load project... ",command=self.OpenProject) # read project files (AA/AAX)
        self.PMenu.add_command(label=" list PC programs ",command=self.ListProjectCode)
        self.PMenu.add_command(label=" search entry ",command=self.Search) # search tag/address through the project
        self.PMenu.add_command(label=" <-source ",command=self.TraceSources) # trace inputs
        self.PMenu.add_command(label="   sink-> ",command=self.TraceSinks) # trace outputs

# tools menu config
    #--------------------------------------------------------------
        self.TMenu.add_command(
            label="unpack AA or BA file...", command=self.OpenAndConverToTxt)
        self.TMenu.add_command(
            label="erase output",command=self.CleanOutputWin)
    #--------------------------------------------------------------
        self.TMenu.add_command(
            label="list uncknown blocks",command=self.ListNewLogicBlocks)
        self.TMenu.add_command(
            label="settings",command=messagebox.showerror)
        self.TMenu.add_command(label="who is responsible?", command=self.About)

# main menu config
        self.MMenu.add_cascade(label=" compare ", menu=self.FMenu)
        self.MMenu.add_cascade(label=" search ",menu=self.PMenu)
        self.MMenu.add_cascade(label=" options ", menu=self.TMenu)

#-----------------------------------------------------------------------
        root.title('LCT rev:%s AMPLA rev:%s' % (rev, ampla_rev))
        root.config(menu=self.MMenu)

# LABELS PICTURES BUTTONS and other widgets
        Label(text=' BEFORE:').grid(row=rowBefore, column=4, sticky='W')
        Label(text=' AFTER:').grid(row=rowAfter, column=4, sticky='w')
        Label(text=' ENTRY:').grid(row=rowEntry, column=4, sticky='w')
        #-------------------------------------------------------------
        Button(text=" ... ",command=self.SelectFileBefore).grid(column=6,row=rowBefore,sticky='W'+'E')
        Button(text=" ... ",command=self.SelectFileAfter).grid(column=6,row=rowAfter,sticky='W'+'E')
        Button(text=" search ",command=self.Search).grid(column=1,row=rowEntry,sticky='W'+'E')
        Button(text=" cls ",command=self.CleanOutputWin).grid(column=6,row=rowEntry,sticky='W'+'E')
        Button(text="<-",command=self.TraceSources).grid(column=0,row=rowEntry,sticky='W'+'E')
        Button(text="->",command=self.TraceSinks).grid(column=2,row=rowEntry,sticky='w'+'E')
        Button(text=" before<->after ",command=self.CompareSelectedFiles).grid(column=0,row=rowBefore,sticky='W'+'E',columnspan=4)
        Button(text=" load project code ",command=self.OpenProject).grid(column=0,row=rowAfter,sticky='W'+'E',columnspan=4)

# OUTPUT
        self.MainWinOutput = STX.ScrolledText(root)
        self.MainWinOutput.grid(row=rowOutput, column=0,
                            sticky='N'+'S'+'w'+'E', columnspan=11)
    
# ENTRIES
# AAX file entry - BEFORE
        self.FileBefore = Entry(root, width=wwidth)
        self.FileBefore.grid(row=rowBefore, column=5, sticky='W'+'E')
# AAX file entry - AFTER
        self.FileAfter = Entry(root, width=wwidth)
        self.FileAfter.grid(row=rowAfter, column=5, sticky='W'+'E')
# TAG NAME entry - cross reference
        self.SearchEntry = Entry(root,width=wwidth)
        self.SearchEntry.grid(row=rowEntry, column=5, sticky='W'+'E')

    def SelectFileAfter(self):
        self.FileAfter.delete(0, len(self.FileAfter.get()))
        self.FileAfter.insert(0, filedialog.askopenfilename(initialdir="~",
                                                         title="Select modified file",
                                                         filetypes=ftypes))
        
    def ListProjectCode(self):
        self.CleanOutputWin()
        self.MainWinOutput.insert(firstline,'\n')
        try:
            for pc in project.SRCE.keys():
                self.MainWinOutput.insert(firstline,pc+'\trev:'+project.SRCE[pc].Header['rev_ind']+\
                                  '\tdate:'+project.SRCE[pc].Header['date']+'\n')
        except:
            messagebox.showwarning('warning','revision number not defined')
            self.MainWinOutput.insert(firstline,'''
There is a PC program without a revision number!!!''')
        pass

    def SelectFileBefore(self):
        # self.cmpOutput.insert(firstline,'\n')
        self.FileBefore.delete(0, len(self.FileBefore.get()))
        self.FileBefore.insert(0, filedialog.askopenfilename(initialdir="~",
                            title="Select original file",
                            filetypes=ftypes)
                            )

    def OpenProject(self): #menu command Proj-Read
        # self.cmpOutput.insert(firstline,'\n')
        projdir=filedialog.askdirectory(title="select forlder with AA or AAX code")
        project.Read(projdir)
        self.ListProjectCode()

    def SelectAndCompare(self):
        '''menu callout to select files before/after and compare
        '''
        self.SelectFileBefore()
        self.SelectFileAfter()
        self.CompareSelectedFiles()

    def CompareSelectedFiles(self):
        '''
        menu callout function to compare selected files 
        '''
        if len(self.FileBefore.get())==0 or len(self.FileAfter.get())==0:
            messagebox.showwarning("oops",
                "BEFORE and AFTER should not be empty!\nUse menu compare->files...\nOr manually enter path to the code")
            self.MainWinOutput.insert(firstline,'''
Please enter full path to the AMPL source files 
    at BEFORE and AFTER fields''')
        fB=LoadABXFile(self.FileBefore.get())
        if fB==None:
            messagebox.showwarning("oops","BEFORE value is invalid")
            self.MainWinOutput.insert(firstline,'''
BEFORE field must contain full path to the source file
    or file is invalid or not found''')
            return
        fA=LoadABXFile(self.FileAfter.get())
        if fA==None:
            messagebox.showwarning("oops","AFTER value is invalid")
            self.MainWinOutput.insert(firstline,'''
AFTER field must contain full path to the source file
    of file not found or invalid''')
            return
        OutputWin(
            str(fB.compare(fA)),
            '\n\tsource BEFORE\n%s\n\n\tsource AFTER\n%s\n' % (fB.fName, fA.fName))

    def CompareDirectories(self):
        '''compare directories and report to xls file
        '''
        self.MainWinOutput.insert(firstline,'''
Comparing directories and excel reporting 
might take some time at the old computers.

Please look for excel files at the AFTER directory
                                  
If the difference(s) in source code found, 
excel file will have suffix _DIF in the name''')
        dibefore = filedialog.askdirectory(title="select directory with code BEFORE")
        diafter = filedialog.askdirectory(title="select directory with code AFTER")
        for dib in Path(dibefore).iterdir():
            if dib.is_file() and (str(dib)[-2:].upper()=="AX" or str(dib)[-2:].upper()=="AA") : # check aax and aa files
                bf=os.path.basename(dib)
                bfile=bf[:bf.index('.')] # get just file name (before)
                dir_before=str(dib) # save full path
                for dia in Path(diafter).iterdir():
                    if dia.is_file() and (str(dia)[-2:].upper()=="AX" or str(dia)[-2:].upper()=="AA"): #look for the same file
                        bf=os.path.basename(dia)
                        afile=bf[:bf.index('.')] # get just file name (after)
                        dir_after=str(dia) # safe full path
                        if bfile.lower()==afile.lower(): # compare if files matched
                            trd.Thread(name=bfile,target=GenXLSreport(dir_before,dir_after)).start()
        messagebox.showinfo("info","Check for results at:\n %s"%diafter)
        
    def OpenAndConverToTxt(self):
        '''unpack AA/BA files to txt 
        '''
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
        self.MainWinOutput.insert(firstline,"\nSuccesfully converted to %s.txt"%afile)
        s=''
        for bl in f.Lines:
            s=s+bl+'\n'
        OutputWin(s,afile)

    def Search(self):
        '''
        if source files selected search throug them.
        then check if project code is loaded and if yes search it too
        '''
        self.CleanOutputWin()
        output_updated=False
        s=''
        pckey=self.SearchEntry.get().upper()
        extB = self.FileBefore.get()[-3:].upper()
        extA = self.FileAfter.get()[-3:].upper()

        if len(pckey)<1:
            messagebox.showwarning("warning","Search request empty\nENTRY: should have something")
            self.MainWinOutput.insert(firstline,'''
ENTRY field must have some data: tag name or PC address''')
            return
        if len(extB)>1 or len(extA)>1:
            fB=LoadABXFile(self.FileBefore.get())
            fA=LoadABXFile(self.FileAfter.get())
            for cradd in fB.xRef(pckey):
                self.MainWinOutput.insert(firstline,str(fB.Blocks[cradd[:cradd.index(':')]]))
            for cradd in fA.xRef(pckey):
                self.MainWinOutput.insert(firstline,str(fA.Blocks[cradd[:cradd.index(':')]]))
            output_updated=True
        if len(project.SRCE.keys())>1:
            if pckey.find(':')>0:
                pckey=pckey[:pckey.find(':')] #cutoff pin number
            pcname=get_PC_name_from_file(pckey)
            if pcname in project.SRCE.keys():
                if pckey in project.SRCE[pcname].Blocks.keys():
                    s=str(project.SRCE[pcname].Blocks[pckey])
            self.MainWinOutput.insert(firstline,'\n'+s+'\n')
            sr=project.Search(pckey)
            for s in sr:
                self.MainWinOutput.insert(firstline,'\n'+s)
            if len(s)>1:
                output_updated=True
        if not output_updated:
            self.MainWinOutput.insert(firstline,'''
    Nothing was found!
    Make sure your search request was correct!''')

    def TraceSources(self):
        self.CleanOutputWin()
        if len(project.SRCE.keys())<1:
            messagebox.showwarning('warning','code is not loaded\nProject->load project code')
            self.MainWinOutput.insert(firstline,'''
To search through the project source files they should be loaded''')
            return
        sourceslist=self.SearchEntry.get().upper().split()
        if len(sourceslist)<1:
            messagebox.showwarning("warning","search request empty\nENTRY: should have an address")
            self.MainWinOutput.insert(firstline,'''
ENTRY field must contain data to search PC address''')
            return
        sources=[]
        for item in sourceslist:
            if project.is_pc_exist(get_addr_pin(item)[0]): 
                pcname=get_PC_name_from_file(item)
                sources.append(get_sources(project.SRCE[pcname],[item,])) # get SOURCE
        for item in sources[0]:
            self.MainWinOutput.insert(firstline,'\n'+str(item)+'\n')
        self.MainWinOutput.insert(firstline,'\n\t<-- Source connections:\n')
    
    def TraceSinks(self):
        self.CleanOutputWin()
        if len(project.SRCE.keys())<1:
            messagebox.showwarning('warning','code is not loaded\nProject->load project code')
            self.MainWinOutput.insert(firstline,'''
Project source code is not loaded''')
            return
        sinklist=self.SearchEntry.get().upper().split()
        if len(sinklist)<1:
            messagebox.showwarning("warning","search request empty\nENTRY: should have an address")
            self.MainWinOutput.insert(firstline,'''
ENTRY field must contain data to search PC address''')
            return
        sinks=[]
        for item in sinklist:
            if project.is_pc_exist(get_addr_pin(item)[0]):
                pcname=get_PC_name_from_file(item)
                sinks.append(get_sinks(project.SRCE[pcname],[item,])) # get SINK
        for item in sinks[0]:
            self.MainWinOutput.insert(firstline,'\n'+str(item)+'\n')
        self.MainWinOutput.insert(firstline,'\n\t--> Sink connections:\n')
        pass

    def About(self):
        self.CleanOutputWin()
        self.MainWinOutput.insert(firstline,'\n'+Disclaimer)
        pass

    def CleanOutputWin(self):
        self.MainWinOutput.delete("0.0","10000.0")
        pass

    # def LoadABXFile(self,fpath):
    #     ''' get path to the file and return AA AAX BA BAX object
    #         or None
    #     '''
    #     match fpath[-3:].upper():
    #         case '.AA':
    #             return AA(fpath)
    #         case '.AAX':
    #             return AAX(fpath)
    #         case '.BA':
    #             return BA(fpath)
    #         case '.BAX':
    #             return BAX(fpath)
    #     return None

    def ListNewLogicBlocks(self):
        self.CleanOutputWin()
        newb={}
        for pcp in project.SRCE.keys(): # for all programs in the project
            for bl in project.SRCE[pcp].Blocks.keys(): # for every block in the program
                bln=project.SRCE[pcp].Blocks[bl].Name 
                if (bln in InputPins.keys()):
                    continue
                else:
                    newb[bln]=0 # add new blok
        for b in newb.keys():
            self.MainWinOutput.insert(firstline,'\t'+str(b)+'\n')
        pass
# ------------------------------------------------------------------------------

Disclaimer = '''
    amplscope - AMPL source code change detector
    (c) 2020-2024, Alim Yusifzada
    reddit: u/Crazy1Dunmer
    gmail: yusifzaj@gmail.com
    Special thanks to Stewart Redman and Baku ABB team.

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
MainGUI(mainwin)

mainwin.grid_rowconfigure(rowOutput, weight=1)
mainwin.grid_columnconfigure(1, weight=1)
mainwin.mainloop()