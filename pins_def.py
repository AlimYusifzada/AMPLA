from ampla import *
import warnings
import threading as trd

if __name__=='__main__':
    print("this is extension to ampla.py","rev:%s"%ampla_rev)
    exit()

# from pathlib import Path
# import threading as trd

# list of sink/source
Sources=[] # upstrean connections
Sinks=[] # downstream connections
Items=[] # database entries or other non-adress items
DeadSources=[] # untraceble sources, dead end
DeadSinks=[] # untraceble sinks, dead end

def is_input(blk,pin)->bool:
    '''
    check if pin is input
    need InputPins dictionary
    '''
    if type(blk) is block and type(pin) is str:
        if blk.Name in InputPins:
            for p in InputPins[blk.Name]:
                if p==pin:
                    return True
    else:
        warnings.warn("incorrect type @is_input(%s,%s)"%(type(blk),type(pin)),stacklevel=2)
    return False

def is_output(blk,pin)->bool:
    '''
    check if pin is output
    need OutputPins dictionary
    '''
    if type(blk) is block and type(pin) is str:
        if blk.Name in OutputPins:
            for p in OutputPins[blk.Name]:
                if p==pin:
                    return True
    else:
        warnings.warn("incorrect type @is_output(%s,%s)"%(type(blk),type(pin)),stacklevel=2)
    return False

def gen_pins(start=1,stop=2,mode='1')->tuple:
    '''
    generate series of pins names
    
    mode=1 gen pins in series between start and stop (1,2,3,...)
    
    mode=SW-C_in gen pins from 11 till stop
    in case stop = 30
    generate (11,12,21,22,31,32)

    mode=SW-C_out gen pins from 13 till stop+3 where stop is deciaml
    in case stop = 40
    generate (13,23,33,43)

    mode=SW_in
    generate inputs (11,21,31,41)

    mode=SW_out
    generate outputs (12,22,32,42)

    mode="Ox"
    generate outputs (O1,O2,...Ox) s=stop
    '''
    T=()
    if stop<=start:
        stop=start
        start=1
    match mode:
        case '1':
            for i in range(start,stop+1):
                T=T+(':'+str(i),)
        case "SW-C_in": #SW-C inputs
            for i in range(1,int(stop+1)):
                T=T+(':'+str(i*10+1),':'+str(i*10+2))
        case "SW-C_out": #SW-C outputs
            for i in range(1,int(stop+1)):
                T=T+(':'+str(i*10+3),)
        case "SW_in":
            for i in range(1,int(stop+1)):
                T=T+(':'+str(i*10+1),)
        case "SW_out":
            for i in range(1,int(stop+1)):
                T=T+(":"+str(i*10+2),)
        case "Ox":
            for i in range(1,int(stop+1)):
                T=T+(":O"+str(i),)
    return T

def get_output_for(blk,pin)->tuple:
    '''
    return tuple of possible output pin(s)
    given pin should be input
    '''
    def getall():
        res=()
        for p in OutputPins[blk.Name]:
            res+=(blk.Address+p,)
        return res
    
    if type(blk) is not block or type(pin) is not str:
        warnings.warn("incorrect type @GetOutput(%s,%s)"%(type(blk),type(pin)))
        return ()
    if not is_input(blk,pin):
        warnings.warn("%s should be an input @GetOutput"%pin)
        return () # return empty tuple if pin is output
    match blk.Name:
        case "MOVE":
            return (blk.Address+':'+str(int(pin[pin.find(':')+1:])+20),)
        # blocks below have only one output pin
        case "OR-C":
            if pin==":ACT":
                return getall()
            else:
                return (blk.Address+':'+pin[1]+'3')
        case _:
            return getall()

        # expand for other blocks
    # warnings.warn("block type:%s not found @GetOutput"%blk.Name)
    return ()

def get_input_for(blk,pin)->tuple:
    '''
    return tuple of possible input pin(s)
    given pin should be output pin
    '''
    def getall():
        res=()
        for p in InputPins[blk.Name]:
            res+=(blk.Address+p,)
        return res
    
    if type(blk) is not block or type(pin) is not str:
        warnings.warn("incorrect type @GetInput(%s,%s)"%(type(blk),type(pin)))
        return ()
    if not is_output(blk,pin):
        warnings.warn("%s should be an output @GetInput"%pin)
        return ()    
    match blk.Name:
        case "MOVE":
            return (blk.Address+':'+str(int(pin[pin.find(':')+1:])-20),)
        case "OR-C":
            return (blk.Address+':'+pin[1]+'1',blk.Address+':'+pin[1]+'2',)
        case _:
            return getall()
    # warnings.warn("block type:%s not found @GetInput"%blk.Name)
    return ()

