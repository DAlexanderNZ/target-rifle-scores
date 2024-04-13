from flask import Flask, render_template, request
import database
import psycopg
import itertools

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

#Sample comptition and matchs
competition = [
    {"competition": "Malvern Club Champs",
    "description": "Range days counting towards the Malvern Club Championship",
    "match_id": "1,2"}
]
match_name =  [
    {"match_id": 1,
    "match_name": "First 300y",
    "match_type": "7s 300y"},
    {"match_id": 2,
    "match_name": "First 500y",
    "match_type":"10s 500y"} 
]
match_type = [
    {"match_type": "7s 300y",
    "match_sighters": 2,
    "match_counters": 7},
    {"match_type": "10s 500y",
    "match_sighters": 2,
    "match_counters": 10}
]

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
        name = request.form['name'].title()
        shots = request.form['shots']
        score = request.form['score']
        #match_id = request.form['match_id']
        date = request.form['date']

        #Validate form data


        #Store data
        print(f'{name} {shots} {score} {date}')
        
    if request.method == 'GET':
        competitions = database.get_competitions(conn)

    return render_template('addscore.html', competitions=competitions, match_name=match_name, match_type=match_type)

if __name__ == '__main__':
    app.run(debug=True)