## v0.1 Feb-24,2020 BAKU ABB ARMOR
## v0.2 Mar,2020 CA offshore - AMPL logic blocks parsing coorection
## v0.3 add INAME parsing and compare
## v0.4 add cross refference search aax.CRef() function
## v0.5 remove unneccessary message in output log, comarison logic compromised
## v0.6 AMPL parsing debugging
## v0.7 Sep-26,2020 debug comparison logic
## v0.8 Oct-06,2020 multiple connections compare bug fix
## v0.9 Nov-15,2020 shortened the output, plan to expand with few extra configs 

import sys
if sys.version_info[0]<3:
	print('Please use Python version 3+')
	sys.exit()

ampla_rev='0.9'
NEQ=' <- ! -> '
NEok=' <- ok -> '
NEX='pin not exist'
NONE='no value assigned'
TAB=30
nSPC=-20


HEADER=('design_ch','tech_ref','resp_dept','date',
        'l_text2','r_text2',
        'l_text3','r_text3',
        'l_text4','r_text4',
        'rev_ind','language')


class block:

        def __init__(self,address='',name='',extra=''):
                "Constructor, create logic block instance\n \
                Pins: contain logic block pins (dictionary keys) and values\n \
                Name: logic block name like MOVE,OR,AND,..\n \
                Adress: logic block address like PC12.1.1.2\n \
                Extra: the logic block parameters MOVE(B,16)"
                self.Pins={} # pins (keys) and connections {pin:connection,..}
                self.Name=name # block NAME
                self.Address=address # PC##.##.##...
                self.Extra=extra # everything in the brackets
                self.Description=''
                return

        def getpin(self,pin):
                "Return string value of the pin"
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
                "Text representation of the block"
                s=self.Description+'\n'
                for k in self.Pins.keys():
                        s+='\t'+str(k).ljust(TAB)+self.getpin(k)+'\n'
                return "%s\t%s %s\n%s"%(self.Address,self.Name,self.Extra,s)

        def __eq__(self,other):
                "Compare blocks, return True or False"
                if isinstance(other,block):
                        if other.Address==self.Address:
                                if other.Name==self.Name:
                                            if other.Extra==self.Extra:
                                                        if other.Pins==self.Pins:
                                                              if other.Description==self.Description:
                                                                    return True
                return False

        def __add__(self,values):
                "Add new pin with values, first element is pin NAME\n \
                rest of the elements added as list or tuple"
                if isinstance(values,tuple) or isinstance(values,list):
                        if len(values)>3:
                                self.addpin(values[0],values[1:len(values)])
                        if len(values)==2:
                                self.addpin(values[0],values[1])
                else:
                        print('...second operand must be a list or tuple')
                return self

        def cmp(self,other):
                "Compare blocks, return difference report"
                s=''
                flag=False
                if isinstance(other,block):
                        if self==other:
                                return s
                        slist=list(self.Pins.keys())
                        olist=list(other.Pins.keys())
                        # if len(slist)<len(olist): ## slist should always bigger...???
                        #       slist=list(other.Pins.keys())
                        #       olist=list(self.Pins.keys())          
                        if self.Name!=other.Name:
                              s+='\t'+self.Name+NEQ+other.Name+'\n'
                              flag=True
                              
                        if self.Extra!=other.Extra:
                              s+='\t'+self.Extra+NEQ+other.Extra+'\n'
                              flag=True
                              
                        if self.Description!=other.Description:
                              s+='\t'+self.Description.ljust(TAB)+NEok+other.Description.rjust(TAB)+'\n'
                              flag=True
                              
                # compare pins
                        #if len(slist)!=len(olist):
                         #     s+='Number of PINS are different!'+ \
                          #    str(' %d '%len(slist)).rjust(TAB)+ \
                           #   'vs'+ \
                            #  str(' %d '%len(olist)).ljust(TAB)+'\n'
                        for k in slist:
                                if k in olist: # pin defined in both logic blocks
                                        if self.Pins[k]!=other.Pins[k]: 
                                                flag=True
                                                s+='\t'+str(k).ljust(TAB)+ \
                                                        str(self.Pins[k]).ljust(TAB)+ \
                                                        NEQ+str(other.Pins[k]).rjust(TAB)+'\n'
                                else: # pin is not in other block
                                        if self.Pins[k]!=NONE:
                                                flag=True
                                                s+='\t'+str(k).ljust(TAB)+ \
                                                        str(self.Pins[k]).ljust(TAB)+ \
                                                        NEQ+NEX.rjust(TAB)+'\n'
                        for k in olist:
                                if k not in slist:
                                        if other.Pins[k]!=NONE:
                                                flag=True
                                                s+='\t'+str(k).ljust(TAB)+ \
                                                        NEX.ljust(TAB)+ \
                                                        NEQ+str(other.Pins[k]).rjust(TAB)+ '\n'
                        if flag:
                            s=self.Address+'\t'+self.Name+'\n'+s
                return s

