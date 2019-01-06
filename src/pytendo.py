import os
from nes import NES
import pygame
from pygame.locals import *

import sys
from PyQt5 import QtWidgets

# Get current directory for application.        
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

filename = os.path.join(__location__, "roms\\Donkey Kong.nes")

emulator = NES()
emulator.load_cartridge(filename)
emulator.reset()
emulator.start()

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle("Pytendo")
        self.setGeometry(50, 50, 500, 300)

        #######################################################################
        # CPU Step Button
        #######################################################################
        self.step_cpu_button = QtWidgets.QPushButton("Step", self)
        self.step_cpu_button.setGeometry(10, 10, 75, 25)
        self.step_cpu_button.clicked.connect(self.step_cpu_button_clicked)
        
        #######################################################################
        # Program Counter Text Edit
        #######################################################################
        program_counter_label = QtWidgets.QLabel(self)
        program_counter_label.setText("Program Counter")
        program_counter_label.setGeometry(10, 40, 100, 25)
        self.program_counter_text = QtWidgets.QTextEdit(self)
        self.program_counter_text.setFontFamily('Monospace')
        self.program_counter_text.setGeometry(10, 60, 75, 25)

        #######################################################################
        # Stack Point Text Edit
        #######################################################################
        stack_pointer_label = QtWidgets.QLabel(self)
        stack_pointer_label.setText("Stack Pointer")
        stack_pointer_label.setGeometry(10, 90, 100, 25)
        self.stack_pointer_text = QtWidgets.QTextEdit(self)
        self.stack_pointer_text.setFontFamily('Monospace')
        self.stack_pointer_text.setGeometry(10, 110, 75, 25)

        #######################################################################
        # Register A Text Edit
        #######################################################################
        stack_pointer_label = QtWidgets.QLabel(self)
        stack_pointer_label.setText("Register A")
        stack_pointer_label.setGeometry(10, 140, 100, 25)
        self.register_a_text = QtWidgets.QTextEdit(self)
        self.register_a_text.setFontFamily('Monospace')
        self.register_a_text.setGeometry(10, 160, 75, 25)

        #######################################################################
        # Register X Text Edit
        #######################################################################
        stack_pointer_label = QtWidgets.QLabel(self)
        stack_pointer_label.setText("Register X")
        stack_pointer_label.setGeometry(10, 190, 100, 25)
        self.register_x_text = QtWidgets.QTextEdit(self)
        self.register_x_text.setFontFamily('Monospace')
        self.register_x_text.setGeometry(10, 210, 75, 25)

        #######################################################################
        # Register Y Text Edit
        #######################################################################
        stack_pointer_label = QtWidgets.QLabel(self)
        stack_pointer_label.setText("Register Y")
        stack_pointer_label.setGeometry(10, 240, 100, 25)
        self.register_y_text = QtWidgets.QTextEdit(self)
        self.register_y_text.setFontFamily('Monospace')
        self.register_y_text.setGeometry(10, 260, 75, 25)

        #######################################################################
        # NES 
        #######################################################################
        self.emulator = NES()
        self.emulator.load_cartridge(filename)
        self.emulator.reset()

        self.show()



    def step_cpu_button_clicked(self):
        self.emulator.step()
        self.program_counter_text.setText(format(self.emulator.cpu._pc,'x').upper())
        self.stack_pointer_text.setText(format(self.emulator.cpu._sp,'x').upper())
        self.register_a_text.setText(format(self.emulator.cpu._a,'x').upper())
        self.register_x_text.setText(format(self.emulator.cpu._x,'x').upper())
        self.register_y_text.setText(format(self.emulator.cpu._y,'x').upper())


app = QtWidgets.QApplication(sys.argv)
gui = Window()
pygame.init()
sys.exit(app.exec_())