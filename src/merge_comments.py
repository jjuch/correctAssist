import os
import json 
from src import path_to_cwd, template_dir, template_file, Q_A_file, data_dir, student_data_dir
def Merge(path_to_comp):
    """
    In place operation, merges the comments
    """

    path_to_current_students = os.path.join(path_to_cwd, data_dir, student_data_dir)
    path_to_current_Q_A = os.path.join(path_to_cwd, template_dir, Q_A_file)

    student_files = [student_json for student_json in os.listdir(path_to_current_students) if student_json.endswith('.json')]

    path_to_students = os.path.join(path_to_comp, data_dir, student_data_dir)
    path_to_Q_A = os.path.join(path_to_comp,template_dir, Q_A_file)
    
    # Merge student files
    for student in student_files:
        student = student.replace("'", '"')

        path_to_current_student = os.path.join(path_to_current_students, student)
        with open(path_to_current_student, 'r') as stc:
            current_student = json.load(stc)
        path_to_student = os.path.join(path_to_students, student)
        with open(path_to_student, 'r') as st:
            student_file = json.load(st)
        for k in current_student.keys():
            for i in student_file[k]:
                if i not in current_student[k]:
                    current_student[k].append(i)
        with open(path_to_current_student, 'w') as stc:
            json.dump(current_student, stc, indent=4)

    # Merge Q_A files
    with open(path_to_Q_A, 'r') as com:
        extra_comments = json.load(com)
    with open(path_to_current_Q_A, 'r') as comc:
        own_comments = json.load(comc)
    for k in own_comments.keys():
        own_comments[k].update(extra_comments[k])
    with open(path_to_current_Q_A, 'w') as updated_qa:
        json.dump(own_comments, updated_qa)

    