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


LOGFILE = "log2.log"

class CPUState:
    def __init__(self):
        pass
    def parse_instr(self, ins):
        pass
    def parse_commit(self, commit):
        pass

if __name__ == "__main__":
    with open(LOGFILE, "r") as f:
        data = f.read()

    datalines = data.split("\n")
    mycpu = CPUState()

    for line in datalines:
        if line[11] == 'x':
            mycpu.parse_instr(line)
        elif line[11] == ' ':
            mycpu.parse_commit(line)
        else:
            # ignore
            pass
