from cpu import CPU
from mmu import MMU
from cartridge import Cartridge

class NES:
    def __init__(self):
        self.cpu = CPU(self)
        self.mmu = MMU(self)
        self.cartridge = None

        # TODO: Initialize 2KB internal RAM

    def start(self):        
        if (self.cartridge is None):
            raise RuntimeError("No ROM loaded!")

        self.cpu.reset()

        raise NotImplementedError()

    def load_cartridge(self, filename):
        self.cartridge = Cartridge(filename)