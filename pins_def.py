if __name__=='__main__':
    print("this is extension of AMPLA","rev:%s"%ampla_rev)
    exit()

from ampla import *
import warnings
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

def get_output_for(blk,pin)->tuple:
    '''
    return tuple of possible output pin(s)
    given pin should be input
    '''
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
    warnings.warn("block type:%s not found @GetOutput"%blk.Name)
    return ()

def get_input_for(blk,pin)->tuple:
    '''
    return tuple of possible input pin(s)
    given pin should be output pin
    '''
    if type(blk) is not block or type(pin) is not str:
        warnings.warn("incorrect type @GetInput(%s,%s)"%(type(blk),type(pin)))
        return ()
    if not is_output(blk,pin):
        warnings.warn("%s should be an output @GetInput"%pin)
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
    warnings.warn("block type:%s not found @GetInput"%blk.Name)
    return ()

def ProcessSources(aax,source:list)->list:
    '''
    iterate trough the Sources list
    '''
    # if type(aax) is not AAX or type(aax) is not AA:
    #     warnings.warn("incorrect type @ProcessSources(%s)"%type(aax))
    #     return
    deadsources=[]
    while len(source)>0:
        src=source.pop(0)
        if is_inverted(src):
            src=src[1:]
        if is_pointer(src):
            blk=get_block(aax,src)
            pin=get_addr_pin(src)[1]
            if is_loop(blk,pin):
                # deadsources.append(src) 
                # looped link any plans?
                warnings.warn("loop detected @%s"%(src))
                pass
            elif is_input(blk,pin):
                for v in get_pin_value(blk,pin):
                    source.append(v)
            elif is_output(blk,pin):
                for v in get_input_for(blk,pin):
                    source.append(v)
            else:
                deadsources.append(src)  
        else:
            deadsources.append(src)
    return deadsources
                   
def ProcessSinks(aax,sink:list)->list:
    '''
    iterate trough the Sink list
    '''
    # if (type(aax) is not AAX) or (type(aax) is not AA):
    #     warnings.warn("incorrect type @ProcessSinks(%s)"%type(aax))
    #     return
    deadsinks=[]
    while len(sink)>0:
        snk=sink.pop(0) # get the top one
        if is_inverted(snk):
            snk=snk[1:] # remove invertion
        if is_pointer(snk): # not database
            blk=get_block(aax,snk) # shell check if block exist?
            pin=get_addr_pin(snk)[1] # extract pin name
            if is_output(blk,pin): # check if the pin is output
                xrefpin=aax.xRef(snk) # search usage of the pin
                for v in xrefpin:
                    if not is_loop(blk,pin):
                        sink.append(v) #add usage points to Sinks
                val=get_pin_value(blk,pin)
                for v in val:
                    if not is_loop(blk,pin):
                        sink.append(v) # push at te end
            elif is_input(blk,pin):
                for v in get_output_for(blk,pin):
                    if not is_loop(blk,pin):
                        sink.append(v) # push at the end
            else:
                deadsinks.append(snk)  
        else:
            deadsinks.append(snk)
    return deadsinks

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