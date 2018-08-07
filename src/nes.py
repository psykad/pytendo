from cpu import CPU
from mmu import MMU
from cartridge import Cartridge
import time

class NES:
    def __init__(self):
        self.cpu = CPU(self)
        self.mmu = MMU(self)
        self.cartridge = None
        self.ram = [0xFF] * 2048

        # TODO: Initialize 2KB internal RAM

    def start(self):        
        if (self.cartridge is None):
            raise RuntimeError("No ROM loaded!")

        self.cpu.reset()

        # TODO: Create proper execution loop.
        while True:
            self.frame()
            time.sleep(0.016)


    def frame(self):
        self.cpu.step()

    def load_cartridge(self, filename):
        self.cartridge = Cartridge(filename)