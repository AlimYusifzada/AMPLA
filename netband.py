#-------------------------------------------------------------------------------
# Name:        netband
# Purpose:     collect data to calculate network bandwidth
#
# Author:      yusifzaj
#
# Created:     12/01/2022
# Copyright:   (c) yusifzaj 2022
# Licence:     N/A free of use (ARMOR only)
#
# run next cmd commands in Macrium backup folder at NAS drive
# dir *.mrimg /s /tc >created.lst
# dir *.mrimg /s /tw >accessed.lst
#
# run this script in the same directory with .lst files
# enjoy
#-------------------------------------------------------------------------------

import re
import xlwt
from datetime import datetime as dt

def getdata(clines):
    date_p='\d+-\D+-\d+' #00-mnt-00
    time_p='\d\d:\d\d' #00:00
    size_p='\d+,\d+,\d+,\d+' #00,000,000,000
    name_p='\S+\.mrimg' #
    arec=[]
    for l in clines:
        #print(l)
        res=[]
        r_date=re.findall(date_p,l)
        r_time=re.findall(time_p,l)
        tmp_size=re.findall(size_p,l)
        r_name=re.findall(name_p,l)
        if r_date and r_time:
            r_size=re.sub('[,]','',tmp_size[0])
            arec.append((r_name[0][:-12],r_date[0],r_time[0],r_size))
    return arec

def main():
    with open('created.lst') as created:
        clist=getdata(created.readlines())
    with open('accessed.lst') as accessed:
        alist=getdata(accessed.readlines())
    if len(clist)==len(alist):
        xlsreport=xlwt.Workbook()
        netwb_sheet=xlsreport.add_sheet('Network Bandwidth')

        cazip=zip(clist,alist)
        rown=0
        for c,a in cazip:
            #print(c,'\t',a)
            #print(c[0],'\t',c[1],'\t',a[1],'\t',c[2])
            netwb_sheet.write(rown,0,c[0]) #host name
            netwb_sheet.write(rown,1,c[1]) #date
            netwb_sheet.write(rown,2,c[2]) #ctime
            netwb_sheet.write(rown,3,a[2]) #atime
            startime = dt.strptime(c[2], '%H:%M')
            stoptime = dt.strptime(a[2], '%H:%M')
            netwb_sheet.write(rown,4,str(stoptime-startime))
            netwb_sheet.write(rown,5,c[3]) #size
            rown+=1
        xlsreport.save('NetworkBandwidthCheck.xls')

    #calculate network bandwidth
    #report


if __name__ == '__main__':
    main()
