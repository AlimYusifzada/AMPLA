## v0.1 Feb-24,2020 BAKU ABB ARMOR AY
## v0.2 Mar,2020 CA offshore ABB AY - AMPL logic blocks parsing coorection
## Advant Controllers AAX files parsing and comparision
import sys
if sys.version_info[0]<3:
	print('Please use Python version 3+')
	sys.exit()

NEQ='<->'
NEX='pin not exist'
NONE='no value assigned'
TAB=30

HEADER=('design_ch','tech_ref','resp_dept','date',
        'l_text2','r_text2',
        'l_text3','r_text3',
        'l_text4','r_text4',
        'rev_ind','language')

#-----------------------------------------------------------------------

class block:

        def __init__(self,address='PC',NAME='dummy',extra='()'):
                "Create object for logic block"
                self.Pins={} # pins (keys) and connections {pin:connection,..}
                self.Name=NAME # block NAME
                self.Address=address # PC##.##.##...
                self.Extra=extra # everything in the brackets
                return

        def getpin(self,pin):
                "Get string value of the pin"
                if pin in self.Pins.keys():
                    return str(self.Pins[pin])
                else:
                    return NEX

        def addpin(self,pin,value):
                "Create a pin with a value. Value could be any type"
                if pin in self.Pins.keys():
                    print('...pin %s already exist'%pin)
                    return False
                self.Pins[pin]=value
                return True

        def __str__(self):
                "Test representation of the block"
                s=''
                for k in self.Pins.keys():
                    s+='\t'+str(k).ljust(TAB)+self.getpin(k)+'\n'
                return "%s\t%s %s\n%s"%(self.Address,self.Name,self.Extra,s)

        def __eq__(self,other):
                "compare blocks equal"
                if isinstance(other,block):
                    if other.Address==self.Address:
                        if other.Name==self.Name:
                            if other.Extra==self.Extra:
                                if other.Pins==self.Pins:
                                    return True
                return False

        def __add__(self,values):
                "Add new pin with values, \
		first element is pin NAME \
		rest of the elements added as list or tuple"
                if isinstance(values,tuple) or isinstance(values,list):
                    if len(values)>=3:
                            self.addpin(values[0],values[1:len(values)])
                    if len(values)==2:
                            self.addpin(values[0],values[1])
                    else:
                            print('...second operand must have two \
					or more elements in the list')
                else:
                        print('...second operand must be a list or tuple')
                return self

        def cmp(self,other):
                "Compare blocks and return differences report"
                s=''
                if isinstance(other,block):
                    slist=list(self.Pins.keys())
                    olist=list(other.Pins.keys())
                    if self.Name!=other.Name:
                        s+=self.Name+NEQ+other.Name+'\n'
                    if self.Extra!=other.Extra:
                        s+=self.Extra+NEQ+other.Extra+'\n'
                    if len(slist)<len(olist): ## slist should always bigger
                        slist=list(other.Pins.keys())
                        olist=list(self.Pins.keys())
                    if len(slist)!=len(olist):
                        s+='Number of PINS are different!'+ \
                        str(' %d '%len(slist)).rjust(TAB)+ \
                        'vs'+ \
                        str(' %d '%len(olist)).ljust(TAB)+'\n'
                    for k in slist:
                        if k in olist:
                            if self.Pins[k]!=other.Pins[k]:
                                s+='\t'+str(k).ljust(TAB)+ \
				 self.getpin(k).ljust(TAB)+ \
				 NEQ+other.getpin(k).rjust(TAB)+'\n'
                        else:
                            s+='\t'+str(k).ljust(TAB)+ \
				 self.getpin(k).ljust(TAB)+ \
				 NEQ+other.getpin(k).rjust(TAB)+'\n'
                    for k in olist:
                        if k not in slist:
                            s=s+'\t'+str(k).ljust(TAB)+ \
				 self.getpin(k).ljust(TAB)+ \
				 NEQ+other.getpin(k).rjust(TAB)+'\n'
                return s


