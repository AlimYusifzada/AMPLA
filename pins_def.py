from ampla import *
if __name__=='__main__':
    print("this is extension of AMPLA","rev:%s"%ampla_rev)
    exit()

import warnings
from pathlib import Path
import threading as trd

#list of sink/source
Sources=[] # upstrean connections
Sinks=[] # downstream connections

DeadSources=[] # untraceble sources, dead end
DeadSinks=[] # untraceble sinks, dead end

Items=[] #database entries or other non-adress item

SRCE={} # contain PC programs dict like "PC_program_name":<class AA>  

def ReadSRCE(path):
    '''
    read all PC programs source code from the path
    and populate PCprograms dictionary
    initiate parsing as different thread for each file
    '''
    dib=""
    if type(path) is not str:
        return
    
    def read_source(dib):
        bn=os.path.basename(dib)
        is_AAX=str(dib)[-2:].upper()=="AX"
        is_AA=str(dib)[-2:].upper()=="AA"
        srcfile=str(dib) #get the filename (full path)
        if is_AAX:
            pc=AAX(srcfile)
        elif is_AA:
            pc=AA(srcfile)
        else:
            warnings.warn("uncknown source")
            return
        SRCE[bn[:bn.index('.')]]=pc

    try:
        for dib in Path(path).iterdir():
            if dib.is_file():
                trd.Thread(target=read_source(dib)).start()
    except:
        warnings.warn("cant read file %s"%(dib))


def SearchSRCE(item)->tuple:
    '''
    search item in PCprograms
    return tuple with addresses where item was found
    '''
    output=()
    if type(item) is str:
        for pc in SRCE:
            output=output+SRCE[pc].xRef(item)
    else:
        warnings.warn("incorrect type @ SearchSRCE")
    return output

def is_dbinst(val)->bool:
    if type(val) is str:
        if val[:1]=='=' or val[:2]=='-=':
            return True
    else:
        warnings.warn("incorrect type @ is_dbinst")
    return False

def is_inverted(val)->bool:
    if type(val) is str:
        if val[0]=='-':
            return True
    else:
        warnings.warn("incorrect type @ is_inverted")
    return False

def is_address(val)->bool:
    '''
    check if the val is an address (starts with PC..)
    '''
    if type(val) is str:
        if val[:2]=='PC'or val[:3]=='-PC':
            return True
    else:
        warnings.warn("incorrect type @ is_address")
    return False

def is_pointer(val)->bool:
    '''
    check if the val is and address and pointing to a pin
    '''
    if type(val) is str:
        if is_address(val):
            if ':' in val:
                return True
    else:
        warnings.warn("incorrect type @ is_pointer")
    return False

def is_input(blk,pin)->bool:
    '''
    check if pin is input
    '''
    if type(blk) is block and type(pin) is str:
        if blk.Name in InputPins:
            for p in InputPins[blk.Name]:
                if p==pin:
                    return True
    else:
        warnings.warn("incorrect type @ is_input")
    return False

def is_output(blk,pin)->bool:
    '''
    check if pin is output
    '''
    if type(blk) is block and type(pin) is str:
        if blk.Name in OutputPins:
            for p in OutputPins[blk.Name]:
                if p==pin:
                    return True
    else:
        warnings.warn("incorrect type @ is_output")
    return False

def is_loop(blk,pin)->bool:
    if type(blk) is block and type(pin) is str:
        pval=GetPinValue(blk,pin)
        for v in pval:
            if is_address(v):
                if GetAddrPin(v)[0]==blk.Address:
                    return True
    else:
        warnings.warn("incorrect type @ is_loop")
    return False

def gen_pins(start,stop)->tuple:
    '''
    generate series of pins names
    '''
    T=()
    for i in range(start,stop+1):
        T=T+(':'+str(i),)
    return T

def GetPCName(path)->str:
    if is_address(path):
        return str.removeprefix(path,'-')[:path.find('.')]
    else:
        warnings.warn("incorrect type @ GetPCName")
    return path

def GetBlockName(aax,path)->str:
    '''
    return block name at path
    '''
    if type(aax) is AAX or type(aax) is AA and type(path) is str:
        if GetAddrPin(path)[0] in aax.Blocks:
            return aax.Blocks[GetAddrPin(path)[0]].Name
    else:
        warnings.warn("incorrect type @ GetBlockName")
    return ''

def GetBlock(aax,path)->block:
    '''
    return block by address or path from aax
    '''
    if path[0]=='-':# dont need inversion.
        path=path[1:] 
    if type(aax) is AAX or type(aax) is AA and is_pointer(path):
        return aax.Blocks[GetAddrPin(path)[0]]
    if type(aax) is AAX or type(aax) is AA and is_address(path):
        return aax.Blocks[path]
    warnings.warn("incorrect type @ GetBlock")
    return None

def GetAddrPin(path)->tuple:
    '''
    return tuple (address, pin) // (str,str)
    '''
    if type(path) is str:
        if is_pointer(path):
            return (path[:path.find(':')],path[path.find(':'):])
        if is_address(path):
            return (path,)
    else:
        warnings.warn("incorrect type @ GetAddrPin")
    return ()

def GetPinValue(blk,pin):
    '''
    return value (str or list) of the <path> PC##.##.##:pin
    <aax> logic blocks container
    '''
    if type(blk) is block and type(pin) is str:
        if pin in blk.Pins:
            tp=type(blk.Pins[pin])
            if tp is list or tp is tuple:
                return blk.Pins[pin]
            else:
                return (blk.Pins[pin],)
    else:
        warnings.warn("incorrect type @ GetPinValue")
    return ()

