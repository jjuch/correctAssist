import os
import json
import uuid
from src import path_to_cwd, template_file, template_dir, data_dir, student_data_dir
import csv


class Student:
    def __init__(self, student_name, template, student_path=None):
        self.template = template
        self.file_path_student = os.path.join(path_to_cwd, data_dir, student_data_dir, student_name + ".json")
        self.student_name = student_name
        self.add_student(student_name)

        # This variable will later on be used to update the corresponding student data
        self.corrections = self.load_student_data(student_name)

        


    def add_student(self, student_name):
        file_name = student_name + ".json"
        try:
            i = 0

            # Create the file
            with open(self.file_path_student, 'x') as f:
                f.write("{}")

            # Adapt the student file
            init_dict = {}
            for key, _ in self.template.template_data.items():
                init_dict.update({str(key): []})
            with open(self.file_path_student, 'w') as f:
                json.dump(init_dict, f)
            
        except FileExistsError as error:
            print("[Error] This student already exists. Please select the student from the existing students.")

    def load_student_data(self, student_name):
        print("load_student called")
        print(self.file_path_student)
        with open(self.file_path_student, 'r') as fps:
            student_dict = json.load(fps)
        print("new update", student_dict)
        return student_dict    
                   

    def remove_comment(self, question_id, comment_id):
        """
        Only for comments
        """
        print("remove_comment called")
        with open(self.file_path_student) as fps:
            student_dict = json.load(fps)
        if question_id not in student_dict.keys():
            student_dict.update({question_id: comment_id})
        else:
            # Avoid adding a comment twice
            if comment_id not in student_dict[question_id]:
                student_dict[question_id].append(comment_id)


    def add_comment(self, question_id, comment_id):
        """
        Q_A is not updated
        """
        print("add_comment called")
        with open(self.file_path_student) as fps:
            student_dict = json.load(fps)
        if question_id not in student_dict.keys():
            student_dict.update({question_id: comment_id})
        else:
            # Avoid adding a comment twice
            if comment_id not in student_dict[question_id]:
                student_dict[question_id].append(comment_id)
    
    def save_data(self):
        with open(self.file_path_student, 'x') as f:
            json.dump(self.corrections, f)
        print("Data saved successfully")

    
        


'''
- questions should have an id: "0", "1", ... (ordereddict <template>)
- init_student: add structure directly (new student -> "0":[], "1":[] ...)
- a student json file should only contain comment_ids, no actual comments
- think about a merging function (merge different )
'''


