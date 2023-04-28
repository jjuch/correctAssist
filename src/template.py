import os

from src import template_file, template_dir, Q_A_file, data_dir
from src.utils.template_manipulation import read_template, create_template
from collections import OrderedDict

class Template():
    def __init__(self, cwd):
        """
        cwd: current working directory
        """
        self.cwd = cwd
        path_template_dir = os.path.join(self.cwd, template_dir)
        init_done = os.path.exists(path_template_dir)
        self.template_data = []
        if init_done:
            print("[Info] The template files exist and are being loaded...")
            self.template_data = read_template(path_template_dir)
        else:
            create_template(path_template_dir)

    def __str__(self) -> str:
        output = """
        * cwd: {}
        * template: 
         """.format(self.cwd)
        if isinstance(self.template_data, OrderedDict):
            for key, value in self.template_data.items():
                output += str(key) +  " -> " + str(value) + "\n         "
        return output
      
    

    def load_template(self):
        pass


    def show_form(self):
        pass