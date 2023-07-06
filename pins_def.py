#AMPL blocks input and output pins definition

def is_input(block,pin)->bool:
    if block in InputPins:
        return pin in InputPins[block]
    return False

def is_output(block,pin)->bool:
    if block in OutputPins:
        return pin in OutputPins[block]
    return False

def gen_pins(start,stop)->tuple:
    T=()
    for i in range(start,stop+1):
        T=T+(':'+str(i),)
    return T

Link=(Block,pin)

Upstream=[]
Downstream=[]


InputPins={
    "BLOCK":(":ON",":1"),
    "MUL":gen_pins(1,20),
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
