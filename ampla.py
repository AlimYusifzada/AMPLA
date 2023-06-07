import sys
amplahelp = '''
  Set of functions to compare AA/AAX and BA/BAX files
  generated by Online Builder (ONB) or Function Chart Builder (FCB)
  ONB and FCB are Asea Brown Bowery company products.
  (c) Copyright,2020 Alim Yusifzada
 '''

ampla_rev = '0.230607'

if sys.version_info[0] < 3:
    print('Please use Python version 3.*')
    sys.exit()

if __name__ == '__main__':
    print('\nAMPLA revision:'+ampla_rev)
    input(amplahelp)

NEQ = ' <- ! -> '
NEok = ' <- ok -> '
NEX = 'not exist'
NONE = 'not assigned'
TAB = 30
nSPC = -20


HEADER = ('design_ch', 'tech_ref', 'resp_dept', 'date',
          'l_text1', 'r_text1',
          'l_text2', 'r_text2',
          'l_text3', 'r_text3',
          'l_text4', 'r_text4',
          'rev_ind', 'language')


def trimD(txt):
    '''
    remove D= and return only numbers as a string
    '''
    if txt[:2].upper() == 'D=':
        return txt[2:]
    return txt
def trimIO(txt):
    '''
    replace =DO. or =DI. with =
    required in cases when AA file dumped from controller (DUPCS)
    usually happened with Safeguards
    '''
    vio=("=DO.","=DI.")
    vEQ="="
    for p in vio:
        txt=txt.upper().replace(p,vEQ)
    return txt
def isNum(txt):
    '''
    check if argument a number
    '''
    try:
        float(trimD(txt))
        return True
    except:
        return False


def ziPins(pinAval, pinBval):
    '''
    compare two lists
    shortes append with NEX(not exist) values till they become equal length
    sort them and return as zip
    '''
    flag = False  # revert flag set if A/B values reverted
    # use to keep output A-first B-second
    if type(pinAval) != list and type(pinBval) != list:
        return None
    if type(pinAval) != list:
        pinAval = [pinAval, ]
    if type(pinBval) != list:
        pinBval = [pinBval, ]

    if max(len(pinAval), len(pinBval)) == len(pinAval):
        # select longest and shortest
        xList = pinAval  # longest
        mList = pinBval  # shortest
    else:
        xList = pinBval  # longest
        mList = pinAval  # shortest
        flag = True
    # vdif = len(xList)-len(mList)  # calculate difference in length
    # if vdif > 0:
    #     for i in range(vdif):
    #         mList.append(NEX)
    yList = []
    for rec in xList:
        if rec in mList:
            yList.append(rec)
        else:
            yList.append(NEX)
    for rec in mList:
        if rec in xList:
            pass
        else:
            xList.append(NEX)
            yList.append(rec)
    # xList.sort()
    # mList.sort()
    if flag:
        return zip(yList, xList)
    else:
        return zip(xList, yList)


def readA(fName):
    '''
    read AA or BA file to Lines
    '''
    Lines = []
    tmpline = ''
    SPC = 0x80
    with open(fName, 'rb') as aafile:
        b = aafile.read(1)
        bip = 0x00  # hold previous bit int value
        while b:
            bi = int.from_bytes(b, 'big')  # convert byte to int
            if bi > SPC:  # check if it is compacted spaces
                # add spaces?
                nofSPC = bi-SPC  # calculate number of the spaces
                tmpline += ' '*nofSPC  # add spaces to the line
                pass
            if bi >= 0x20 and bi <= 0x7F and bip != 0x00:  # ASCII symbol add as it is
                tmpline += b.decode()
                pass
            # if bi<0x20 and bip==0x00:
            #    pass
            if bi == 0x00 and bip > 0x00:
                # new line add
                # append self.Lines
                Lines.append(tmpline)
                tmpline = ''
                pass
            bip = bi
            b = aafile.read(1)
    return Lines


