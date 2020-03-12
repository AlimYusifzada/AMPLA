from block import *
import sys

print('Mar,2020,AY AMPL logic block compare')


if len(sys.argv)<3:
    print('not enough arguments')
    print('from command line prompt run: aaxcmp [file1.aax] [file2.aax]')
    exit()
try:
    file1=aax(sys.argv[1])
    file2=aax(sys.argv[2])
    print(file1.cmp(file2))
except:
    print('fatal error')
