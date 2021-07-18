# -------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Alim Yusif-zada
#
# Created:     05/05/2020
# Copyright:   (c) Alim 2020
# Licence:
# -------------------------------------------------------------------------------
from tkinter import Tk, Button, Frame, Label, Listbox, filedialog
from shutil import copy


mainFrame = Tk()
btnROW = 0
lstROW = 1
fileList = ()


def addfile():
    global fileList
    fn = filedialog.askopenfile(initialdir='/',
                                title='select files to harvest')
    if fn != None:
        fileList += (fn.name,)
        print('%s\tadded to the list' % fn.name)
    pass


def start():
    global fileList
    mainFrame.iconify()
    dest = filedialog.askdirectory(initialdir='/',
                                   title='select destination for the files')
    print("\n!!!!! COPY IN PROGRESS!, PLEASE DO NOT TERMINATE !!!!!")
    for f in fileList:
        copy(f, dest)
    print('DONE')
    pass


def clearlist():
    global fileList
    fileList = ()
    print('\nfile list empty\n', fileList)


addBTN = Button(text='add file', command=addfile)
exeBTN = Button(text='start', command=start)
clsBTN = Button(text='clear', command=clearlist)


def framesetup():
    mainFrame.grid_columnconfigure(0, weight=1)
    mainFrame.grid_rowconfigure(0, weight=1)
    mainFrame.title("harvester")
    addBTN.grid(row=btnROW, column=0, sticky='W'+'E')
    clsBTN.grid(row=btnROW, column=1, sticky='W'+'E')
    exeBTN.grid(row=btnROW, column=2, sticky='W'+'E')
    pass


def main():
    framesetup()
    mainFrame.mainloop()
    pass


if __name__ == '__main__':
    main()
