#AMPL blocks input and output pins definition
from ampla import *

#list of sink/source
Sources=[] # upstrean connections
Sinks=[] # downstream connections

DeadSources=[] # untraceble sources, dead end
DeadSinks=[] # untraceble sinks, dead end

def is_input(blk,pin)->bool:
    '''
    check if pin is input
    '''
    if blk.Name in InputPins:
        return pin in InputPins[blk.Name]
    return False

def is_output(blk,pin)->bool:
    '''
    check if pin is output
    '''
    if blk.Name in OutputPins:
        return pin in OutputPins[blk.Name]
    return False

def gen_pins(start,stop)->tuple:
    '''
    generate series of pins names
    '''
    T=()
    for i in range(start,stop+1):
        T=T+(':'+str(i),)
    return T

def GetSink(blk,pin):
    '''
    return tuple of possible output pin(s)
    given pin should be input
    '''
    if not is_input(blk,pin):
        return () # return empty tuple if pin is output
        pass
    
    match blk.Name:
        case "MOVE":
            return (blk.Address+':'+str(int(pin[pin.find(':')+1:])+20),)
            pass
        case "OR":
            return (blk.Address+':20',)
            pass
        case "AND":
            return (blk.Address+':20',)
            pass
        case "MUL":
            return (blk.Address+':20',)
            pass
        case "ADD":
            return (blk.Address+':20',)
            pass
        # expand for other blocks
    pass

def GetSource(blk,pin):
    '''
    return tuple of possible input pin(s)
    given pin should be output pin
    '''
    if not is_output(blk,pin):
        return ()
    #----------------------------    
    def ginp(blk):
        # get all inputs pins for blocks like
        # ADD, AND, OR, MUL
        inputs=()
        for p in blk.GetPins():
            if int(p[pin.find(':')+1:])<20:
                inputs=inputs+(blk.Address+p,)
        return inputs
    
    #----------------------------    
    
    match blk.Name:
        case "MOVE":
            return (blk.Address+':'+str(int(pin[pin.find(':')+1:])-20),)
        case "OR":
            # return all pins less than 20
            return ginp(blk)        
        case "AND":
            return ginp(blk)
        case "MUL":
            return ginp(blk)
        case "ADD":
            return ginp(blk)
    pass




InputPins={
    "BLOCK":(":ON",":1"),
    "MUL":gen_pins(1,19),
    "MOVE":gen_pins(1,19),
    "MOVE-A":gen_pins(1,19),
    "AND":gen_pins(1,19),
    "OR":gen_pins(1,19)
    }

OutputPins={
    "BLOCK":(":RUN",":5"),
    "MUL":(":20"),
    "MOVE":gen_pins(21,39),
    "MOVE-A":gen_pins(21,39),
    "AND":(":20"),
    "OR":(":20"),
    "ADD":(":20"),
    "I-AND":(":20"),
    "IOR":(":20"),
    "INOT":(":5"),
    "BTST":(":5"),
    "ABS":(":5"),
    "ADD-MR":(":50"),
    "ADD-MR1":(":95"),
    "AND-O":(":60"),
    "DB-COP":(":8",":9"),
    "FI-VOTE":gen_pins(80,93),
    "GI-VOTE":gen_pins(80,93),
    "CE-OPC":(":5",":21"),
    "CE-MATR":(),
}