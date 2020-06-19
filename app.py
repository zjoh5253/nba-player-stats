#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import pyrebase
from flask import Flask, render_template, request, url_for, redirect
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
import os
import csv
import json

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')

#----------------------------------------------------------------------------#
# Firebase Config.
#----------------------------------------------------------------------------#


# not best practice, ideally API key is inside os environment variables
config = {
    "apiKey": "AIzaSyBBVFq71jRTtSqFxWj2GalQ47bXtmR9F_k",
    "authDomain": "nba-player-stats-4361b.firebaseapp.com",
    "databaseURL": "https://nba-player-stats-4361b.firebaseio.com",
    "storageBucket": "nba-player-stats-4361b.appspot.com"
}

firebase = pyrebase.initialize_app(config)

db = firebase.database()

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def home():
    return redirect(url_for('insights'))


@app.route('/insights')
def insights():
    player_data = db.child('player_data').get().val()

    count = 0

    averageFTpct = 0
    average2pct = 0
    average3pct = 0
    lakers_players = 0
    jazz_players = 0

    labels = []
    two_pt_data = []
    three_pt_data = []
    ft_data = []

    for id, val in player_data.items():

        if val['Year'] not in labels:
             labels.append(val['Year'])

        if val['Tm'] == 'LAL':
            lakers_players += 1

        if val['Tm'] == 'UTA':
            jazz_players += 1

        count += 1

        if val['FTpct'] != '':
            if "." in val['FTpct']:
                averageFTpct += float(val['FTpct']) * 100.00
            else:
                averageFTpct += int(val['FTpct']) * 100.00
        else:
            averageFTpct += 0

        if val['2Ppct'] != '':
            if "." in val['2Ppct']:
                average2pct += float(val['2Ppct']) * 100.00
            else:
                average2pct += int(val['2Ppct']) * 100
        else:
            average2pct += 0

        if val['3Ppct'] != '':
            if "." in val['3Ppct']:
                average3pct += float(val['3Ppct']) * 100.00
            else:
                average3pct += int(val['3Ppct']) * 100
        else:
            average3pct += 0

    # divide by count
    averageFTpct = averageFTpct / count
    average2pct = average2pct / count
    average3pct = average3pct / count

    # format
    averageFTpct = str(round(averageFTpct, 2)) + "%"
    average2pct = str(round(average2pct, 2)) + "%"
    average3pct = str(round(average3pct, 2)) + "%"


    json_player_data = json.dumps(player_data)

    return render_template('pages/insights.html', 
    player_data=player_data,
    json_player_data=json_player_data,
    averageFTpct=averageFTpct,
    average2pct=average2pct,
    average3pct=average3pct,
    ft_data=ft_data,
    three_pt_data=three_pt_data,
    two_pt_data=two_pt_data,
    lakers_players=lakers_players,
    jazz_players=jazz_players)


@app.route('/raw')
def raw():
    player_data = db.child('player_data').get().val()
    return render_template('pages/raw.html', player_data=player_data)


@app.route('/import-csv')
def import_csv():
    try:
        count = 0
        with open('static/data/Seasons_Stats.csv') as csv_file:
            print(csv_file)
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                data = {
                    "Year": row[1],
                    "Player": row[2],
                    "Pos": row[3],
                    "Age": row[4],
                    "Tm": row[5],
                    "G": row[6],
                    "GS": row[7],
                    "MP": row[8],
                    "PER": row[9],
                    "TSpct": row[10],
                    "3PAr": row[11],
                    "FTr": row[12],
                    "ORBpct": row[13],
                    "DRBpct": row[14],
                    "TRBpct": row[15],
                    "ASTpct": row[16],
                    "STLpct": row[17],
                    "BLKpct": row[18],
                    "TOVpct": row[19],
                    "USGpct": row[20],
                    "blanl": row[21],
                    "OWS": row[22],
                    "DWS": row[23],
                    "WS": row[24],
                    "WS48": row[25],
                    "blank2": row[26],
                    "OBPM": row[27],
                    "DBPM": row[28],
                    "BPM": row[29],
                    "VORP": row[30],
                    "FG": row[31],
                    "FGA": row[32],
                    "FGpct": row[33],
                    "3P": row[34],
                    "3PA": row[35],
                    "3Ppct": row[36],
                    "2P": row[37],
                    "2PA": row[38],
                    "2Ppct": row[39],
                    "eFGpct": row[40],
                    "FT": row[41],
                    "FTA": row[42],
                    "FTpct": row[43],
                    "ORB": row[44],
                    "DRB": row[45],
                    "TRB": row[46],
                    "AST": row[47],
                    "STL": row[48],
                    "BLK": row[49],
                    "TOV": row[50],
                    "PF": row[51],
                    "PTS": row[52]
                }

                db.child('player_data').push(data)
                count += 1
                print(count)

        return 'success'

    except Exception as e:
        print(e)
        return 'error'

    return 'import_csv'

# Error handlers.


@app.errorhandler(500)
def internal_error(error):
    # db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            'pct(asctime)s pct(levelname)s: pct(message)s [in pct(pathname)s:pct(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
