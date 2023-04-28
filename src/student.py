class Student:
    def __init__(self, student_name):
        self.corrections = self.load_student_data(student_name)

    def load_student_data(self, student_name):
        # open json file van student en stokeer de huidige correcties
        pass