import PySimpleGUI as sg
from json import load, dump
import os
from uuid import uuid4
import csv
from src import path_to_cwd, template_dir, template_file, Q_A_file, data_dir, student_data_dir, student_pdf_dir, __version__, __developers__, __year__
 
from src.utils.merge_comments import merge

from src.template import Template
from src.student import Student

class GUI():
    def __init__(self, cwd):
        self.template = Template()
        self.cwd = cwd
        self.student_data_full_dir = os.path.join(self.cwd, data_dir, student_data_dir)
        if not os.path.exists(self.student_data_full_dir):
            print("[Info] create a student data directory...")
            os.makedirs(self.student_data_full_dir)
        self.student_pdf_full_dir = os.path.join(self.cwd, data_dir, student_pdf_dir)
        if not os.path.exists(self.student_pdf_full_dir):
            print("[Info] create a student reports directory...")
            os.makedirs(self.student_pdf_full_dir)
        self.existing_student_data = [x.split('.')[0] for x in os.listdir(self.student_data_full_dir)] # remove extensions
        self.current_student = None
        if len(self.template.template_data) > 0:
            self.QA_dir = os.path.join(self.cwd, template_dir, Q_A_file)
            self.QA_data = None
            self.load_QA()
            self.show()
    
    def __str__(self):
        return self.template.__str__()

    def load_QA(self):  
        with open(self.QA_dir, 'r') as f:
            self.QA_data = load(f)

        # write questions structure if QA is empty
        if len(self.QA_data) == 0:
            init_dict = {}
            for key, _ in self.template.template_data.items():
                init_dict.update({str(key): {}})
            with open(self.QA_dir, 'w') as f:
                dump(init_dict, f)
            self.load_QA()


    def add_student(self, first_name, last_name, window=None):
        file_name_wo_extension = last_name.replace(" ", "") + "_" + first_name.replace(" ", "")
        if file_name_wo_extension not in self.existing_student_data:
            if self.current_student is not None:
                self.current_student.save_data(extra_info="The content of the former student has changed and is not saved yet.")
            self.current_student = Student(file_name_wo_extension, self.template, self.student_data_full_dir)
            self.clear_form(window)       
            self.existing_student_data.append(file_name_wo_extension)
            if window is not None:
                window["_ALL_STUDENTS_"].update((*self.existing_student_data,))
                window["_CURRENT_STUDENT_"].update(file_name_wo_extension)
                window.refresh()
        else:
            if window is not None:
                window["_CURRENT_STUDENT_"].update(file_name_wo_extension)
                window.refresh() 
                    
        
    def create_comments(self, question_id):
        current_comments_dict = self.QA_data[str(question_id)]
        no_comments_present = len(current_comments_dict) == 0
        comments = []
        comments.append([sg.Text("No answers yet.", visible=no_comments_present, key=('_DEFAULT_EMPTY_COMMENT_', question_id))])
        for key, value in current_comments_dict.items():
            comment = [sg.Col([
                        [
                            sg.Checkbox(value, key=('_CHECKBOX_COMMENT_', question_id, key), enable_events=True), 
                            sg.Button("X", key=("_REMOVE_COMMENT", question_id, key), enable_events=True)
                        ]], key=('_COMMENT_ROW_', key))]
            comments.append(comment)
        comments = [sg.Col(comments, key=('_COMMENT_FRAME_', question_id))]
        return comments
    

    def add_comment(self, question_id, comment_text):
        comment_id = str(uuid4())
        comment_dict = {comment_id: comment_text}
        self.QA_data[str(question_id)].update(comment_dict)
        with open(self.QA_dir, 'w') as f:
            dump(self.QA_data, f)
        new_comment = [
            sg.pin(
                sg.Col([
                    [
                        sg.Checkbox(comment_text, key=('_CHECKBOX_COMMENT_', question_id, comment_id), enable_events=True, default=True), 
                        sg.Button("X", key=("_REMOVE_COMMENT", question_id, comment_id), enable_events=True)
                    ]
                ], key=('_COMMENT_ROW_', comment_id))
            )
        ]
        self.current_student.add_comment(question_id, comment_id)
        return new_comment
    
    def delete_comment(self, question_id, comment_id):
        self.QA_data[str(question_id)].pop(comment_id)
        with open(self.QA_dir, 'w') as f:
            dump(self.QA_data, f)
        

    def create_layout(self):
        def TextLabel(text): return sg.Text(text+':', justification='r', size=(50,1))

        def questionTitle(text, score, question_id): 
            if score is not None:
                result = [
                    sg.Text(text, size=(50,1), font='Any 18'),
                    sg.Input(size=(4, 1), font='Any 15', key=('_SCORE_', question_id), enable_events=True),
                    sg.Text('/' + str(score), font='Any 15')
                    ]
            else:
                result = [sg.Text(text, size=(50,1), font='Any 18')]           
            return result

        menu_def = [
            ['File', ['Load students (csv)', 'Save', 'View comments']],['Tools', ['Merge']], ['Generate', ['PDF - Current student', 'PDF - All students']], ['Info', ['About']]
        ]
        
        select_student_column = [
            [sg.Text("Current Student: ", justification='l'), sg.Text("Nothing selected",key="_CURRENT_STUDENT_")],
            [sg.Listbox(list(self.existing_student_data), size=(35,50), expand_y=True, enable_events=True, key='_ALL_STUDENTS_')]
        ]

        add_student_column = [
            [sg.Col([
                [TextLabel("First Name"), sg.Input(key='_FIRST_NAME_')],
                [TextLabel("Last Name"), sg.Input(key='_LAST_NAME_')]
            ]) ,
            sg.Col([
                [sg.Button('Add student', enable_events=True, key='_ADD_STUDENT_')],
            ])
            ]
        ]
        
        student_selection_frame = [[
            sg.Col(select_student_column), sg.Col(add_student_column)
        ]]

        questions_frame_content = []

        for i in range(len(self.template.template_data)):
            temp_question_dict = self.template.template_data[i]
            if temp_question_dict['sublevel'] !=0:
                question_text = temp_question_dict['prescript'] + " " + temp_question_dict['title']
                question = [sg.Col([
                    questionTitle(question_text, temp_question_dict['score'], i)
                ])]
                comments = self.create_comments(i)
                add_comment = [sg.Col([
                    [sg.Input(size=(50, 1), key=('_NEW_COMMENT_', i)), sg.Button('Add',enable_events=True, key=("_ADD_COMMENT_", i), size=(5, 1))]])]
                questions_frame_content.append(question)
                questions_frame_content.append(comments)
                questions_frame_content.append(add_comment)
        total = [sg.Col([
            [sg.Text("Total: "), sg.Text("", key='_TOTAL_SCORE_'), sg.Text(" /{}".format(self.template.max_total_score))]
        ])]
        questions_frame_content.append(total)
        
        questions_frame_column = [[
                sg.Col(questions_frame_content, scrollable=True, vertical_scroll_only=True, expand_x=True, expand_y=True, key='_QUESTION_FRAME_ALL_')
        ]]

        display_no_students = 'Number of students: \n' + str(len(self.existing_student_data))
        bottom_content = [
            [sg.Text(display_no_students), sg.Cancel(button_color='red', size=(10, 5), key='_CANCEL_'), sg.Button("Save", key='_SAVE_STUDENT_', size=(10,5))]
        ]
        
        
        self.layout = [
            [[sg.Menu(menu_def, key='_MENU_')],
            [sg.Text("", key='-TXT-',
            expand_x=True, font='Any 18')]],
            [sg.Push(), sg.Text(self.template.template_data[0]['title'], font='Any 23', justification='c'), sg.Push()],
            [sg.Frame('Student Selection', student_selection_frame, size=(920, 200), pad=50,  expand_x=True,  relief=sg.RELIEF_GROOVE, border_width=3)],
            [sg.Frame("Questions", questions_frame_column, size=(920, 100), pad=50,  expand_x=True, expand_y=True, relief=sg.RELIEF_GROOVE, border_width=3)],
            [sg.Col(bottom_content, justification='r')]   
                ]
        
    def create_window(self):
        sg.theme('LightGrey')
        self.create_layout()
        window = sg.Window('correctAssist - V' + __version__, self.layout, keep_on_top=False, finalize=True, margins=(0,0), resizable=True, size=(1500,500)).finalize()
        window.Maximize()
        return window
    
    
    def clear_form(self, window):
        if window is not None:
            for e in window.element_list():
                if type(e) is sg.Checkbox:
                    e.update(value=False)
                elif type(e) is sg.Input:
                    e.update(value="")

    def load_student(self, student_file, window=None):
        if window is not None:
            if self.current_student is not None:
                self.current_student.save_data(extra_info="The content of the former student has changed and is not saved yet.")
            window['_CURRENT_STUDENT_'].update(student_file)
            self.clear_form(window)
            self.current_student = Student(student_file, self.template, new_student=False)
            for question_id, value in self.current_student.corrections.items():
                # Iterate over all question ids and avoid the total score element. That is handled later.
                if question_id != 'total_score': 
                    comments = value['comments']
                    score = value['score']
                    for comment_id in comments:
                        window[('_CHECKBOX_COMMENT_', int(question_id), comment_id)].update(value=True)
                    if score is not None:
                        window[('_SCORE_', int(question_id))].update(value=score)
                else:
                    window['_TOTAL_SCORE_'].update(value)


    def show(self):
        window = None

        while True:             # Event Loop
            if window is None:
                window = self.create_window()

            event, values = window.read()
            print(event, " - ", values)

            if not isinstance(event, tuple):
                if event in (sg.WIN_CLOSED, '_CANCEL_'):
                    if self.current_student is not None:
                        self.current_student.save_data()
                    break
                elif event == '_ALL_STUDENTS_':
                    if len(self.existing_student_data) != 0:
                        self.load_student(values['_ALL_STUDENTS_'][0], window=window)
                    else:
                        print("No student selected, please select an existing student or add a new one.")
                    
                elif event == '_ADD_STUDENT_':
                    self.add_student(values['_FIRST_NAME_'], values['_LAST_NAME_'], window=window)

                elif event == 'Merge':
                    folder_address = None

                    folder_address = sg.popup_get_folder('Merge editor', initial_folder=path_to_cwd)
                    if folder_address is not None:
                        merge(folder_address)
                        print("Files merged successfully!")
                        folder_address = None

                elif event in ('_SAVE_STUDENT_', 'Save'):
                    if self.current_student is not None:
                        self.current_student.save_data()
                elif event == 'PDF - Current student':
                    self.current_student.generate_report(self.QA_data)
                elif event == 'PDF - All students':
                    for student in self.existing_student_data:
                        temp_student = Student(student, self.template, new_student=False)
                        temp_student.generate_report(self.QA_data)

                elif event == 'Load students (csv)':
                    student_csv = None
                    student_csv = sg.popup_get_file('Select the list of students', initial_folder=path_to_cwd)
                    if student_csv is not None:
                        self.load_students(student_csv)
                elif event == 'About':
                    sg.popup_ok(""" 
                    Created by: {}
                    year: {}
                    version: {}
                    more: https://github.com/jjuch/correctAssist""".format(__developers__, __year__, __version__), title="About correctAssist")
            else:
                if event[0] == '_ADD_COMMENT_':
                    # create new comment layout
                    question_id = event[1]
                    comment_text = values[('_NEW_COMMENT_', question_id)]
                    new_comment_layout = self.add_comment(question_id, comment_text)
                    if window is not None:
                        # add new layout to existing
                        window[('_NEW_COMMENT_', question_id)].update("")
                        window.extend_layout(window[('_COMMENT_FRAME_', question_id)], [new_comment_layout])

                        # remove default text
                        window[('_DEFAULT_EMPTY_COMMENT_', question_id)].update(visible=False)
                        window[('_DEFAULT_EMPTY_COMMENT_', question_id)].hide_row()

                        # resize column such that scrollbar is adjusted
                        window.visibility_changed()
                        window['_QUESTION_FRAME_ALL_'].contents_changed()
                elif event[0] == '_CHECKBOX_COMMENT_':
                    question_id = event[1]
                    comment_id = event[2]
                    if window is not None:
                        if values[event]:
                            self.current_student.add_comment(question_id, comment_id)
                        else:
                            self.current_student.remove_comment(question_id, comment_id)

                elif event[0] == '_REMOVE_COMMENT':
                    question_id = event[1]
                    comment_id = event[2]
                    if window is not None:
                        # uncheck before deleting
                        window[('_CHECKBOX_COMMENT_', question_id, comment_id)].update(value=False)
                        
                        # hide layout element as it cannot be actually removed
                        window[('_COMMENT_ROW_', comment_id)].update(visible=False)
                        window[('_COMMENT_ROW_', comment_id)].hide_row()

                        # resize column such that scrollbar is adjusted
                        window.visibility_changed()
                        window['_QUESTION_FRAME_ALL_'].contents_changed()
                    
                    # delete comment from QA JSON
                    self.delete_comment(question_id, comment_id)
                elif event[0] == '_SCORE_':
                    question_id = event[1]
                    if values[event] == '':
                        new_score = None
                    else:
                        new_score = values[event]
                    total_score = self.current_student.add_score(question_id, new_score)
                    window['_TOTAL_SCORE_'].update(total_score)
                
        window.close()



    def load_students(self, path_to_students_csv):
        """
        path_to_student_csv is created by selecting the appropriate folder that contains all functionalities present in the 'correctAssist' folder and the complementary comments to the current one. This function is called via "Tools>Merge" in the gui.
        """
        '''
        In case a student list is available, this function allows to load all students at once and create their accompanying '.json'-files containing an empty template for their feedback.
        '''
        '''
        expected format: the studentfile should be a csv-file, organised as follows: (usually available as the exam list)
        ____________________
        |full name         |
        |------------------|
        |Willy, Wonka      |
        |------------------|
        |__________________|
        '''

        with open(path_to_students_csv, mode='r', encoding='UTF-8') as student_file:
            csv_reader = csv.reader(student_file, delimiter=',')
            header = 0
            # print(csv_reader)
            for row in csv_reader:
                if header == 0:
                    header += 1
                else:
                    name = row[0].split(", ")
                    first_name = name[1]
                    last_name = name[0]
                    student_file_format = last_name.replace(" ", "") + "_" + first_name.replace(" ", "")
                    if student_file_format not in self.existing_student_data:
                        self.add_student(first_name, last_name)
