"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.branchtable = {
            0b00000001: self.HLT,
            0b10000010: self.LDI,
            0b01000111: self.PRN,
            0b10100000: self.ADD,
            0b10100010: self.MUL,
            0b10100111: self.CMP,
            0b10101000: self.AND,
            0b10101010: self.OR,
            0b10101011: self.XOR,
            0b01101001: self.NOT,
            0b10101100: self.SHL,
            0b10101101: self.SHR,
            0b10100100: self.MOD,
            0b01000101: self.PUSH,
            0b01000110: self.POP,
            0b01010000: self.CALL,
            0b00010001: self.RET,
            0b01010100: self.JMP,
            0b01010101: self.JEQ,
            0b01010110: self.JNE
        }
        self.running = True
        self.sp = 7
        self.reg[self.sp] = 244
        self.fl = 0b00000000

    def load(self):
        """Load a program into memory."""
        if len(sys.argv) != 2:
            print("Error: incorrect usage")
            print("Please enter in format: python ls8.py filename")
            sys.exit(1)

        filename = sys.argv[1]

        try:
            address = 0
            with open(filename) as f:
                for line in f:
                    # remove comments and whitespace
                    b = line.split("#")[0].strip()

                    # skip if line is empty
                    if b == '':
                        continue

                    d = int(b, 2)
                    self.ram[address] = d
                    address += 1

        except FileNotFoundError:
            print(f"File {filename} not found.")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b=1):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
            self.pc += 3
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
            self.pc += 3
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            self.pc += 3
        elif op == "AND":
            self.reg[reg_a] &= self.reg[reg_b]
            self.pc += 3
        elif op == "OR":
            self.reg[reg_a] |= self.reg[reg_b]
            self.pc += 3
        elif op == "XOR":
            self.reg[reg_a] ^= self.reg[reg_b]
            self.pc += 3
        elif op == "NOT":
            self.reg[reg_a] = 0b11111111 - self.reg[reg_a]
            self.pc += 2
        elif op == "SHL":
            self.reg[reg_a] <<= self.reg[reg_b]
            self.pc += 3
        elif op == "SHR":
            self.reg[reg_a] >>= self.reg[reg_b]
            self.pc += 3
        elif op == "MOD":
            self.reg[reg_a] %= self.reg[reg_b]
            self.pc += 3
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, addr):
        return self.ram[addr]

    def ram_write(self, addr, val):
        self.ram[addr] = val

    # op functions
    def HLT(self):
        self.running = False

    def LDI(self, reg_addr, val):
        self.reg[reg_addr] = val
        self.pc += 3

    def PRN(self, reg_addr):
        print(self.reg[reg_addr])
        self.pc += 2

    def ADD(self, reg_a, reg_b):
        self.alu("ADD", reg_a, reg_b)

    def MUL(self, reg_a, reg_b):
        self.alu("MUL", reg_a, reg_b)

    def CMP(self, reg_a, reg_b):
        self.alu("CMP", reg_a, reg_b)

    def AND(self, reg_a, reg_b):
        self.alu("AND", reg_a, reg_b)

    def OR(self, reg_a, reg_b):
        self.alu("OR", reg_a, reg_b)

    def XOR(self, reg_a, reg_b):
        self.alu("XOR", reg_a, reg_b)

    def NOT(self, reg_a):
        self.alu("NOT", reg_a)

    def SHL(self, reg_a, reg_b):
        self.alu("SHL", reg_a, reg_b)

    def SHR(self, reg_a, reg_b):
        self.alu("SHR", reg_a, reg_b)

    def MOD(self, reg_a, reg_b):
        self.alu("MOD", reg_a, reg_b)

    def PUSH(self, reg_addr):
        self.sp -= 1
        self.ram[self.sp] = self.reg[reg_addr]
        self.pc += 2

    def POP(self, reg_addr):
        self.reg[reg_addr] = self.ram[self.sp]
        self.sp += 1
        self.pc += 2

    def CALL(self, reg_addr):
        reg = self.ram[self.pc + 1]
        self.LDI(4, self.pc + 2)
        self.PUSH(4)
        self.pc = self.reg[reg]

    def RET(self):
        self.POP(4)
        self.pc = self.reg[4]

    def JMP(self, reg_addr):
        self.pc = self.reg[reg_addr]

    def JEQ(self, reg_addr):
        if self.fl == 1:
            self.pc = self.reg[reg_addr]
        else:
            self.pc += 2

    def JNE(self, reg_addr):
        if self.fl != 1:
            self.pc = self.reg[reg_addr]
        else:
            self.pc += 2

    def run(self):
        """Run the CPU."""
        while self.running:
            # get current instruction
            IR = self.ram_read(self.pc)

            # get potential operands
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # run op
            op_func = self.branchtable[IR]
            num_params = IR >> 6
            if num_params == 1:
                op_func(operand_a)
            elif num_params == 2:
                op_func(operand_a, operand_b)
            else:
                op_func()
