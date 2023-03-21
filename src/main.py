import os

from src.template import Template

# Initialize Form
cwd = os.getcwd()
template = Template(cwd)
print(template)