class block:
    def __init__(self, address='', name='', extra=''):
        '''
        Constructor, create logic block instance, parent for dbinst
        Pins: contain logic block pins (dictionary keys) and values
        Name: logic block name: MOVE,OR,AND,..
        in case of BAX element used to keep instance type: DIC,AIC..
        Adress (unique): logic block address: PC12.1.1.2
        in case of BAX element used to keep instance name:
        Extra: the logic block parameters: MOVE(B,16)
        in case of BAX element can keep type of DAT: DAT4 (I)
        '''

        self.Pins = {}  # pins (keys) and connections {pin:connection,..}
        self.Name = name  # block NAME or Instance type if DB element
        self.Address = address  # PC##.##.##... or Instance name if DB element
        self.Extra = extra  # everything in the brackets no in use if DB element
        self.Description = ''
        self.LineNumber = 0  # line number at aax file.
        return

    def GetPin(self, pin):
        '''
        Return string value of the pin
        block_obj.GetPin('pin')
        '''
        if pin in self.GetPins():
            return str(self.Pins[pin])
        else:
            return NEX

    def AddPin(self, pin, value):
        '''
        Create a pin with a value
        block_obj.AddPin('pin',pin_value)
        '''
        dPatn="D="
        hcFlag=False
        hcValue=.0

        if pin in self.GetPins():
            print('pin %s already exist' % pin)
            return False
        # analise the values and change if required.
        # hardcoded values MD,D,CD..
        if dPatn in value:# if dPatn in st get it's position
            dPos=value.index(dPatn)+2
            try:
                hcValue=float(value[dPos:])
                hcFlag=True
            except: hcFlag=False
        if hcFlag: self.Pins[pin]=str("D=%.6f"%hcValue)
        else: self.Pins[pin] = value
        return True

    def __str__(self):
        '''
        Text representation of the Block
        print(block_obj) or str(block_obj)
        '''
        s = self.Address+'\t'+self.Name+self.Extra+'\t' + \
            self.Description+" aax.line#"+str(self.LineNumber)+'\n'
        for k in self.GetPins():
            s += '\t'+str(k).ljust(TAB)+self.GetPin(k)+'\n'
        return s

    def __eq__(self, other):
        '''
        Compare blocks, return True or False
        block_obj1==block_obj2
        '''
        if isinstance(other, block):
            if other.Address == self.Address:
                if other.Name == self.Name:
                    if other.Extra == self.Extra:
                        if other.Pins == self.Pins:
                            if other.Description == self.Description:
                                return True
        return False

    def __add__(self, values):
        '''
        "Add new pin with values, first element is pin NAME
        rest of the elements added as list or tuple
        block_obj+=('pin',pin_value)
        block_obj=block_obj+('pin',pin_value)
        block_obj+=('pin',(pin_value1,pin_value2,..))
        '''
        if isinstance(values, tuple) or isinstance(values, list):
            if len(values) > 3:
                tmp = values[1:]
                self.AddPin(values[0], tmp)
            if len(values) == 2:
                self.AddPin(values[0], values[1])
        else:
            print('function operand must be a list or a tuple')
        return self

    def __cmp(self, other):
        '''
        Compare self to other logic block, return difference report
        (block_obj1.compare(block_obj2))
        '''
        flag = False  # used to switch comparision logic - if set difference found
        s = ''  # difference will be asembled here
        if isinstance(other, block):
            if self == other:
                return s
        sPinsList = list(self.GetPins())
        oPinsList = list(other.GetPins())

        if self.Name != other.Name:
            # Logic block names are different (replaced or moved)
            s += '\t'+' '*TAB + \
                self.Name.ljust(TAB)+NEQ+other.Name.rjust(TAB)+'\n'
            flag = True
            '''
            Possible that block was replaced or moved
            old block need to be deleted
            '''

        if self.Extra != other.Extra:
            # Configuartion parameters of the blocks are ifferent
            s += '\t'+' '*TAB + \
                self.Extra.ljust(TAB)+NEQ+other.Extra.rjust(TAB)+'\n'
            flag = True
            '''
            configuration paramenters changed
            it is possible that new change affect the parameters only
            if so the block need to be recreated
            '''

        if self.Description != other.Description:
            # Non critical difference in description found
            s += '\t'+' '*TAB + \
                self.Description.ljust(TAB)+NEok + \
                other.Description.rjust(TAB)+'\n'
            flag = True
            '''
            the description change and could be changed harmlessly
            '''

      # compare pins of the blocks
        for k in sPinsList:
            if k in oPinsList:
                # pin defined in both logic blocks
                if self.Pins[k] != other.Pins[k]:
                    # pin 'k' are not equal
                    flag = True
                    if isNum(self.Pins[k]) and isNum(other.Pins[k]):
                        if float(trimD(self.Pins[k])) == float(trimD(other.Pins[k])):
                            continue
                    zipns = ziPins(self.Pins[k], other.Pins[k])
                    stmp = str(self.Pins[k]).ljust(TAB) + \
                        NEQ+str(other.Pins[k]).rjust(TAB)+'\n'
                    if zipns != None:
                        stmp = ''
                        for z in zipns:
                            if z[0] != z[1]:
                                stmp += '\t'+' '*TAB+str(z[0]).ljust(TAB)+NEQ + \
                                    str(z[1]).rjust(TAB)+'\n'
                                '''
                                pin values dont match
                                '''
                            else:
                                stmp += '\t'+' '*TAB+str(z[0]).ljust(TAB)+NEok + \
                                    str(z[1]).rjust(TAB)+'\n'
                    s += '\t'+str(k).ljust(TAB)+stmp.lstrip()
                    '''
                    call function to add CF code
                    reconnect pins
                    '''

            else:  # pin is not in other block, probably the extra parameters changed
                if self.Pins[k] != NONE:
                    flag = True
                    s += '\t'+str(k).ljust(TAB) + \
                        str(self.Pins[k]).ljust(TAB) + \
                        NEQ+NEX.rjust(TAB)+'\n'
                    '''
                    call function to add CF code
                    recreate(replace) statement with new extra parameters
                    '''

        for k in oPinsList:
            if k not in sPinsList:
                if other.Pins[k] != NONE:
                    flag = True
                    s += '\t'+str(k).ljust(TAB) + \
                        NEX.ljust(TAB) + \
                        NEQ+str(other.Pins[k]).rjust(TAB) + '\n'
                    '''
                    call function to generate CF code
                    '''
        if flag:
            s = '\n'+self.Address+'\t'+self.Name+self.Extra+'\t' + \
                self.Description+"aax.line#"+str(self.LineNumber)+'\n'+s
        return s
    compare = __cmp

    def GetPins(self):
        return self.Pins.keys()

