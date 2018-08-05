import os
from nes import NES

# Get current directory for application.        
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

filename = os.path.join(__location__, "roms\\Donkey Kong.nes")

emulator = NES()
emulator.load_cartridge(filename)
emulator.start()