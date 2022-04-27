from os.path import join, dirname
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
from pdfkit.api import configuration
import html
import csv
import os

def export_model():

    current_dir = dirname(__file__)

    meta_model = metamodel_from_file(join(current_dir, 'reporter.tx'), debug=False)

    metamodel_export(meta_model, join(current_dir, 'reporter.dot'))


def load_json(connection):
    
    return json.loads(connection.getresponse().read().decode())


def get_responses():

    connection = http.client.HTTPConnection('api.football-data.org')
    headers = { 'X-Auth-Token': '168f3965594844d190db11b5388f9085' }

    connection.request('GET', '/v2/competitions/PL/teams/', None, headers )
    responseTeams = load_json(connection)
    
    connection.request('GET', '/v2/teams/66/matches', None, headers )
    responseMatches = load_json(connection)

    return responseTeams, responseMatches


def store_data(table_name, df):

    con = create_engine("postgresql://postgres:root@localhost/jsd").connect()

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


def get_data():

    responseTeams, responseMatches = get_responses()

    for match in responseMatches['matches']:
        referees = pd.json_normalize(match["referees"])
        df_referees = pd.DataFrame.from_dict(referees)
        if not df_referees.empty:
            #print(match['referees'])
            #print(next((referee['name'] for referee in match['referees'] if referee['role'] == 'REFEREE'), None))
            #obj = next((referee for referee in referees if referee['name'] == 'REFEREE'), None)
            #match["referees"] = str(df_referees).encode('cp1252', errors='replace').decode('cp1252')
            match['referees'] = next((referee['name'] for referee in match['referees'] if referee['role'] == 'REFEREE'), None)

    new_dict_teams = pd.json_normalize(responseTeams['teams'])
    df_teams = pd.DataFrame.from_dict(new_dict_teams)
    df_teams.to_csv("templates/csv/teams.csv")
    df_teams.to_html("templates/html/teams.html")  
    store_data("PremierLeagueTeams", df_teams)

    new_dict_matches = pd.json_normalize(responseMatches['matches'])
    df_matches = pd.DataFrame.from_dict(new_dict_matches)
    df_matches.to_csv("templates/csv/matches.csv")
    df_teams.to_html("templates/html/matches.html")
    store_data("ManUtdMatches", df_matches)

    with open("templates/txt/teams.txt", "w") as teams_file:
        teams_file.write(df_teams.to_string())
    
   # with open("Matches.txt", "w") as matches_file:
   #     matches_file.write(df_matches.to_string())

    create_pdf("teams")


if __name__ == "__main__":

    export_model()

    get_data()




