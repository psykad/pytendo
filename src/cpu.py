class CPU:
    def __init__(self, system):
        self._system = system        

    def reset(self):
        # Program Counter 16-bit
        # Load WORD from reset vector $FFFC
        self._pc = self._system.mmu.read_word(0xFFFC)

        # Stack Pointer 8-bit, ranges from 0x0100 to 0x01FF
        self._sp = 0x01FF

        # Accumulator 8-bit
        self._a = 0x00

        # Index Register X 8-bit
        self._x = 0x0000

        # Index Register Y 8-bit
        self._y = 0x0000

        #### Processor Status Flags

        # Carry - set if the last operation caused an overflow from bit 7, or an underflow from bit 0.
        self._carry = False

        # Zero - the result of the last operation was zero.
        self._zero  = False

        # Interrupt Disable - set if the program executed an SEI instruction. It's cleared with a CLI instruction.
        self._interruptDisable = True   

        # Decimal Mode - Enables binary coded decimal arithmetic. Enabled with SED instruction, disabled with CLD instruction.
        self._decimalMode = False # TODO: Verify if this is needed for the NES CPU. It seems like it's not included with its version of the 6502.

        # Break Command - Set when a BRK instruction is hit and an interrupt has been generated to process it.
        self._breakCommand = False

        # Overflow - Set during arithmetic operations if the result has yielded an invalid 2's compliment result.
        self._overflow = False

        # Negative - Set if the result of the last operation had bit 7 set to a one.
        self._negative = False