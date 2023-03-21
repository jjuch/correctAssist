import PySimpleGUI as sg
from json import load, dump
import os

from src import data_dir, student_data_dir

class GUI():
    def __init__(self, template):
        self.template = template
        self.student_data_full_dir = os.path.join(self.template.cwd, data_dir, student_data_dir)
        if not os.path.exists(self.student_data_full_dir):
            print("[Info] create a student data directory...")
            os.mkdir(self.student_data_full_dir)
        self.existing_student_data = [x.split('.')[0] for x in os.listdir(self.student_data_full_dir)] # remove extensions
        self.show()
        


    def add_student(self, first_name, last_name):
        file_name_wo_extension = last_name + "_" + first_name
        file_name = file_name_wo_extension + ".json"
        try:
            with open(os.path.join(self.student_data_full_dir, file_name), 'x') as f:
                f.write("")
            self.existing_student_data.append(file_name_wo_extension) 
        except FileExistsError as error:
            print("[Error] This student already exists. Please select the student from the existing students.") 

        

    def update_layout(self):
        def TextLabel(text): return sg.Text(text+':', justification='r', size=(50,1))

        def subTitle(text): return sg.Text(text, size=(50,1), font='Any 18')

        student_selection_window = [
            [sg.Text("Current Student", justification='l'), sg.Push()],
            [sg.Listbox(list(self.existing_student_data), size=(35,10), enable_events=True, key='_CURRENT_STUDENT_'), sg.Column([[TextLabel("First Name"), sg.Input(enable_events=True, key='_FIRST_NAME_')], [TextLabel("Last Name"), sg.Input(enable_events=True, key='_LAST_NAME_')]]) , sg.Button('Add student', enable_events=True, key='_ADD_STUDENT_')]
        ]

        self.layout = [
            [sg.Push(), sg.Text(self.template.template_data[0]['title'], font='Any 23', justification='c'), sg.Push()],
            [sg.Frame('Student Selection', student_selection_window, size=(920, 100), pad=50,  expand_x=True,  relief=sg.RELIEF_GROOVE, border_width=3)]        
                  ]
        
    def create_window(self):
        sg.theme('LightGrey')
        self.update_layout()
        window = sg.Window('correctAssist', self.layout, keep_on_top=True, finalize=True, margins=(0,0), resizable=True, size=(1500,500))
        return window
        

    def save_student(self):
        print('saving...')

    def show(self):
        window = None

        while True:             # Event Loop
            if window is None:
                window = self.create_window()

            event, values = window.read()
            print(event, " - ", values)

            if event in (sg.WIN_CLOSED, 'Exit'):
                break
            if event in ('Change Settings', 'Settings'):
                event, values = self.create_window().read(close=True)
                if event == 'Save':
                    self.save_student()

            if event == '_ADD_STUDENT_':
                self.add_student(values['_FIRST_NAME_'], values['_LAST_NAME_'])
                window = self.create_window()
        window.close()


