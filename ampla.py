" Set of functions to compare AAX and BAX files \n \
  generated by ApplicationBuilder, FunctionChartBuilder AMPL language \n \
  ApplcationBuilder, FunctionChartBuilder and AMPL are ABB products\n \
  used to configure Advant Controllers 400 series\n \
  v0.1 Feb-24,2020 first try \n \
  v0.2 Mar,2020 logic blocks parsing coorection \n \
  v0.3 add INAME parsing and compare \n \
  v0.4 add cross refference search aax.cref() function and other minor changes \n \
  v0.5 remove unneccessary message in output log, comarison logic compromised \n \
  v0.6 AMPL parsing logic debug after test \n \
  v0.7 Sep-26,2020 debug comparison logic \n \
  v0.8 Oct-06,2020 pin multiple connections compare bug fix \n \
  v0.9 Nov-15,2020 shortened the output, debug \n \
  v0.9.1 Mar-12,2021 add dbinst and bax classes, deprecate statout function, logic polishing and commenting \n \
  v0.9.2 Mar-21,2021 check code consistency function added <keysaround> \n \
  v0.9.3 Mar-23 2021 compare numbers D=# as numbers but not like string, so D=5.0 and D=5 treated as equal"

ampla_rev='0.9.3'

import sys
if sys.version_info[0]<3:
    print('Please use Python version 3.*')
    sys.exit()


NEQ=' <- ! -> '
NEok=' <- ok -> '
NEX='not exist'
NONE='not assigned'
TAB=30
nSPC=-20


HEADER=('design_ch','tech_ref','resp_dept','date',
        'l_text1','r_text1',
        'l_text2','r_text2',
        'l_text3','r_text3',
        'l_text4','r_text4',
        'rev_ind','language')

def trimd(txt):
    if txt[:2].upper()=='D=':
        return txt[2:]
    return txt

def isnum(txt):
    try:
        float(trimd(txt))
        return True
    except:
        return False

def zipins(pinAval,pinBval):
    flag=False # revert flag set if A/B values reverted
    # use to keep output A-first B-second
    if type(pinAval)!=list and type(pinBval)!=list:
        return None 
    if type(pinAval)!=list:
        pinAval=[pinAval,]
    if type(pinBval)!=list:
        pinBval=[pinBval,]
    if max(len(pinAval),len(pinBval))==len(pinAval):
    # select longest and shortest
        xList=pinAval
        mList=pinBval
    else:
        xList=pinBval
        mList=pinAval
        flag=True
    vdif=len(xList)-len(mList) # calculate difference in length
    if vdif>0:
        for i in range(vdif):
            mList.append(NEX)
    if flag:
        return zip(mList,xList)
    else:
        return zip(xList,mList)

