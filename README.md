                                                      JSD 2021/2022
                                                      
## General Description

DSL for data is created for the purpose of the Domain-Specific Lanugages course at the Faculty of Technical Sciences.

We are creating the reports for football commentators in which they can get all the informations they want about the matches, clubs and players for English Premier League.
 
User will be allowed to get the complete informations generated from postgreSQL scripts or he could do a filtering in which he will get only specific informations from the API databases.

In both cases data will be stored in postgreSQL databases and CSV files.

Reports of the matches are generated as HTML files and they can be transformed to the PDFs if needed.

The way that the data is collected from the databases is enabled via the language we created specifically for this cause.
Data used for this application is collected from: 
https://www.football-data.org/


## Example

Football commentators before the broadcast usually want to be informed about the events in the last round through reports, or events about a team since the beginning of the season.


## Technologies used
- [textX](https://github.com/textX/textX)
- Jinja2 template engine
- Python 3.9+
- PostgreSQL

## Contributors

|       *Student 1*       |       *Student 2*       |       *Student 3*       |       *Student 4*       |
|:----------------------:|:----------------------:|:----------------------:|:----------------------:|
| [Ana Atanacković](https://github.com/Ana00000/) <br> <img src="https://avatars.githubusercontent.com/u/57576323?s=400&u=1ef5aae0fac636355c779a07004eb66378464adc&v=4" width="170" height="170"> | [Aleksandar Savić](https://github.com/aca24) <br> <img src="https://avatars.githubusercontent.com/u/57627600?v=4" width="170" height="170"> | [Branislav Dobrokes](https://github.com/braned98) <br> <img src="https://avatars.githubusercontent.com/u/41323689?v=4" width="170" height="170"> | [David Ereš](https://github.com/erosdavid) <br> <img src="https://avatars.githubusercontent.com/u/30242404?v=4" width="170" height="170"> |


## Credits

Initial project layout generated with `textx startproject`.


## Installation Instructions

'''
$ git clone https://github.com/Ana00000/JSD
$ python -m venv venv   // creating local environment
$ venv/Scripts/activate   // activating environment
$ cd match_reporter   // positioning
$ pip install -e .   // handling dependencies
$ cd reporter_jsd   // positioning
$ pip install -r instalation.txt   // installation of needed libraries 
$ textx check reporter.tx   // checking grammar
$ textx list-languages   // checking language
$ textx list-generators   // checking generator
$ python reporter_interpreter.py   // running interpreter which creates first set of files and gets all data 
$ textx generate rpt/model_name.rpt --target html+pdf   // generating html and pdf files for all 'model_name' data found
'''

note for Visual Studio Code:  
for syntax highlighting extension copy the rpt folder into the VSC Extensions folder



## General Usage

We use following commands for checking of languages and generators:
1) textx list-languages
2) textx list-generators
Once the csv files are generated via 
	python reporter_interpreter.py
command, generator can be successfully used with command
	textx generate rpt/team.rpt --target html+pdf 
for generating html and pdf files of all teams data. Same goes for 'match' and 'player':
	textx generate rpt/match.rpt --target html+pdf 
	textx generate rpt/player.rpt --target html+pdf
Every time we choose to generate team/match/player data, 'home.html' will be generated as well. This file is basic home page welcome designed using jinja while other files are mainly manipulated via css stylings.



## Generating Reports
Reports can be created for matches, teams and players. 


# Matches
The names of both teams has to be specified, either the full name of the team or the short name ("Arsenal FC" "Arsenal").
Keyword is "Match: "
Example:
    "Match: "Arsenal" vs "Newcastle""

# Teams
The name of the team has to be specified.
Keyword is "Team: "
Example:
    "Team:  "Arsenal""


# Players
When creating reports for a given player, we need to specify the name of the player in conjunction with the name of the club.
Keyword is "Team: " and "Club- "
Example:
    "Player: Name- "Marcos Alonso", Club- "Chelsea""



# EXAMPLES:
# 1
begin
    Team:  "Everton"
    Filter by match date: from-"2020-05-01", to-"2021-09-01"
    Limit: "20"
end

# 2
begin 
    Match: "Arsenal" vs "Newcastle"
end

# 3
begin 
    Player: Name- "Marcos Alonso", Club- "Chelsea"
    Team:  "Arsenal" 
    Filter by match date: from-"2020-05-01", to-"2021-09-01"
    Filter by status: "FINISHED"

end




## Using Filters

There are three filters that can be applied to each report, these are:
1.  Filter by match date
2.  Filter by match status
3.  Limit the search results

Below are the detailed instructions for the application of the above mentioned filters:

# Filter by DATE
It can be used to specify a time interval for the report/search based on the dates of the matches. 
'from' must be used in conjunction with 'to' and vice versa.
example:
Filter by match date: from-"2021-01-01", to-"2021-06-01"

# Filter by STATUS
This filter can be used to narrow down the focus of our report based on the status of the matches.
'status' is expected to be in enum { SCHEDULED | LIVE | IN_PLAY | PAUSED | FINISHED | POSTPONED | SUSPENDED | CANCELLED }
example:
Filter by status: "FINISHED"

# LIMIT
When applied to a report, it limits the number of results
example:
Limit: "10"

