from os import mkdir
from os.path import join, dirname, exists
from signal import SIG_DFL
from textx import metamodel_from_file
from textx.export import metamodel_export, model_export_to_file
import pandas as pd
import requests
from io import StringIO
import json
import http.client
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy as db
import pdfkit
import html
import csv


css_folder_path = "css/"
all_files_folder_path = "files/"
csv_folder_path = all_files_folder_path + "csv_files/"
html_folder_path = all_files_folder_path + "html_files/"
pdf_folder_path = all_files_folder_path + "pdf_files/"
database_password = "root"


def create_folder(folder_path):

    if not exists(folder_path):
        mkdir(folder_path)


def create_data_folders():

    create_folder(all_files_folder_path)
    create_folder(csv_folder_path)
    create_folder(html_folder_path)
    create_folder(pdf_folder_path)
    create_folder(css_folder_path)


def get_meta_model():

    current_dir = dirname(__file__)

    meta_model = metamodel_from_file(join(current_dir, 'reporter.tx'), debug=False)

    return meta_model


def get_model(file_name):

    meta_model = get_meta_model()

    model = meta_model.model_from_file(file_name)

    return model


def export_meta_model():

    meta_model = get_meta_model()

    metamodel_export(meta_model, join(dirname(__file__), 'reporter.dot'))


def create_connection():
    
    engine = create_engine("postgresql://postgres:" + database_password + "@localhost/jsd")

    connection = engine.connect()

    return connection


def set_pdf_styling(data_name):

    if "Referees" in data_name or "Players" in data_name:
        pdf_style_file = css_folder_path + "Referees.css"
    elif "Teams" in data_name:
        pdf_style_file = css_folder_path + "Teams.css"
    else:
        pdf_style_file = css_folder_path + "Matches.css"

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


def create_files(data_name, data_frame):

    data_frame.to_csv(csv_folder_path + data_name + ".csv")

    data_frame.to_html(html_folder_path + data_name + ".html")

    create_pdf(data_name)


def store_data(table_name, data_frame):

    connection = create_connection()

    data_frame.to_sql(table_name, connection, if_exists='replace', index='False')

    connection.close()


def get_team_ids_for_team_name(team_name):

    connection = create_connection()

    teams_columns = db.Table('PremierLeagueTeams', db.MetaData(), autoload=True, autoload_with=connection).columns
    query = db.select([teams_columns.id]).where(teams_columns.shortName == team_name)
    team_ids = connection.execute(query).fetchall()[0][0]

    connection.close()

    return team_ids


def load_json(connection):
    
    return json.loads(connection.getresponse().read().decode())
    

def get_data_response(request_path):

    connection = http.client.HTTPConnection('api.football-data.org')
    headers = { 'X-Auth-Token': '168f3965594844d190db11b5388f9085' }

    connection.request('GET', request_path, None, headers)
    response = load_json(connection)

    return response


def create_data(normalized_json_data, data_name):

    data_frame = pd.DataFrame.from_dict(normalized_json_data)

    create_files(data_name, data_frame)

    store_data(data_name.replace(' ', ''), data_frame)


def compose_data(response, data_name, normalized_json_data):

    if not normalized_json_data:
        normalized_json_data = pd.json_normalize(response[data_name])

    create_data(normalized_json_data, data_name)


def separateRefereesFromMatches(response):

    all_referees = {}
    for match in response['matches']:
        referees = pd.json_normalize(match["referees"])
        df_referees = pd.DataFrame.from_dict(referees)

        if not df_referees.empty:
            all_referees.update(df_referees)
            match['referees'] = next((referee['name'] for referee in match['referees'] if referee['role'] == 'REFEREE'), None)

    return all_referees


def save_referees_from_matches(responseMatches, data_name):

    normalized_json_referees = separateRefereesFromMatches(responseMatches)
    
    compose_data({}, data_name + "Referees", normalized_json_referees)


def save_team_data(team_id, team_name):

    responseMatches = get_data_response('/v2/teams/' + str(team_id) + '/matches')

    save_referees_from_matches(responseMatches, team_name)

    normalized_json_data = pd.json_normalize(responseMatches['matches'])

    create_data(normalized_json_data, team_name)


def save_teams_data(firstTeam, secondTeam):

    save_team_data(get_team_ids_for_team_name(firstTeam), firstTeam.replace(' ', ''))
    save_team_data(get_team_ids_for_team_name(secondTeam), secondTeam.replace(' ', ''))


def export_teams_model():

    model = get_model('example1.rpt')

    export_meta_model()

    for report in model.reports:
        save_teams_data(report.firstTeam, report.secondTeam)


def export_players_model():

    get_model('player1.rpt')

    export_meta_model()


def save_player_matches(id):

    responsePlayerMatches = get_data_response('/v2/players/' + str(id) + '/matches')

    save_referees_from_matches(responsePlayerMatches, 'PremierLeaguePlayerMatches')

    normalized_json_data = pd.json_normalize(responsePlayerMatches['matches'])
    create_data(normalized_json_data, "PremierLeaguePlayerMatches")


def save_teams():

    responseTeams = get_data_response('/v2/competitions/PL/teams/')

    normalized_json_data = pd.json_normalize(responseTeams['teams'])

    create_data(normalized_json_data, 'PremierLeagueTeams')


def save_players(player_id):

    responsePlayers = get_data_response('/v2/players/' + str(player_id))

    normalized_json_data = pd.json_normalize(responsePlayers)
    
    create_data(normalized_json_data, 'PremierLeaguePlayers')


if __name__ == "__main__":

    create_data_folders()

    player_id = input("Enter positive number: ")
    if not player_id.isnumeric():
        print("You must input positive number!")
    else:
        save_player_matches(player_id)
        save_players(player_id)
        export_players_model()

        save_teams()
        export_teams_model()
