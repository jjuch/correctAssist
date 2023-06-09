import csv
import os
from json import load

def generate_csv(student_names, path_to_students, path_to_grades, template):
    csv_table = []

    # Create headers
    header_prescripts = []
    header_titles = []
    for template_id in template.template_data.keys():
        prescript = template.template_data[template_id]['prescript']
        title = template.template_data[template_id]['title']
        if prescript is not None:
            header_prescripts.append(prescript)
            header_titles.append(title)
    header_prescripts.append(None)
    header_titles.append('Total')

    csv_table.append(header_prescripts)
    csv_table.append(header_titles)

    # Append student scores
    for student_name in student_names:
        student_file_name = student_name + '.json'
        student_path = os.path.join(path_to_students, student_file_name)
        with open(student_path, 'r') as sp:
            student_file = load(sp)

        # Row-by-row, add the student name and the grade for that respective question
        student_row = [student_name]
        for question_id in student_file.keys():
            if question_id != 'total_score':
                student_row.append(float(student_file[question_id]['score']))
            else:
                student_row.append(float(student_file[question_id]))
        csv_table.append(student_row)
    
    # Write to csv
    with open(path_to_grades,mode='w',encoding='UTF-8')as csv_file:
        csv_writer = csv.writer(csv_file)
        for i in csv_table:
            csv_writer.writerow(i)
        