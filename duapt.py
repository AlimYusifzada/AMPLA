import os
from datetime import datetime as dt
import xlwt

duapt_rev='0.22.02.08'

duapthelp='''
Search for *.LG files at the project directory.
Transfer all of them to the convenient folder.
Upon completion look for duap_timing.xls.

Enter the path to the LG files:'''

nodeslist = []

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


    nodeA_col=0
    nodeB_col=1
    startA_col=2
    stopA_col=3
    startB_col=4
    stopB_col=5

    prevNodeNum=0
    rec_cnt=1 # start from this row

    new_pair=False

    xlsreport=xlwt.Workbook()
    duaptsheet=xlsreport.add_sheet("Duap timimng") #add date to the sheet name
    duaptsheet.write(0,nodeA_col,'Side-A node')
    duaptsheet.write(0,nodeB_col,'Side-B node')
    duaptsheet.write(0,startA_col,'Start time A')
    duaptsheet.write(0,startB_col,'Start time B')
    duaptsheet.write(0,stopA_col,'Stop time A')
    duaptsheet.write(0,stopB_col,'Stop time B')
    for rec in nodeslist:
        if (prevNodeNum+1)==int(rec[0]) and new_pair:
            duaptsheet.write(rec_cnt,nodeB_col,rec[0])
            duaptsheet.write(rec_cnt,startB_col,rec[1])
            duaptsheet.write(rec_cnt,stopB_col,rec[2])
            rec_cnt+=1
            new_pair=False
        else:
            duaptsheet.write(rec_cnt,nodeA_col,rec[0])
            duaptsheet.write(rec_cnt,startA_col,rec[1])
            duaptsheet.write(rec_cnt,stopA_col,rec[2])
            new_pair=True
        prevNodeNum=int(rec[0])

    xlsreport.save(dir+'\Duap_Timing.xls')
    pass

def duaptreport(dir):
    rowcnt=0
    for duaplog in getfiles(dir):
        # nodenum=duaplog[4:6]
        dumptime = gettime(dir+'/'+duaplog)
        num = dumptime[0]  # node number
        stt = str(dumptime[1])[-8:]  # duap start time
        stp = str(dumptime[2])[-8:]  # duap stop time
        dur = dumptime[3]  # duap duration
        #print('Node '+num+'\tstart: '+str(stt)
        #      [-8:]+'\tstop: '+str(stp)[-8:]+'\tduration: '+str(dur)[-8:])
        # save data -reserved for future calculations
        nodeslist.append((num, stt, stp, dur))
    xlsreport(dir,nodeslist)
    ##input('\n\tpress ENTER to exit')

def main():
    print('='*60)
    print('DUAP time collector')
    dir = input(duapthelp)
    print('-'*60)
    duaptreport(dir)

if __name__=='__main__':
    main()