# ------------------------------------------------------------------------------


class AAX:

    def __init__(self, fname):
        '''
        Constructor, create AAX file instance, parse AMPL logic
        Blocks: contains all logic blocks from AAX file
        fName: full path to AMPL aax file including file name
        Lines: text lines from AMPL file
        Header: AMPL code header
        Labels: all labels with addresses in the AMPL code
        '''
        self.Blocks = {}  # logic elements (blocks)
        self.fName = fname  # aax file NAME
        self.Lines = []  # lines collection from aax file
        self.Header = {}  # aax header
        self.Labels = {}  # strore labels {"PC##.##.##":label}
        self.Read()
        self.Parse()

    def Read(self):
        try:
            with open(self.fName, 'r') as file:
                self.Lines = file.readlines()  # read aax file to Lines
        except:
            print('...error reading file: ...'+self.fName[nSPC:])
            return

    def Write(self):
        try:
            with open(self.fName+'.txt', 'w') as file:
                for l in self.Lines:
                    file.write(l+'\n')
        except:
            print("...error while writing to:%s.txt" % self.Lines)

    def Parse(self):
        par_pos = 0  # used for parsing
        linecounter = 0
        '''
        =0 ouside logic block
        =1 inside logic block
        =2 inside block the pin has several connections assignment 
        '''
        Address = ''  # address of the block
        BlockName = ''  # NAME of the block  or  pin
        PinName = ''
        Extra = ''
        PinValue = ''
        PinMulValues = []  # list of the values for multiple connected PINS
        ElementsCounter = 0  # number of elements in the line

        # AMPLE parsing logic from here
        for currentLine in self.Lines:
            linecounter += 1
            LineElements = currentLine.split()  # read line and split by spaces
            # count the elements in the line
            ElementsCounter = len(LineElements)
            if ElementsCounter > 0:
                # reading text from aax file header
                if LineElements[0].lower() in HEADER:
                    ss = ''
                    i = 0
                    for s in LineElements:
                        if i != 0:
                            ss = ss+s+' '
                        i += 1
                    self.Header[LineElements[0].lower()] = ss
                    continue

                # start of the logic block status=1 get address, name and params
                if LineElements[0][:2] == 'PC' and LineElements[0][2:3].isdigit() and par_pos != 2:
                    Address = LineElements[0]  # get address
                    par_pos = 1  # block mark if position ==1 we are inside logic block
                    BlockName = ''
                    Extra = ''
                    if ElementsCounter > 1:
                        BlockName = LineElements[1]  # get blok NAME
                    if ElementsCounter > 2:
                        Extra = LineElements[2]  # get extra params
                    else:
                        if '(' in BlockName:  # no space between block name and extra
                            Extra = BlockName[BlockName.find('('):]
                            BlockName = BlockName[:BlockName.find('(')]
                    # create dbinstance block obj
                    self.Blocks[Address] = block(Address, BlockName, Extra)
                    self.Blocks[Address].LineNumber = linecounter
                    continue  # next line

                # inside block and try read block name if exist
                if par_pos == 1 and LineElements[0] == 'INAME':
                    if ElementsCounter > 1:
                        st = ''
                        for e in LineElements[1:]:
                            st += e
                        self.Blocks[Address].Description = st
                    continue  # go to the next line

                # inside block and read pins
                if par_pos == 1 and LineElements[0][:1] == ':':  # pin found
                    PinName = LineElements[0]  # get pin NAME
                    if ElementsCounter == 1:  # empty pin
                        PinValue = NONE
                        continue  # go to the next line
                    if ElementsCounter >= 2:  # if there are spaces in the pin value
                        st = ''
                        for e in LineElements[1:]:
                            st += e+''  # put all back in to one string
                        PinValue = trimIO(st)
                    if PinValue[-1:] == ',':  # another value at the next line
                        par_pos = 2  # pin values occupy several lines
                        PinMulValues.append(PinValue[:-1])
                        continue  # go to the next line
                    else:
                        self.Blocks[Address].AddPin(
                            PinName, PinValue)  # last value for the pin
                        par_pos = 1
                        continue  # go to the next line

                # if pin has several values
                if par_pos == 2:  # one of the values for the pin - add it to the list

                    if ElementsCounter > 1:  # if there are spaces in the pin value
                        st = ''
                        for e in LineElements:
                            st += e+''  # put all back in to one string
                        PinValue = trimIO(st)
                    else:
                        PinValue = trimIO(LineElements[0])

                    if PinValue[-1:] == ',':  # there are still another value at the next line
                        PinMulValues.append(PinValue[:-1])
                    else:  # this is a last value for the pin
                        PinMulValues.append(PinValue)
                        PinMulValues.sort()
                        self.Blocks[Address].AddPin(
                            PinName, PinMulValues)  # add list to the pin
                        PinMulValues = []
                        par_pos = 1  # finish of multiple values reading

    def GetLabels(self):
        '''
        Populate dictionary 'self.Labels'
        with addresses and labels, then return it as result
        '''
        def getlabel(vx):
            if vx[0:2] == 'N=':  # label found
                return str(addr)+str(pinname)
            else:
                return ''

        for addr in self.Blocks:  # start for each logic block
            for pinname in self.Blocks[addr].Pins:  # for all PINS
                pinval = self.Blocks[addr].Pins[pinname]  # ger pin val
                if type(pinval) == list or type(pinval) == tuple:  # several connections
                    for val in pinval:
                        if type(val) == str:
                            if len(getlabel(val)) > 2:
                                self.Labels[getlabel(val)] = val[2:]
                elif type(pinval) == str:
                    if len(getlabel(pinval)) > 2:
                        self.Labels[getlabel(pinval)] = pinval[2:]
        return self.Labels

    # def countblocks(self, BlockName='dummy'):
    #     '''
    #     Count entries of the logic block
    #     print number of DIC: print(BAX_obj.countblocks('DIC'))
    #     print number of MOVE: print(AAX_obj.contblocks('MOVE'))
    #     '''
    #     counter = 0
    #     for ad in self.Blocks.keys():
    #         if self.Blocks[ad].Name == BlockName:
    #             counter += 1
    #     return counter

    # def averagepins(self, BlockName='dummy'):
    #     '''
    #     Return average number of pins for given block type
    #     '''
    #     pcnt = 0
    #     bcnt = 0
    #     for ad in self.Blocks.keys():
    #         if self.Blocks[ad].Name == BlockName:
    #             bcnt += 1
    #             pcnt += len(self.Blocks[ad].Pins)
    #     if bcnt == 0:  # stop div by 0
    #         bcnt = 1
    #     return round(pcnt/bcnt, 1)

    def BlocksAround(self, key):
        '''
        return tuple of the previous block and next block
        '''
        keys = tuple(self.Blocks.keys())
        key_ind = keys.index(key)
        if key_ind == 0:
            k1 = 0
            k2 = keys[key_ind+1]
        elif key_ind == len(keys)-1:
            k1 = keys[key_ind-1]
            k2 = 0
        else:
            k1 = keys[key_ind-1]
            k2 = keys[key_ind+1]
        return (k1, k2)

    def xRef(self, tag='dummy'):
        '''
        Cross referense search for the tag_name
        return tuple of addresses where it was found.
        Use cref(NONE) to search for unconnected pins
        To print all blocks out use as shown below
        for a in f.cref('tag_name'):
            print(f.Blocks[a[:a.index(':')]])
        '''
        out = ()
        for addr in self.Blocks:
            for pin in self.Blocks[addr].Pins:
                pinval = self.Blocks[addr].getpin(pin)
                if tag in pinval:
                    out += (str(addr)+str(pin),)
        return out

    def GetAllBlocks(self):
        '''
        Return list of the blocks (keys)
        list_of_blocks=BAXorAAX_obj.allblocks()
        '''
        return self.Blocks.keys()

    def GetBlock(self, blkey=''):
        '''
        Return block by name
        dbinst=BAX_obj.getblock('DIC101')
        pcinst=AAX_obj.getblock('PC23.12.1.3')
        '''
        if blkey in self.GetAllBlocks():
            return self.Blocks[blkey]
        else:
            return NONE

    def GetRevision(self):
        '''
        Return revision number
        '''
        k = 'rev_ind'
        if k in self.Header.keys():
            return self.Header[k].strip()
        else:
            return NEX

    def __cmp(self, other):
        '''
        Compare AAX files and return text report
        print(AAX_obj1.compare(AAX_obj2))

        future version will have option to generate CF file
        '''
        s = ''
        if isinstance(other, AAX):
            selfBlocks = self.Blocks.keys()
            otherBlocks = other.Blocks.keys()
            if self.Header != other.Header:
                s += '\nConflict at the HEADER:'
                for k in HEADER:
                    if k in other.Header and k in self.Header:
                        if self.Header[k] != other.Header[k]:
                            s += '\n\t'+str(k).ljust(TAB) + \
                                str(self.Header[k]).ljust(TAB)+NEok + \
                                str(other.Header[k]).rjust(TAB)
                '''
                Put warning to change header manually
                MDT command          
                '''
            s += '\n'
            if len(selfBlocks) != len(otherBlocks):
                s += '\nNumber of logic statements are different\n \
                    at ..%s =%d\n \
                    at ..%s =%d\n' % \
                    (self.fName[nSPC:], len(self.Blocks.keys()),
                     other.fName[nSPC:], len(other.Blocks.keys()))
            for statement in self.Blocks.keys():
                if statement in other.Blocks.keys():
                    if self.Blocks[statement] != other.Blocks[statement]:
                        s += str(self.Blocks[statement].compare(other.Blocks[statement]))
                    if self.BlocksAround(statement) != other.BlocksAround(statement):
                        ksA, ksB = self.BlocksAround(statement)
                        koA, koB = other.BlocksAround(statement)
                        if ksA != koA and ksB != koB:
                            s += str("\nMisplaced statement %s\n" % statement)
                else:
                    # generate DS (Delete Statement ONB command)
                    s += '\nstatement %s not found in (AFTER)..%s but exist in (BEFORE)..%s\n' % \
                        (statement, other.fName[nSPC:],
                         self.fName[nSPC:])+str(self.Blocks[statement])
                    '''
                    call function to generate CF code
                    (delete statement DS)
                    '''
            for statement in other.Blocks.keys():
                if statement not in self.Blocks.keys():
                    # generate IS (Insert Statement ONB command)
                    s += '\nstatement %s not found at (BEFORE)..%s but Exist at (AFTER)..%s\n' % \
                        (statement, self.fName[nSPC:],
                         other.fName[nSPC:])+str(other.Blocks[statement])
                    '''
                    call function to generate CF code
                    (insert statement IS)
                    '''
        return s
    compare = __cmp