class block:
    def __init__(self,address='',name='',extra=''):
        "Constructor, create logic block instance, parent for dbinst\n \
        Pins: contain logic block pins (dictionary keys) and values\n \
        Name: logic block name: MOVE,OR,AND,..\n \
        in case of BAX element used to keep instance type: DIC,AIC.. \n \
        Adress (unique): logic block address: PC12.1.1.2\n \
        in case of BAX element used to keep instance name:\n \
        Extra: the logic block parameters: MOVE(B,16)\n \
        in case of BAX element can keep type of DAT: DAT4 (I)\n"

        self.Pins={} # pins (keys) and connections {pin:connection,..}
        self.Name=name # block NAME or Instance type if DB element
        self.Address=address # PC##.##.##... or Instance name if DB element
        self.Extra=extra # everything in the brackets no in use if DB element
        self.Description=''
        return
    
    def getpin(self,pin):
        "Return string value of the pin \n \
        block_obj.getpin('pin')"
        if pin in self.Pins.keys():
            return str(self.Pins[pin])
        else:
            return NEX
            
    def addpin(self,pin,value):

        "Create a pin with a value. Value could be any type\n \
        block_obj.addpin('pin',pin_value)"

        if pin in self.Pins.keys():
            print('...pin %s already exist'%pin)
            return False
        self.Pins[pin]=value
        return True

    def __str__(self):

        "Text representation of the block\n \
        print(block_obj) or str(block_obj)"

        s=self.Description
        for k in self.Pins.keys():
            s+='\t'+str(k).ljust(TAB)+self.getpin(k)+'\n'
        return "%s\t%s %s\n%s"%(self.Address,self.Name,self.Extra,s)

    def __eq__(self,other):

        "Compare blocks, return True or False\n \
        block_obj1==block_obj2"

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
        rest of the elements added as list or tuple\n \
        block_obj+=('pin',pin_value)\n \
        block_obj=block_obj+('pin',pin_value)\n \
        block_obj+=('pin',(pin_value1,pin_value2,..)) "

        if isinstance(values,tuple) or isinstance(values,list):
            if len(values)>3:
                tmp=values[1:]
                self.addpin(values[0],tmp)
            if len(values)==2:
                self.addpin(values[0],values[1])
        else:
            print('...second operand must be a list or tuple')
        return self

    def __cmp(self,other):

        "Compare blocks, return difference report\n \
        (block_obj1.compare(block_obj2))"

        flag=False # in future could be used to switch comarision logic
        s=''
        if isinstance(other,block):
            if self==other:
                return s
        slist=list(self.Pins.keys())
        olist=list(other.Pins.keys())
        
        if self.Name!=other.Name:
            s+='\t'+' '*TAB+self.Name.ljust(TAB)+NEQ+other.Name.rjust(TAB)+'\n'
            flag=True
        if self.Extra!=other.Extra:
            s+='\t'+' '*TAB+self.Extra.ljust(TAB)+NEQ+other.Extra.rjust(TAB)+'\n'
            flag=True
        if self.Description!=other.Description:
            s+='\t'+' '*TAB+self.Description.ljust(TAB)+NEok+other.Description.rjust(TAB)+'\n'
            flag=True
      # compare pins
        for k in slist:
            if k in olist: # pin defined in both logic blocks
                if self.Pins[k]!=other.Pins[k]: # check if pin is a number and compare as numbers
                    flag=True
                    if isnum(self.Pins[k]) and isnum(other.Pins[k]):
                        if float(trimd(self.Pins[k]))==float(trimd(other.Pins[k])):
                            continue
                    zipns=zipins(self.Pins[k],other.Pins[k])
                    stmp=str(self.Pins[k]).ljust(TAB)+NEQ+str(other.Pins[k]).rjust(TAB)+'\n'
                    if zipns!=None:
                        stmp=''
                        for z in zipns:
                            if z[0]!=z[1]:
                                stmp+='\t'+' '*TAB+str(z[0]).ljust(TAB)+NEQ+ \
                                    str(z[1]).rjust(TAB)+'\n'
                            else:
                                stmp+='\t'+' '*TAB+str(z[0]).ljust(TAB)+NEok+ \
                                    str(z[1]).rjust(TAB)+'\n' 
                    s+='\t'+str(k).ljust(TAB)+stmp.lstrip()
                        
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
            s='\n'+self.Address+'\t'+self.Name+'\n'+s
        return s    
    compare=__cmp

    def allpins(self):
        return self.Pins.keys()

#------------------------------------------------------------------------------

