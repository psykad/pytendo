class CPU:
    VECTOR_RESET = 0xFFFC # Reset Vector address.       

    def __init__(self, system):
        self._system = system
        self._debug_log = open("debug.log", "w")

    def reset(self):
        # Program Counter 16-bit, default to value located at the reset vector address.
        #self._pc = self._system.mmu.read_word(self.VECTOR_RESET)
        self._pc = 0xC000 # NES TEST Start point
        # Stack Pointer 8-bit, ranges from 0x0100 to 0x01FF
        self._sp = 0xFD
        # Accumulator 8-bit
        self._a = 0x00
        # Index Register X 8-bit
        self._x = 0x00
        # Index Register Y 8-bit
        self._y = 0x00

        #### Processor Status Flags
        # Carry - set if the last operation caused an overflow from bit 7, or an underflow from bit 0.
        self._carry = False
        # Zero - the result of the last operation was zero.
        self._zero  = False
        # Interrupt Disable - set if the program executed an SEI instruction. It's cleared with a CLI instruction.
        self._interrupt_disable = True   
        # Break Command - Set when a BRK instruction is hit and an interrupt has been generated to process it.
        self._break_command = False
        # Decimal Mode
        self._decimal_mode = False
        # Overflow - Set during arithmetic operations if the result has yielded an invalid 2's compliment result.
        self._overflow = False
        # Negative - Set if the result of the last operation had bit 7 set to a one.
        self._negative = False

        # Reset clock
        self.clock = 0

        # Reset previous instruction cycle count
        self.instruction_cycles = 0

    def step(self):
        # Fetch next instruction.
        pc = self._pc
        self._current_instruction = pc
        print(f"{format(pc,'x').upper()}")
        self._debug_log.write(f"{format(pc,'x').upper()}\n")
        op_code = self._get_next_byte()
        #print(f"PC: {hex(pc)} / INS: {hex(op_code)}")

        # Decode op code.
        instruction = self.decode_instruction(op_code)

        # Execute instruction.
        instruction(op_code)

        # Update CPU clock with instruction cycles.
        self.clock += self.instruction_cycles
        self.clock &= 0xFFFFFFFF

    def decode_instruction(self, op_code):
        instructions = {
            0x69: self.ADC, 0x65: self.ADC, 0x75: self.ADC, 0x6D: self.ADC, 0x7D: self.ADC, 0x79: self.ADC, 0x61: self.ADC, 0x71: self.ADC,       
            0x29: self.AND, 0x25: self.AND, 0x35: self.AND, 0x2D: self.AND, 0x3D: self.AND, 0x39: self.AND, 0x21: self.AND, 0x31: self.AND,
            0x0A: self.ASL, 0x06: self.ASL, 0x16: self.ASL, 0x0E: self.ASL, 0x1E: self.ASL,
            0x90: self.BCC, 0xB0: self.BCS, 0xF0: self.BEQ,
            0x24: self.BIT, 0x2C: self.BIT,
            0x30: self.BMI, 0xD0: self.BNE, 0x10: self.BPL, 0x00: self.BRK, 0x50: self.BVC, 0x70: self.BVS,
            0x18: self.CLC, 0xD8: self.CLD, 0x58: self.CLI, 0xB8: self.CLV,
            0xC9: self.CMP, 0xC5: self.CMP, 0xD5: self.CMP, 0xCD: self.CMP, 0xDD: self.CMP, 0xD9: self.CMP, 0xC1: self.CMP, 0xD1: self.CMP,
            0xE0: self.CPX, 0xE4: self.CPX, 0xEC: self.CPX,
            0xC0: self.CPY, 0xC4: self.CPY, 0xCC: self.CPY, 
            0xC6: self.DEC, 0xD6: self.DEC, 0xCE: self.DEC, 0xDE: self.DEC, 0xCA: self.DEX, 0x88: self.DEY,
            0x49: self.EOR, 0x45: self.EOR, 0x55: self.EOR, 0x4D: self.EOR, 0x5D: self.EOR, 0x59: self.EOR, 0x41: self.EOR, 0x51: self.EOR,
            0xE6: self.INC, 0xF6: self.INC, 0xEE: self.INC, 0xFE: self.INC, 0xE8: self.INX, 0xC8: self.INY,
            0x4C: self.JMP, 0x6C: self.JMP, 0x20: self.JSR,
            0xA9: self.LDA, 0xA5: self.LDA, 0xB5: self.LDA, 0xAD: self.LDA, 0xBD: self.LDA, 0xB9: self.LDA, 0xA1: self.LDA, 0xB1: self.LDA,
            0xA2: self.LDX, 0xA6: self.LDX, 0xB6: self.LDX, 0xAE: self.LDX, 0xBE: self.LDX, 
            0xA0: self.LDY, 0xA4: self.LDY, 0xB4: self.LDY, 0xAC: self.LDY, 0xBC: self.LDY, 
            0x4A: self.LSR, 0x46: self.LSR, 0x56: self.LSR, 0x4E: self.LSR, 0x5E: self.LSR, 
            0xEA: self.NOP,
            0x09: self.ORA, 0x05: self.ORA, 0x15: self.ORA, 0x0D: self.ORA, 0x1D: self.ORA, 0x19: self.ORA, 0x01: self.ORA, 0x11: self.ORA, 
            0x48: self.PHA, 0x08: self.PHP, 0x68: self.PLA, 0x28: self.PLP,
            0x2A: self.ROL, 0x26: self.ROL, 0x36: self.ROL, 0x2E: self.ROL, 0x3E: self.ROL, 
            0x6A: self.ROR, 0x66: self.ROR, 0x76: self.ROR, 0x6E: self.ROR, 0x7E: self.ROR, 
            0x40: self.RTI, 0x60: self.RTS,
            0xE9: self.SBC, 0xE5: self.SBC, 0xF5: self.SBC, 0xED: self.SBC, 0xFD: self.SBC, 0xF9: self.SBC, 0xE1: self.SBC, 0xF1: self.SBC, 
            0x38: self.SEC, 0xF8: self.SED, 0x78: self.SEI,
            0x85: self.STA, 0x95: self.STA, 0x8D: self.STA, 0x9D: self.STA, 0x99: self.STA, 0x81: self.STA, 0x91: self.STA, 
            0x86: self.STX, 0x96: self.STX, 0x8E: self.STX, 
            0x84: self.STY, 0x94: self.STY, 0x8C: self.STY, 
            0xAA: self.TAX, 0xA8: self.TAY, 0xBA: self.TSX, 0x8A: self.TXA, 0x9A: self.TXS, 0x98: self.TYA
        }
        instruction = instructions.get(op_code, None)
        if (instruction == None):
            raise RuntimeError(f"No instruction found: {hex(op_code)}")
        return instruction

    def _get_next_byte(self):
        value = self._system.mmu.read_byte(self._pc)
        self._pc += 1
        return value

    def _get_next_word(self):
        lo = self._get_next_byte()
        hi = self._get_next_byte()
        return (hi<<8)+lo

    def _set_status_flag(self, byte):
        self._negative = byte&0x80 > 0
        self._overflow = byte&0x40 > 0
        self._decimal_mode = byte&0x08 > 0
        self._interrupt_disable = byte&0x04 > 0
        self._zero = byte&0x02 > 0
        self._carry = byte&0x01 > 0

    def _get_status_flag(self):
        value = 0
        value |= 0x80 if (self._negative) else 0
        value |= 0x40 if (self._overflow) else 0
        value |= 0x08 if (self._decimal_mode) else 0
        value |= 0x04 if (self._interrupt_disable) else 0
        value |= 0x02 if (self._zero) else 0
        value |= 0x01 if (self._carry) else 0
        return value

    # Pushes a byte onto the stack.
    def push(self, value):
        self._system.mmu.write_byte(self._sp, value)
        self._sp = (self._sp-1)&0xFF

    # Pulls the next byte off the stack.
    def pull(self):
        self._sp = (self._sp+1)&0xFF
        value = self._system.mmu.read_byte(self._sp)
        return value

    ###############################################################################
    # Address Mode Helpers
    ###############################################################################
    def _get_address_at_zeropage(self):
        return self._get_next_byte()

    def _get_address_at_zeropage_x(self):
        return (self._get_next_byte() + self._x)&0xFF

    def _get_address_at_zeropage_y(self):
        return (self._get_next_byte() + self._y)&0xFF
        
    def _get_address_at_absolute(self):
        return self._get_next_word()

    def _get_address_at_absolute_x(self):
        return self._get_next_word() + self._x

    def _get_address_at_absolute_y(self):
        return self._get_next_word() + self._y

    def _get_address_at_indirect(self):
        return self._system.mmu.read_word(self._get_next_byte())

    def _get_address_at_indirect_x(self):
        return self._system.mmu.read_word((self._get_next_byte()+self._x)&0xFF)

    def _get_address_at_indirect_y(self):
        return self._system.mmu.read_word(self._get_next_byte())+self._y

    def _get_value_at_zeropage(self):
        return self._system.mmu.read_byte(self._get_address_at_zeropage())

    def _get_value_at_zeropage_x(self):
        return self._system.mmu.read_byte(self._get_address_at_zeropage_x())

    def _get_value_at_absolute(self):
        return self._system.mmu.read_byte(self._get_address_at_absolute())

    def _get_value_at_absolute_x(self):
        return self._system.mmu.read_byte(self._get_address_at_absolute_x())

    def _get_value_at_absolute_y(self):
        return self._system.mmu.read_byte(self._get_address_at_absolute_y())

    def _get_value_at_indirect_x(self):
        return self._system.mmu.read_byte(self._get_address_at_indirect_x())

    def _get_value_at_indirect_y(self):
        return self._system.mmu.read_byte(self._get_address_at_indirect_y())

    ###############################################################################
    # Instructions
    # TODO: Implement * modifiers to instruction timing. i.e. add 1 if page boundary is crossed.
    ###############################################################################
    def ADC(self, op_code):        
        # Add Memory to Accumulator with Carry    
        # A + M + C -> A, C                N Z C I D V
        #                                  + + + - - +
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # immediate     ADC #oper     69    2     2
        # zeropage      ADC oper      65    2     3
        # zeropage,X    ADC oper,X    75    2     4
        # absolute      ADC oper      6D    3     4
        # absolute,X    ADC oper,X    7D    3     4*
        # absolute,Y    ADC oper,Y    79    3     4*
        # (indirect,X)  ADC (oper,X)  61    2     6
        # (indirect),Y  ADC (oper),Y  71    2     5*
        value = None
        if (op_code == 0x69): # immediate
            value = self._get_next_byte()
            self.instruction_cycles = 2
        elif (op_code == 0x65): # zeropage
            value = self._get_value_at_zeropage()
            self.instruction_cycles = 3
        elif (op_code == 0x75): # zeropage,X
            value = self._get_value_at_zeropage_x()
            self.instruction_cycles = 4
        elif (op_code == 0x6D): # absolute
            value = self._get_value_at_absolute()
            self.instruction_cycles = 4
        elif (op_code == 0x7D): # absolute,X
            value = self._get_value_at_absolute_x()
            self.instruction_cycles = 4
        elif (op_code == 0x79): # absolute,Y
            value = self._get_value_at_absolute_y()
            self.instruction_cycles = 4
        elif (op_code == 0x61): # (indirect,X)
            value = self._get_value_at_indirect_x()
            self.instruction_cycles = 6
        elif (op_code == 0x71): # (indirect),Y
            value = self._get_value_at_indirect_y()
            self.instruction_cycles = 5
        else:
            raise RuntimeError(f"Unknown op code: {op_code}")

        result = self._a + value + (1 if self._carry == True else 0)
        self._carry = result > 0xFF
        # More info on source: https://stackoverflow.com/a/29224684
        self._overflow = ~(self._a ^ value) & (self._a ^ result) & 0x80
        self._a = result&0xFF
        self._negative = (self._a>>7) == 1
        self._zero = self._a == 0

    def AND(self, op_code):
        # AND Memory with Accumulator
        # A AND M -> A                     N Z C I D V
        #                                  + + - - - -       
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # immediate     AND #oper     29    2     2
        # zeropage      AND oper      25    2     3
        # zeropage,X    AND oper,X    35    2     4
        # absolute      AND oper      2D    3     4
        # absolute,X    AND oper,X    3D    3     4*
        # absolute,Y    AND oper,Y    39    3     4*
        # (indirect,X)  AND (oper,X)  21    2     6
        # (indirect),Y  AND (oper),Y  31    2     5*
        value = None
        if (op_code == 0x29): # immediate
            value = self._get_next_byte()
            self.instruction_cycles = 2
        elif (op_code == 0x25): # zeropage
            value = self._get_value_at_zeropage()
            self.instruction_cycles = 3
        elif (op_code == 0x35): # zeropage,X
            value = self._get_value_at_zeropage_x()
            self.instruction_cycles = 4
        elif (op_code == 0x2D): # absolute
            value = self._get_value_at_absolute()
            self.instruction_cycles = 4
        elif (op_code == 0x3D): # absolute,X
            value = self._get_value_at_absolute_x()
            self.instruction_cycles = 4
        elif (op_code == 0x39): # absolute,Y
            value = self._get_value_at_absolute_y()
            self.instruction_cycles = 4
        elif (op_code == 0x21): # (indirect,X)            
            value = self._get_value_at_indirect_x()
            self.instruction_cycles = 6
        elif (op_code == 0x31): # (indirect),Y
            value = self._get_value_at_indirect_y()
            self.instruction_cycles = 5
        else:
            raise RuntimeError(f"Unknown op code: {op_code}")

        self._a = (self._a&value)&0xFF        
        self._negative = (self._a&0x80) > 0
        self._zero = self._a == 0

    def ASL(self, op_code):
        # Shift Left One Bit (Memory or Accumulator)
        # C <- [76543210] <- 0             N Z C I D V
        #                                  + + + - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # accumulator   ASL A         0A    1     2
        # zeropage      ASL oper      06    2     5
        # zeropage,X    ASL oper,X    16    2     6
        # absolute      ASL oper      0E    3     6
        # absolute,X    ASL oper,X    1E    3     7
        address = None
        if (op_code == 0x0A): # accumulator
            self._carry = self._a&0x80 > 0
            self._a = (self._a<<1)&0xFF
            self._negative = self._a&0x80 > 0
            self._zero = self._a == 0
            self.instruction_cycles = 2
            return
        elif (op_code == 0x06): # zeropage
            address = self._get_address_at_zeropage()
            self.instruction_cycles = 5
        elif (op_code == 0x16): # zeropage,X
            address = self._get_address_at_zeropage_x()
            self.instruction_cycles = 6
        elif (op_code == 0x0E): # absolute
            address = self._get_address_at_absolute()
            self.instruction_cycles = 6
        elif (op_code == 0x1E): # absolute,X
            address = self._get_address_at_absolute_x()
            self.instruction_cycles = 7
        else:
            raise RuntimeError(f"Unknown op code: {op_code}")

        value = self._system.mmu.read_byte(address)
        self._carry = value&0x80 > 0
        value = (value<<1)&0xFF
        self._negative = value&0x80 > 0
        self._zero = value == 0
        self._system.mmu.write_byte(address, value)

    def BCC(self, op_code):
        # Branch on Carry Clear
        # branch on C = 0                  N Z C I D V
        #                                  - - - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # relative      BCC oper      90    2     2**
        offset = self._get_next_byte()

        if (not self._carry):
            if (offset > 127):
                offset = -((~offset+1)&255) # Signed byte
            self._pc += offset

        self.instruction_cycles = 2

    def BCS(self, op_code):
        # Branch on Carry Set
        # branch on C = 1                  N Z C I D V
        #                                  - - - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # relative      BCS oper      B0    2     2**
        offset = self._get_next_byte()

        if (self._carry):
            if (offset > 127):
                offset = -((~offset+1)&255) # Signed byte
            self._pc += offset

        self.instruction_cycles = 2

    def BEQ(self, op_code):
        # Branch on Result Zero
        # branch on Z = 1                  N Z C I D V
        #                                  - - - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # relative      BEQ oper      F0    2     2**
        offset = self._get_next_byte()

        if (self._zero):
            if (offset > 127):
                offset = -((~offset+1)&255) # Signed byte
            self._pc += offset

        self.instruction_cycles = 2

    def BIT(self, op_code):
        # Test Bits in Memory with Accumulator
        # bits 7 and 6 of operand are transfered to bit 7 and 6 of SR (N,V);
        # the zeroflag is set to the result of operand AND accumulator.
        # A AND M, M7 -> N, M6 -> V        N Z C I D V
        #                                 M7 + - - - M6
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # zeropage      BIT oper      24    2     3
        # absolute      BIT oper      2C    3     4
        value = None
        
        if (op_code == 0x24): # zeropage
            value = self._get_value_at_zeropage()
            self.instruction_cycles = 3
        elif (op_code == 0x2C): # absolute
            value = self._get_value_at_absolute()
            self.instruction_cycles = 4

        self._negative = value&0x80 > 0
        self._overflow = value&0x40 > 0
        value &= self._a
        self._zero = value == 0

    def BMI(self, op_code):
        # Branch on Result Minus
        # branch on N = 1                  N Z C I D V
        #                                  - - - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # relative      BMI oper      30    2     2**
        offset = self._get_next_byte()

        if (self._negative):
            if (offset > 127):
                offset = -((~offset+1)&255) # Signed byte
            self._pc += offset

        self.instruction_cycles = 2

    def BNE(self, op_code):
        # Branch on Result not Zero
        # branch on Z = 0                  N Z C I D V
        #                                  - - - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # relative      BNE oper      D0    2     2**
        offset = self._get_next_byte()

        if (not self._zero):
            if (offset > 127):
                offset = -((~offset+1)&255) # Signed byte
            self._pc += offset

        self.instruction_cycles = 2

    def BPL(self, op_code):
        # Branch on Result Plus
        # branch on N = 0                  N Z C I D V
        #                                  - - - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # relative      BPL oper      10    2     2**
        offset = self._get_next_byte()

        if (not self._negative):
            if (offset > 127):
                offset = -((~offset+1)&255) # Signed byte
            self._pc += offset

        self.instruction_cycles = 2

    def BRK(self, op_code):
        # Force Break
        # interrupt,                       N Z C I D V
        # push PC+2, push SR               - - - 1 - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # implied       BRK           00    1     7
        raise NotImplementedError()

    def BVC(self, op_code):
        # Branch on Overflow Clear
        # branch on V = 0                  N Z C I D V
        #                                  - - - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # relative      BVC oper      50    2     2**
        offset = self._get_next_byte()

        if (not self._overflow):
            if (offset > 127):
                offset = -((~offset+1)&255) # Signed byte
            self._pc += offset

        self.instruction_cycles = 2

    def BVS(self, op_code):
        # Branch on Overflow Set
        # branch on V = 1                  N Z C I D V
        #                                  - - - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # relative      BVC oper      70    2     2**
        offset = self._get_next_byte()

        if (self._overflow):
            if (offset > 127):
                offset = -((~offset+1)&255) # Signed byte
            self._pc += offset

        self.instruction_cycles = 2

    def CLC(self, op_code):
        # Clear Carry Flag
        # 0 -> C                           N Z C I D V
        #                                  - - 0 - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # implied       CLC           18    1     2
        self._carry = False
        self.instruction_cycles = 2

    def CLD(self, op_code):
        # Clear Decimal Mode
        # 0 -> D                           N Z C I D V
        #                                  - - - - 0 -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # implied       CLD           D8    1     2        
        self._decimal_mode = False
        self.instruction_cycles = 2

    def CLI(self, op_code):
        # Clear Interrupt Disable Bit
        # 0 -> I                           N Z C I D V
        #                                  - - - 0 - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # implied       CLI           58    1     2        
        self._interrupt_disable = False
        self.instruction_cycles = 2
    
    def CLV(self, op_code):
        # Clear Overflow Flag
        # 0 -> V                           N Z C I D V
        #                                  - - - - - 0
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # implied       CLV           B8    1     2        
        self._overflow = False
        self.instruction_cycles = 2

    def CMP(self, op_code):
        # Compare Memory with Accumulator
        # A - M                            N Z C I D V
        #                                  + + + - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # immediate     CMP #oper     C9    2     2
        # zeropage      CMP oper      C5    2     3
        # zeropage,X    CMP oper,X    D5    2     4
        # absolute      CMP oper      CD    3     4
        # absolute,X    CMP oper,X    DD    3     4*
        # absolute,Y    CMP oper,Y    D9    3     4*
        # (indirect,X)  CMP (oper,X)  C1    2     6
        # (indirect),Y  CMP (oper),Y  D1    2     5*
        value = None

        if (op_code == 0xC9): # immediate
            value = self._get_next_byte()
            self.instruction_cycles = 2
        elif (op_code == 0xC5): # zeropage
            value = self._get_value_at_zeropage()
            self.instruction_cycles = 3
        elif (op_code == 0xD5): # zeropage,X
            value = self._get_value_at_zeropage_x()
            self.instruction_cycles = 4
        elif (op_code == 0xCD): # absolute
            value = self._get_value_at_absolute()
            self.instruction_cycles = 4
        elif (op_code == 0xDD): # absolute,X
            value = self._get_value_at_absolute_x()
            self.instruction_cycles = 4
        elif (op_code == 0xD9): # absolute,Y
            value = self._get_value_at_absolute_y()
            self.instruction_cycles = 4
        elif (op_code == 0xC1): # (indirect,X)
            value = self._get_value_at_indirect_x()
            self.instruction_cycles = 6
        elif (op_code == 0xD1): # (indirect),Y
            value = self._get_value_at_indirect_y()
            self.instruction_cycles = 5
        else:
            raise RuntimeError(f"Unknown op code: {op_code}")
        
        result = (self._a - value)&0xFF

        self._carry = self._a >= value
        self._zero = self._a == value
        self._negative = result&0x80 > 0

    def CPX(self, op_code):
        # Compare Memory and Index X
        # X - M                            N Z C I D V
        #                                  + + + - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # immediate     CPX #oper     E0    2     2
        # zeropage      CPX oper      E4    2     3
        # absolute      CPX oper      EC    3     4
        value = None

        if (op_code == 0xE0): # immediate
            value = self._get_next_byte()
            self.instruction_cycles = 2
        elif (op_code == 0xE4): # zeropage
            value = self._get_value_at_zeropage()
            self.instruction_cycles = 3
        elif (op_code == 0xEC): # absolute
            value = self._get_value_at_absolute()
            self.instruction_cycles = 4
        else:
            raise RuntimeError(f"Unknown op code: {op_code}")

        result = (self._x - value)&0xFF

        self._carry = self._x >= value
        self._zero = self._x == value
        self._negative = result&0x80 > 0

    def CPY(self, op_code):
        # Compare Memory and Index Y
        # Y - M                            N Z C I D V
        #                                  + + + - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # immediate     CPY #oper     C0    2     2
        # zeropage      CPY oper      C4    2     3
        # absolute      CPY oper      CC    3     4
        value = None

        if (op_code == 0xC0): # immediate
            value = self._get_next_byte()
            self.instruction_cycles = 2
        elif (op_code == 0xC4): # zeropage
            value = self._get_value_at_zeropage()
            self.instruction_cycles = 3
        elif (op_code == 0xCC): # absolute
            value = self._get_value_at_absolute()
            self.instruction_cycles = 4
        else:
            raise RuntimeError(f"Unknown op code: {op_code}")

        result = (self._y - value)&0xFF

        self._carry = self._y >= value
        self._zero = self._y == value
        self._negative = result&0x80 > 0

    def DEC(self, op_code):
        # Decrement Memory by One
        # M - 1 -> M                       N Z C I D V
        #                                  + + - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # zeropage      DEC oper      C6    2     5
        # zeropage,X    DEC oper,X    D6    2     6
        # absolute      DEC oper      CE    3     3
        # absolute,X    DEC oper,X    DE    3     7
        address = None

        if (op_code == 0xC6): # zeropage
            address = self._get_address_at_zeropage()
            self.instruction_cycles = 5
        elif (op_code == 0xD6): # zeropage,X            
            address = self._get_address_at_zeropage_x()
            self.instruction_cycles = 6
        elif (op_code == 0xCE): # absolute
            address = self._get_address_at_absolute()
            self.instruction_cycles = 3
        elif (op_code == 0xDE): # absolute,X
            address = self._get_address_at_absolute_x()
            self.instruction_cycles = 7
        else:
            raise RuntimeError(f"Unknown op code: {op_code}")

        value = (self._system.mmu.read_byte(address)-1)&0xFF        
        self._negative = value&0x80 > 1
        self._zero = value == 0
        self._system.mmu.write_byte(address, value)        

    def DEX(self, op_code):
        # Decrement Index X by One
        # X - 1 -> X                       N Z C I D V
        #                                  + + - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # implied       DEC           CA    1     2
        self._x = (self._x - 1)&0xFF
        self._negative = self._x&0x80 > 1
        self._zero = self._x == 0
        self.instruction_cycles = 2

    def DEY(self, op_code):
        # Decrement Index Y by One
        # Y - 1 -> Y                       N Z C I D V
        #                                  + + - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # implied       DEC           88    1     2
        self._y = (self._y - 1)&0xFF
        self._negative = self._y&0x80 > 1
        self._zero = self._y == 0
        self.instruction_cycles = 2

    def EOR(self, op_code):
        # Exclusive-OR Memory with Accumulator
        # A EOR M -> A                     N Z C I D V
        #                                  + + - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # immediate     EOR #oper     49    2     2
        # zeropage      EOR oper      45    2     3
        # zeropage,X    EOR oper,X    55    2     4
        # absolute      EOR oper      4D    3     4
        # absolute,X    EOR oper,X    5D    3     4*
        # absolute,Y    EOR oper,Y    59    3     4*
        # (indirect,X)  EOR (oper,X)  41    2     6
        # (indirect),Y  EOR (oper),Y  51    2     5*
        value = None

        if (op_code == 0x49): # immediate
            value = self._get_next_byte()
            self.instruction_cycles = 2
        elif (op_code == 0x45): # zeropage
            value = self._get_value_at_zeropage()
            self.instruction_cycles = 3
        elif (op_code == 0x55): # zeropage,X
            value = self._get_value_at_zeropage_x()
            self.instruction_cycles = 4
        elif (op_code == 0x4D): # absolute
            value = self._get_value_at_absolute()
            self.instruction_cycles = 4
        elif (op_code == 0x5D): # absolute,X
            value = self._get_value_at_absolute_x()
            self.instruction_cycles = 4
        elif (op_code == 0x59): # absolute,Y
            value = self._get_value_at_absolute_y()
            self.instruction_cycles = 4
        elif (op_code == 0x41): # (indirect,X)
            value = self._get_value_at_indirect_x()
            self.instruction_cycles = 6
        elif (op_code == 0x51): # (indirect),Y
            value = self._get_value_at_indirect_y()
            self.instruction_cycles = 5
        else:
            raise RuntimeError(f"Unknown op code: {op_code}")

        self._a ^= value
        self._negative = (self._a>>7) == 1
        self._zero = self._a == 0

    def INC(self, op_code):
        # Increment Memory by One
        # M + 1 -> M                       N Z C I D V
        #                                  + + - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # zeropage      INC oper      E6    2     5
        # zeropage,X    INC oper,X    F6    2     6
        # absolute      INC oper      EE    3     6
        # absolute,X    INC oper,X    FE    3     7
        address = None

        if (op_code == 0xE6): # zeropage
            address = self._get_address_at_zeropage()
            self.instruction_cycles = 5
        elif (op_code == 0xF6): # zeropage,X            
            address = self._get_address_at_zeropage_x()
            self.instruction_cycles = 6
        elif (op_code == 0xEE): # absolute
            address = self._get_address_at_absolute()
            self.instruction_cycles = 6
        elif (op_code == 0xFE): # absolute,X
            address = self._get_address_at_absolute_x()
            self.instruction_cycles = 7
        else:
            raise RuntimeError(f"Unknown op code: {op_code}")

        value = (self._system.mmu.read_byte(address)+1)&0xFF
        
        self._negative = (value>>7) == 1
        self._zero = value == 0

        self._system.mmu.write_byte(address, value)

    def INX(self, op_code):
        # Increment Index X by One
        # X + 1 -> X                       N Z C I D V
        #                                  + + - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # implied       INX           E8    1     2
        self._x = (self._x + 1)&0xFF
        self._negative = self._x&0x80 > 0
        self._zero = self._x == 0
        self.instruction_cycles = 2

    def INY(self, op_code):
        # Increment Index Y by One
        # Y + 1 -> Y                       N Z C I D V
        #                                  + + - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # implied       INY           C8    1     2
        self._y = (self._y + 1)&0xFF
        self._negative = self._y&0x80 > 0
        self._zero = self._y == 0        
        self.instruction_cycles = 2

    def JMP(self, op_code):
        # Jump to New Location
        # (PC+1) -> PCL                    N Z C I D V
        # (PC+2) -> PCH                    - - - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # absolute      JMP oper      4C    3     3
        # indirect      JMP (oper)    6C    3     5
        address = None
        if (op_code == 0x4C): # absolute
            pcl = self._system.mmu.read_byte(self._pc)
            pch = self._system.mmu.read_byte(self._pc+1)
            address = (pch<<8)+pcl
            self.instruction_cycles = 3
        elif (op_code == 0x6C): # indirect
            address = self._get_address_at_indirect()
            self.instruction_cycles = 5
        
        self._pc = address

    def JSR(self, op_code):
        # Jump to New Location Saving Return Address
        # push (PC+2),                     N Z C I D V
        # (PC+1) -> PCL                    - - - - - -
        # (PC+2) -> PCH
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # absolute      JSR oper      20    3     6
        next_address = self._pc+2
        print(f"JSR next address: {hex(next_address)}")
        self.push(next_address>>8) # HI byte
        self.push(next_address&0xFF) # LO byte
        self._pc = self._get_address_at_absolute()
        self.instruction_cycles = 6

    def LDA(self, op_code):
        # Load Accumulator with Memory
        # M -> A                           N Z C I D V
        #                                  + + - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # immediate     LDA #oper     A9    2     2
        # zeropage      LDA oper      A5    2     3
        # zeropage,X    LDA oper,X    B5    2     4
        # absolute      LDA oper      AD    3     4
        # absolute,X    LDA oper,X    BD    3     4*
        # absolute,Y    LDA oper,Y    B9    3     4*
        # (indirect,X)  LDA (oper,X)  A1    2     6
        # (indirect),Y  LDA (oper),Y  B1    2     5*
        value = None

        if (op_code == 0xA9): # immedidate
            value = self._get_next_byte()
            self.instruction_cycles = 2
        elif (op_code == 0xA5): # zeropage
            value = self._get_value_at_zeropage()
            self.instruction_cycles = 3
        elif (op_code == 0xB5): # zeropage,X
            value = self._get_value_at_zeropage_x()
            self.instruction_cycles = 4
        elif (op_code == 0xAD): # absolute
            value = self._get_value_at_absolute()
            self.instruction_cycles = 4
        elif (op_code == 0xBD): # absolute,X
            value = self._get_value_at_absolute_x()
            self.instruction_cycles = 4
        elif (op_code == 0xB9): # absolute,Y
            value = self._get_value_at_absolute_y()
            self.instruction_cycles = 4
        elif (op_code == 0xA1): # (indirect,X)
            value = self._get_value_at_indirect_x()
            self.instruction_cycles = 6
        elif (op_code == 0xB1): # (indirect),Y
            value = self._get_value_at_indirect_y()
            self.instruction_cycles = 5
        else:
            raise RuntimeError(f"Unknown op code: {op_code}")

        self._negative = (value&0x80) > 0
        self._zero = value == 0
        self._a = value        

    def LDX(self, op_code):
        # Load Index X with Memory
        # M -> X                           N Z C I D V
        #                                  + + - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # immediate     LDX #oper     A2    2     2
        # zeropage      LDX oper      A6    2     3
        # zeropage,Y    LDX oper,Y    B6    2     4
        # absolute      LDX oper      AE    3     4
        # absolute,Y    LDX oper,Y    BE    3     4*
        value = None

        if (op_code == 0xA2): # immediate
            value = self._get_next_byte()
            self.instruction_cycles = 2
        elif (op_code == 0xA6): # zeropage
            value = self._get_value_at_zeropage()
            self.instruction_cycles = 3
        elif (op_code == 0xB6): # zeropage,Y
            value = self._get_value_at_zeropage_y()
            self.instruction_cycles = 4
        elif (op_code == 0xAE): # absolute
            value = self._get_value_at_absolute()
            self.instruction_cycles = 4
        elif (op_code == 0xBE): # absolute,Y
            value = self._get_value_at_absolute_y()
            self.instruction_cycles = 4
        else:
            raise RuntimeError(f"Unknown op code: {op_code}")

        self._negative = (value&0x80) > 0
        self._zero = value == 0
        self._x = value

    def LDY(self, op_code):
        # Load Index Y with Memory
        # M -> Y                           N Z C I D V
        #                                  + + - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # immediate     LDY #oper     A0    2     2
        # zeropage      LDY oper      A4    2     3
        # zeropage,X    LDY oper,X    B4    2     4
        # absolute      LDY oper      AC    3     4
        # absolute,X    LDY oper,X    BC    3     4*
        value = None

        if (op_code == 0xA0): # immediate
            value = self._get_next_byte()
            self.instruction_cycles = 2
        elif (op_code == 0xA4): # zeropage
            value = self._get_value_at_zeropage()
            self.instruction_cycles = 3
        elif (op_code == 0xB4): # zeropage,X
            value = self._get_value_at_zeropage_x()
            self.instruction_cycles = 4
        elif (op_code == 0xAC): # absolute
            value = self._get_value_at_absolute()
            self.instruction_cycles = 4
        elif (op_code == 0xBC): # absolute,X
            value = self._get_value_at_absolute_x()
            self.instruction_cycles = 4
        else:
            raise RuntimeError(f"Unknown op code: {op_code}")

        self._negative = (value&0x80) > 0
        self._zero = value == 0
        self._y = value

    def LSR(self, op_code):
        # Shift One Bit Right (Memory or Accumulator)
        # 0 -> [76543210] -> C             N Z C I D V
        #                                  - + + - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # accumulator   LSR A         4A    1     2
        # zeropage      LSR oper      46    2     5
        # zeropage,X    LSR oper,X    56    2     6
        # absolute      LSR oper      4E    3     6
        # absolute,X    LSR oper,X    5E    3     7
        address = None
        if (op_code == 0x4A): # accumulator
            self._carry = (self._a&0x01) > 0
            self._a >>= 1
            self._negative = (self._a&0x80) > 0
            self._zero = self._a == 0
            self.instruction_cycles = 2
            return
        elif (op_code == 0x46): # zeropage
            address = self._get_address_at_zeropage()
            self.instruction_cycles = 5
        elif (op_code == 0x56): # zeropage,X
            address = self._get_address_at_zeropage_x()
            self.instruction_cycles = 6
        elif (op_code == 0x4E): # absolute
            address = self._get_address_at_absolute()
            self.instruction_cycles = 6
        elif (op_code == 0x5E): # absolute,X
            address = self._get_address_at_absolute_x()
            self.instruction_cycles = 7
        else:
            raise RuntimeError(f"Unknown op code: {op_code}")

        value = self._system.mmu.read_byte(address)

        self._carry = (value&0x80) > 0

        value <<= 1

        self._negative = (value&0x80) > 0
        self._zero = value == 0

        self._system.mmu.write_byte(address, value)

    def NOP(self, op_code):
        # No Operation
        # ---                              N Z C I D V
        #                                  - - - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # implied       NOP           EA    1     2
        self.instruction_cycles = 2

    def ORA(self, op_code):
        # OR Memory with Accumulator
        # A OR M -> A                      N Z C I D V
        #                                  + + - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # immediate     ORA #oper     09    2     2
        # zeropage      ORA oper      05    2     3
        # zeropage,X    ORA oper,X    15    2     4
        # absolute      ORA oper      0D    3     4
        # absolute,X    ORA oper,X    1D    3     4*
        # absolute,Y    ORA oper,Y    19    3     4*
        # (indirect,X)  ORA (oper,X)  01    2     6
        # (indirect),Y  ORA (oper),Y  11    2     5*
        value = None
        if (op_code == 0x09): # immediate
            value = self._get_next_byte()
            self.instruction_cycles = 2
        elif (op_code == 0x05): # zeropage
            value = self._get_value_at_zeropage()
            self.instruction_cycles = 3
        elif (op_code == 0x15): # zeropage,X
            value = self._get_value_at_zeropage_x()
            self.instruction_cycles = 4
        elif (op_code == 0x0D): # absolute
            value = self._get_value_at_absolute()
            self.instruction_cycles = 4
        elif (op_code == 0x1D): # absolute,X
            value = self._get_value_at_absolute_x()
            self.instruction_cycles = 4
        elif (op_code == 0x19): # absolute,Y
            value = self._get_value_at_absolute_y()
            self.instruction_cycles = 4
        elif (op_code == 0x01): # (indirect,X)            
            value = self._get_value_at_indirect_x()
            self.instruction_cycles = 6
        elif (op_code == 0x11): # (indirect),Y
            value = self._get_value_at_indirect_y()
            self.instruction_cycles = 5
        else:
            raise RuntimeError(f"Unknown op code: {op_code}")

        self._a = (self._a|value)&0xFF
        
        self._negative = (self._a&0x80) > 0
        self._zero = self._a == 0

    def PHA(self, op_code):
        # Push Accumulator on Stack
        # push A                           N Z C I D V
        #                                  - - - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # implied       PHA           48    1     3        
        self.push(self._a)
        self.instruction_cycles = 3

    def PHP(self, op_code):
        # Push Processor Status on Stack
        # push SR                          N Z C I D V
        #                                  - - - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # implied       PHP           08    1     3
        value = self._get_status_flag()
        value |= 0x30 # Bits 5 and 4 are set when pushed by PHP
        self.push(value)
        self.instruction_cycles = 3

    def PLA(self, op_code):
        # Pull Accumulator from Stack
        # pull A                           N Z C I D V
        #                                  + + - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # implied       PLA           68    1     4
        self._a = self.pull()
        self._negative = self._a&0x80 > 0
        self._zero = self._a == 0
        self.instruction_cycles = 4

    def PLP(self, op_code):
        # Pull Processor Status from Stack
        # pull SR                          N Z C I D V
        #                                  from stack
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # implied       PHP           28    1     4
        self._set_status_flag(self.pull())
        self.instruction_cycles = 4

    def ROL(self, op_code):
        # Rotate One Bit Left (Memory or Accumulator)
        # C <- [76543210] <- C             N Z C I D V
        #                                  + + + - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # accumulator   ROL A         2A    1     2
        # zeropage      ROL oper      26    2     5
        # zeropage,X    ROL oper,X    36    2     6
        # absolute      ROL oper      2E    3     6
        # absolute,X    ROL oper,X    3E    3     7
        address = None

        if (op_code == 0x2A): # accumulator
            carryOut = True if (self._a&0x80 > 0) else False
            self._a = ((self._a<<1) + (1 if (self._carry) else 0))&0xFF
            self._carry = carryOut
            self._negative = self._a&0x80 > 0
            self._zero = self._a == 0
            self.instruction_cycles = 2
            return
        elif (op_code == 0x26): # zeropage
            address = self._get_address_at_zeropage()
            self.instruction_cycles = 5
        elif (op_code == 0x36): # zeropage,X
            address = self._get_address_at_zeropage_x()
            self.instruction_cycles = 6
        elif (op_code == 0x2E): # absolute
            address = self._get_address_at_absolute()
            self.instruction_cycles = 6
        elif (op_code == 0x3E): # absolute,X
            address = self._get_address_at_absolute_x()
            self.instruction_cycles = 7
        else:
            raise RuntimeError(f"Unknown op code: {op_code}")            

        value = self._system.mmu.read_byte(address)
        carryOut = True if (value&0x80 > 0) else False
        value = ((value<<1) + (1 if (self._carry) else 0))&0xFF
        self._carry = carryOut
        self._system.mmu.write_byte(address, value)
        self._negative = value&0x80 > 0
        self._zero = value == 0

    def ROR(self, op_code):
        # Rotate One Bit Right (Memory or Accumulator)
        # C -> [76543210] -> C             N Z C I D V
        #                                  + + + - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # accumulator   ROR A         6A    1     2
        # zeropage      ROR oper      66    2     5
        # zeropage,X    ROR oper,X    76    2     6
        # absolute      ROR oper      6E    3     6
        # absolute,X    ROR oper,X    7E    3     7
        address = None

        if (op_code == 0x6A): # accumulator
            carryOut = True if (self._a&0x01 > 0) else False
            self._a = ((self._a>>1) + (0x80 if (self._carry) else 0))&0xFF
            self._carry = carryOut
            self._negative = self._a&0x80 > 0
            self._zero = self._a == 0
            self.instruction_cycles = 2
            return
        elif (op_code == 0x66): # zeropage
            address = self._get_address_at_zeropage()
            self.instruction_cycles = 5
        elif (op_code == 0x76): # zeropage,X
            address = self._get_address_at_zeropage_x()
            self.instruction_cycles = 6
        elif (op_code == 0x6E): # absolute
            address = self._get_address_at_absolute()
            self.instruction_cycles = 6
        elif (op_code == 0x7E): # absolute,X
            address = self._get_address_at_absolute_x()
            self.instruction_cycles = 7
        else:
            raise RuntimeError(f"Unknown op code: {op_code}")            

        value = self._system.mmu.read_byte(address)
        carryOut = True if (value&0x01 > 0) else False
        value = ((value>>1) + (0x80 if (self._carry) else 0))&0xFF
        self._carry = carryOut
        self._system.mmu.write_byte(address, value)
        self._negative = value&0x80 > 0
        self._zero = value == 0

    def RTI(self, op_code):
        # Return from Interrupt
        # pull SR, pull PC                 N Z C I D V
        #                                  from stack
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # implied       RTI           40    1     6
        self._set_status_flag(self.pull())
        pc_lo = self.pull()
        pc_hi = self.pull()
        self._pc = ((pc_hi<<8) + pc_lo)&0xFFFF
        self.instruction_cycles = 6

    def RTS(self, op_code):
        # Return from Subroutine
        # pull PC, PC+1 -> PC              N Z C I D V
        #                                  - - - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # implied       RTS           60    1     6        
        pc_lo = self.pull()
        pc_hi = self.pull()
        print(f"hi: {hex(pc_hi)} / lo: {hex(pc_lo)}")
        self._pc = ((pc_hi<<8) + pc_lo)&0xFFFF
        self.instruction_cycles = 6

    def SBC(self, op_code):
        # Subtract Memory from Accumulator with Borrow
        # A - M - C -> A                   N Z C I D V
        #                                  + + + - - +
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # immediate     SBC #oper     E9    2     2
        # zeropage      SBC oper      E5    2     3
        # zeropage,X    SBC oper,X    F5    2     4
        # absolute      SBC oper      ED    3     4
        # absolute,X    SBC oper,X    FD    3     4*
        # absolute,Y    SBC oper,Y    F9    3     4*
        # (indirect,X)  SBC (oper,X)  E1    2     6
        # (indirect),Y  SBC (oper),Y  F1    2     5*
        value = None
        if (op_code == 0xE9): # immediate
            value = self._get_next_byte()
            self.instruction_cycles = 2
        elif (op_code == 0xE5): # zeropage
            value = self._get_value_at_zeropage()
            self.instruction_cycles = 3
        elif (op_code == 0xF5): # zeropage,X
            value = self._get_value_at_zeropage_x()
            self.instruction_cycles = 4
        elif (op_code == 0xED): # absolute
            value = self._get_value_at_absolute()
            self.instruction_cycles = 4
        elif (op_code == 0xFD): # absolute,X
            value = self._get_value_at_absolute_x()
            self.instruction_cycles = 4
        elif (op_code == 0xF9): # absolute,Y
            value = self._get_value_at_absolute_y()
            self.instruction_cycles = 4
        elif (op_code == 0xE1): # (indirect,X)
            value = self._get_value_at_indirect_x()
            self.instruction_cycles = 6
        elif (op_code == 0xF1): # (indirect),Y
            value = self._get_value_at_indirect_y()
            self.instruction_cycles = 5
        else:
            raise RuntimeError(f"Unknown op code: {op_code}")

        # Invert value and run through same logic as ADC.
        value ^= 0xFF

        result = self._a + value + (1 if self._carry == True else 0)

        self._carry = result > 0xFF

        # More info on source: https://stackoverflow.com/a/29224684
        self._overflow = ~(self._a ^ value) & (self._a ^ result) & 0x80

        self._a = result&0xFF

        self._negative = self._a&0x80 > 1
        self._zero = self._a == 0

    def SEC(self, op_code):
        # Set Carry Flag
        # 1 -> C                           N Z C I D V
        #                                  - - 1 - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # implied       SEC           38    1     2
        self._carry = True
        self.instruction_cycles = 2

    def SED(self, op_code):
        # Set Decimal Flag
        # 1 -> D                           N Z C I D V
        #                                  - - - - 1 -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # implied       SED           F8    1     2
        self._decimal_mode = True
        self.instruction_cycles = 2

    def SEI(self, op_code):
        # Set Interrupt Disable Status
        # 1 -> I                           N Z C I D V
        #                                  - - - 1 - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # implied       SEI           78    1     2
        self._interrupt_disable = True
        self.instruction_cycles = 2

    def STA(self, op_code):
        # Store Accumulator in Memory
        # A -> M                           N Z C I D V
        #                                  - - - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # zeropage      STA oper      85    2     3
        # zeropage,X    STA oper,X    95    2     4
        # absolute      STA oper      8D    3     4
        # absolute,X    STA oper,X    9D    3     5
        # absolute,Y    STA oper,Y    99    3     5
        # (indirect,X)  STA (oper,X)  81    2     6
        # (indirect),Y  STA (oper),Y  91    2     6
        address = None

        if (op_code == 0x85): # zeropage
            address = self._get_address_at_zeropage()
            self.instruction_cycles = 3
        elif (op_code == 0x95): # zeropage,X            
            address = self._get_address_at_zeropage_x()
            self.instruction_cycles = 4
        elif (op_code == 0x8D): # absolute
            address = self._get_address_at_absolute()
            self.instruction_cycles = 4
        elif (op_code == 0x9D): # absolute,X
            address = self._get_address_at_absolute_x()
            self.instruction_cycles = 5
        elif (op_code == 0x99): # absolute,Y
            address = self._get_address_at_absolute_y()
            self.instruction_cycles = 5
        elif (op_code == 0x81): # (indirect,X)
            address = self._get_address_at_indirect_x()
            self.instruction_cycles = 6
        elif (op_code == 0x91): # (indirect),Y
            address = self._get_address_at_indirect_y()
            self.instruction_cycles = 6
        else:
            raise RuntimeError(f"Unknown op code: {op_code}")

        self._system.mmu.write_byte(address, self._a)

    def STX(self, op_code):
        # Store Index X in Memory
        # X -> M                           N Z C I D V
        #                                  - - - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # zeropage      STX oper      86    2     3
        # zeropage,Y    STX oper,Y    96    2     4
        # absolute      STX oper      8E    3     4
        address = None
        if (op_code == 0x86): # zeropage
            address = self._get_address_at_zeropage()
            self.instruction_cycles = 3
        elif (op_code == 0x96): # zeropage,Y
            address = self._get_address_at_zeropage_y()            
            self.instruction_cycles = 4
        elif (op_code == 0x8E): # absolute
            address = self._get_address_at_absolute()
            self.instruction_cycles = 4
        else:
            raise RuntimeError(f"Unknown op code: {op_code}")

        self._system.mmu.write_byte(address, self._x)

    def STY(self, op_code):
        # Sore Index Y in Memory
        # Y -> M                           N Z C I D V
        #                                  - - - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # zeropage      STY oper      84    2     3
        # zeropage,X    STY oper,X    94    2     4
        # absolute      STY oper      8C    3     4
        address = None
        if (op_code == 0x84): # zeropage
            address = self._get_address_at_zeropage()
            self.instruction_cycles = 3
        elif (op_code == 0x94): # zeropage,X
            address = self._get_address_at_zeropage_x()
            self.instruction_cycles = 4
        elif (op_code == 0x8C): # absolute
            address = self._get_address_at_absolute()
            self.instruction_cycles = 4
        else:
            raise RuntimeError(f"Unknown op code: {op_code}")

        self._system.mmu.write_byte(address, self._y)

    def TAX(self, op_code):
        # Transfer Accumulator to Index X
        # A -> X                           N Z C I D V
        #                                  + + - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # implied       TAX           AA    1     2
        self._x = self._a
        self._negative = (self._x>>7) > 0
        self._zero = self._x == 0
        self.instruction_cycles = 2

    def TAY(self, op_code):
        # Transfer Accumulator to Index Y
        # A -> Y                           N Z C I D V
        #                                  + + - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # implied       TAY           A8    1     2
        self._y = self._a
        self._negative = (self._y>>7) > 0
        self._zero = self._y == 0
        self.instruction_cycles = 2

    def TSX(self, op_code):
        # Transfer Stack Pointer to Index X
        # SP -> X                          N Z C I D V
        #                                  + + - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # implied       TSX           BA    1     2
        self._x = self._sp
        self._negative = (self._x>>7) > 0
        self._zero = self._x == 0
        self.instruction_cycles = 2

    def TXA(self, op_code):
        # Transfer Index X to Accumulator
        # X -> A                           N Z C I D V
        #                                  + + - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # implied       TXA           8A    1     2
        self._a = self._x
        self._negative = (self._a>>7) > 0
        self._zero = self._a == 0
        self.instruction_cycles = 2

    def TXS(self, op_code):
        # Transfer Index X to Stack Register
        # X -> SP                          N Z C I D V
        #                                  - - - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # implied       TXS           9A    1     2
        self._sp = self._x
        self.instruction_cycles = 2

    def TYA(self, op_code):
        # Transfer Index Y to Accumulator
        # Y -> A                           N Z C I D V
        #                                  + + - - - -
        # addressing    assembler    opc  bytes  cyles
        # --------------------------------------------
        # implied       TYA           98    1     2
        self._a = self._y
        self._negative = (self._a>>7) > 0
        self._zero = self._a == 0
        self.instruction_cycles = 2