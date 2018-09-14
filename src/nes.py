from cpu import CPU
from mmu import MMU
from ppu import PPU
from cartridge import Cartridge
import time

class NES:
    def __init__(self):
        self.cpu = CPU(self)
        self.mmu = MMU(self)
        self.ppu = PPU(self)
        self.cartridge = None
        self.ram = [0xFF] * 2048
        self._clock = 0

    def reset(self):
        self.cpu.reset()

    def start(self):        
        if (self.cartridge is None):
            raise RuntimeError("No ROM loaded!")

        self.cpu.reset()

        # TODO: Create proper execution loop.
        while True:
            self.frame()
            #time.sleep(0.016)

    def frame(self):
        self.step()                

    def step(self):
        self.cpu.step()        

    def consume_cycles(self, cycles):
        # Update clock with instruction cycles.
        self._clock = (self._clock+cycles)&0xFFFFFFFF

        self.ppu.step(cycles)

    def load_cartridge(self, filename):
        self.cartridge = Cartridge(filename)