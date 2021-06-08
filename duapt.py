import os
from datetime import datetime as dt


def gettime(logfile):
    
    try:
        with open(logfile,'rb') as lf: # open and read LG file
            rawdata=lf.read()
    except:
        print('cant find file '+logfile)
        return

    logtext=str(rawdata) # convert bytes to string
    nodenumidx=logtext.find('Node')
    startimeidx=logtext.find('TIME') # find position of the first (start)
    stoptimeidx=logtext.rfind('TIME') # and finish time
    nodenum=logtext[nodenumidx+10:nodenumidx+12]
    sstartime=logtext[startimeidx+18:startimeidx+26] # get HH:MM:SS DUAP time start
    sstoptime=logtext[stoptimeidx+18:stoptimeidx+26] # get HH:MM:SS DUAP time finish 

    startime=dt.strptime(sstartime,'%H:%M:%S') # convert text to datetime format
    stoptime=dt.strptime(sstoptime,'%H:%M:%S')
    difftime=stoptime-startime # calculate DUAP duration

    return (nodenum,startime,stoptime,difftime) 

def getfiles(dir):
    files=0
    try:
        w=os.walk(dir)
        for r,d,f in w:
            files=f
    except:
        print('cant read directory:'+dir)
    
    return files

print('='*60)
print('DUAP time collector')
dir=input('enter directory with LG files (DUAPT results):')
print('-'*60)
nodeslist=[]
for duaplog in getfiles(dir):
    # nodenum=duaplog[4:6]
    dumptime=gettime(dir+'/'+duaplog)
    num=dumptime[0] # node number
    stt=dumptime[1] # duap start time
    stp=dumptime[2] # duap stop time
    dur=dumptime[3] # duap duration 
    print('Node '+num+'\tstart: '+str(stt)[-8:]+'\tstop: '+str(stp)[-8:]+'\tduration: '+str(dur)[-8:])
    nodeslist.append((num,stt,stp,dur)) # save data -reserved for future calculations

input('\n\tpress ENTER to exit')