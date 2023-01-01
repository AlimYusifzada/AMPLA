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
# run this script in the same directory with .lst files
# enjoy
#-------------------------------------------------------------------------------

from os import getcwd
import re
import xlwt

from datetime import datetime as dt

created_filename='1.lst'
accessed_filename='2.lst'

netband_rev='0.23.01.01'
netbandhelp='''
Run commands below:
dir (path to Macrium backups)*.mrimg /s /tc >1.lst
dir (path to Macrium backups)*.mrimg /s /tw >2.lst

Transfer .lst files to the convenient folder
Upon completion look for NetworkBandwidthCheck.xls.

Enter folder with lst files:'''

def getnetdata(clines):
    date_p='\W\d{2,4}-\d{2}-\d{2,4}\W' #yyyy-mm-dd or yy-mm-dd or dd-mm-yyyy all numbers
    date_p1='\d{2}-\D{3}-\d{2}' #dd-mmm-yy mmm=literals
    time_p='\d+:\d+' #00:00
    size_p='\d+,\d+,\d+,\d+' #00,000,000,000 must be at least 1Gb size
    name_p='\S+\.mrimg' #
    arec=[]
    for l in clines:
        r_date=re.findall(date_p,l)
        if r_date==[]:
            r_date=re.findall(date_p1,l)
        r_time=re.findall(time_p,l)
        tmp_size=re.findall(size_p,l)
        r_name=re.findall(name_p,l)
        if r_date and r_time and tmp_size:
            r_size=re.sub('[,]','',tmp_size[0])
            arec.append((r_name[0][:-12],r_date[0],r_time[0],r_size))
    return arec

def netbandcalc(dir):
    if dir=='':
        dir=getcwd()
    try:
        with open(dir+'\\'+created_filename) as created:
            clist=getnetdata(created.readlines())
        with open(dir+'\\'+accessed_filename) as accessed:
            alist=getnetdata(accessed.readlines())
        if len(clist)==len(alist):
            xlsreport=xlwt.Workbook()
            netwb_sheet=xlsreport.add_sheet('Network Bandwidth')
            cazip=zip(clist,alist)
            netwb_sheet.write(0,0,'Date') #date
            netwb_sheet.write(0,1,'Host Name') #host name
            netwb_sheet.write(0,2,'Size (MB)') #size
            netwb_sheet.write(0,3,'Start') #ctime
            netwb_sheet.write(0,4,'Stop') #atime
            netwb_sheet.write(0,5,'Duration')
            netwb_sheet.write(0,6,'Speed (MB/s)')
            rown=1
            for c,a in cazip:
                duration=dt.strptime(a[2], '%H:%M')-dt.strptime(c[2], '%H:%M')
                duration_sec=abs(duration.total_seconds())
                MB_size=int(c[3])/1000000
                MBpS=MB_size/duration_sec

                netwb_sheet.write(rown,0,c[1]) #date 
                netwb_sheet.write(rown,1,c[0]) #host name 
                netwb_sheet.write(rown,2,str("%.2f" % MB_size)) #size
                netwb_sheet.write(rown,3,c[2]) #ctime 
                netwb_sheet.write(rown,4,a[2]) #atime 
                netwb_sheet.write(rown,5,str(duration))
                netwb_sheet.write(rown,6,str("%.2f" % MBpS))
                
                rown+=1
            xlsreport.save(dir+'/'+'Network_Bandwidth.xls')
            return "Network_Bandwidth.xls generated"
    except Exception as e:
        return str('error:'+e.args[1])
        pass

def main():
    print(netbandcalc(input(netbandhelp)))

if __name__ == '__main__':
    main()
