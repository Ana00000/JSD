import os
from os import mkdir
from os.path import join, exists
import pdfkit
import pandas as pd


reporter_path = "match_reporter/reporter_jsd/"
css_folder_path = reporter_path + "css/"
all_files_folder_path = reporter_path + "generated_files/"
csv_folder_path = all_files_folder_path + "csv_files/"
html_folder_path = all_files_folder_path + "html_files/"
pdf_folder_path = all_files_folder_path + "pdf_files/"


def create_folder(folder_path):

    if not exists(folder_path):
        mkdir(folder_path)


def create_data_folders():

    create_folder(html_folder_path)
    create_folder(pdf_folder_path)


def create_html(data_name):

    from_file = join(csv_folder_path, data_name + ".csv")
    to_file = join(html_folder_path, data_name + ".html")

    csv_file = pd.read_csv(from_file)
    
    with open(to_file, 'w') as f:
        csv_file.to_html(to_file)


def set_pdf_styling(data_name):

    if "Referees" in data_name or "Players" in data_name:
        pdf_style_file = css_folder_path + "Referees.css"
    elif "Team" in data_name:
        pdf_style_file = css_folder_path + "Teams.css"
    else:
        pdf_style_file = css_folder_path + "General.css"

    return pdf_style_file


def set_pdf_options(data_name):

    pdf_style_file = set_pdf_styling(data_name)

    return {
        'encoding': "UTF-8",
        'user-style-sheet': pdf_style_file
    }


def create_pdf(data_name):

    from_file = join(html_folder_path, data_name + ".html")
    to_file = join(pdf_folder_path, data_name + ".pdf")
    options = set_pdf_options(data_name)

    pdfkit.from_file(from_file, to_file, options)
    

def generate_files_from_data(data_name):

    create_html(data_name)

    create_pdf(data_name)


def generate():

    create_data_folders()

    for csv_file_name in os.listdir(csv_folder_path):
        if '.csv' in csv_file_name: 
            data_name = csv_file_name.replace('.csv', '')
            generate_files_from_data(data_name)