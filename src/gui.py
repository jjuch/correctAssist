import PySimpleGUI as sg
from json import load, dump
import os

from src import data_dir, student_data_dir
from src.template import Template
from src.student import Student

class GUI():
    def __init__(self, cwd):
        self.template = Template(cwd)
        self.student_data_full_dir = os.path.join(self.template.cwd, data_dir, student_data_dir)
        if not os.path.exists(self.student_data_full_dir):
            print("[Info] create a student data directory...")
            os.mkdir(self.student_data_full_dir)
        self.existing_student_data = [x.split('.')[0] for x in os.listdir(self.student_data_full_dir)] # remove extensions
        self.current_student = Student("")
        self.show()

    
    def __str__(self):
        return self.template.__str__()     


    def add_student(self, first_name, last_name, window=None):
        file_name_wo_extension = last_name.replace(" ", "") + "_" + first_name.replace(" ", "")
        file_name = file_name_wo_extension + ".json"
        try:
            with open(os.path.join(self.student_data_full_dir, file_name), 'x') as f:
                f.write("")
            self.existing_student_data.append(file_name_wo_extension)
            if window is not None:
                window["_ALL_STUDENTS_"].update((*self.existing_student_data,))
                window["_CURRENT_STUDENT_"].update(file_name_wo_extension)
                window.refresh()
        except FileExistsError as error:
            print("[Error] This student already exists. Please select the student from the existing students.")
        

        

    def create_layout(self):
        def TextLabel(text): return sg.Text(text+':', justification='r', size=(50,1))

        def questionTitle(text): return sg.Text(text, size=(50,1), font='Any 18')

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
                question = [questionTitle(question_text)]
                comments = [sg.Text("No answers yet.", visible=True)] 
                # TODO: update answers from Q_A.json
                # TODO: add new comment
                questions_frame_content.append(question)
                questions_frame_content.append(comments)
        
        questions_frame_column = [[
            sg.Col(questions_frame_content, scrollable=True, vertical_scroll_only=True, expand_x=True, expand_y=True)
        ]]


        bottom_content = [
            [sg.Cancel(button_color='red', size=(10, 5), key='_CANCEL_'), sg.Button("Save", key='_SAVE_STUDENT_', size=(10,5))]
        ]             

        self.layout = [
            [sg.Push(), sg.Text(self.template.template_data[0]['title'], font='Any 23', justification='c'), sg.Push()],
            [sg.Frame('Student Selection', student_selection_frame, size=(920, 100), pad=50,  expand_x=True,  relief=sg.RELIEF_GROOVE, border_width=3)],
            [sg.Frame("Questions", questions_frame_column, size=(920, 100), pad=50,  expand_x=True, expand_y=True, relief=sg.RELIEF_GROOVE, border_width=3)],
            [sg.Col(bottom_content, justification='r')]   
                  ]
        
    def create_window(self):
        sg.theme('LightGrey')
        self.create_layout()
        window = sg.Window('correctAssist', self.layout, keep_on_top=True, finalize=True, margins=(0,0), resizable=True, size=(1500,500)).finalize()
        window.Maximize()
        return window
        

    def save_student(self):
        print('saving...')

    def load_student(self, student_file, window=None):
        if window is not None:
            window['_CURRENT_STUDENT_'].update(student_file)
            self.current_student = Student(student_file)

    def show(self):
        window = None

        while True:             # Event Loop
            if window is None:
                window = self.create_window()

            event, values = window.read()
            print(event, " - ", values)

            if event in (sg.WIN_CLOSED, '_CANCEL_'):
                break
            elif event == '_ALL_STUDENTS_':
                self.load_student(values['_ALL_STUDENTS_'][0], window=window)
                
            elif event == '_ADD_STUDENT_':
                self.add_student(values['_FIRST_NAME_'], values['_LAST_NAME_'], window=window)
                
        window.close()


