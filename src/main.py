import os

from src.template import Template
from src.gui import GUI

# Initialize Form
cwd = os.getcwd()
template = Template(cwd)
print(template)

GUI(template)
