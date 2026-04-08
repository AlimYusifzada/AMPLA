# Refactored on 08/04/2026 13:51
import os
from datetime import datetime as dt

import xlwt

DUAPT_REV = '0.22.02.08'

DUAPT_HELP = '''
Search for *.LG files at the project directory.
Transfer all of them to the convenient folder.
Upon completion look for duap_timing.xls.

Enter the path to the LG files:'''


def get_duap_time(logfile):
    try:
        with open(logfile, 'rb') as lf:
            rawdata = lf.read()
    except Exception:
        print(f"cant find file {logfile}")
        return None

    logtext = str(rawdata)
    nodenumidx = logtext.find('Node')
    startimeidx = logtext.find('TIME')
    stoptimeidx = logtext.rfind('TIME')
    bkpsizeidx = logtext.find('DUMP SIZE')

    bkpsize = logtext[bkpsizeidx + 11:bkpsizeidx + 15]
    nodenum = logtext[nodenumidx + 10:nodenumidx + 12]
    sstartime = logtext[startimeidx + 18:startimeidx + 26]
    sstoptime = logtext[stoptimeidx + 18:stoptimeidx + 26]

    startime = dt.strptime(sstartime, '%H:%M:%S')
    stoptime = dt.strptime(sstoptime, '%H:%M:%S')
    difftime = stoptime - startime
    
    bs = int(bkpsize) / difftime.total_seconds()
    speed = f"{bs:.2f}"

    return nodenum, startime, stoptime, difftime, bkpsize, speed


def get_files(directory):
    files = []
    try:
        for _, _, filenames in os.walk(directory):
            files = filenames
    except Exception:
        print(f"cant read directory:{directory}")

    return files


def xls_report(directory, nodes_list):
    node_a_col = 0
    node_b_col = 1
    size_col = 2
    start_a_col = 3
    stop_a_col = 4
    speed_a_col = 5
    start_b_col = 6
    stop_b_col = 7
    speed_b_col = 8

    prev_node_num = 0
    rec_cnt = 1
    new_pair = False

    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("Duap timimng")
    
    sheet.write(0, node_a_col, 'Side-A node')
    sheet.write(0, node_b_col, 'Side-B node')
    sheet.write(0, start_a_col, 'Start time A')
    sheet.write(0, start_b_col, 'Start time B')
    sheet.write(0, stop_a_col, 'Stop time A')
    sheet.write(0, stop_b_col, 'Stop time B')
    sheet.write(0, size_col, 'Size kb')
    sheet.write(0, speed_a_col, 'Speed A kb/s')
    sheet.write(0, speed_b_col, 'Speed B kb/s')

    for rec in nodes_list:
        if (prev_node_num + 1) == int(rec[0]) and new_pair:
            sheet.write(rec_cnt, node_b_col, rec[0])
            sheet.write(rec_cnt, start_b_col, rec[1])
            sheet.write(rec_cnt, stop_b_col, rec[2])
            sheet.write(rec_cnt, speed_b_col, rec[5])
            rec_cnt += 1
            new_pair = False
        else:
            sheet.write(rec_cnt, node_a_col, rec[0])
            sheet.write(rec_cnt, start_a_col, rec[1])
            sheet.write(rec_cnt, stop_a_col, rec[2])
            sheet.write(rec_cnt, size_col, rec[4])
            sheet.write(rec_cnt, speed_a_col, rec[5])
            new_pair = True
        
        prev_node_num = int(rec[0])

    workbook.save(os.path.join(directory, 'Duap_Timing.xls'))


def duapt_report(directory):
    nodes_list = []
    
    for duaplog in get_files(directory):
        if 'LG' not in duaplog[-2:]:
            continue
            
        dumptime = get_duap_time(os.path.join(directory, duaplog))
        if not dumptime:
            continue
            
        num = dumptime[0]
        stt = str(dumptime[1])[-8:]
        stp = str(dumptime[2])[-8:]
        dur = dumptime[3]
        siz = dumptime[4]
        spd = dumptime[5]
        
        nodes_list.append((num, stt, stp, dur, siz, spd))
        
    xls_report(directory, nodes_list)


def main():
    print('=' * 60)
    print('DUAP time collector')
    directory = input(DUAPT_HELP)
    print('-' * 60)
    duapt_report(directory)


if __name__ == '__main__':
    main()
