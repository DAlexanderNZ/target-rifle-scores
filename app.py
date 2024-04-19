from flask import Flask, render_template, request, Response
import database
import psycopg
import itertools
import json

app = Flask(__name__)

#Sample scores
#Shot types: 0 - coutning shot, 1 - non converted sighter
scores = [
    {"name": "John Snowden", 
    "shots": ['4', '5', 'V', 'V', 'X', 'V', '5', '5', 'V', 'V', 'V'],
    "shot_type": [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    "score": 50.07,
    "match_sighters": 2,
    "match_counters": 10},
    {"name": "Oliver G", 
    "shots": ['3', '4', '5', '4', '3', '5', '5', '4', 'V', '4', '5', '5'],
    "shot_type": [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    "score": 45.01,
    "match_sighters": 2,
    "match_counters": 10}
]
#Check shot types are the correct size for the number of shots
#If the sighters are converted copy them to counters
for score in scores:
    count = 1
    for (shot, shot_type) in zip(score["shots"], score["shot_type"]):
        if len(score["shots"]) < (score["match_counters"] + score["match_sighters"]):
            if shot_type == 0 and count <= score["match_sighters"]:
                print(shot)
                score["shots"].insert(count , shot)
                score["shot_type"].insert(count , 0)
        count += 1
    if len(score["shots"]) != len(score["shot_type"]):
        print(f'Number of shots and shot types do not match, {score["name"]}')

#Get data from database
config = database.load_config()
conn = psycopg.connect(**config)

@app.route('/')
def index():
    return render_template('index.html', results=scores, zip=zip)

@app.route('/addscore', methods=['GET', 'POST'])
def add_score():
    if request.method == 'POST':
        #Handle form submission
        #TODO: get shooter ID instead of name
        shooter_id = request.form['name'].title() 
        competition = request.form['competition']
        match_id = request.form['match_id']
        shots = request.form['shots']
        shot_type = request.form['shot_type']
        total = request.form['score']
        class_type = request.form['class']
        date = request.form['match_date']

        #Validate form data
        classes = database.get_classes(conn)

        score = [shooter_id, competition, match_id, shots, shot_type, total, class_type, date]
        #Store data
        print(score)
        database.record_score(score, conn)
        
    if request.method == 'GET':
        competitions = database.get_competitions(conn)
        classes = database.get_classes(conn)
        default_match = [{"match_sighters": 2, "match_counters": 10}]
    return render_template('addscore.html', competitions=competitions, classes=classes, match_type=default_match)

@app.route('/getmatches', methods=['POST'])
def get_matches():
    competition = request.json['competition'].strip()
    print(competition)
    matches = database.get_matches(conn, competition)
    return Response(json.dumps(matches), mimetype='application/json')

@app.route('/addcompetition', methods=['GET', 'POST'])
def add_competition():
    if request.method == 'POST':
        #Handle form submission
        competition = request.form['competition']
        description = request.form['description']
        match_id = request.form['match_id']
        match_name = request.form['match_name']
        match_description = request.form['match_description']


if __name__ == '__main__':
    app.run(debug=True)