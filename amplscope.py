#!/usr/bin/env python3
# Refactored 5/12/2026, 9:21:26 AM

import os
import threading as trd
from pathlib import Path
from tkinter import Label, Entry, Tk, Button, filedialog, Menu, messagebox, Toplevel
from tkinter import scrolledtext as stx

from ampla import Proj, LoadABXFile, AA, BA, get_PC_name, get_addr_pin, get_sources, get_sinks, InputPins, ampla_rev

try:
    import pyi_splash
    pyi_splash.close()
except ImportError:
    pass

# Constants
REVISION = 'Erzurum'
FILE_TYPES = [
    ("AA/AAX files", "*.aa*"),
    ("AA/AAX files", "*.AA*"),
    ("BA/BAX files", "*.ba*"),
    ("BA/BAX files", "*.BA*"),
]
FIRST_LINE = '1.0'
W_WIDTH = 80

# Grid Layout Constants
ROW_BEFORE = 2
ROW_AFTER = 3
ROW_ENTRY = 4
ROW_OUTPUT = 5

RESPONSIBILITY = '''
    amplscope - AMPL source code change detector
    (c) 2020-2024, Alim Yusifzada
    reddit: u/Crazy1Dunmer
    gmail: yusifzaj@gmail.com
'''

ABB_LOGO = r'''             
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

# Global project instance
project = Proj('dummy')


class SettingsWin:
    def __init__(self) -> None:
        self.win = Toplevel()
        self.win.title('Settings')
        Label(self.win, text="Settings window is not functional yet").pack(padx=20, pady=20)


class OutputWin:
    def __init__(self, text_data='', title='---') -> None:
        self.win = Toplevel()
        self.win.title(title)
        self.win.grid_rowconfigure(0, weight=1)
        self.win.grid_columnconfigure(0, weight=1)
        
        self.data_output = stx.ScrolledText(master=self.win)
        self.data_output.insert("1.0", text_data)
        self.data_output.grid(sticky='nsew', row=0, column=0)


class MainGUI:
    def __init__(self, root) -> None:
        self.root = root
        self.setup_menu()
        self.setup_widgets()
        
        self.root.title(f'GUI:{REVISION}; ampla rev:{ampla_rev}')
        self.root.config(menu=self.main_menu)

    def setup_menu(self):
        self.main_menu = Menu(self.root)
        
        # Compare Menu
        self.compare_menu = Menu(self.main_menu, tearoff=0)
        self.compare_menu.add_command(label=" before<->after ", command=self.compare_selected_files)
        self.compare_menu.add_command(label=" files... ", command=self.select_and_compare)
        self.compare_menu.add_command(label=" directories... ", command=self.compare_directories)
        
        # Project Menu
        self.project_menu = Menu(self.main_menu, tearoff=0)
        self.project_menu.add_command(label=" load project... ", command=self.open_project)
        self.project_menu.add_command(label=" list PC programs ", command=self.list_project_code)
        self.project_menu.add_command(label=" search entry ", command=self.search)
        self.project_menu.add_command(label=" <-source ", command=self.trace_sources)
        self.project_menu.add_command(label="   sink-> ", command=self.trace_sinks)
        
        # Tools Menu
        self.tools_menu = Menu(self.main_menu, tearoff=0)
        self.tools_menu.add_command(label="open AA or BA file... ", command=self.open_and_convert_to_txt)
        self.tools_menu.add_command(label="clear screen", command=self.clean_output_win)
        self.tools_menu.add_separator()
        self.tools_menu.add_command(label="list unknown blocks", command=self.list_new_logic_blocks)
        self.tools_menu.add_command(label="settings... ", command=self.call_settings)
        self.tools_menu.add_command(label="who is responsible?", command=self.about)

        self.main_menu.add_cascade(label=" compare ", menu=self.compare_menu)
        self.main_menu.add_cascade(label=" search/trace ", menu=self.project_menu)
        self.main_menu.add_cascade(label=" options ", menu=self.tools_menu)

    def setup_widgets(self):
        # Labels
        Label(self.root, text=' BEFORE:').grid(row=ROW_BEFORE, column=4, sticky='w')
        Label(self.root, text=' AFTER:').grid(row=ROW_AFTER, column=4, sticky='w')
        Label(self.root, text=' ENTRY:').grid(row=ROW_ENTRY, column=4, sticky='w')

        # Buttons
        Button(self.root, text=" ... ", command=self.select_file_before).grid(column=6, row=ROW_BEFORE, sticky='we')
        Button(self.root, text=" ... ", command=self.select_file_after).grid(column=6, row=ROW_AFTER, sticky='we')
        Button(self.root, text=" search ", command=self.search).grid(column=1, row=ROW_ENTRY, sticky='we')
        Button(self.root, text=" CLS ", command=self.clean_output_win).grid(column=6, row=ROW_ENTRY, sticky='we')
        Button(self.root, text="<-", command=self.trace_sources).grid(column=0, row=ROW_ENTRY, sticky='we')
        Button(self.root, text="->", command=self.trace_sinks).grid(column=2, row=ROW_ENTRY, sticky='we')
        Button(self.root, text=" before<->after ", command=self.compare_selected_files).grid(column=0, row=ROW_BEFORE, sticky='we', columnspan=4)
        Button(self.root, text=" load project code ", command=self.open_project).grid(column=0, row=ROW_AFTER, sticky='we', columnspan=4)

        # Entries
        self.file_before_entry = Entry(self.root, width=W_WIDTH)
        self.file_before_entry.grid(row=ROW_BEFORE, column=5, sticky='we')
        
        self.file_after_entry = Entry(self.root, width=W_WIDTH)
        self.file_after_entry.grid(row=ROW_AFTER, column=5, sticky='we')
        
        self.search_entry = Entry(self.root, width=W_WIDTH)
        self.search_entry.grid(row=ROW_ENTRY, column=5, sticky='we')

        # Output Window
        self.main_win_output = stx.ScrolledText(self.root)
        self.main_win_output.grid(row=ROW_OUTPUT, column=0, sticky='nsew', columnspan=11)

    def select_file_after(self):
        path = filedialog.askopenfilename(initialdir="~", title="Select modified file", filetypes=FILE_TYPES)
        if path:
            self.file_after_entry.delete(0, 'end')
            self.file_after_entry.insert(0, path)
        
    def select_file_before(self):
        path = filedialog.askopenfilename(initialdir="~", title="Select original file", filetypes=FILE_TYPES)
        if path:
            self.file_before_entry.delete(0, 'end')
            self.file_before_entry.insert(0, path)

    def call_settings(self):
        messagebox.showwarning('Warning', 'Settings window is not functional yet')
        SettingsWin()
    
    def list_project_code(self):
        self.clean_output_win()
        self.main_win_output.insert('1.0', '\n')
        try:
            for pc, data in project.SRCE.items():
                rev_ind = data.Header.get('rev_ind', 'N/A')
                date = data.Header.get('date', 'N/A')
                self.main_win_output.insert('1.0', f"{pc}\trev:{rev_ind}\tdate:{date}\n")
        except Exception:
            messagebox.showwarning('Warning', 'Revision number not defined')
            self.main_win_output.insert('1.0', '\nThere is a PC program without a revision number!!!')

    def open_project(self):
        proj_dir = filedialog.askdirectory(title="Select folder with AA or AAX code")
        if proj_dir:
            project.Read(proj_dir)
            self.list_project_code()

    def select_and_compare(self):
        self.clean_output_win()
        self.select_file_before()
        self.select_file_after()
        self.compare_selected_files()

    def compare_selected_files(self):
        self.clean_output_win()
        path_b = self.file_before_entry.get()
        path_a = self.file_after_entry.get()

        if not path_b or not path_a:
            messagebox.showwarning("Oops", "BEFORE and AFTER should not be empty!")
            self.main_win_output.insert('1.0', "Please enter full path to the AMPL source files.")
            return

        fb = LoadABXFile(path_b)
        if fb is None:
            messagebox.showwarning("Oops", "BEFORE value is invalid")
            return

        fa = LoadABXFile(path_a)
        if fa is None:
            messagebox.showwarning("Oops", "AFTER value is invalid")
            return

        OutputWin(str(fb.Compare(fa)), f'Source Comparison\nBEFORE: {fb.fName}\nAFTER: {fa.fName}')

    def compare_directories(self):
        self.clean_output_win()
        self.main_win_output.insert('1.0', "Comparing directories... check AFTER directory for Excel reports.")
        
        dir_before = filedialog.askdirectory(title="Select directory with code BEFORE")
        dir_after = filedialog.askdirectory(title="Select directory with code AFTER")
        
        if not dir_before or not dir_after:
            return

        path_before = Path(dir_before)
        path_after = Path(dir_after)

        # This logic assumes a GenXLSreport function exists in ampla or globally
        # Note: The original code had a potential bug calling GenXLSreport(dir_before, dir_after) 
        # inside the thread target which executes it immediately. Fixed to pass as args.
        
        for dib in path_before.iterdir():
            if dib.is_file() and dib.suffix.upper() in ['.AA', '.AAX']:
                b_name = dib.stem.lower()
                for dia in path_after.iterdir():
                    if dia.is_file() and dia.suffix.upper() in ['.AA', '.AAX']:
                        if dia.stem.lower() == b_name:
                            # Assuming GenXLSreport is defined elsewhere as it was in original
                            from ampla import GenXLSreport
                            trd.Thread(name=b_name, target=GenXLSreport, args=(str(dib), str(dia))).start()
                            
        messagebox.showinfo("Info", f"Check for results at:\n {dir_after}")
        
    def open_and_convert_to_txt(self):
        self.clean_output_win()
        afile = filedialog.askopenfilename(initialdir="~", title="Select AA or BA file", filetypes=FILE_TYPES)
        if not afile:
            return
            
        ext = Path(afile).suffix.upper()
        if ext == '.AA':
            f = AA(afile)
        elif ext == '.BA':
            f = BA(afile)
        else:
            return

        f.Write()
        self.main_win_output.insert('1.0', f"\nSuccessfully converted to {afile}.txt")
        content = "\n".join(f.Lines)
        OutputWin(content, afile)

    def search(self):
        self.clean_output_win()
        updated = False
        query = self.search_entry.get().upper()
        path_b = self.file_before_entry.get()
        path_a = self.file_after_entry.get()

        if not query:
            messagebox.showwarning("Warning", "Search request empty")
            return

        if path_b or path_a:
            if path_b:
                fb = LoadABXFile(path_b)
                if fb:
                    self.main_win_output.insert('end', f'\n Searching at {fb.PCName} BEFORE\n')
                    for cradd in fb.xRef(query):
                        block_key = cradd.split(':')[0]
                        self.main_win_output.insert('end', str(fb.Blocks.get(block_key, '')))
                    updated = True
            if path_a:
                fa = LoadABXFile(path_a)
                if fa:
                    self.main_win_output.insert('end', f'\n Searching at {fa.PCName} AFTER\n')
                    for cradd in fa.xRef(query):
                        block_key = cradd.split(':')[0]
                        self.main_win_output.insert('end', str(fa.Blocks.get(block_key, '')))
                    updated = True

        if len(project.SRCE.keys()) > 0:
            clean_query = query.split(':')[0]
            pc_name = get_PC_name(clean_query)
            
            if pc_name in project.SRCE:
                pc_data = project.SRCE[pc_name]
                if clean_query in pc_data.Blocks:
                    self.main_win_output.insert('end', f"\n{pc_data.Blocks[clean_query]}\n")
            
            results = project.Search(query)
            for res in results:
                self.main_win_output.insert('end', f'\n{res}')
            if results:
                updated = True

        if not updated:
            self.main_win_output.insert('1.0', '\nNothing was found!')

    def trace_sources(self):
        self.clean_output_win()
        if not project.SRCE:
            messagebox.showwarning('Warning', 'Code is not loaded')
            return
            
        query_list = self.search_entry.get().upper().split()
        if not query_list:
            messagebox.showwarning("Warning", "Search request empty")
            return

        for item in query_list:
            addr, _ = get_addr_pin(item)
            if project.is_pc_exist(addr):
                pc_name = get_PC_name(item)
                sources = get_sources(project.SRCE[pc_name], [item])
                for src in sources:
                    self.main_win_output.insert('1.0', f'\n{src}\n')
        self.main_win_output.insert('1.0', '\n\t<-- Source connections:\n')
    
    def trace_sinks(self):
        self.clean_output_win()
        if not project.SRCE:
            messagebox.showwarning('Warning', 'Code is not loaded')
            return
            
        query_list = self.search_entry.get().upper().split()
        if not query_list:
            messagebox.showwarning("Warning", "Search request empty")
            return

        for item in query_list:
            addr, _ = get_addr_pin(item)
            if project.is_pc_exist(addr):
                pc_name = get_PC_name(item)
                sinks = get_sinks(project.SRCE[pc_name], [item])
                for snk in sinks:
                    self.main_win_output.insert('1.0', f'\n{snk}\n')
        self.main_win_output.insert('1.0', '\n\t--> Sink connections:\n')

    def about(self):
        self.clean_output_win()
        self.main_win_output.insert('1.0', f'\n{RESPONSIBILITY}')

    def clean_output_win(self):
        self.main_win_output.delete("1.0", "end")

    def list_new_logic_blocks(self):
        self.clean_output_win()
        new_blocks = set()
        for pcp in project.SRCE.values():
            for block in pcp.Blocks.values():
                if block.Name not in InputPins:
                    new_blocks.add(block.Name)
        
        for b in sorted(new_blocks):
            self.main_win_output.insert('1.0', f'\t{b}\n')


if __name__ == "__main__":
    print(ABB_LOGO)
    print(RESPONSIBILITY)

    main_win = Tk()
    app = MainGUI(main_win)

    main_win.grid_rowconfigure(ROW_OUTPUT, weight=1)
    main_win.grid_columnconfigure(1, weight=1)
    main_win.mainloop()