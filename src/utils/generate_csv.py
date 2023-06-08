import csv
import os
from json import load
def generate_csv(student_names, path_to_students, path_to_grades):
    
    first_row_OK = False
    csv_table = []
    for student_name in student_names:
        student_file_name = student_name.replace(' ','_') + '.json'
        student_path = os.path.join(path_to_students, student_file_name)
        with open(student_path, 'r') as sp:
            student_file = load(sp)

        # Row-by-row, add the student name and the grade for that respective question
        first_row = ['']
        student_row = [student_name]
        for question_id in student_file.keys():
            if first_row_OK == False:
                first_row.append(question_id)
        firs_row_OK = True
        student_row.append(student_file[question_id]['score'])
        csv_table.append(student_row)
    csv_table = first_row.append(csv_table)
    with open(path_to_grades,mode='w',encoding='UTF-8')as csv_file:
        csv_writer = csv.writer(csv_file)
        for i in csv_table:
            csv_writer.writerow(i)
        