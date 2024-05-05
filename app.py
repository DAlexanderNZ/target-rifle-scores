from flask import Flask, render_template, request, Response
from database import database
from datetime import date
import json

app = Flask(__name__)
db = database()

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

@app.route('/')
def index():
    return render_template('index.html', results=scores, zip=zip)

@app.route('/allscores')
def all_scores():
    scores = db.get_all_scores()
    return render_template('allscores.html', results=scores)

#Display all scores by split by match and then by class
@app.route('/compscores', methods=['GET'])
def comp_scores():    
    competitions = db.get_competitions()
    return render_template('compscores.html', competitions=competitions)

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


@app.route('/getcompscores', methods=['POST'])
def get_comp_scores():
    competition = request.json['competition'].strip()
    print(competition)
    scores = db.get_comp_scores(competition)
    return Response(json.dumps(scores, default=json_serial), mimetype='application/json')

@app.route('/addscore', methods=['GET', 'POST'])
def add_score():
    #Request data from database required for the page and data validation
    competitions = db.get_competitions()
    classes = db.get_classes()
    default_match = [{"match_sighters": 2, "match_counters": 10}]

    if request.method == 'POST':
        #Handle form submission
        shooter_id = request.form['name']
        competition = request.form['competition'].strip()
        match_id = request.form['match_id']
        shots = request.form.getlist('shots')
        shot_type = request.form.getlist('shot_type')
        total = request.form.get('score')
        class_type = request.form['class_type']
        date = request.form['match_date']

        #Validate form data
        score = [shooter_id, competition, match_id, shots, shot_type, total, class_type, date]
        #Store data
        db.record_score(score)
        #Store selected competition
        selected_competition = competition
    else:
        selected_competition = ''

    return render_template('addscore.html', competitions=competitions, classes=classes, match_type=default_match)

@app.route('/addmatchcomp', methods=['GET', 'POST'])
def add_match_comp():
    competitions = db.get_competitions()
    if request.method == 'POST':
        #Handle form submission
        competition = request.form['competition']
        match_name = request.form['match_name'].strip()
        match_distance = request.form['match_distance']
        match_distance_type = request.form['match_distance_type']
        #match_sighters = request.form['match_sighters']
        match_counters = request.form['match_counters']
        match_description = request.form['match_description'].strip()
        #TODO: Check if match distance, counters and sighters match a match_type and add to match types if not. May require rethinking match_type table

        #Format data for submission
        new_match = [match_name, match_distance + match_distance_type, match_counters, match_description, competition]
        db.record_new_match(new_match)
        #Store selected competition
        selected_competition = competition
    else:
        selected_competition = ''

    return render_template('addmatchcomp.html', competitions=competitions, selected_competition=selected_competition)

@app.route('/removematch', methods=['POST'])
def remove_match():
    """ Removes match from database if it has no scores """
    match_id = request.json['match_id']
    success = db.remove_match(match_id)
    return Response(json.dumps({'success': success}), mimetype='application/json')

@app.route('/getmatches', methods=['POST'])
def get_matches():
    competition = request.json['competition'].strip()
    matches = db.get_matches(competition)
    return Response(json.dumps(matches), mimetype='application/json')

@app.route('/getnamesuggestion', methods=['POST'])
def get_name_suggestion():
    print(request.json)
    names = request.json['name'].strip().lower()
    suggestions = db.get_name_suggestions(names)
    print(suggestions)
    return Response(json.dumps(suggestions), mimetype='application/json')

@app.route('/addcompetition', methods=['GET', 'POST'])
def add_competition():
    if request.method == 'POST':
        #Handle form submission
        competition = request.form['competition']
        description = request.form['description']
        match_id = request.form['match_id']
        match_name = request.form['match_name']
        match_description = request.form['match_description']

        comp = [competition, description, match_id, match_name, match_description]
        print(comp) #TODO: store data


if __name__ == '__main__':
    app.run(debug=True)
