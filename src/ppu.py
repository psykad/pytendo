class PPU:
    # More info on NES registers: http://wiki.nesdev.com/w/index.php/PPU_registers
    PPUCTRL   = 0x2000
    PPUMASK   = 0x2001
    PPUSTATUS = 0x2002
    OAMADDR   = 0x2003
    OAMDATA   = 0x2004
    PPUSCROLL = 0x2005
    PPUADDR   = 0x2006
    PPUDATA   = 0x2007
    OAMDMA    = 0x4014

    def __init__(self, system):
        self._system = system
        self.ram = [0xFF] * 16384 # 16kB of video RAM.
        self.oam = [0xFF] * 256   # 256 bytes of OAM RAM

        self.registers = {
            0x2000: 0x00, # PPUCTRL
            0x2001: 0x00, # PPUMASK
            0x2002: 0x00, # PPUSTATUS
            0x2003: 0x00, # OAMADDR
            0x2004: 0x00, # OAMDATA
            0x2005: 0x00, # PPUSCROLL
            0x2006: 0x00, # PPUADDR
            0x2007: 0x00, # PPUDATA
            0x4014: 0x00  # OAMDMA
        }

    def read_byte(self, address):        
        if (address == self.PPUSTATUS):
            return self.registers[self.PPUSTATUS]
        elif (address == self.OAMDATA):
            return self.registers[self.OAMDATA]
        elif (address == self.PPUDATA):
            return self.registers[self.PPUDATA]

        raise RuntimeError(f"Unknown Read @ Address: ${hex(address)}")

    def write_byte(self, address, byte):
        print(f"PPU: Write {hex(address)} / {hex(byte)}")
        if (address == self.PPUCTRL):
            self.registers[self.PPUCTRL] = byte
            return
        elif (address == self.PPUMASK):
            self.registers[self.PPUMASK] = byte
            return
        elif (address == self.OAMADDR):
            self.registers[self.OAMADDR] = byte
            return
        elif (address == self.OAMDATA):
            self.registers[self.OAMDATA] = byte
            return
        elif (address == self.PPUSCROLL):
            self.registers[self.PPUSCROLL] = byte
            return
        elif (address == self.PPUADDR):
            self.registers[self.PPUADDR] = byte
            return
        elif (address == self.PPUDATA):
            self.registers[self.PPUDATA] = byte
            return
        elif (address == self.OAMDMA):
            self.registers[self.OAMDMA] = byte
            return

        raise RuntimeError(f"Unknown Write @ Address: ${hex(address)} / Byte: {hex(byte)}")