def GetOutput(blk,pin)->tuple:
    '''
    return tuple of possible output pin(s)
    given pin should be input
    '''
    if type(blk) is not block or type(pin) is not str:
        warnings.warn("incorrect type @ GetOutput")
        return ()
    if not is_input(blk,pin):
        warnings.warn("incorrect type @ GetOutput")
        return () # return empty tuple if pin is output
    
    match blk.Name:
        case "MOVE":
            return (blk.Address+':'+str(int(pin[pin.find(':')+1:])+20),)
        # blocks below have only one output pin
        case "OR":
            return (blk.Address+':20',)
        case "AND":
            return (blk.Address+':20',)
        case "MUL":
            return (blk.Address+':20',)
        case "ADD":
            return (blk.Address+':20',)
        case "DIV":
            return (blk.Address+':20',)
        case "SUB":
            return (blk.Address+':20',)
        # expand for other blocks
    warnings.warn("block type not found @ GetOutput")
    return ()

def GetInput(blk,pin)->tuple:
    '''
    return tuple of possible input pin(s)
    given pin should be output pin
    '''
    if type(blk) is not block or type(pin) is not str:
        warnings.warn("incorrect type @ GetInput")
        return ()
    if not is_output(blk,pin):
        warnings.warn("incorrect type @ GetInput")
        return ()
    #----------------------------    
    def gtinp(blk,maxp):
        # get all inputs pins before maxp for blocks like
        # ADD, AND, OR, MUL
        inputs=()
        for p in blk.GetPins():
            if int(p[pin.find(':')+1:])<maxp:
                inputs=inputs+(blk.Address+p,)
        return inputs
    #----------------------------    
    match blk.Name:
        case "MOVE":
            return (blk.Address+':'+str(int(pin[pin.find(':')+1:])-20),)
        case "OR":
            return gtinp(blk,20)
        case "AND":
            return gtinp(blk,20)
        case "MUL":
            return gtinp(blk,20)
        case "ADD":
            return gtinp(blk,20)
        case "DIV":
            return gtinp(blk,20)
        case "SUB":
            return gtinp(blk,20)
        case "OR-A":
            return gtinp(blk,20)
    warnings.warn("block type not found @ GetInput")
    return ()

def ProcessSources(aax):
    '''
    iterate trough the Sources list
    '''
    if type(aax) is not AAX or type(aax) is not AA:
        warnings.warn("incorrect type @ ProcessSources")
        return
    while len(Sources)>0:
        src=Sources.pop(0)
        if is_inverted(src):
            src=src[1:]
        if is_pointer(src) and src:
            blk=GetBlock(aax,src)
            pin=GetAddrPin(src)[1]
            if is_loop(blk,pin):
                DeadSources.append(src) 
            elif is_input(blk,pin):
                val=GetPinValue(blk,pin) # empty pins need to be processed
                for v in val:
                    Sources.append(v)
            elif is_output(blk,pin):
                for v in GetInput(blk,pin):
                    Sources.append(v)
            else:
                DeadSources.append(src)  
        else:
            DeadSources.append(src)
    return
                   
def ProcessSinks(aax):
    '''
    iterate trough the Sink list
    '''
    if type(aax) is not AAX or type(aax) is not AA:
        warnings.warn("incorrect type @ ProcessSinks")
        return
    while len(Sinks)>0:
        snk=Sinks.pop(0) # get the top one
        if is_inverted(snk):
            snk=snk[1:] # remove invertion
        if is_pointer(snk) and snk:
            blk=GetBlock(aax,snk) # shell check if block exist?
            pin=GetAddrPin(snk)[1] # extract pin name
            if is_output(blk,pin): # check if the pin is output
                xrefpin=aax.xRef(snk) # search usage of the pin
                for v in xrefpin:
                    if not is_loop(blk,pin):
                        Sinks.append(v) #add usage points to Sinks
                val=GetPinValue(blk,pin)
                for v in val:
                    if not is_loop(blk,pin):
                        Sinks.append(v) # push at te end
            elif is_input(blk,pin) and GetOutput(blk,pin):
                for v in GetOutput(blk,pin):
                    if not is_loop(blk,pin):
                        Sinks.append(v) # push at the end
            else:
                DeadSinks.append(snk)  
        else:
            DeadSinks.append(snk)
    return

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
    "OR-A":gen_pins(11,59),
    "ABS":(":1",":2"),
    "ADD-MR":gen_pins(1,49),
    "ADD-MR1":gen_pins(1,94),
    "ANALYSE":(":1",":2",":11",":21",":31"),
    "BLOCK":(":1",),
    "COM-AIS":(":1",":2",":3",":4",":5",":6",":21",":23",":24"),
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
    "I-AND":(":20",),
    "IOR":(":20",),
    "INOT":(":5",),
    "BTST":(":5",),
    "ABS":(":5",),
    "ADD-MR":(":50",),
    "ADD-MR1":(":95",),
    "AND-O":(":60",),
    "OR-A":(":60",),
    "DB-COP":(":8",":9"),
    "FI-VOTE":gen_pins(80,93),
    "GI-VOTE":gen_pins(80,93),
    "CE-OPC":(":5",":21"),
    "CE-MATR":(),
    "ABS":(":5",),
    "ADD-MR":(":50",),
    "ADD-MR1":(":95",),
    "ANALYSE":(":5",":6",":7",":8",":12",":22",":32"),
    "BLOCK":(":5",),
    "COM-AIS":(":7",":8",":9",":10",":11",":22",":25",":33",":36"),

}