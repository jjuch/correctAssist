import os
from collections import OrderedDict

from src import template_file, template_dir, Q_A_file, data_dir

def create_template(path_template_dir):
    os.mkdir(path_template_dir)
    with open(os.path.join(path_template_dir, template_file), 'x') as f:
        f.write("""
~> [correctAssist] Template: Create your template using the following structure

= This is the title
            
1. Question 1 //5

1. A. Question 1A //1

1. B. Question 1B //2

2. Question 2 //3
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
        max_total_score = 0.0
        for i in range(len(template)):
            sublevel, result, prescript, score = process_template_line(template[i])
            if result is not None:
                temp = dict(sublevel=sublevel, title=result, prescript=prescript, score=score)
                template_data[_ctr] = temp
                _ctr += 1
            if score is not None:
                max_total_score += float(score)
    return template_data, max_total_score
                


def process_template_line(_str):
    result = None
    sublevel = None
    prescript = None
    score = None
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
                prescript = _str[:last_idx + 1]
                result = _str[last_idx + 1:]
                result = result.lstrip()
                idx_score = result.find("//")
                if idx_score:
                    try:
                        score = float(result[idx_score + 2:])
                        result = result[0: idx_score]
                    except ValueError:
                        print("[Error] Something went wrong in the template. A score should be indicated by two backslashes and a number, e.g. '//5.4'.")
                        exit()

    return (sublevel, result, prescript, score)