class aax:
        def __init__(self,fname):
                "Create object and parsing AAX file"
                self.Block={} # logic elements (blocks)
                self.fName=fname # aax file NAME
                status=0 # used for parsing
                self.Lines=None # lines collection from aax file
                self.Header={} # aax header
                self.Labels={} # strore labels {"PC##.##.##":label}

                try: # open aax file
                    file=open(self.fName,'r')
                    self.Lines=file.readlines()
                    file.close()
                except:
                    print('...error reading file: ...'+self.fName[-10:])
                    return
                address='' # address of the block
                BlockName='' # NAME of the block  or  pin
                PinName=''
                extra=''
                pinval=''
                lpinval=[] # list of the values for multiple connected PINS
                elcnt=0 # number of elements in the line
                ## AMPLE parsing logic from here
                for  L in self.Lines:
                    line=L.split()
                    elcnt=len(line)  # count the elements in the line
                    if elcnt>0 and line[0].lower() in HEADER: # reading text from aax file header
                        ss=''
                        i=0
                        for s in line:
                            if i==0:
                                i+=1
                            else:
                                ss=ss+s+' '
                                i+=1
                        self.Header[line[0].lower()]=ss
                    if elcnt>0 and line[0][:2]=='PC' and line[0][2:3].isdigit(): #start of the logic block
                        address=line[0] # get address
                        status=1 #    block mark
                        if elcnt>1:
                            BlockName=line[1] # get blok NAME
                        else:
                            BlockName=''
                        if elcnt>2:
                            extra=line[2] # get extra params
                        else:
                            extra=''
                        self.Block[address]=block(address,BlockName,extra) # create logic block obj
                    if elcnt>0 and line[0][:1]==':': # start of the pin definition
                        PinName=line[0]# get pin NAME
                        status=2 #  pin mark
                        if elcnt>2: # if there are spaces in the pin value
                            st=''
                            for i in range(elcnt):
                                if i>0:
                                    st+=line[i]+' ' # put all of them in to one string
                            #line.clear()
                            line=[PinName,st]
                        if elcnt>1:
                            pinval=line[1] #get pin value
                        if elcnt==1:
                            pinval=NONE #empty pin
                        if pinval[-1:]==',':# another value at the next line
                            status=3
                            lpinval.append(pinval[:-1])
                        else:
                            self.Block[address].addpin(PinName,pinval) # last value for the pin
                            status=0
                    if elcnt==1 and status==3: # one of the values for the pin - add it to the list
                        pinval=line[0]
                        if pinval[-1:]==',': # there are still another value at the next line
                            lpinval.append(pinval[:-1])
                        else: # this is a last value for the pin
                            lpinval.append(pinval)
                            self.Block[address].addpin(PinName,lpinval) # add list to the pin
                            lpinval=[]
                            status=0

        def GetLabels(self):
                "Populate dictionary 'self.Labels' with addresses and labels ;) \
				 return it as result"
                def glb(vx):
                        if vx[0:2]=='N=': # label found
                                s=str(addr)+str(pname)
                        else:
                                s=''
                        return s

                for addr in self.Block: # start for each logic block
                        for pname in self.Block[addr].Pins: # for all PINS
                                pinval=self.Block[addr].Pins[pname] # ger pin val
                                if type(pinval)==list or type(pinval)==tuple: # several connections
                                        for val in pinval:
                                                if type(val)==str:
                                                        if len(glb(val))>2:
                                                                self.Labels[glb(val)]=val[2:]
                                elif type(pinval)==str:
                                        if len(glb(pinval))>2:
                                                self.Labels[glb(pinval)]=pinval[2:]
                return self.Labels

        def CountBlock(self,BlockName='dummy'):
                "Count entries of the logic block"
                counter=0
                for ad in self.Block.keys():
                    if self.Block[ad].Name==BlockName:
                        counter+=1
                return counter

        def AveragePins(self,BlockName='dummy'):
                "Return average count of pins for given block type"
                pcnt=0
                bcnt=0
                for ad in self.Block.keys():
                    if self.Block[ad].Name==BlockName:
                        bcnt+=1
                        pcnt+=len(self.Block[ad].Pins)
                if bcnt==0: # stop div by 0
                        bcnt=1
                return round(pcnt/bcnt,1)

        def cmp(self,other):
                "Compare AAX files and return text report"
                s=''
                if isinstance(other,aax):
                    skeys=self.Block.keys()
                    okeys=other.Block.keys()
                    if self.Header!=other.Header:
                        s+='\nConflict at HEADER:\n'
                        for k in HEADER:
                            if self.Header[k]!=other.Header[k]:
                                s+='\n'+str(k).ljust(TAB)+ \
				 str(self.Header[k]).rjust(TAB)+ \
				 str(other.Header[k]).rjust(TAB)
                        s+='\n'
                    if len(skeys)!=len(okeys):
                        s+='\nNumers of logic blocks are different\n \
		at ..%s =%d\n \
		at ..%s =%d\n'% \
		(self.fName[-10:],len(self.Block.keys()),other.fName[-10:],len(other.Block.keys()))
                    for key in self.Block.keys():
                        if key in other.Block.keys():
                            if self.Block[key]!=other.Block[key]:
                                s+='\nConflict at %s %s\n'%(key,self.Block[key].Name)+ \
			str(self.Block[key].cmp(other.Block[key]))
                        else:
                            s+='\naddress %s not found at ..%s but exist at ..%s\n'% \
		        (key,other.fName[-10:],self.fName[-10:])+str(self.Block[key])
                    for key in other.Block.keys():
                        if key not in self.Block.keys():
                            s+='\naddress %s not found at ..%s but exist at ..%s\n'% \
			(key,self.fName[-10:],other.fName[-10:])+str(other.Block[key])
                return s

        def statout(self):
                "Return list with statistic data: \
		 (block NAME, block usage count, average pins number)"
                s=''
                blocks=()
                stout=()
                for ad in self.Block.keys():
                    NAME=self.Block[ad].Name
                    if NAME not in blocks:
                        blocks=blocks+(NAME,)
                        stout=stout+((NAME,self.CountBlock(NAME),self.AveragePins(NAME)),)
                return stout
