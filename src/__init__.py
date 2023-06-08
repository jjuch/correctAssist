import os
## Declare global variables
# template variables
template_dir = "template"
template_file = "template.txt"
Q_A_file = "Q_A.json"

path_to_cwd = os.getcwd() 

# data variables
data_dir = "data"
student_data_dir = "students"
student_pdf_dir = "reports"
existing_student_data = "list_of_grades"
csv_grades = "student_grades.csv"
# metadata
from .version import __version__, __developers__, __year__