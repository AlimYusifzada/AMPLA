from block import *


##f=open('test.aax','r')
##l=f.readlines()
##
##for i in l:
##    s=i.split()
##    sm=''
##    if len(s)>0: # line is not empty
##        if len(s[0])>2: # there are more than 2 elemets
##            if s[0][0:2]=='PC'  and s[0][2:3].isdigit(): # it's an address  
##                if len(s)>=3: # it has extra
##                    sm=s[2]  
##                else:
##                    sm='' #sorry no extra
##                print(s[0],s[1],sm) # print address, block name, and extra if exist

a=aax('test.aax')
b=aax('test1.aax')
print(a.cmp(b))
