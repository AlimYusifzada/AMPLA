from block import *
import sys
import difflib as Dif


file1=''
file2=''
options=()

def help():
    print('aaxcmp [file1.aax] [file2.aax] <options>')
    print('options could be:')
    print(' -i  compare logic blocs')
    print(' -l  compare line by line')
    print(' -s print some statistics (in development)')
    print(' -h print this help')
    return

print('Mar,2020,AY AMPL logic block compare')


if len(sys.argv)<3:
    help()
    exit(0)
          
for arg in sys.argv[1:]:
    if arg[0]=='-' and len(arg)==2: # option
        options=options+(arg,)
    elif file1=='':
        file1=arg
    elif file2=='':
        file2=arg

if file1=='' or file2=='':
    print('cant find files in arguments')
    help()
    sys.exit(-1)

try:
    fileOne=aax(file1)
    fileTwo=aax(file2)
except:
    sys.exit(-2)

for op in options:
    if op=='-i':
        print(fileOne.cmp(fileTwo))
    if op=='-s':
        print('File %s'%fileOne.fname)
        print(fileOne.statout())
        print('File %s'%fileTwo.fname)
        print(fileTwo.statout())
    if op=='-l':
        d=Dif.Differ()
        cmpres=d.compare(fileOne.lines,fileTwo.lines)
        for i in cmpres:
            print(i,end='')
    if op=='-h':
        help()
    