def get_source(aax,source:list)->list:
    '''
    iterate trough the Sources list
    multythreading!!!
    '''
    # if type(aax) is not AAX or type(aax) is not AA:
    #     warnings.warn("incorrect type @ProcessSources(%s)"%type(aax))
    #     return
    deadsources=[]
    processed=[]
    def innerfunc(source,srcn):
        if is_inverted(srcn):
            srcn=srcn[1:] # remove inversion
        if is_pointer(srcn): # check if it is address with pin (pointer)
            blk=get_block(aax,srcn) #get block object
            pin=get_addr_pin(srcn)[1] #getpin name
            if is_loop(blk,pin): #if it's link to itself - just warn
                warnings.warn("loop detected @%s"%srcn) 
            elif is_input(blk,pin): #check if the pin is input for the block
                for v in get_pin_value(blk,pin): #it should be only one value but...
                    source.append(v)
            elif is_output(blk,pin):
                for v in get_input_for(blk,pin):
                    source.append(v)
            else:
                if srcn not in deadsources:
                    deadsources.append(srcn)
        else:
            if srcn not in deadsources: #check if it's already there
                deadsources.append(srcn) #add to the deads list
        pass

    while len(source)>0:
        src=source.pop(0) # get the first element
        if src not in processed:
            processed.append(src)
            trd.Thread(target=innerfunc(source,src),name=src)
    return deadsources
                   
def get_sink(aax,sink:list)->list:
    '''
    iterate trough the Sink list
    multythreading!!!
    '''
    # if (type(aax) is not AAX) or (type(aax) is not AA):
    #     warnings.warn("incorrect type @ProcessSinks(%s)"%type(aax))
    #     return
    deadsinks=[]
    processed=[]
    def innerfunc(sink,snkn):
        if is_inverted(snkn):
            snkn=snkn[1:] # remove invertion
        if is_pointer(snkn): # check not database
            blk=get_block(aax,snkn) # shell check if block exist?
            pin=get_addr_pin(snkn)[1] # extract pin name
            if is_output(blk,pin): # check if the pin is output
                xrefpin=aax.xRef(snkn) # search usage of the pin
                for v in xrefpin:
                    if not is_loop(blk,pin):
                        sink.append(v) #add usage points to Sinks
                val=get_pin_value(blk,pin)
                for v in val:
                    if not is_loop(blk,pin):
                        sink.append(v)
            elif is_input(blk,pin):
                for v in get_output_for(blk,pin):
                    if not is_loop(blk,pin):
                        sink.append(v) # push at the end
            else:
                if snkn not in deadsinks:
                    deadsinks.append(snkn)  
        else:
            if snkn not in deadsinks:
                deadsinks.append(snkn)
   
    while len(sink)>0:
        snk=sink.pop(0)
        if snk not in processed:
            processed.append(snk)
            trd.Thread(target=innerfunc(sink,snk),name=snk)
    return deadsinks

def check_block_dict():
    
    for ky in InputPins.keys():
        if ky in OutputPins.keys():
            pass
        else:
            warnings.warn("%s\t/-> OutputPins"%ky)
   
    for ky in OutputPins.keys():
        if ky in InputPins.keys():
            pass
        else:
            warnings.warn("%s\t/-> InputPins"%ky)

def get_max(stat)->tuple:
    max=('dummy',0)
    for k in stat:
        if stat[k]>max[1]:
            max=(k,stat[k])
    return max

def get_sorted(stat)->tuple:
    res=()
    while len(stat)>0:
        i=get_max(stat)
        res+=(i,)
        stat.pop(i[0])
    return res

def get_stat(prj)->dict:
    '''
    statistical data
    logic blocks frequency
    '''
    stat={}
    for aax in prj.SRCE.keys():
        for blk in prj.SRCE[aax].Blocks.keys():
            blknme=get_block_name(prj.SRCE[aax],blk)
            if blknme in stat.keys():
                stat[blknme]+=1
            else:
                stat[blknme]=1
    return stat


