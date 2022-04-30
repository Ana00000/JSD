from os.path import join, dirname
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
from pdfkit.api import configuration
import html
import csv
import os

def export_model():

    current_dir = dirname(__file__)

    meta_model = metamodel_from_file(join(current_dir, 'reporter.tx'), debug=False)

    model = meta_model.model_from_file('example1.rpt')

    print("TEAMS: \n")
    for report in model.reports:
        print(report.firstTeam)
        print(report.secondTeam)
        save_team_data(get_team_id(report.firstTeam), report.firstTeam)
        save_team_data(get_team_id(report.secondTeam), report.secondTeam)


    metamodel_export(meta_model, join(current_dir, 'reporter.dot'))

def export_player_model():

    current_dir = dirname(__file__)

    meta_model = metamodel_from_file(join(current_dir, 'reporter.tx'), debug=False)

    model = meta_model.model_from_file('player1.rpt')

    print("Player:\n")
    for report in model.reports:
        print(report.name)
        print(report.surname)
        print(get_player_first_name(report.name + " " + report.surname))
        print(get_player_last_name(report.name + " " + report.surname))

    metamodel_export(meta_model, join(current_dir, 'reporter.dot'))


def get_team_id(team_name):

    engine = create_engine("postgresql://postgres:admin@localhost/jsd")
    
    connection = engine.connect()
    metadata = db.MetaData()
    teams = db.Table('PremierLeagueTeams', metadata, autoload=True, autoload_with=engine)

    query = db.select([teams.columns.id]).where(teams.columns.shortName == team_name)

    try:
        team_id = connection.execute(query).fetchall()[0][0]
        print(team_id)
        return team_id
    except:
        return -1

def get_player_name(player_id):

    engine = create_engine("postgresql://postgres:admin@localhost/jsd")
    
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
    data = get_matches_data(team_id)
    table_name = team_name.replace(' ', '') + 'Matches'
    store_data(table_name, data)




def load_json(connection):
    
    return json.loads(connection.getresponse().read().decode())


def get_matches_response(team_id):
    connection = http.client.HTTPConnection('api.football-data.org')
    headers = { 'X-Auth-Token': '168f3965594844d190db11b5388f9085' }

    connection.request('GET', '/v2/teams/66/matches', None, headers )
    responseMatches = load_json(connection)

    return responseMatches


def get_teams_responses():

    connection = http.client.HTTPConnection('api.football-data.org')
    headers = { 'X-Auth-Token': '168f3965594844d190db11b5388f9085' }

    connection.request('GET', '/v2/competitions/PL/teams/', None, headers )
    responseTeams = load_json(connection)

    return responseTeams

def get_player_responses(id):

    connection = http.client.HTTPConnection('api.football-data.org')
    headers = { 'X-Auth-Token': '168f3965594844d190db11b5388f9085' }

    connection.request('GET', '/v2/players/' + str(id), None, headers )
    responsePlayer = load_json(connection)

    return responsePlayer

def get_player_matches_responses(id):
    connection = http.client.HTTPConnection('api.football-data.org')
    headers = { 'X-Auth-Token': '168f3965594844d190db11b5388f9085' }

    connection.request('GET', '/v2/players/' + str(id) + '/matches', None, headers )
    responsePlayerMatches = load_json(connection)

    return responsePlayerMatches

def store_data(table_name, df):

    con = create_engine("postgresql://postgres:admin@localhost/jsd").connect()

    df.to_sql(table_name, con, if_exists='replace', index='False')

    con.close()


def create_pdf(file_name):

    with open("templates/txt/" + file_name + ".txt", "rb") as f:
        count = 1
        text = ''
        columns = []
            
        for line in f.readlines():
            line = format(line).replace("b'", '').replace("\\r", '').replace("\\n'", '')
            liner = '__________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________'
            
            if count == 1:
                header = ''
                for column in format(line).split():
                    columns.append(column)
                    header += ' ' + column 
                text += ' Provided info for: {} '.format(header) + liner
            else:
                for index, column in enumerate(columns):
                    text += ' {} | {} '.format(column, format(line).split()[index])

            text += liner
            count += 1

        config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
        pdfkit.from_string(text, 'templates/pdf/' + file_name + '.pdf', configuration=config)


def get_matches_data(team_id):

    responseMatches = get_matches_response(team_id)

    for match in responseMatches['matches']:
        referees = pd.json_normalize(match["referees"])
        df_referees = pd.DataFrame.from_dict(referees)
        if not df_referees.empty:
            match['referees'] = next((referee['name'] for referee in match['referees'] if referee['role'] == 'REFEREE'), None)

    new_dict_matches = pd.json_normalize(responseMatches['matches'])
    df_matches = pd.DataFrame.from_dict(new_dict_matches)
    df_matches.to_csv("templates/csv/matches.csv")
    #store_data("ManUtdMatches", df_matches)

    #with open("templates/txt/teams.txt", "w") as teams_file:
    #    teams_file.write(df_teams.to_string())
    
   # with open("Matches.txt", "w") as matches_file:
   #     matches_file.write(df_matches.to_string())

    create_pdf("teams")
    
    return df_matches

def get_teams_data():

    responseTeams = get_teams_responses()

    new_dict_teams = pd.json_normalize(responseTeams['teams'])
    df_teams = pd.DataFrame.from_dict(new_dict_teams)
    df_teams.to_csv("templates/csv/teams.csv")
    df_teams.to_html("templates/html/teams.html")  
    store_data("PremierLeagueTeams", df_teams)

def get_player_data(id):

    responsePlayer = get_player_responses(id)

    new_dict_player = pd.json_normalize(responsePlayer)
    df_player = pd.DataFrame.from_dict(new_dict_player)
    df_player.to_csv("templates/csv/player.csv")
    df_player.to_html("templates/html/player.html")
    store_data("PremierLeaguePlayer", df_player)

def get_player_matches_data(id):

    responsePlayerMatches = get_player_matches_responses(id)

    for match in responsePlayerMatches['matches']:
        referees = pd.json_normalize(match["referees"])
        df_referees = pd.DataFrame.from_dict(referees)
        if not df_referees.empty:
            match['referees'] = next((referee['name'] for referee in match['referees'] if referee['role'] == 'REFEREE'), None)

    new_dict_matches = pd.json_normalize(responsePlayerMatches['matches'])
    df_player_matches = pd.DataFrame.from_dict(new_dict_matches)
    df_player_matches.to_csv("templates/csv/player_matches.csv")
    df_player_matches.to_html("templates/html/player_matches.html")
    store_data("PremierLeaguePlayerMatches", df_player_matches)


if __name__ == "__main__":

    player_id = input("Enter positive number: ")

    if (player_id.isnumeric()):
        get_player_data(player_id)
    else:
        print("You must input positive number!")
    get_player_matches_data(player_id)
    export_player_model()

    export_model()

    #get_data()




