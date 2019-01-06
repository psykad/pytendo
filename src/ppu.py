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

        self.clock = 0
        self.scanline = -1

    def read_byte(self, address):        
        if (address == self.PPUSTATUS):
            value = self.registers[self.PPUSTATUS]
            self.registers[self.PPUSTATUS] &= ~0x80 # Clear VBlank
            return value
        elif (address == self.OAMDATA):
            return self.registers[self.OAMDATA]
        elif (address == self.PPUSCROLL):
            return self.registers[self.PPUSCROLL]
        elif (address == self.PPUDATA):
            value = self.ram[self.registers[self.PPUADDR]] = byte
            increment = 32 if (self.registers[self.PPUCTRL]&0x04 > 0) else 1
            self.registers[self.PPUADDR] = (self.registers[self.PPUADDR]+increment)&0xFF
            return value

        raise RuntimeError(f"Unknown Read @ Address: ${hex(address)}")

    def write_byte(self, address, byte):
        # print(f"PPU: Write {hex(address)} / {hex(byte)}")
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
            # 16-bits will be written to this register before accessing PPUDATA.
            # MSB written first, then LSB 2nd.
            value = ((self.registers[self.PPUADDR]<<8)+byte)&0xFFFF
            print(f"ppuaddress byte ${hex(byte)} value ${hex(value)}")
            self.registers[self.PPUADDR] = value
            return
        elif (address == self.PPUDATA):
            self.ram[self.registers[self.PPUADDR]] = byte
            increment = 32 if (self.registers[self.PPUCTRL]&0x04 > 0) else 1
            self.registers[self.PPUADDR] = (self.registers[self.PPUADDR]+increment)&0xFF
            return
        elif (address == self.OAMDMA):
            self.registers[self.OAMDMA] = byte
            return

        raise RuntimeError(f"Unknown Write @ Address: ${hex(address)} / Byte: {hex(byte)}")

    def _read_byte(self, address):
        return

    def _write_byte(self, address, byte):
        return

    def step(self, cycles):
        # Note: 1 CPU cycle = 3 PPU cycles
        self.clock = self.clock + (cycles * 3)        

        # A scanline lasts for 341 PPU cycles.
        # Each PPU cycle is one pixel.
        # There are 262 scanlines per frame.

        if (self.clock >= 341):
            self.clock -= 341
            if (self.scanline == -1 or self.scanline == 261):
                # Pre-render scanline
                self.registers[self.PPUSTATUS] &= ~0x80 # Clear VBlank
            elif (self.scanline >= 0 and self.scanline <= 239):
                # Visible scanline
                pass
            elif (self.scanline == 240):
                # Post-render scanline
                pass
            elif (self.scanline == 241):
                # Vertical blanking lines
                self.registers[self.PPUSTATUS] |= 0x80 # Enable VBlank
            elif (self.scanline == 260):
                self.scanline = -2

            self.scanline += 1