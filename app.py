from flask import Flask, render_template, request, Response, redirect
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
    match_id = request.json['match']
    #Return code 400 if the request didn't send a match_id
    if len(match_id) < 1:
        return redirect(request.referrer, 400)
    results = db.get_comp_results(match_id)
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

@app.route('/bulkaddscore', methods=['GET'])
def bulk_add_score_page():
    competitions = db.get_competitions()
    return render_template('bulkaddscore.html', competitions=competitions)

def bulk_scores_to_list(competition, match_id, date, scores):
    lines = scores.split('\n')
    lines.pop(0)
    results = []
    for line in lines:
        if len(line) != 0:
            print(line)
            line = line.replace('\r', '')
            items = line.split(',')
            #Format shots to expected format
            items[3] = [*items[3]]
            for i, score in enumerate(items[3]):
                if score == 'V':
                    items[3][i] = 5.001
                elif score == 'X':
                    items[3][i] = 6.001
            print(items)
            items.append(competition)
            items.append(match_id)
            items.append(date)
            results.append(items)
    return results

@app.route('/bulkaddscore', methods=['POST'])
def bulk_add_score():
    #Submitted data
    competition = request.form['competition']
    match_id = request.form['match_id']
    date = request.form['match_date']
    data = request.form['csv_text']
    print(f'Competition: {competition}, Match ID: {match_id}, Date: {date}, Data: {data}')
    bulk_scores = bulk_scores_to_list(competition, match_id, date, data)
    #Add scores
    db.bulk_record_scores(bulk_scores)

    return redirect(request.referrer)

def string_to_lists(string):
    lines = string.split('\n')
    return [line.replace('\r', '').split(',') for line in lines]

@app.route('/bulkaddshooter', methods=['POST'])
def bulk_add_shooter():
    shooters = request.form['csv_text']
    shooters = string_to_lists(shooters)
    db.bulk_create_shooters(shooters)
    return redirect(request.referrer)

@app.route('/addmatchcomp', methods=['GET'])
def add_match_comp_page():
    competitions = db.get_competitions()
    return render_template('addmatchcomp.html', competitions=competitions)

@app.route('/addcomp', methods=['POST'])
def add_comp():
    #Handle form submission
    new_competition = request.form['new_competition']
    new_competition_desc = request.form['new_competition_desc']
    new_comp = (new_competition, new_competition_desc)
    db.record_new_competition(new_comp)

    selected_competition = new_competition
    return redirect(request.referrer)

@app.route('/addmatch', methods=['POST'])
def add_match():
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

    return redirect(request.referrer)

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

#Routes for handling adding of shooters, clubs, etc
@app.route('/addshooter', methods=['GET'])
def add_shooter():
    return render_template('addshooter.html')

@app.route('/addshooter', methods=['POST'])
def add_shooter_sub():
    #Handle form submission
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    nra_id = request.form['nra_id']
    #TODO: Add clubs
    #club = request.form['club']
    dob = request.form['dob']
    if nra_id == '':
        nra_id = None
    new_shooter = [nra_id, first_name, last_name, dob]
    print(f'Submited new shooter: {new_shooter}')
    db.create_shooter(new_shooter)

    return redirect(request.referrer)

#Routes for user accounts
@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_sub():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    #TODO: DB insert

    return redirect(request.referrer)

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_sub():
    username = request.form['username']
    password = request.form['password']
    #TODO: DB check
    return redirect(request.referrer)


if __name__ == '__main__':
    app.run(debug=True)
