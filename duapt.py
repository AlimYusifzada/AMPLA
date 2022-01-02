import os
from datetime import datetime as dt
import xlwt


def gettime(logfile):

    try:
        with open(logfile, 'rb') as lf:  # open and read LG file
            rawdata = lf.read()
    except:
        print('cant find file '+logfile)
        return

    logtext = str(rawdata)  # convert bytes to string
    nodenumidx = logtext.find('Node')
    startimeidx = logtext.find('TIME')  # find position of the first (start)
    stoptimeidx = logtext.rfind('TIME')  # and finish time
    nodenum = logtext[nodenumidx+10:nodenumidx+12]
    # get HH:MM:SS DUAP time start
    sstartime = logtext[startimeidx+18:startimeidx+26]
    # get HH:MM:SS DUAP time finish
    sstoptime = logtext[stoptimeidx+18:stoptimeidx+26]

    # convert text to datetime format
    startime = dt.strptime(sstartime, '%H:%M:%S')
    stoptime = dt.strptime(sstoptime, '%H:%M:%S')
    difftime = stoptime-startime  # calculate DUAP duration

    return (nodenum, startime, stoptime, difftime)


def getfiles(dir):
    files = 0
    try:
        w = os.walk(dir)
        for r, d, f in w:
            files = f
    except:
        print('cant read directory:'+dir)

    return files

def xlsreport(dir,nodeslist):

    date_col=0
    nodeA_col=1
    nodeB_col=2
    startA_col=5
    stopA_col=6
    startB_col=10
    stopB_col=11
    prevNodeNum=0
    rec_cnt=0
    
    xlsreport=xlwt.Workbook()
    duaptsheet=xlsreport.add_sheet("Duap timimng") #add date to the sheet name
    
    for rec in nodeslist:
        if (prevNodeNum+1)==rec[0]:
            duaptsheet.write(rec_cnt,nodeB_col,rec[0])
            duaptsheet.write(rec_cnt,startB_col,rec[1])
            duaptsheet.write(rec_cnt,stopB_col,rec[2])
        else:
            duaptsheet.write(rec_cnt,nodeA_col,rec[0])
            duaptsheet.write(rec_cnt,startA_col,rec[1])
            duaptsheet.write(rec_cnt,stopA_col,rec[2])
        rec_cnt+=1
        prevNodeNum=rec[0]
    
    xlsreport.save(dir+'duap_timing.xls')
    pass
  


print('='*60)
print('DUAP time collector')
dir = input('enter directory with LG files (DUAPT results):')
print('-'*60)
nodeslist = []
rowcnt=0


for duaplog in getfiles(dir):
    # nodenum=duaplog[4:6]
    dumptime = gettime(dir+'/'+duaplog)
    num = dumptime[0]  # node number
    stt = dumptime[1]  # duap start time
    stp = dumptime[2]  # duap stop time
    dur = dumptime[3]  # duap duration
    
    print('Node '+num+'\tstart: '+str(stt)
          [-8:]+'\tstop: '+str(stp)[-8:]+'\tduration: '+str(dur)[-8:])
    # save data -reserved for future calculations
    nodeslist.append((num, stt, stp, dur))
    
xlsreport(dir,nodeslist)
input('\n\tpress ENTER to exit')