class AAX:


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

        # open aax file
        try:
            file=open(self.fName,'r')
            self.Lines=file.readlines() #read aax file to Lines
            file.close()
        except:
            print('...error reading file: ...'+self.fName[nSPC:])
            return

        self.aaxparse()
    
    def aaxparse(self):
        
        status=0 # used for parsing
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
                # start of the logic block status=1 get address, name and params
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
                    self.Blocks[address]=block(address,BlockName,extra) # create dbinstance block obj
                    continue
                # try read block name if exist
                if status==1 and word[0]=='INAME':
                    if elcnt>1:
                        st=''
                        for e in word[1:]:
                            st+=e
                        self.Blocks[address].Description=st
                    continue # go to the next line
                # read pins
                if status==1 and word[0][:1]==':': # start of the pin definition
                    PinName=word[0]# get pin NAME
                    if elcnt==1:
                        pinval=NONE #empty pin
                        continue  # go to the next line                
                    
                    if elcnt>=2: # if there are spaces in the pin value
                        st=''
                        for e in word[1:]:
                            st+=e+'' # put all back in to one string
                        pinval=st

                    if pinval[-1:]==',':# another value at the next line
                        status=2 #  pin values occupy several lines
                        lpinval.append(pinval[:-1])
                        continue # go to the next line
                    else:
                        self.Blocks[address].addpin(PinName,pinval) # last value for the pin
                        status=1
                        continue # go to the next line
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
                        lpinval.sort()
                        self.Blocks[address].addpin(PinName,lpinval) # add list to the pin
                        lpinval=[]
                        status=1
                      

    def getlabels(self):
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

    def countblocks(self,BlockName='dummy'):
        "Count entries of the logic block\n \
        print number of DIC: print(BAX_obj.countblocks('DIC'))\n \
        print number of MOVE: print(AAX_obj.contblocks('MOVE'))"
        counter=0
        for ad in self.Blocks.keys():
            if self.Blocks[ad].Name==BlockName:
                counter+=1
        return counter

    def averagepins(self,BlockName='dummy'):
        "Return average number of pins for given block type"
        pcnt=0
        bcnt=0
        for ad in self.Blocks.keys():
            if self.Blocks[ad].Name==BlockName:
                bcnt+=1
                pcnt+=len(self.Blocks[ad].Pins)
        if bcnt==0: # stop div by 0
            bcnt=1
        return round(pcnt/bcnt,1)

    def keysaround(self,key):
        " return tuple of the previous key and next key "
        keys=tuple(self.Blocks.keys())
        key_ind=keys.index(key)
        if key_ind==0:
            k1=0
            k2=keys[key_ind+1]
        elif key_ind==len(keys)-1:
            k1=keys[key_ind-1]
            k2=0
        else:
            k1=keys[key_ind-1]
            k2=keys[key_ind+1]
        return (k1,k2)

    def cref(self,tag='dummy'):
        "Cross referense search for the tag_name\n \
        return tuple of addresses where it was found.\n \
        Use cref(NONE) to search for unconnected pins\n \
        To print all blocks out use as shown below\n \
        for a in f.cref('tag_name'):\n \
            print(f.Blocks[a[:a.index(':')]])\n "
        out=()
        for addr in self.Blocks:
            for pin in self.Blocks[addr].Pins:
                pinval=self.Blocks[addr].getpin(pin)
                if tag in pinval:
                    out+=(str(addr)+str(pin),)
        return out

    def allblocks(self):
        "Return list of the blocks (keys)\n \
        list_of_blocks=BAXorAAX_obj.allblocks()"
        return self.Blocks.keys()

    def getblock(self,blkey=''):
        "Return block by name\n \
        dbinst=BAX_obj.getblock('DIC101')\n \
        pcinst=AAX_obj.getblock('PC23.12.1.3')"
        if blkey in self.allblocks():
            return self.Blocks[blkey]
        else:
            return NONE

    def getrevision(self):
        "Return revision number"
        k='rev_ind'
        if k in self.Header.keys():
            return self.Header[k].strip()
        else:
            return NEX

    def __cmp(self,other):
        "Compare AAX files and return text report\n \
        print(AAX_obj1.compare(AAX_obj2))"
        s=''
        if isinstance(other,AAX):
            skeys=self.Blocks.keys()
            okeys=other.Blocks.keys()
            if self.Header!=other.Header:
                s+='\nConflict at the HEADER:'
                for k in HEADER:
                    if k in other.Header and k in self.Header:
                        if self.Header[k]!=other.Header[k]:
                            s+='\n\t'+str(k).ljust(TAB)+ \
                                str(self.Header[k]).ljust(TAB)+NEok+ \
                                str(other.Header[k]).rjust(TAB)
            s+='\n'
            if len(skeys)!=len(okeys):
                s+='\nNumers of logic statements are different\n \
                    at ..%s =%d\n \
                    at ..%s =%d\n'% \
                    (self.fName[nSPC:],len(self.Blocks.keys()),other.fName[nSPC:],len(other.Blocks.keys()))
            for key in self.Blocks.keys():
                if key in other.Blocks.keys():
                    if self.Blocks[key]!=other.Blocks[key]:
                        s+=str(self.Blocks[key].compare(other.Blocks[key]))
                    if self.keysaround(key)!=other.keysaround(key):
                        ksA,ksB=self.keysaround(key)
                        koA,koB=other.keysaround(key)
                        if ksA!=koA and ksB!=koB:
                            s+=str("\nMisplaced statement %s\n"%key)
                else:
                    s+='\nstatement %s not found at ..%s but exist at ..%s\n'% \
                        (key,other.fName[nSPC:],self.fName[nSPC:])+str(self.Blocks[key])
            for key in other.Blocks.keys():
                if key not in self.Blocks.keys():
                    s+='\nstatement %s not found at ..%s but exist at ..%s\n'% \
                        (key,self.fName[nSPC:],other.fName[nSPC:])+str(other.Blocks[key])
        return s
    compare=__cmp
    
#------------------------------------------------------------------------------

