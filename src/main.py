import os

from src.gui import GUI

# create a GUI
cwd = os.getcwd()
gui = GUI(cwd)
print(gui)
