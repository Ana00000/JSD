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


def export_teams_model():

    current_dir = dirname(__file__)

    meta_model = metamodel_from_file(join(current_dir, 'reporter.tx'), debug=False)

    model = meta_model.model_from_file('example1.rpt')

    for report in model.reports:
        save_team_data(get_team_id(report.firstTeam), report.firstTeam)
        save_team_data(get_team_id(report.secondTeam), report.secondTeam)

    metamodel_export(meta_model, join(current_dir, 'reporter.dot'))

def export_player_model():

    current_dir = dirname(__file__)

    meta_model = metamodel_from_file(join(current_dir, 'reporter.tx'), debug=False)

    model = meta_model.model_from_file('player1.rpt')

    for report in model.reports:
        get_player_first_name(report.name + " " + report.surname)
        get_player_last_name(report.name + " " + report.surname)

    metamodel_export(meta_model, join(current_dir, 'reporter.dot'))


def get_team_id(team_name):

    connection = create_engine("postgresql://postgres:" + database_password + "@localhost/jsd").connect()
    metadata = db.MetaData()
    teamResponse = get_data_response('/v2/competitions/PL/teams/')
    normalized_json_data = pd.json_normalize(teamResponse["teams"])
    data_frame = pd.DataFrame.from_dict(normalized_json_data)
    data_frame.to_sql("PremierLeagueTeams", connection, if_exists='replace', index='False')

    teams = db.Table('PremierLeagueTeams', metadata, autoload=True, autoload_with=connection)
    query = db.select([teams.columns.id]).where(teams.columns.shortName == team_name)

    try:
        team_id = connection.execute(query).fetchall()[0][0]
        connection.close()
        return team_id
    except:
        connection.close()
        return -1


def get_player_name(player_id):

    engine = create_engine("postgresql://postgres:" + database_password + "@localhost/jsd")
    
    connection = engine.connect()
    metadata = db.MetaData()
    player = db.Table('PremierLeaguePlayer', metadata, autoload=True, autoload_with=engine)

    query = db.select([player.columns.name]).where(player.columns.id == player_id)

    try:
        player_name = connection.execute(query).fetchall()[0][0]
        print(player_name)
        return player_name
    except:
        return -1


def get_player_first_name(player_name):

    player_name_part = player_name.split(" ")

    return player_name_part[0]


def get_player_last_name(player_name):

    player_name_part = player_name.split(" ")

    if (len(player_name_part) == 2):
        return player_name_part[1]

    return ""
    

def save_team_data(team_id, team_name):

    teamResponse = get_data_response('/v2/teams/' + str(team_id) + '/matches')

    normalized_json_data = pd.json_normalize(teamResponse['matches'])

    data_frame = pd.DataFrame.from_dict(normalized_json_data)

    create_files(team_name, data_frame)

   # store_data(team_name.replace(' ', ''), data_frame)


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


def get_player_matches_responses(id):
    connection = http.client.HTTPConnection('api.football-data.org')
    headers = { 'X-Auth-Token': '168f3965594844d190db11b5388f9085' }

    connection.request('GET', '/v2/players/' + str(id) + '/matches', None, headers )
    responsePlayerMatches = load_json(connection)

    return responsePlayerMatches


def set_pdf_styling(data_name):

    if data_name == 'referees':
        pdf_style_file = css_folder_path + data_name + ".css"
    elif data_name == 'teams':
        pdf_style_file = css_folder_path + data_name + ".css"
    else:
        pdf_style_file = css_folder_path + "matches.css"

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

    con = create_engine("postgresql://postgres:" + database_password + "@localhost/jsd").connect()

    df.to_sql(table_name, con, if_exists='replace', index='False')

    con.close()


def compose_data(response, data_name, normalized_json_data):

    if not normalized_json_data:
        normalized_json_data = pd.json_normalize(response[data_name])

    data_frame = pd.DataFrame.from_dict(normalized_json_data)
    create_files(data_name, data_frame)
    store_data(data_name.replace(' ', ''), data_frame)


def get_data(player_id):

    responseTeams = get_data_response('/v2/competitions/PL/teams/')
    responseMatches = get_data_response('/v2/teams/66/matches')
    responseMatches, normalized_json_referees = separateRefereesFromMatches(responseMatches)
    responsePlayers = get_data_response('/v2/players/' + str(player_id))

    compose_data(responseMatches, "matches", {})
    compose_data(responseTeams, "teams", {})

    data_name = "players"
    normalized_json_data = pd.json_normalize(responsePlayers)
    data_frame = pd.DataFrame.from_dict(normalized_json_data)
    create_files(data_name, data_frame)
    store_data(data_name.replace(' ', ''), data_frame)

    compose_data({}, "referees", normalized_json_referees)


def get_player_matches_data(id):

    responsePlayerMatches = get_player_matches_responses(id)

    for match in responsePlayerMatches['matches']:
        referees = pd.json_normalize(match["referees"])
        df_referees = pd.DataFrame.from_dict(referees)
        if not df_referees.empty:
            match['referees'] = next((referee['name'] for referee in match['referees'] if referee['role'] == 'REFEREE'), None)

    new_dict_matches = pd.json_normalize(responsePlayerMatches['matches'])
    df_player_matches = pd.DataFrame.from_dict(new_dict_matches)
    df_player_matches.to_csv(all_files_folder_path+ "csv_files/player_matches.csv")
    df_player_matches.to_html(all_files_folder_path+ "/html_files/player_matches.html")
    store_data("PremierLeaguePlayerMatches", df_player_matches)


if __name__ == "__main__":

    create_data_folders()

    player_id = input("Enter positive number: ")
    if not player_id.isnumeric():
        print("You must input positive number!")
    else:
        get_player_matches_data(player_id)

        export_teams_model()

        export_player_model()

        get_data(player_id)
