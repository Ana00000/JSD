                                                      JSD 2021/2022
                                                      
## Description

DSL for data is created for the purpose of the Domain-Specific Lanugages course at the Faculty of Technical Sciences.

We are creating the reports for football commentators in which they can get all the informations they want about the matches, clubs and players.
User will be allowed to get the complete informations generated from postgreSQL scripts or he could do a filtering in which he will get only specific informations from the databases.

In both cases data will be stored in postgreSQL databases, but for the second case request from user will generate a sql query which will alter the data gotten from databases so he gets more appropriate and specific data he needs.
Reports of the matches are generated as HTML files and they can be transformed to the PDFs if needed.

The way that the data is collected from the databases is enabled via the language we created specifically for this cause.
Data used for this application is collected from few different sources, such as:
1. https://www.api-football.com/
2. https://serpapi.com/sports-results
3. ...

and many others.

## Example

Football commentators before the broadcast usually want to be informed about the events in the last round through reports, or events about a team since the beginning of the season.

Several different types of Jinja2 templates are used for the elements (tables, pictures, paragraphs, labels, etc.) in the report.

## Technologies used
- [textX](https://github.com/textX/textX)
- Jinja2 template engine
- Python 3.9+
- PostgreSQL

## Contributors

|       *Student 1*       |       *Student 2*       |       *Student 3*       |       *Student 4*       |
|:----------------------:|:----------------------:|:----------------------:|:----------------------:|
| [Ana Atanacković](https://github.com/Ana00000/) <br> <img src="https://avatars.githubusercontent.com/u/57576323?s=400&u=1ef5aae0fac636355c779a07004eb66378464adc&v=4" width="170" height="170"> | [Aleksandar Savić](https://github.com/aca24) <br> <img src="https://avatars.githubusercontent.com/u/57627600?v=4" width="170" height="170"> | [Branislav Dobrokes](https://github.com/braned98) <br> <img src="https://avatars.githubusercontent.com/u/41323689?v=4" width="170" height="170"> | [David Ereš](https://github.com/erosdavid) <br> <img src="https://avatars.githubusercontent.com/u/30242404?v=4" width="170" height="170"> |

