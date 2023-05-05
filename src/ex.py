import json 
import os
## Declare global variables
# template variables
template_dir = "template"
template_file = "template.txt"
Q_A_file = "Q_A.json"

path_to_cwd = os.getcwd() 
path_to_cwd = os.path.join(path_to_cwd, "..")
print(path_to_cwd)
# data variables
data_dir = "data"
student_data_dir = "students"

path_to_current_students = os.path.join(path_to_cwd, data_dir, student_data_dir)

path_to_current_Q_A = os.path.join(path_to_cwd,template_dir, Q_A_file)
student_files = [student_json for student_json in os.listdir(path_to_current_students) if student_json.endswith('.json')]
print(student_files)