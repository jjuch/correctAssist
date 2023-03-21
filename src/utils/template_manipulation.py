import os
from collections import OrderedDict

from src import template_file, template_dir, Q_A_file, data_dir

def create_template(path_template_dir):
    os.mkdir(path_template_dir)
    with open(os.path.join(path_template_dir, template_file), 'x') as f:
        f.write("""
~> [correctAssist] Template: Create your template using the following structure

= This is the title
            
1. Question 1

1. A. Question 1A

1. B. Question 1B

2. Question 2
            """)
        print("[Info] An empty template file is created...")
    with open(os.path.join(path_template_dir, Q_A_file), 'x') as f:
        f.write("{}")
        print("[Info] An empty Q\&A file is created...")


def read_template(path_template_dir):
    template_data = OrderedDict()
    with open(os.path.join(path_template_dir, template_file), 'r') as f:
        template = f.readlines()
        _ctr = 0 
        for i in range(len(template)):
            sublevel, result = process_template_line(template[i])
            if result is not None:
                temp = dict(sublevel=sublevel, title=result)
                template_data[_ctr] = temp
                _ctr += 1
    
    # for key, value in template_data.items():
    #     print(key, " -> ", value)
    return template_data
                


def process_template_line(_str):
    result = None
    sublevel = None
    _str = _str.lstrip()
    _str = _str.replace("\n", "")
    # remove empty lines
    if len(_str) != 0:
        # remove comments
        if _str[0] != '~':
            # process title
            if _str[0] ==  '=':
                result = _str[1:]
                sublevel = 0
            else:
                _idx = 0
                _ctr = 0
                last_idx = 0
                while _idx != -1:
                    last_idx = _idx
                    _idx = _str.find('.', _idx + 1, len(_str) - 1)
                    _ctr += 1
                sublevel = _ctr - 1
                result = _str[last_idx + 1:]
                result = result.lstrip()

    return (sublevel, result)
