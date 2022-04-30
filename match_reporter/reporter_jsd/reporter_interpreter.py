from os import mkdir
from os.path import join, dirname, exists
from textx import metamodel_from_file
from textx.export import metamodel_export, model_export_to_file
import pandas as pd
import requests
from io import StringIO
import json
import http.client
import psycopg2
from sqlalchemy import create_engine
import pdfkit
import html
import csv


css_folder_path = "css/"
all_files_folder_path = "files/"
csv_folder_path = all_files_folder_path + "csv_files/"
html_folder_path = all_files_folder_path + "html_files/"
pdf_folder_path = all_files_folder_path + "pdf_files/"


def export_model():

    current_dir = dirname(__file__)

    meta_model = metamodel_from_file(join(current_dir, 'reporter.tx'), debug=False)

    metamodel_export(meta_model, join(current_dir, 'reporter.dot'))


def load_json(connection):
    
    return json.loads(connection.getresponse().read().decode())


def create_folder(folder_path):

    if not exists(folder_path):
        mkdir(folder_path)


def create_data_folders():

    create_folder(all_files_folder_path)
    create_folder(csv_folder_path)
    create_folder(html_folder_path)
    create_folder(pdf_folder_path)
    create_folder(css_folder_path)


def separateRefereesFromMatches(response):

    all_referees = {}
    for match in response['matches']:
        referees = pd.json_normalize(match["referees"])
        df_referees = pd.DataFrame.from_dict(referees)

        if not df_referees.empty:
            all_referees.update(df_referees)
            match['referees'] = next((referee['name'] for referee in match['referees'] if referee['role'] == 'REFEREE'), None)

    return response, all_referees


def get_data_response(request_path):

    connection = http.client.HTTPConnection('api.football-data.org')
    headers = { 'X-Auth-Token': '168f3965594844d190db11b5388f9085' }

    connection.request('GET', request_path, None, headers)
    response = load_json(connection)

    return response


def set_pdf_styling(data_name):

    if data_name == 'matches':
        pdf_style_file = css_folder_path + data_name + ".css"
    elif data_name == 'teams':
        pdf_style_file = css_folder_path + data_name + ".css"
    elif data_name == 'referees':
        pdf_style_file = css_folder_path + data_name + ".css"

    return pdf_style_file


def set_pdf_options(data_name):

    pdf_style_file = set_pdf_styling(data_name)

    return {
        'user-style-sheet': pdf_style_file
    }


def create_pdf(data_name):

    from_file = join(html_folder_path, data_name + ".html")
    to_file = join(pdf_folder_path, data_name + ".pdf")
    options = set_pdf_options(data_name)

    pdfkit.from_file(from_file, to_file, options)


def create_files(data_name, data_frame):

    data_frame.to_csv(csv_folder_path + data_name + ".csv")

    data_frame.to_html(html_folder_path + data_name + ".html")

    create_pdf(data_name)
    

def store_data(table_name, df):

    con = create_engine("postgresql://postgres:root@localhost/jsd").connect()

    df.to_sql(table_name, con, if_exists='replace', index='False')

    con.close()


def compose_data(response, data_name, normalized_json_data):

    if not normalized_json_data:
        normalized_json_data = pd.json_normalize(response[data_name])
    
    data_frame = pd.DataFrame.from_dict(normalized_json_data)
    create_files(data_name, data_frame)
    store_data(data_name, data_frame)


def get_data():

    create_data_folders()

    responseTeams = get_data_response('/v2/competitions/PL/teams/')
    responseMatches = get_data_response('/v2/teams/66/matches')
    responseMatches, normalized_json_referees = separateRefereesFromMatches(responseMatches)

    compose_data(responseTeams, "teams", {})
    compose_data(responseMatches, "matches", {})
    compose_data({}, "referees", normalized_json_referees)


if __name__ == "__main__":

    export_model()

    get_data()




