class Cartridge:
    def __init__(self, filename):
        self._filename = filename

        # Load ROM data from file.
        self._rom = open(filename, "rb").read()
        
        # Check first 3 bytes for the letters 'NES'
        if (self._rom[0] != 78 or self._rom[1] != 69 or self._rom[2] != 83):
            raise RuntimeError("Not a valid NES ROM!")            

        # Number of 16k program ROM pages.
        self._total_program_rom_pages = self._rom[4]

        # Number of 8k character ROM pages.
        self._total_character_rom_pages = self._rom[5]

        # Byte 6
        self._mapper_number = (self._rom[6]>>4)&0x0F # Bits 4-7 are lower nybble of mapper number.
        self._four_screen_mode = True if self._rom[6]&0x08 == 0x08 else False
        self._trainer = True if self._rom[6]&0x04 == 0x04 else False
        self._has_battery = True if self._rom[6]&0x02 == 0x02 else False
        self._mirroring = True if self._rom[6]&0x01 == 0x01 else False

        # Byte 7
        self._mapper_number |= (self._rom[7]&0xF0) # Bits 4-7 are upper nyblle of mapper number.
        self._nes_2_Format = True if (self._rom[7]&0x0C)>>2 == 0b10 else False # If the two bits equal binary 10, use NES 2.0 rules.

        self._program_rom_size = (self._rom[9]&0x0F)<<4 # PRG ROM size
        self._character_rom_size = self._rom[9]&0xF0 # CHR ROM size

        # TODO: Byte 8
        # TODO: Byte 9
        # TODO: Byte 10
        # TODO: Byte 11
        # TODO: Byte 12
        # TODO: Byte 13
        # TODO: Byte 14
        # TODO: Byte 15, not needed? Reserved. Byte should be zero.

        # TODO: Verify file size with specified memory characteristics.

        # Initialize mapper
        if (self._mapper_number == 0):
            self._mapper = NROM(self, self._rom)
        else:
            raise RuntimeError(f"No mapper found for ID {self._mapper_number}")

        print(f"File loaded {filename}")
        print(f"Program ROM pages: {self._total_program_rom_pages}")
        print(f"Character ROM pages: {self._total_character_rom_pages}")
        print(f"Mapper #: {self._mapper_number}")
        print(f"Four screen mode: {self._four_screen_mode}")
        print(f"Trainer: {self._trainer}")
        print(f"Has battery: {self._has_battery}")
        print(f"Mirroring: {self._mirroring}")

    def read_byte(self, address):
        return self._mapper.read_byte(address)

    def write_byte(self, address, byte):
        raise NotImplementedError()


###############################################################################
# Mapper base 
###############################################################################
class Mapper:
    def __init__(self):
        pass

    def read_byte(self, address):
        raise NotImplementedError()

    def write_byte(self, address, byte):
        raise NotImplementedError()


###############################################################################
# iNES Mapper ID: 0
# Name: NROM
# PRG ROM capacity: 16K or 32K
# PRG ROM window: n/a
# PRG RAM capacity: 2K or 4K in Family Basic only
# PRG RAM window: n/a
# CHR capacity: 8K
# CHR window: n/a
# Nametable mirroring: Fixed H or V, controlled by solder pads (*V only)
# Bus conflicts: Yes
# IRQ: No
# Audio: No
###############################################################################
class NROM(Mapper):
    def __init__(self, cartridge, rom):
        self._rom = rom
        self._cartridge = cartridge

        # Slice ROM into banks.
        rom_offset = 528 if self._cartridge._trainer else 16
        self._prog_rom_banks = [0xFF] * self._cartridge._total_character_rom_pages

        for bank in (0, self._cartridge._total_character_rom_pages-1):
            self._prog_rom_banks[bank] = self._rom[rom_offset + (16384 * bank):]

        self._prog_ram_banks = []

    def read_byte(self, address):
        # Family Basic only: PRG RAM, mirrored as necessary to fill entire 8KB window, write protectable with external switch.
        if (address >= 0x6000 and address <= 0x7FFF):
            return self._prog_ram_banks[0][address - 0x6000]

        # First 16KB of ROM.
        if (address >= 0x8000 and address <= 0xBFFF):
            return self._prog_rom_banks[0][address - 0x8000]

        # Last 16KB of ROM.
        if (address >= 0xC000 and address <= 0xFFFF):
            # If there's only one page 16K of ROM, mirror bank 0 here.
            if (self._cartridge._total_program_rom_pages == 1):
                return self._prog_rom_banks[0][address - 0xC000]
            else:
                return self._prog_rom_banks[1][address - 0xC000]

    def write_byte(self, address, byte):
        raise NotImplementedError()