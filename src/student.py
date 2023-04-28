class Student:
    def __init__(self, student_name):
        self.corrections = self.load_student_data(student_name)

    def load_student_data(self, student_name):
        # open json file van student en stokeer de huidige correcties
        pass

    def remove_comment(self, question_id, comment_id):
        pass

    def add_comment(self, question_id, comment_id):
        '''
        - questions should have an id: "0", "1", ... (ordereddict <template>)
            - init_Student: add structure directly (new student -> "0":[], "1":[] ...)

        '''
        pass


