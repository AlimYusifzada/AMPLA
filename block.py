## version 0.1 Feb-24,2020
## AMPL logic block

EQ=' = '
NEQ=' ! '
ERR1='ERROR:check types'
NONE='NONE'
_tab=16

##-----------------------------------------------------------------------
    
class Block:

    def __init__(self,address='PC',name='dummy',extra='()'):
        self.pins={} ## block pins (keys) and connections {pin:connection,..}
        self.name=name ## block name
        self.address=address ## PC##.##.##...
        self.extra=extra ## everything in the brackets
        return

    def gpin(self,pin): ## get string value of the pin
        if pin in self.pins.keys():
            return str(self.pins[pin])
        else:
            return NONE
    
    def apin(self,pin,value): ## add pin
        if pin in self.pins.keys():
            return False
        self.pins[pin]=value
        return True

    def __str__(self):  ## print block
        s=''
        for k in self.pins.keys():
            s=s+'\t'+str(k).ljust(_tab)+self.gpin(k)+'\n'
        return "%s\t%s %s\n%s"%(self.address,self.name,self.extra,s)

    def __eq__(self,other):
        if isinstance(other,Block):
            if other.address==self.address:
                if other.name==self.name:
                    if other.extra==self.extra:
                        if other.pins==self.pins:
                            return True
        return False

    def cmp(self,other):
        s=''
        if isinstance(other,Block):
            slist=list(self.pins.keys())
            olist=list(other.pins.keys())
            if len(slist)<len(olist): ## slist should always bigger
                slist=list(other.pins.keys())
                olist=list(self.pins.keys())    
            for k in slist:
                if k in olist:
                    if self.pins[k]==other.pins[k]:
                        i=EQ
                    else:
                        i=NEQ
                else:
                    i=NEQ
                s=s+'\t'+str(k).ljust(_tab)+self.gpin(k).ljust(_tab)+i.ljust(_tab)+other.gpin(k)+'\n'
            for k in olist:
                if k not in slist:
                    s=s+'\t'+str(k).ljust(_tab)+self.gpin(k).ljust(_tab)+NEQ.ljust(_tab)+other.gpin(k)+'\n'               
        return s

    
class aax:
    
    def __init__(self,fname):
        self.el={}
        self.fname=fname
        status=0
        try: # open aax file
            file=open(self.fname,'r')
            self.lines=file.readlines()
            file.close()
        except:
            print('error reading file:'+self.fname)
            return
## 
        address='' # address of the block 
        blkname='' # name of the block  or  pin
        pinname=''
        extra=''
        pinval='' 
        lpinval=[] # for multiple connections
        elcnt=0 # number of elements in the line
        
## AMPLE parsing logic from here
        
        for  L in self.lines:
            line=L.split()
            elcnt=len(line)  # count the elements in the line
                
            if elcnt>0 and line[0][:2]=='PC' and line[0][2:3].isdigit(): #start of the logic block
                address=line[0] # get address
                status=1 #    block mark
                if elcnt>1:
                    blkname=line[1] # get blok name
                else:
                    blkname=''
                if elcnt>2:
                    extra=line[2] # get extra params
                else:
                    extra=''
                self.el[address]=Block(address,blkname,extra) # create logic block obj
                
            if elcnt>0 and line[0][:1]==':': # start of the pin definition 
                pinname=line[0]# get pin name
                status=2 #  pin mark
                if elcnt>2: # if there are spaces 
                    st=''
                    for i in range(elcnt):
                        if i>0:
                            st+=line[i]+' ' # put all of them in to one string
                    line.clear()
                    line=[pinname,st]
                        
                if elcnt>1:
                    pinval=line[1] #get pin value
                if pinval[-1:]==',':# another value at the next line
                    status=3
                    lpinval.append(pinval[:-1])
                else:
                    self.el[address].apin(pinname,pinval)
                    
            if elcnt==1 and status==3:
                pinval=line[0]
                if pinval[-1:]==',':
                    lpinval.append(pinval[:-1])
                else:
                    lpinval.append(pinval)
                    self.el[address].apin(pinname,lpinval)
                    status=0
        return

    def count(self,blkname='dummy'):
        counter=0
        for k in self.el.keys():
            if self.el[k].name==blkname:
                counter+=1
        return counter

 
            
            
## simple format
## (* commentary notes *)
    
## BEGIN PC##
    
## HEADER
## text

## PC##     PCPGM ()

## address       name   extra
## [PC##.##...] [name] <(parameters)>
##    list of pins and connections/values
##    [:][pin]   [value]
    
## END PC##

