from operator import or_
from os import mkdir
from os.path import join, dirname, exists
from pkgutil import get_data
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
from sqlalchemy import or_
import pdfkit
import html
import csv


css_folder_path = "css/"
rpt_folder_path = "rpt/"
all_files_folder_path = "generated_files/"
csv_folder_path = all_files_folder_path + "csv_files/"
html_folder_path = all_files_folder_path + "html_files/"
pdf_folder_path = all_files_folder_path + "pdf_files/"
dot_folder_path = all_files_folder_path + "dot_files/"
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
    create_folder(rpt_folder_path)
    create_folder(dot_folder_path)


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

    metamodel_export(meta_model, join(dirname(__file__), join(dot_folder_path, 'reporter.dot')))


def create_connection():
    
    engine = create_engine("postgresql://postgres:" + database_password + "@localhost/jsd")

    connection = engine.connect()

    return connection


def create_csv(data_name, data_frame):

    data_frame.to_csv(csv_folder_path + data_name + ".csv")


def store_data(table_name, data_frame):

    connection = create_connection()

    data_frame.to_sql(table_name, connection, if_exists='replace', index='False')

    connection.close()


def get_team_ids_for_team_name(team_name):

    connection = create_connection()

    teams_columns = db.Table('PremierLeagueTeams', db.MetaData(), autoload=True, autoload_with=connection).columns
    query = db.select([teams_columns.id]).where(or_(teams_columns.shortName == team_name, teams_columns.name == team_name))
    team_ids = -1

    try:
        team_ids = connection.execute(query).fetchall()[0][0]
    except:
        print("Nije ok")

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

    create_csv(data_name, data_frame)

    store_data(data_name.replace(' ', ''), data_frame)


def separate_referees_from_matches(response):

    all_referees = {}

    if response == None or 'matches' not in response:
        return all_referees

    for match in response['matches']:
        referees = pd.json_normalize(match["referees"])
        df_referees = pd.DataFrame.from_dict(referees)

        if not df_referees.empty:
            all_referees.update(df_referees)
            match['referees'] = next((referee['name'] for referee in match['referees'] if referee['role'] == 'REFEREE'), None)

    return all_referees


def save_referees_from_matches(responseMatches, data_name):

    normalized_json_referees = separate_referees_from_matches(responseMatches)
    
    create_data(normalized_json_referees, data_name + "Referees")


def save_match_data(team_id, team_name, filter):
    
    
    responseMatches = get_data_response('/v2/teams/' + str(team_id) + '/matches' + filter)
    save_referees_from_matches(responseMatches, team_name + "Matches")

    normalized_json_data = pd.json_normalize(responseMatches['matches'])

    create_data(normalized_json_data, team_name + "Matches")


def save_matches_data(firstTeam, secondTeam, filter):

    save_match_data(get_team_ids_for_team_name(firstTeam), firstTeam.replace(' ', ''), filter)
    save_match_data(get_team_ids_for_team_name(secondTeam), secondTeam.replace(' ', ''), filter)


def save_teams():

    responseTeams = get_data_response('/v2/competitions/PL/teams/')
    normalized_json_data = pd.json_normalize(responseTeams['teams'])

    create_data(normalized_json_data, 'PremierLeagueTeams')


def save_player_matches(id):

    responsePlayerMatches = get_data_response('/v2/players/' + str(id) + '/matches')

    save_referees_from_matches(responsePlayerMatches, 'PremierLeaguePlayerMatches')

    normalized_json_data = pd.json_normalize(responsePlayerMatches['matches'])
    create_data(normalized_json_data, "PremierLeaguePlayerMatches")


def save_players(player_id):

    responsePlayers = get_data_response('/v2/players/' + str(player_id))

    normalized_json_data = pd.json_normalize(responsePlayers)
    
    create_data(normalized_json_data, 'PremierLeaguePlayers')

    
def export_players_model(player_id):
    
    save_player_matches(player_id)
    save_players(player_id)

    get_model(join(rpt_folder_path, 'player.rpt'))

    export_meta_model()


def set_active_competition_from_team(responseTeam):

    activeCompetitions = pd.json_normalize(responseTeam["activeCompetitions"])

    df_activeCompetitions = pd.DataFrame.from_dict(activeCompetitions)

    if not df_activeCompetitions.empty:
        responseTeam["activeCompetitions"] = next((activeCompetition['name'] for activeCompetition in responseTeam["activeCompetitions"]), None)


def set_squads_from_team(responseTeam):

    squads = pd.json_normalize(responseTeam["squad"])

    df_squads = pd.DataFrame.from_dict(squads)

    if not df_squads.empty:
        responseTeam["squad"] = next((squad['name'] for squad in responseTeam["squad"]), None)


def save_team_data(team_id, team_name, filter):
    
    responseTeam = get_data_response('/v2/teams/' + str(team_id) + filter)

    set_active_competition_from_team(responseTeam)
    set_squads_from_team(responseTeam)
    
    normalized_json_data = pd.json_normalize(responseTeam)
    create_data(normalized_json_data, team_name.replace(' ', '') + 'Team')
    

def export_teams_model(report, filter):
    save_team_data(get_team_ids_for_team_name(report.teamName), report.teamName, filter)
    save_match_data(get_team_ids_for_team_name(report.teamName), report.teamName.replace(' ', ''), filter)


def export_matches_model(report, filter):
    save_matches_data(report.firstTeam, report.secondTeam, filter)

def export_player_model(report, filter):

    team_id = get_team_ids_for_team_name(report.club)

    responseSquad = get_data_response('/v2/teams/' + str(team_id) + filter)

    requested_player = -1

    for player in responseSquad['squad']:
        if player['name'] == report.name:
            requested_player = player
            break

    response_matches = get_data_response('/v2/players/' + str(requested_player['id']) + '/matches' + filter)

    separate_referees_from_matches(response_matches)

    normalized_player = pd.json_normalize(requested_player)
    
    normalized_player_matches = pd.json_normalize(response_matches['matches'])

    df_player = pd.DataFrame.from_dict(normalized_player_matches)

    #with open("matches.txt", "w") as teams_file:
    #    teams_file.write(df_player.to_string())

    #print(normalized_player_matches)

    create_data(normalized_player, requested_player['name'])
    create_data(normalized_player_matches, requested_player['name'] + 'Matches')

    

def interpret(model):

    filter = ''

    if model.filters:
        filters = model.filters
        filter = '?'
        for f in filters: 
            if filter != '?':
                filter = filter + '&'            
            if 'MatchDate' in str(f):
                filter = filter + 'dateFrom=' + f.matchDateFrom + '&dateTo=' + f.matchDateTo
            if 'Status' in str(f):
                filter = filter + 'status=' + f.status
            if 'Limit' in str(f):
                filter = filter + 'limit=' + f.limit

    for report in model.reports:
        if report.__class__.__name__ == "Team":
            export_teams_model(report, filter)
        elif report.__class__.__name__ == "Match":
            export_matches_model(report, filter)
        elif report.__class__.__name__ == "Player":
            export_player_model(report, filter)

    

if __name__ == "__main__":

    save_teams()

    model = get_model(join(rpt_folder_path, 'player.rpt'))
    export_meta_model()

    interpret(model)
    