# dictionary of tuples!, even single elemets should be stored as tuple
InputPins={
    "BLOCK":(":ON",":1"),
    "MUL":gen_pins(1,19),
    "MOVE":gen_pins(1,19),
    "MOVE-A":gen_pins(1,19),
    "AND":gen_pins(1,19),
    "OR":gen_pins(1,19),
    "SUB":(":1",":2"),
    "DIV":(":1",":2"),
    "OR-A":gen_pins(1,59),
    "ABS":(":1",":2",":I",":K"),
    "ADD-MR":gen_pins(1,49),
    "ADD-MR1":gen_pins(1,94),
    "ANALYSE":(":1",":2",":11",":21",":31",":MPLDH1",":HYS",":CLDH1",":CLDH2",":CLDH3"),
    "BLOCK":(":1",),
    "COM-AIS":(":1",":2",":3",":4",":5",":6",":21",":23",":24"),
    "ADD":gen_pins(1,19),
    "AND-O": gen_pins(1,59),
    "MONO": (":1",":2",":3",":I",":TP"),
    "SW":(":ACT",":1")+gen_pins(9,mode="SW_in"),#calculate
    "SW-C":(":ACT",":1")+gen_pins(9,mode="SW-C_in"),#calculate
    "COMP":(":I1",":I2",":1",":2"),
    "COMP-I":(":I1",":I2",":1",":2"),
    "CONTRM":(":ON",":1",":SINGLE",":2",":R",":3"),
    "CONV":(":I",":1"),
    "CONV-AI":(":1",":BA_1",":2","::BA_2",":3","::BA_3",":4","::BA_4"),
    "TON":(":I",":TD",":1",":2"),
    "TOFF":(":I",":TD",":1",":2"),
    "COUNT":(":L",":U/D-N",":C",":R",":EN",":21",":I")+gen_pins(1,5),
    "CONV-IB":(":S",":L",":R",":I",":1",":2",":3",":10"),
    "MONO":(":RTG",":I",":TP",":1",":2",":3"),
    "TRIGG":(":1"),
    
    }

# dictionary of tuples!, even single elemets should be stored as tuple
OutputPins={
    "BLOCK":(":RUN",":5"),
    "MUL":(":20",),
    "SUB":(":20",),
    "DIV":(":20",),
    "MOVE":gen_pins(21,39),
    "MOVE-A":gen_pins(21,39),
    "AND":(":20",),
    "OR":(":20",),
    "ADD":(":20",),
    "ABS":(":5",":O"),
    "ADD-MR":(":50",),
    "ADD-MR1":(":95",),
    "AND-O":(":60",),
    "OR-A":(":60",),
    "ABS":(":5",),
    "ADD-MR":(":50",),
    "ADD-MR1":(":95",),
    "ANALYSE":(":5",":6",":7",":8",":12",":22",":32",":MPLD",":OVERLD",":MPLD>H1",":CLD",":CLD>H1",":CLD>H2",":CLD>H3"),
    "BLOCK":(":5",),
    "COM-AIS":(":7",":8",":9",":10",":11",":22",":25",":33",":36"),
    "MONO":(":O",":TE",":5",":6"),
    "SW":gen_pins(9,mode="SW_out"),#calculate
    "SW-C":gen_pins(9,mode="SW-C_out"),#calculate
    "COMP":(":I1>I2",":I1=I2",":I1<I2",":5",":6",":7"),
    "COMP-I":(":I1>I2",":I1=I2",":I1<I2",":5",":6",":7"),
    "CONTRM":(":RUN",":5",":MODP",":6"),
    "CONV":(":O",":ERR",":5",":6"),
    "CONV-AI":(":O",":5"),
    "TON":(":O",":5",":TE",":6"),
    "TOFF":(":O",":5",":TE",":6"),
    "COUNT":(":>0",":=0",":<0",":O",":10",":11",":12",":22"),
    "CONV-IB":(":ERR",":SIGN",":ZERO")+gen_pins(start=1,stop=32,mode="Ox"),
    "MONO":(":O",":TE"),
    "TRIGG":(":5"),

}