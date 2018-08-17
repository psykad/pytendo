class MMU:    
    def __init__(self, system):
        self._system = system                

    def read_byte(self, address):
        # Check if memory read is outside addressable memory range.
        if (address < 0x0000 or address > 0xFFFF):
            raise RuntimeError(f"Segfault read @ ${hex(address)}")

        # 2KB Internal RAM
        if (address >= 0x0000 and address <= 0x07FF):
            return self._system.ram[address]

        # 2KB Internal RAM Mirror #1
        if (address >= 0x0800 and address <= 0x0FFF):
            return self._system.ram[address-0x0800]

        # 2KB Internal RAM Mirror #2
        if (address >= 0x1000 and address <= 0x17FF):
            return self._system.ram[address-0x1000]

        # 2KB Internal RAM Mirror #3
        if (address >= 0x1800 and address <= 0x1FFF):            
            return self._system.ram[address-0x1800]

        # PPU registers
        if (address >= 0x2000 and address <= 0x2007):
            return self._system.ppu.read_byte(address)

        # Mirrors of PPU registers (repeat every 8 bytes)
        if (address >= 0x2008 and address <= 0x3FFF):
            raise NotImplementedError(f"Read @ Address: ${hex(address)}")

        # APU and I/O registers
        if (address >= 0x4000 and address <= 0x4017):
            raise NotImplementedError(f"Read @ Address: ${hex(address)}")

        # APU and I/O functionality that is normally disabled
        if (address >= 0x4018 and address <= 0x401F):
            raise NotImplementedError(f"Read @ Address: ${hex(address)}")

        # Cartridge space: PRG ROM, PRG RAM, and mapper registers
        if (address >= 0x4020 and address <= 0xFFFF):
            return self._system.cartridge.read_byte(address)

    def read_word(self, address):
        return (self.read_byte(address+1)<<8) + self.read_byte(address)

    def write_byte(self, address, byte):
        # Check if memory read is outside addressable memory range.
        if (address < 0x0000 or address > 0xFFFF):
            raise RuntimeError(f"Segfault write @ ${hex(address)}")

        print(f"MMU: Write {hex(address)} / {hex(byte)}")

        # 2KB Internal RAM
        if (address >= 0x0000 and address <= 0x07FF):
            self._system.ram[address] = byte
            return

        # 2KB Internal RAM Mirror #1
        if (address >= 0x0800 and address <= 0x0FFF):
            self._system.ram[address-0x0800] = byte
            return

        # 2KB Internal RAM Mirror #2
        if (address >= 0x1000 and address <= 0x17FF):
            self._system.ram[address-0x1000] = byte
            return

        # 2KB Internal RAM Mirror #3
        if (address >= 0x1800 and address <= 0x1FFF):
            self._system.ram[address-0x1800] = byte
            return

        # PPU registers
        if (address >= 0x2000 and address <= 0x2007):
            self._system.ppu.write_byte(address, byte)
            return

        # Mirrors of PPU registers (repeat every 8 bytes)
        if (address >= 0x2008 and address <= 0x3FFF):
            raise NotImplementedError(f"Write @ Address: ${hex(address)} / Byte: {hex(byte)}")

        # APU and I/O registers
        if (address >= 0x4000 and address <= 0x4017):
            raise NotImplementedError(f"Write @ Address: ${hex(address)} / Byte: {hex(byte)}")

        # APU and I/O functionality that is normally disabled
        if (address >= 0x4018 and address <= 0x401F):
            raise NotImplementedError(f"Write @ Address: ${hex(address)} / Byte: {hex(byte)}")

        # Cartridge space: PRG ROM, PRG RAM, and mapper registers
        if (address >= 0x4020 and address <= 0xFFFF):
            self._system.cartridge.write_byte(address, byte)