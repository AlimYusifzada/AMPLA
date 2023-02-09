import re

def get_logins(logsfilename='logins.txt'):
    '''
    run @ domain controller
    wevtutil qe Security | find /i "4648</EventID" >logins.txt
    '''
    timepattern="\d+-\d+-\d+T\d+:\d+:\d+"
    namepattern="'TargetUserName'>\w+"
    ippattern="'IpAddress'>\d+.\d+.\d+.\d+"
    portpattern="'IpPort'>\d+"
    targdompattern="'TargetDomainName'>\w+"
    processpattern="'ProcessName'>\D:[\\\w*\w+]+\\w+\.\w+"

    timef=re.compile(timepattern)
    namef=re.compile(namepattern)
    ipf=re.compile(ippattern)
    portf=re.compile(portpattern)
    targdomf=re.compile(targdompattern)
    processf=re.compile(processpattern)
    result=""

    with open(logsfilename,'r') as logfile:
        l=logfile.readline()
        lcounter=0
        while len(l)>0:
            s=""
            flag=True
            l=logfile.readline()
            if len(timef.findall(l))>0: 
                s+=" Time:"+timef.findall(l)[0]
            else:
                flag=False
            if len(namef.findall(l))>0: 
                s+=" Username:"+namef.findall(l)[0][17:]
            else:
                flag=False
            if len(ipf.findall(l))>0: 
                s+= " IP address:"+ipf.findall(l)[0][12:]
            else:
                flag=False
            if len(portf.findall(l))>0: 
                s+=" Port number:"+portf.findall(l)[0][9:]
            else:
                flag=False
            if len(targdomf.findall(l))>0:
                s+=" Target Domain:"+targdomf.findall(l)[0][19:]
            else:
                flag=False
            if len(processf.findall(l))>0:
                s+=" Target Process:"+processf.findall(l)[0][14:]
            else:
                flag=False
            if flag:
                result+=s+'\n'
    return result