import os
from datetime import datetime as dt
import xlwt

duapt_rev = '0.220214'

duapthelp = '''
Search for *.LG files at the project directory.
Transfer all of them to the convenient folder.

Enter the path to the LG files:'''

nodeslist = []


def getDUAPtime(logfile):
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
    bkpsizeidx = logtext.find('DUMP SIZE')  # DUAP size in bytes here

    # get DUAP backup size in bytes
    bkpsize = logtext[bkpsizeidx+11:bkpsizeidx+16]
    nodenum = logtext[nodenumidx+10:nodenumidx+12]
    # get HH:MM:SS DUAP time start
    sstartime = logtext[startimeidx+18:startimeidx+26]
    # get HH:MM:SS DUAP time finish
    sstoptime = logtext[stoptimeidx+18:stoptimeidx+26]

    # convert text to datetime format
    startime = dt.strptime(sstartime, '%H:%M:%S')
    stoptime = dt.strptime(sstoptime, '%H:%M:%S')
    difftime = stoptime-startime  # calculate DUAP duration
    bs = (int(bkpsize))/difftime.total_seconds()
    speed = str("%.2f" % bs)  # speed b/s

    return (nodenum, startime, stoptime, difftime, bkpsize, speed)


def getfiles(dir):
    files = 0
    try:
        w = os.walk(dir)
        for r, d, f in w:
            files = f
    except:
        print('cant read directory:'+dir)

    return files


def xlsreport(dir, nodeslist):

    nodeA_col = 0
    nodeB_col = 1
    size_col = 2
    startA_col = 3
    stopA_col = 4
    speedA_col = 5
    startB_col = 6
    stopB_col = 7
    speedB_col = 8

    prevNodeNum = 0
    rec_cnt = 1  # start from this row

    new_pair = False

    xlsreport = xlwt.Workbook()
    duaptsheet = xlsreport.add_sheet(
        "Duap timimng")  # add date to the sheet name
    duaptsheet.write(0, nodeA_col, 'Side-A node')
    duaptsheet.write(0, nodeB_col, 'Side-B node')
    duaptsheet.write(0, startA_col, 'Start time A')
    duaptsheet.write(0, startB_col, 'Start time B')
    duaptsheet.write(0, stopA_col, 'Stop time A')
    duaptsheet.write(0, stopB_col, 'Stop time B')
    duaptsheet.write(0, size_col, 'Size kb')
    duaptsheet.write(0, speedA_col, 'Speed A kb/s')
    duaptsheet.write(0, speedB_col, 'Speed B kb/s')

    for rec in nodeslist:
        if (prevNodeNum+1) == int(rec[0]) and new_pair:
            duaptsheet.write(rec_cnt, nodeB_col, rec[0])
            duaptsheet.write(rec_cnt, startB_col, rec[1])
            duaptsheet.write(rec_cnt, stopB_col, rec[2])
            duaptsheet.write(rec_cnt, speedB_col, rec[5])
            rec_cnt += 1
            new_pair = False
        else:
            duaptsheet.write(rec_cnt, nodeA_col, rec[0])
            duaptsheet.write(rec_cnt, startA_col, rec[1])
            duaptsheet.write(rec_cnt, stopA_col, rec[2])
            duaptsheet.write(rec_cnt, size_col, rec[4])
            duaptsheet.write(rec_cnt, speedA_col, rec[5])
            new_pair = True
        prevNodeNum = int(rec[0])

    xlsreport.save(dir+'\Duap_Timing.xls')
    pass


def duaptreport(dir):
    if (len(dir) == 0):
        return
    rowcnt = 0
    nodeslist.clear()
    for duaplog in getfiles(dir):
        if ('LG' not in duaplog[-2:]):
            continue
        dumptime = getDUAPtime(dir+'/'+duaplog)
        num = dumptime[0]  # node number
        stt = str(dumptime[1])[-8:]  # start time
        stp = str(dumptime[2])[-8:]  # stop time
        dur = dumptime[3]  # duration
        siz = dumptime[4]  # size
        spd = dumptime[5]  # speed
        nodeslist.append((num, stt, stp, dur, siz, spd))
    xlsreport(dir, nodeslist)
    # input('\n\tpress ENTER to exit')


def main():
    print('='*60)
    print('DUAP time collector')
    dir = input(duapthelp)
    print('-'*60)
    duaptreport(dir)


if __name__ == '__main__':
    main()
