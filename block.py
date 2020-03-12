## version 0.1 Feb-24,2020 BAKU ABB ARMOR AY
## Advant Controllers AAX files parsing and comparision

NEQ=' <not equal> '
NONE='NONE'
_tab=16

HEADER=('Design_ch','Tech_ref','Resp_dept','Date',
        'L_Text2','R_Text2',
        'L_Text3','R_Text3',
        'L_Text4','R_Text4',
        'Rev_ind','Language')

##-----------------------------------------------------------------------

class block:

    def __init__(self,address='PC',name='dummy',extra='()'):
        "create logic block"
        self.pins={} ## block pins (keys) and connections {pin:connection,..}
        self.name=name ## block name
        self.address=address ## PC##.##.##...
        self.extra=extra ## everything in the brackets
        return

    def getpin(self,pin): ##
        "get string value of the pin"
        if pin in self.pins.keys():
            return str(self.pins[pin])
        else:
            return NONE

    def addpin(self,pin,value):
        "create a pin with a value"
        if pin in self.pins.keys():
            print('pin %s already exist'%pin)
            return False
        self.pins[pin]=value
        return True

    def __str__(self):
        "string representation of the block"
        s=''
        for k in self.pins.keys():
            s+='\t'+str(k).ljust(_tab)+self.getpin(k)+'\n'
        return "%s\t%s %s\n%s"%(self.address,self.name,self.extra,s)

    def __eq__(self,other):
        "compare blocks equal"
        if isinstance(other,block):
            if other.address==self.address:
                if other.name==self.name:
                    if other.extra==self.extra:
                        if other.pins==self.pins:
                            return True
        return False

    def __add__(self,values):
        "add pin with values, first element is pin name rest of the elements add as list or tuple"
        if isinstance(values,tuple) or isinstance(values,list):
            if len(values)>=3:
                self.addpin(values[0],values[1:len(values)])
            if len(values)==2:
                self.addpin(values[0],values[1])
        return self

    def cmp(self,other):
        "compare blocks and return report about differences"
        s=''
        if isinstance(other,block):
            slist=list(self.pins.keys())
            olist=list(other.pins.keys())
            if self.name!=other.name:
                s+=self.name+NEQ+other.name+'\n'
            if self.extra!=other.extra:
                s+=self.extra+NEQ+other.extra+'\n'
            if len(slist)<len(olist): ## slist should always bigger
                slist=list(other.pins.keys())
                olist=list(self.pins.keys())
            for k in slist:
                if k in olist:
                    if self.pins[k]!=other.pins[k]:
                        s+='\t'+str(k).ljust(_tab)+self.getpin(k).ljust(_tab)+NEQ+other.getpin(k).rjust(_tab)+'\n'
            for k in olist:
                if k not in slist:
                    s=s+'\t'+str(k).ljust(_tab)+self.getpin(k).ljust(_tab)+NEQ+other.getpin(k).rjust(_tab)+'\n'
        return s


class aax:

    def __init__(self,fname):
        "parsing aax file"
        self.el={} # logic elements (blocks)
        self.fname=fname # aax file name
        status=0 # used for parsing
        self.lines=None # lines collection from aax file
        self.header={} # aax header

        try: # open aax file
            file=open(self.fname,'r')
            self.lines=file.readlines()
            file.close()
        except:
            print('error reading file:'+self.fname)
            return
        address='' # address of the block
        blkname='' # name of the block  or  pin
        pinname=''
        extra=''
        pinval=''
        lpinval=[] # list of the values for multiple connected pins
        elcnt=0 # number of elements in the line
## AMPLE parsing logic from here
        for  L in self.lines:
            line=L.split()
            elcnt=len(line)  # count the elements in the line
            if elcnt>0 and line[0] in HEADER: # reading text from aax file header
                ss=''
                i=0
                for s in line:
                    if i==0:
                        i+=1
                    else:
                        ss=ss+s+' '
                        i+=1
                self.header[line[0]]=ss

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
                self.el[address]=block(address,blkname,extra) # create logic block obj
            if elcnt>0 and line[0][:1]==':': # start of the pin definition
                pinname=line[0]# get pin name
                status=2 #  pin mark
                if elcnt>2: # if there are spaces in the pin value
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
                    self.el[address].addpin(pinname,pinval) # last value for the pin
                    status=0
            if elcnt==1 and status==3: # one of the values for the pin - add it to the list
                pinval=line[0]
                if pinval[-1:]==',': # there are still another value at the next line
                    lpinval.append(pinval[:-1])
                else: # this is a last value for the pin
                    lpinval.append(pinval)
                    self.el[address].addpin(pinname,lpinval) # add list to the pin
                    lpinval=[]
                    status=0

    def countblock(self,blkname='dummy'):
        "count logic blocks in aax file"
        counter=0
        for ad in self.el.keys():
            if self.el[ad].name==blkname:
                counter+=1
        return counter

    def countpin(self,blkname='dummy'):
        "return average count of pins for given block type"
        pcnt=0
        bcnt=0
        for ad in self.el.keys():
            if self.el[ad].name==blkname:
                bcnt+=1
                pcnt+=len(self.el[ad].pins)
        return round(pcnt/bcnt,1)

    def cmp(self,other):
        "compare aax files and return report"
        s=''
        if isinstance(other,aax):
            skeys=self.el.keys()
            okeys=other.el.keys()

            if self.header!=other.header:
                s+='\nConflict at HEADER:\n'
                for k in HEADER:
                    if self.header[k]!=other.header[k]:
                        s+='\n'+str(k).ljust(_tab)+str(self.header[k]).rjust(_tab)+str(other.header[k]).rjust(_tab)
                s+='\n'
            if len(skeys)!=len(okeys):
                s+='\nNumers of logic blocks at %s =%d differnet from %s =%d\n'%(self.fname,len(self.el.keys()),other.fname,len(other.el.keys()))
            for key in self.el.keys():
                if key in other.el.keys():
                    if self.el[key]!=other.el[key]:
                        s+='\nConflict at %s\n'%(key)+str(self.el[key].cmp(other.el[key]))
                else:
                    s+='\nAddress %s not found at %s but exist at %s\n'%(key,other.fname,self.fname)+str(self.el[key])
            for key in other.el.keys():
                if key not in self.el.keys():
                    s+='\nAddress %s not found at %s but exist at %s\n'%(key,self.fname,other.fname)+str(other.el[key])
        return s

    def statout(self):
        "output statistics (block name, block count, average pins)"
        s=''
        blocks=()
        stout=()
        for ad in self.el.keys():
            name=self.el[ad].name
            if name not in blocks:
                blocks=blocks+(name,)
                stout=stout+((name,self.countblock(name),self.countpin(name)),)
        return stout
                
