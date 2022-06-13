import os
from os import mkdir
from os.path import join, exists, dirname
import pdfkit
import pandas as pd
import jinja2


css_folder_path = "css/"
j2_folder_path = "j2/"
all_files_folder_path = "generated_files/"
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

    data_name = data_name.replace('.csv', '')

    create_html(data_name)

    create_pdf(data_name)


def generate_home_html():

    home_file_path = join(html_folder_path, "Home.html")

    with open(home_file_path, 'w') as f:
        jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(j2_folder_path))
        template = jinja_env.get_template('Home.j2')

        f.write(template.render(title="Welcome to foodball reports", background=dirname(__file__) + '\\home.png'))


def generate_match_and_team_files(model_path):

    generated_files = 0

    for csv_file_name in os.listdir(csv_folder_path):
        model_name = model_path.split('\\')[-1][:-4]
        if '.csv' in csv_file_name and model_name in csv_file_name.lower():
            generated_files +=1
            generate_files_from_data(csv_file_name)

    return generated_files


def generate_player_files():

    for csv_file_name in os.listdir(csv_folder_path):
        if '.csv' in csv_file_name and 'Matches' not in csv_file_name and 'Team' not in csv_file_name:
            generate_files_from_data(csv_file_name)


def generate(model_path):

    create_data_folders()

    generate_home_html()

    if generate_match_and_team_files(model_path) == 0:
        generate_player_files()