class BAX(AAX):

    def __init__(self,fname):

        "Constructor, create BAX file instance, parse AMPL logic\n \
        Blocks: contains all instances from BAX file\n \
        fName: full path to AMPL bax file including file name\n \
        Lines: text lines from AMPL file\n \
        Header: AMPL code header\n \
        Labels: all labels with addresses in the AMPL code"

        self.Blocks={} # database elements (blocks)
        self.fName=fname # bax file NAME
        self.Lines=None # lines collection from bax file
        self.Header={} # aax header
        self.Labels={} # strore labels
        #open bax file
        try:
            file=open(self.fName,'r')
            self.Lines=file.readlines() #read bax file to Lines
            file.close()
        except:
            print('...error reading file: ...'+self.fName[nSPC:])
            return
        self.baxparse()


    def baxparse(self):
        address='' # database instance unique value
        BlockName='' # type of the block  or  pin name
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
                #get address, name and params
                if word[0][:1]!=':' and \
                word[0]!='BEGIN' and word[0]!='END' and word[0]!='(':
                    address=word[0] # get address (Instance name)
                    if len(word)>=2:
                        BlockName=''
                        for w in word[1:]:
                            BlockName=BlockName+w
                    self.Blocks[address]=block(address,BlockName,extra='') # create logic block obj
                    continue
                # read pins
                if word[0][:1]==':': # start of the pin definition
                    PinName=word[0]# get pin NAME
                    if elcnt>=2: # if there are spaces in the pin value
                        st=''
                        for e in word[1:]:
                            st+=e+'' # put all back in to one string
                        pinval=st
                    if elcnt==1:
                        pinval=NONE #empty pin
                    self.Blocks[address].addpin(PinName,pinval) # last value for the pin
                     

                        
    def __cmp(self,other):
        "Compare BAX files and return text report"
        s=''
        if isinstance(other,AAX):
            skeys=self.Blocks.keys()
            okeys=other.Blocks.keys()
            if self.Header!=other.Header:
                s+='\nConflict at the HEADER:'
                for k in HEADER:
                    if k in other.Header and k in self.Header:
                        if self.Header[k]!=other.Header[k]:
                            s+='\n\t'+str(k).ljust(TAB)+ \
                            str(self.Header[k]).ljust(TAB)+NEok+ \
                            str(other.Header[k]).rjust(TAB)
            s+='\n'
            if len(skeys)!=len(okeys):
                s+='\nNumers of db instances are different\n \
                at ..%s =%d\n \
                at ..%s =%d\n'% \
                (self.fName[nSPC:],len(self.Blocks.keys()),other.fName[nSPC:],len(other.Blocks.keys()))
            for key in self.Blocks.keys():
                if key in other.Blocks.keys():
                    if self.Blocks[key]!=other.Blocks[key]:
                        s+=str(self.Blocks[key].compare(other.Blocks[key]))
                    if self.keysaround(key)!=other.keysaround(key):
                        ksA,ksB=self.keysaround(key)
                        koA,koB=other.keysaround(key)
                        if ksA!=koA and ksB!=koB:
                            s+=str("\nMisplaced db instance %s\n"%key)                    
                else:
                    s+='\ninstance %s not found at ..%s but exist at ..%s\n'% \
                    (key,other.fName[nSPC:],self.fName[nSPC:])+str(self.Blocks[key])
            for key in other.Blocks.keys():
                if key not in self.Blocks.keys():
                    s+='\ninstance %s not found at ..%s but exist at ..%s\n'% \
                    (key,self.fName[nSPC:],other.fName[nSPC:])+str(other.Blocks[key])
        return s
    compare=__cmp


class AA(AAX):
    '''
    read (decode) AA file to self.Lines
    '''
    SPC=0x80
    def __init__(self, fname):
        
        self.Blocks={} # logic elements (blocks)
        self.fName=fname # aax file NAME
        self.Lines=None # lines collection from aax file
        self.Header={} # aax header
        self.Labels={} # strore labels {"PC##.##.##":label}

        tmpline=''
        self.Lines=[]
        self.fName=fname
        with open(fname,'rb') as aafile:
            b=aafile.read(1)
            bip=0x00 # hold previous bit int value
            while b:
                bi=int.from_bytes(b,'big') # convert byte to int
                if bi>self.SPC: # check if it is compacted spaces
                    # add spaces?
                    nofSPC=bi-self.SPC # calculate number of the spaces
                    tmpline+=' '*nofSPC #add spaces to the line
                    pass
                if bi>=0x20 and bi<=0x7F and bip!=0x00: # ASCII symbol add as it is
                    tmpline+=b.decode()
                    pass
                #if bi<0x20 and bip==0x00:
                #    pass
                if bi==0x00 and bip>0x00:
                    # new line add
                    # append self.Lines
                    self.Lines.append(tmpline)
                    tmpline=''
                    pass
                bip=bi
                b=aafile.read(1)
            pass
        self.aaxparse()
    