class aax:

      def __init__(self,fname):
                  "Constructor, create AAX file instance, parse AMPL logic\n \
                  Blocks: contains all logic blocks from AAX file\n \
                  fName: full path to AMPL aax file including file name\n \
                  Lines: text lines from AMPL file\n \
                  Header: AMPL code header\n \
                  Labels: all labels with addresses in the AMPL code"
                  self.Blocks={} # logic elements (blocks)
                  self.fName=fname # aax file NAME
                  self.Lines=None # lines collection from aax file
                  self.Header={} # aax header
                  self.Labels={} # strore labels {"PC##.##.##":label}

                  status=0 # used for parsing

                  # open aax file
                  try: 
                        file=open(self.fName,'r')
                        self.Lines=file.readlines() #read aax file to Lines
                        file.close()
                  except:
                        print('...error reading file: ...'+self.fName[nSPC:])
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
                        word=L.split() # read line and split by spaces
                        elcnt=len(word)  # count the elements in the line
                        if elcnt>0:
                                # reading text from aax file header
                                if word[0].lower() in HEADER: 
                                        ss=''
                                        i=0
                                        for s in word:
                                                if i==0:
                                                        i+=1
                                                else:
                                                        ss=ss+s+' '
                                                        i+=1
                                        self.Header[word[0].lower()]=ss
                                        continue
                                #start of the logic block status=1 get address, name and params
                                if word[0][:2]=='PC' and word[0][2:3].isdigit() and status!=2: 
                                        address=word[0] # get address
                                        status=1 # block mark if status ==1 we are inside logic block
                                        if elcnt>1:
                                                BlockName=word[1] # get blok NAME
                                        else:
                                                BlockName='' # address without logic block! not possible
                                        if elcnt>2:
                                                extra=word[2] # get extra params
                                        else:
                                                extra=''
                                                if '(' in BlockName: # no space between block name and extra
                                                    extra=BlockName[BlockName.find('('):]
                                                    BlockName=BlockName[:BlockName.find('(')]
                                        self.Blocks[address]=block(address,BlockName,extra) # create logic block obj
                                        continue
                                # try read block name if exist
                                if status==1 and word[0]=='INAME':
                                        if elcnt>1:
                                                st=''
                                                for e in word[1:]:
                                                        st+=e
                                                self.Blocks[address].Description=st
                                        continue
                                # read pins
                                if status==1 and word[0][:1]==':': # start of the pin definition
                                        PinName=word[0]# get pin NAME
                                        if elcnt>=2: # if there are spaces in the pin value
                                                st=''
                                                for e in word[1:]:
                                                        st+=e+'' # put all back in to one string
                                                pinval=st
                                        if elcnt==1:
                                                pinval=NONE #empty pin
                                        if pinval[-1:]==',':# another value at the next line
                                                lpinval=[]
                                                status=2 #  pin mark pin value could ocupy several lines
                                                lpinval.append(pinval[:-1])
                                                continue
                                        else:
                                                self.Blocks[address].addpin(PinName,pinval) # last value for the pin
                                                status=1
                                                continue
                                # if pin has several values (output)
                                if status==2: # one of the values for the pin - add it to the list
                                        if elcnt>1: # if there are spaces in the pin value
                                                st=''
                                                for e in word:
                                                        st+=e+'' # put all back in to one string
                                                pinval=st
                                        else:
                                                pinval=word[0]
                                        if pinval[-1:]==',': # there are still another value at the next line
                                              lpinval.append(pinval[:-1])
                                        else: # this is a last value for the pin
                                              lpinval.append(pinval)
                                              lpinval=lpinval.sort()
                                              self.Blocks[address].addpin(PinName,lpinval) # add list to the pin
                                              lpinval=[]
                                              status=1

      def GetLabels(self):
            "Populate dictionary 'self.Labels'\n \
            with addresses and labels, then return it as result"
            
            def glb(vx):
                  if vx[0:2]=='N=': # label found
                          s=str(addr)+str(pname)
                  else:
                          s=''
                  return s
            
            for addr in self.Blocks: # start for each logic block
                  for pname in self.Blocks[addr].Pins: # for all PINS
                          pinval=self.Blocks[addr].Pins[pname] # ger pin val
                          if type(pinval)==list or type(pinval)==tuple: # several connections
                                  for val in pinval:
                                          if type(val)==str:
                                                  if len(glb(val))>2:
                                                          self.Labels[glb(val)]=val[2:]
                          elif type(pinval)==str:
                                  if len(glb(pinval))>2:
                                          self.Labels[glb(pinval)]=pinval[2:]
            
            return self.Labels
      _getlabels=GetLabels

      def CountBlock(self,BlockName='dummy'):
            "Count entries of the logic block"
            counter=0
            for ad in self.Blocks.keys():
                  if self.Blocks[ad].Name==BlockName:
                        counter+=1
            return counter
      _countblock=CountBlock

      def AveragePins(self,BlockName='dummy'):
            "Return average count of pins for given block type"
            pcnt=0
            bcnt=0
            for ad in self.Blocks.keys():
                  if self.Blocks[ad].Name==BlockName:
                        bcnt+=1
                        pcnt+=len(self.Blocks[ad].Pins)
            if bcnt==0: # stop div by 0
                  bcnt=1
            return round(pcnt/bcnt,1)
      _averagepins=AveragePins

      def cmp(self,other):
            "Compare AAX files and return text report"
            s=''
            if isinstance(other,aax):
                  skeys=self.Blocks.keys()
                  okeys=other.Blocks.keys()
                  if self.Header!=other.Header:
                          s+='\nConflict at HEADER:'
                          for k in HEADER:
                                if k in other.Header and k in self.Header:
                                  if self.Header[k]!=other.Header[k]:
                                          s+='\n\t'+str(k).ljust(TAB)+ \
                                                   str(self.Header[k]).ljust(TAB)+NEok+ \
                                                   str(other.Header[k]).rjust(TAB)
                  s+='\n'
                  if len(skeys)!=len(okeys):
                          s+='\nNumers of logic blocks are different\n \
                                  at ..%s =%d\n \
                                  at ..%s =%d\n'% \
                                  (self.fName[nSPC:],len(self.Blocks.keys()),other.fName[nSPC:],len(other.Blocks.keys()))
                  for key in self.Blocks.keys():
                          if key in other.Blocks.keys():
                              if self.Blocks[key]!=other.Blocks[key]:
                                    s+=str(self.Blocks[key].cmp(other.Blocks[key]))
                                #  s+='\nConflict at %s %s\n'%(key,self.Blocks[key].Name)+ \
                                 #         str(self.Blocks[key].cmp(other.Blocks[key]))
                          else:
                                  s+='\naddress %s not found at ..%s but exist at ..%s\n'% \
                                          (key,other.fName[nSPC:],self.fName[nSPC:])+str(self.Blocks[key])
                  for key in other.Blocks.keys():
                          if key not in self.Blocks.keys():
                                  s+='\naddress %s not found at ..%s but exist at ..%s\n'% \
                                          (key,self.fName[nSPC:],other.fName[nSPC:])+str(other.Blocks[key])
            return s
      _cmp=cmp

      def StatOut(self):
            "Return list with statistic data:\n \
            (block NAME, block usage count, average pins number)"
            blocks=()
            out=()
            for ad in self.Blocks.keys():
                  NAME=self.Blocks[ad].Name
                  if NAME not in blocks:
                        blocks+=(NAME,)
                        out+=((NAME,self._countblock(NAME),self._averagepins(NAME)),)
            return out
      _statout=StatOut

      def CRef(self,tag='dummy'):
            "Cross referense search for the tag_name \
            return tuple of addresses where it was found.\
            CRef(NONE) search for unconnected pins \
            to print all blocks out use as shown below \
            for a in f.CRef('tag_name'): \
                print(f.Blocks[a[:a.index(':')]]) "
            out=()
            for addr in self.Blocks:
                for pin in self.Blocks[addr].Pins:
                    pinval=self.Blocks[addr].getpin(pin)
                    if tag in pinval:
                        out+=(str(addr)+str(pin),)
            return out
      _cref=CRef
