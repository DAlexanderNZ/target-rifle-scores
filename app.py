from flask import Flask, render_template, request, Response
from database import database
from datetime import date
import json

app = Flask(__name__)
db = database()

@app.route('/')
def index():
    #TODO: Create proper index page. Show highlighted results from recent matchs
    scores = db.get_all_scores()
    return render_template('allscores.html', results=scores)

#Routes for score display and submision
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
    raise TypeError(f"Type {type(obj)} not serializable")

@app.route('/getcompscores', methods=['POST'])
def get_comp_scores():
    competition = request.json['competition'].strip()
    scores = db.get_comp_scores(competition)
    return Response(json.dumps(scores, default=json_serial), mimetype='application/json')

@app.route('/compresults', methods=['GET'])
def comp_results():
    competitions = db.get_competitions()
    return render_template('compresults.html', competitions=competitions)

@app.route('/getcompresults', methods=['POST'])
def get_comp_results():
    competition = request.json['competition'].strip()
    results = db.get_comp_results(competition)
    return Response(json.dumps(results, default=json_serial), mimetype='application/json')

#Routes for adding scores, matchs and competitions
@app.route('/addscore', methods=['GET'])
def add_score_page():
    competitions = db.get_competitions()
    classes = db.get_classes()
    default_match = [{"match_sighters": 2, "match_counters": 10}]
    return render_template('addscore.html', competitions=competitions, classes=classes, match_type=default_match)

@app.route('/addscore', methods=['POST'])
def add_score():
    #Request data from database required for the page and data validation
    competitions = db.get_competitions()
    classes = db.get_classes()
    default_match = [{"match_sighters": 2, "match_counters": 10}]

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

    return render_template('addscore.html', competitions=competitions, classes=classes, match_type=default_match)

@app.route('/addmatchcomp', methods=['GET'])
def add_match_comp_page():
    competitions = db.get_competitions()
    return render_template('addmatchcomp.html', competitions=competitions)

@app.route('/addmatchcomp', methods=['POST'])
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

@app.route('/addcompetition', methods=['POST'])
def add_competition():
    #Handle form submission
    competition = request.form['competition']
    description = request.form['description']
    match_id = request.form['match_id']
    match_name = request.form['match_name']
    match_description = request.form['match_description']

    comp = [competition, description, match_id, match_name, match_description]
    print(comp) #TODO: store data

#Routes for handling adding of shooters, clubs, etc
@app.route('/addshooter', methods=['GET'])
def add_shooter_page():
    return render_template('addshooter.html')

app.route('/addshooter', methods=['POST'])
def add_shooter():
    #Handle form submission
    shooter_name = request.form['name']



    return render_template('addshooter.html')

if __name__ == '__main__':
    app.run(debug=True)
