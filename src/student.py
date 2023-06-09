import os
import json
import PySimpleGUI as sg
from src import path_to_cwd, data_dir, student_data_dir



from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import Color
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak


class Student:
    def __init__(self, student_name, template, new_student=True):
        self.template = template
        self.file_path_student = os.path.join(path_to_cwd, data_dir, student_data_dir, student_name + ".json")
        self.student_name = student_name
        if new_student:
            self.add_student()

        # This variable will later on be used to update the corresponding student data
        self.corrections = self.load_student_data()


    def add_student(self):
        '''
        Called when a new name is typed in the gui, it reports the given name in the 'Student' class and makes an accompanying '.json' file. If the student already exists, an error will be raised, without further disrupting the program. 
        '''
        try:
            # Create the file
            with open(self.file_path_student, 'x') as f:
                f.write("{}")

            # Adapt the student file
            init_dict = {}
            for key, _ in self.template.template_data.items():
                init_dict.update({str(key): {
                                    'comments': [],
                                    'score': None
                                    }
                                })
            init_dict.update({"total_score": None})
            with open(self.file_path_student, 'w') as f:
                json.dump(init_dict, f)
            
        except FileExistsError as error:
            print("[Info] This student already exists. The data will be loaded...")

    def load_student_data(self):
        '''
        When an existing student is selected, his/her data will be loaded into a (temporary) class variable 'corrections' to be further manipulated by 'add_comment', 'remove_comment', ... \n
        The manipulations are not continuously saved, only when 'Save' is pressed, the adaptations become permanent.
        '''
        with open(self.file_path_student, 'r') as fps:
            student_dict = json.load(fps)
        return student_dict    
                   

    def remove_comment(self, question_id, comment_id):
        '''
        Arguments: question_id and comment_id \n
        These arguments are automatically selected by un-checking the desired comment at the appropriate question in the gui. \n
        Remove a comment from a selected student.
        '''
        current_comments = self.corrections[str(question_id)]['comments']
        if comment_id in current_comments:
            current_comments.remove(comment_id)
        new_corrections = self.corrections
        new_corrections[str(question_id)]['comments'] = current_comments
        self.corrections = new_corrections


    def add_comment(self, question_id, comment_id):
        current_comments = self.corrections[str(question_id)]['comments']
        if comment_id not in current_comments:
            current_comments.append(comment_id)
        new_corrections = self.corrections
        new_corrections[str(question_id)]['comments'] = current_comments
        self.corrections = new_corrections
    
    def add_score(self, question_id, score):
        score = '0.' if score == '.' else score # handle error
        # update total score
        new_score = self.corrections
        old_score = new_score[str(question_id)]['score']
        old_total_score = new_score['total_score']
        new_total_score = 0.0 if old_total_score is None else float(old_total_score)        
        if score is not None:
            if old_score is not None:
                new_total_score -= float(old_score)
                new_total_score += float(score)
            else:
                new_total_score += float(score)
        else:
            if old_score is not None:
                new_total_score -= float(old_score)
        new_score['total_score'] = str(new_total_score)

        # save new score in dict
        new_score[str(question_id)]['score'] = score
        self.corrections = new_score
        return new_total_score

    def changed(self):
        old_data = self.load_student_data()
        new_data = self.corrections
        return old_data != new_data
    
    def save_data(self, extra_info=''):
        if self.changed():
            save = sg.popup_yes_no(extra_info, "\nDo you want to save?", title='Save')
            print("Save: ", save)
            if save.lower() == 'yes':
                with open(self.file_path_student, 'w') as f:
                    json.dump(self.corrections, f)
                print("Data saved successfully")
        else:
            print("Nothing to be saved...")


    def generate_report(self, QA_dict):
        font_path = os.path.join(path_to_cwd, 'src', 'fonts')
        pdfmetrics.registerFont(TTFont('UGent Panno normal', os.path.join(font_path, 'UGentPannoText-Normal.ttf')))
        pdfmetrics.registerFont(TTFont('UGent Panno medium', os.path.join(font_path, 'UGentPannoText-Medium.ttf')))
        pdfmetrics.registerFont(TTFont('UGent Panno semiBold', os.path.join(font_path, 'UGentPannoText-SemiBold.ttf')))
        pdfmetrics.registerFont(TTFont('UGent Panno semiLight', os.path.join(font_path,'UGentPannoText-semiLight.ttf')))
        ugentBlue = Color(30/255, 100/255, 200/255, alpha=1)
        ugentBlack = Color(0, 0, 0, alpha=1)
        ugentWhite = Color(1, 1, 1, alpha=1)

        normalParagraphStyle = ParagraphStyle(
            name='normal',
            fontName='UGent Panno normal',
            fontSize=10,
            textColor=ugentBlack
        )
        titleParagraphStyle = ParagraphStyle(
            name='title',
            fontName='UGent Panno semiBold',
            fontSize=16,
            textColor=ugentBlue,
            spaceAfter=10
        )
        subtitleParagraphStyle = ParagraphStyle(
            name='subtitle',
            fontName='UGent Panno semiBold',
            fontsize=16, 
            textcolor=ugentBlack,
            spaceAfter=10
        )

        def fileContent():
            # Name on top
            elements = []
            for question_id, el in self.template.template_data.items():
                if el['sublevel'] == 0:
                    #title
                    elements.append(Paragraph("<font face='UGent Panno semiBold'><u>{} - {}</u></font>".format(el['title'], self.student_name), style=titleParagraphStyle))
                else:
                    # section/subsection
                    if el['score'] is None:
                        text = "<font face='UGent Panno semiBold'>{} {}</font>".format(el['prescript'], el['title'])
                    else:
                        current_score = self.corrections[str(question_id)]['score']
                        current_score = '' if current_score is None else current_score
                        text = "<font face='UGent Panno semiBold'>{} {} - {}/{}</font>".format(el['prescript'], el['title'], current_score, el['score'])
                    elements.append(Paragraph(text, style=subtitleParagraphStyle))

                    for comment_id in self.corrections[str(question_id)]['comments']:
                        text_comment = QA_dict[str(question_id)][comment_id]
                        elements.append(Paragraph(text_comment, style=normalParagraphStyle, bulletText='-'))

            # append total score
            text = "<font face='UGent Panno semiBold'>Total: {}/{}</font>".format(self.corrections['total_score'], self.template.max_total_score)
            elements.append(Paragraph(text, style=subtitleParagraphStyle))
            return elements
    
        path_to_pdf = os.path.join(path_to_cwd, data_dir, 'reports')
        document = SimpleDocTemplate(os.path.join(path_to_pdf, self.student_name + ".pdf"), pagesize=A4)
        story = fileContent()
        document.build(story)
