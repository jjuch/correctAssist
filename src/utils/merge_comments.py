from json import dump, load
import os
from src import *

def merge(path_to_comp):
    """
    In place operation, merges the comments
    """

    path_to_current_students = os.path.join(path_to_cwd, data_dir, student_data_dir)
    path_to_current_Q_A = os.path.join(path_to_cwd, template_dir, Q_A_file)
    path_to_students = os.path.join(path_to_comp, data_dir, student_data_dir)
    path_to_Q_A = os.path.join(path_to_comp, template_dir, Q_A_file)

    current_student_files = [student_json for student_json in os.listdir(path_to_current_students) if student_json.endswith('.json')]
    student_files = [student_json for student_json in os.listdir(path_to_students) if student_json.endswith('.json')]

    if len(current_student_files) < len(student_files):
        print("[Warning] the imported list of students contains more students.")
        print("The names of the students that were not included in the current list are: ")
        forgotten_students = set(student_files)-set(current_student_files)
        for name in forgotten_students: 
            print("* ", name.replace(".json", ""))
    elif len(current_student_files) > len(student_files):
        print("[Warning] the imported list of students contains less students.")
        print("The names of the students that were not included in the imported list are: ")
        forgotten_students = set(current_student_files)-set(student_files)
        for name in forgotten_students: 
            print("* ", name.replace(".json", ""))
    
    # Merge student files
    for student in current_student_files:
        # student = student.replace("'", '"')
        try:
            path_to_current_student = os.path.join(path_to_current_students, student)
            with open(path_to_current_student, 'r') as stc:
                current_student = load(stc)
            path_to_student = os.path.join(path_to_students, student)
            with open(path_to_student, 'r') as st:
                student_file = load(st)
            for question_id in current_student.keys():
                for key in current_student[question_id].keys():
                    if key == "comments":
                        try: 
                            for comment_id in student_file[question_id][key]:
                                if comment_id not in current_student[question_id][key]:
                                    current_student[question_id][key].append(comment_id)
                        except:
                            continue
                    elif key == "score":
                        try:
                            if current_student[question_id][key] is None:
                                current_student[question_id][key] = student_file[question_id][key]
                        except:
                            continue
            with open(path_to_current_student, 'w') as stc:
                dump(current_student, stc, indent=4)
        except FileNotFoundError:
            print("Student does not exist in the merge file.")
    
    
    # Merge Q_A files
    with open(path_to_Q_A, 'r') as com:
        extra_comments = load(com)
    with open(path_to_current_Q_A, 'r') as comc:
        own_comments = load(comc)
    for k in own_comments.keys():
        try:
            own_comments[k].update(extra_comments[k])
        except:
            pass
    with open(path_to_current_Q_A, 'w') as updated_qa:
        dump(own_comments, updated_qa)