import os

class Student:
    def __init__(self, student_name, student_path=None):
        self.add_student(student_name, student_path)
        self.corrections = self.load_student_data(student_name)

    def add_student(self, student_name, student_path):
        file_name = student_name + ".json"
        try:
            with open(os.path.join(student_path, file_name), 'x') as f:
                f.write("") 
                #TODO: { "0": [],
                #       "1": [],
                #       ...
                #       }
            
        except FileExistsError as error:
            print("[Error] This student already exists. Please select the student from the existing students.")

    def load_student_data(self, student_name):
        # open json file van student en stokeer de huidige correcties
        pass