import PySimpleGUI as sg
from json import load, dump
import os
from uuid import uuid4
import csv

from src import path_to_cwd, template_dir, template_file, Q_A_file, data_dir, student_data_dir
from src.template import Template
from src.student import Student

class GUI():
    def __init__(self, cwd):
        self.template = Template(cwd)
        self.cwd = cwd
        self.student_data_full_dir = os.path.join(self.cwd, data_dir, student_data_dir)
        if not os.path.exists(self.student_data_full_dir):
            print("[Info] create a student data directory...")
            os.makedirs(self.student_data_full_dir)
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
            self.current_student = Student(file_name_wo_extension, self.template, self.student_data_full_dir)        
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
                            sg.Checkbox(value, key=('_CHECKBOX_COMMENT_', key), enable_events=True), 
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
                        sg.Checkbox(comment_text, key=('_CHECKBOX_COMMENT_', comment_id), enable_events=True, default=True), 
                        sg.Button("X", key=("_REMOVE_COMMENT", question_id, comment_id), enable_events=True)
                    ]
                ], key=('_COMMENT_ROW_', comment_id))
            )
        ]
        return new_comment
    
    def delete_comment(self, question_id, comment_id):
        self.QA_data[str(question_id)].pop(comment_id)
        with open(self.QA_dir, 'w') as f:
            dump(self.QA_data, f)
        

    def create_layout(self):
        def TextLabel(text): return sg.Text(text+':', justification='r', size=(50,1))

        def questionTitle(text): return sg.Text(text, size=(50,1), font='Any 18')

        menu_def = [
            ['File', ['Add Students', 'Save', 'View comments']],['Tools', ['Merge']]
        ]
        
        select_student_column = [
            [sg.Text("Current Student: ", justification='l'), sg.Text("Nothing selected",key="_CURRENT_STUDENT_")],
            [sg.Listbox(list(self.existing_student_data), size=(35,25), enable_events=True, key='_ALL_STUDENTS_')]
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
                    [questionTitle(question_text)]
                ])]
                comments = self.create_comments(i)
                add_comment = [sg.Col([
                    [sg.Input(size=(50, 1), key=('_NEW_COMMENT_', i)), sg.Button('Add',enable_events=True, key=("_ADD_COMMENT_", i), size=(5, 1))]])]
                questions_frame_content.append(question)
                questions_frame_content.append(comments)
                questions_frame_content.append(add_comment)
        
        questions_frame_column = [[
                sg.Col(questions_frame_content, scrollable=True, vertical_scroll_only=True, expand_x=True, expand_y=True, key='_QUESTION_FRAME_ALL_')
        ]]


        bottom_content = [
            [sg.Cancel(button_color='red', size=(10, 5), key='_CANCEL_'), sg.Button("Save", key='_SAVE_STUDENT_', size=(10,5))]
        ]            
        
        self.layout = [
            [[sg.Menu(menu_def)],
            [sg.Text("", key='-TXT-',
            expand_x=True, font='Any 18')]],
            [sg.Push(), sg.Text(self.template.template_data[0]['title'], font='Any 23', justification='c'), sg.Push()],
            [sg.Frame('Student Selection', student_selection_frame, size=(920, 100), pad=50,  expand_x=True,  relief=sg.RELIEF_GROOVE, border_width=3)],
            [sg.Frame("Questions", questions_frame_column, size=(920, 100), pad=50,  expand_x=True, expand_y=True, relief=sg.RELIEF_GROOVE, border_width=3)],
            [sg.Col(bottom_content, justification='r')]   
                ]
        
    def create_window(self):
        sg.theme('LightGrey')
        self.create_layout()
        window = sg.Window('correctAssist', self.layout, keep_on_top=False, finalize=True, margins=(0,0), resizable=True, size=(1500,500)).finalize()
        window.Maximize()
        return window
        

    def save_student(self):
        print('saving...')

    def load_student(self, student_file, window=None):
        if window is not None:
            window['_CURRENT_STUDENT_'].update(student_file)
            self.current_student = Student(student_file, self.template)

    def show(self):
        window = None

        while True:             # Event Loop
            if window is None:
                window = self.create_window()

            event, values = window.read()
            print(event, " - ", values)

            if not isinstance(event, tuple):
                if event in (sg.WIN_CLOSED, '_CANCEL_'):
                    break
                elif event == '_ALL_STUDENTS_':
                    self.load_student(values['_ALL_STUDENTS_'][0], window=window)
                    
                elif event == '_ADD_STUDENT_':
                    self.add_student(values['_FIRST_NAME_'], values['_LAST_NAME_'], window=window)

                elif event == 'Merge':
                    left_col = [
                        [sg.Text('Folder:'), sg.In(size=(25,1), enable_events=True, key='_FOLDER_'), sg.FolderBrowse()]
                    ]
                    layout = [
                        [sg.Column(left_col, element_justification='c')],
                        [sg.Button('Merge files',  key='_MERGE_CONTENT_', size=(10,5))]

                    ]

  
                
                    folder_address = None

                    folder_address = sg.popup_get_folder('Merge editor', initial_folder=path_to_cwd)
                    # folder_address is instantiated once the 'Ok' is clicked
                    # print(folder_address)
                    if folder_address is not None:
                        self.Merge(folder_address)
                        print("Files merged successfully!")
                        folder_address = None

                elif event == 'Save':
                    save = sg.popup_yes_no("Do you want to save?", title='Save')
                    if save:
                        self.save_student()
                        print("Files saved successfully!")

                elif event == 'Add Students':
                    student_csv = None
                    student_csv = sg.popup_get_file('Select the list of students', initial_folder=path_to_cwd)
                    if student_csv is not None:
                        self.load_students(student_csv)

                        # merge_event, merge_value = merge_window.read()
                        # if merge_event in (sg.WIN_CLOSED, 'Exit'):
                        #     break

                        # elif merge_event == '_FOLDER_':
                        #     folder_address = merge_value['_FOLDER_']
                        
                        # elif folder_address is not None:
                        #     if merge_event == '_MERGE_CONTENT_':
                        #         self.Merge(folder_address)
                        #         print("Files merged successfully!")
                        #         merge_window.close()

                        # elif merge_event == '_MERGE_CONTENT_' and folder_address is None:
                        #     print('Please select a folder first')

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

                elif event[0] == '_REMOVE_COMMENT':
                    question_id = event[1]
                    comment_id = event[2]
                    if window is not None:
                        # uncheck before deleting
                        window[('_CHECKBOX_COMMENT_', comment_id)].update(value=False)
                        
                        # hide layout element as it cannot be actually removed
                        window[('_COMMENT_ROW_', comment_id)].update(visible=False)
                        window[('_COMMENT_ROW_', comment_id)].hide_row()

                        # resize column such that scrollbar is adjusted
                        window.visibility_changed()
                        window['_QUESTION_FRAME_ALL_'].contents_changed()
                    
                    # delete comment from QA JSON
                    self.delete_comment(question_id, comment_id)
                

        window.close()
    def load_students(self, path_to_students_csv):
        with open(path_to_students_csv, mode='r') as student_file:
            csv_reader = csv.reader(student_file, delimiter=';')
            header = 0
            print(csv_reader)
            for row in csv_reader:
                if header == 0:
                    header += 1
                else:
                    '''
                    expected format: col(first_name), col(last_name)
                    ''' 
                    print(row)
                    first_name = row[0]
                    last_name = row[1]
                    # student_file_format = last_name.replace(" ", "") + "_" + first_name.replace(" ", "")
                    self.add_student(first_name, last_name)

    def Merge(self, path_to_comp):
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
                current_student = load(stc)
            path_to_student = os.path.join(path_to_students, student)
            with open(path_to_student, 'r') as st:
                student_file = load(st)
            for k in current_student.keys():
                for i in student_file[k]:
                    if i not in current_student[k]:
                        current_student[k].append(i)
            with open(path_to_current_student, 'w') as stc:
                dump(current_student, stc, indent=4)

        # Merge Q_A files
        with open(path_to_Q_A, 'r') as com:
            extra_comments = load(com)
        with open(path_to_current_Q_A, 'r') as comc:
            own_comments = load(comc)
        for k in own_comments.keys():
            own_comments[k].update(extra_comments[k])
        with open(path_to_current_Q_A, 'w') as updated_qa:
            dump(own_comments, updated_qa)
        
    '''
    call Student.save_data
    call mergy.py to merge the documents
    '''
