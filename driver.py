import json

REGISTERS = {
    "x1": "ra",
    "x2": "sp",
    "x3": "gp",
    "x4": "tp",
    "x5": "t0",
    "x6": "t1",
    "x7": "t2",
    "x8": "s0",
    "x9": "s1",
    "x10": "a0",
    "x11": "a1",
    "x12": "a2",
    "x13": "a3",
    "x14": "a4",
    "x15": "a5",
    "x16": "a6",
    "x17": "a7",
    "x18": "s2",
    "x19": "s3",
    "x20": "s4",
    "x21": "s5",
    "x22": "s6",
    "x23": "s7",
    "x24": "s8",
    "x25": "s9",
    "x26": "s10",
    "x27": "s11",
    "x28": "t3",
    "x29": "t4",
    "x30": "t5",
    "x31": "t6"
}

BRANCHES = ["beqz", "beq", "bnez", "bne", "blez", "ble", "bgez", "bge", "bltz", "blt", "bgtz", "bgt", "bgtu", "bltu", "bleu", "bgeu"]


LOGFILE = "BranchPredictionBenchmarks\EmptyLoop\instructions_rannedWithoutBootloader.log"

class CPUState:
    def __init__(self):
        self.reg_values = dict()
        for i in range(1,32):
            self.reg_values[f"x{i}"] = int("0x00000000",16)
        self.logs = list()
    def parse_instr(self, ins, nextline):
        ins_name = ins[34:42].strip()
        ins_addr = ins[10:20]
        nxt_addr = nextline[10:20]
        if ins_name in BRANCHES:
            addr0_int = int(ins_addr, 16)
            addr1_int = int(nxt_addr, 16)
            addr_diff = addr1_int - addr0_int
            state = ""
            if addr_diff == 4:
                state = "NOT TAKEN"
            else:
                state = "TAKEN"
            self.logs.append((ins_name, state, ins_addr, json.dumps(self.reg_values)))
    def parse_commit(self, commit):
        register = commit[36:39].strip()
        if len(register) == 0 or register[0] != 'x':
            # core   0: 3 0x80005dc8 (0x02c12423) mem 0x80013ca8 0x00001144
            # core   0: 3 0x80005dcc (0x08048a63)
            return
        value = commit[40:50]
        self.reg_values[register] = int(value, 16)

if __name__ == "__main__":
    with open(LOGFILE, "r") as f:
        data = f.read()

    datalines = data.split("\n")
    mycpu = CPUState()

    for i in range(len(datalines)-2):  # last line is empty anyways
        line = datalines[i]
        nextline = datalines[i+2]  # next ins line
        if line[11] == 'x':
            mycpu.parse_instr(line, nextline)
        elif line[11] == ' ':
            mycpu.parse_commit(line)
        else:
            # ignore
            pass

    with open("output.txt", "w+") as f:
        for line in mycpu.logs:
            f.write(json.dumps(line) + "\n")