# ------------------------------------------------------------------------------


class BAX(AAX):

    def __init__(self, fname):
        '''
        Constructor, create BAX file instance, parse AMPL logic
        Blocks: contains all instances from BAX file
        fName: full path to AMPL bax file including file name
        Lines: text lines from AMPL file
        Header: AMPL code header
        Labels: all labels with addresses in the AMPL code
        '''
        super().__init__(fname)

    def Parse(self):
        Address = ''  # database instance unique value
        BlockName = ''  # type of the block  or  pin name
        PinName = ''
        # Extra = '' # not in use for BAX
        PinValue = ''
        # lpinval = []  # list of the values for multiple connected PINS
        ElementsCounter = 0  # number of elements in the line

        # AMPLE parsing logic from here
        for currentLine in self.Lines:
            lineWords = currentLine.split()  # read line and split by spaces
            ElementsCounter = len(lineWords)  # count the elements in the line
            if ElementsCounter > 0:
                # reading text from aax file header
                if lineWords[0].lower() in HEADER:
                    ss = ''
                    i = 0
                    for s in lineWords:
                        if i != 0:
                            ss = ss+s+' '
                        i += 1
                    self.Header[lineWords[0].lower()] = ss
                    continue
                # get address, name and params
                if lineWords[0][:1] != ':' and \
                        lineWords[0] != 'BEGIN' and lineWords[0] != 'END' and lineWords[0] != '(':
                    Address = lineWords[0]  # get address (Instance name)
                    if len(lineWords) >= 2:
                        BlockName = ''
                        for w in lineWords[1:]:
                            BlockName = BlockName+w
                    self.Blocks[Address] = block(
                        Address, BlockName, extra='')  # create logic block obj
                    continue
                # read pins
                if lineWords[0][:1] == ':':  # start of the pin definition
                    PinName = lineWords[0]  # get pin NAME
                    if ElementsCounter >= 2:  # if there are spaces in the pin value
                        st = ''
                        for e in lineWords[1:]:
                            st += e+''  # put all back in to one string
                        PinValue = st
                    if ElementsCounter == 1:
                        PinValue = NONE  # empty pin
                    self.Blocks[Address].AddPin(
                        PinName, PinValue)  # last value for the pin

    def __cmp(self, other):
        '''
        Compare BAX files and return text report
        '''
        s = ''
        if isinstance(other, AAX):
            skeys = self.Blocks.keys()
            okeys = other.Blocks.keys()
            if self.Header != other.Header:
                s += '\nConflict at the HEADER:'
                for k in HEADER:
                    if k in other.Header and k in self.Header:
                        if self.Header[k] != other.Header[k]:
                            s += '\n\t'+str(k).ljust(TAB) + \
                                str(self.Header[k]).ljust(TAB)+NEok + \
                                str(other.Header[k]).rjust(TAB)
            s += '\n'
            if len(skeys) != len(okeys):
                s += '\nNumers of db instances are different\n \
                at ..%s =%d\n \
                at ..%s =%d\n' % \
                    (self.fName[nSPC:], len(self.Blocks.keys()),
                     other.fName[nSPC:], len(other.Blocks.keys()))
            for key in self.Blocks.keys():
                if key in other.Blocks.keys():
                    if self.Blocks[key] != other.Blocks[key]:
                        s += str(self.Blocks[key].compare(other.Blocks[key]))
                    if self.BlocksAround(key) != other.BlocksAround(key):
                        ksA, ksB = self.BlocksAround(key)
                        koA, koB = other.BlocksAround(key)
                        if ksA != koA and ksB != koB:
                            s += str("\nMisplaced db instance %s\n" % key)
                else:
                    # generate MDB command to spare the instance (do not delete)
                    # topup.bax
                    s += '\ninstance %s not found at (AFTER)..%s but exist at (BEFORE)..%s\n' % \
                        (key, other.fName[nSPC:],
                         self.fName[nSPC:])+str(self.Blocks[key])
            for key in other.Blocks.keys():
                if key not in self.Blocks.keys():
                    # generate command to create new DB instance
                    s += '\ninstance %s not found at (BEFOER)..%s but Exist at (AFETR)..%s\n' % \
                        (key, self.fName[nSPC:],
                         other.fName[nSPC:])+str(other.Blocks[key])
        return s
    compare = __cmp


class AA(AAX):
    '''
    read (decode) AA file to self.Lines
    '''

    def __init__(self, fname):
        super().__init__(fname)

    def Read(self):
        self.Lines = readA(self.fName)
        self.Parse()


class BA(BAX):
    '''
    read BA files and parse using BAX class
    '''

    def __init__(self, fname):
        super().__init__(fname)

    def Read(self):
        self.Lines = readA(self.fName)
        self.Parse()
