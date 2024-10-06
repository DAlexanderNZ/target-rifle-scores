from flask import Flask, render_template, request, Response, redirect, flash, send_from_directory
from flask_httpauth import HTTPBasicAuth
from database import database
from datetime import date
import json
import secrets

app = Flask(__name__)
#New App Secret key on start. Needs to be a stored key for production
SECRET_KEY = secrets.token_hex(16)
app.secret_key = SECRET_KEY
auth = HTTPBasicAuth()
db = database()

@app.route('/')
def index():
    #TODO: Create proper index page. Show highlighted results from recent matchs
    #scores = db.get_all_scores()
    #return render_template('allscores.html', results=scores)
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/message', methods=['GET'])
def get_message():
    return Response(json.dumps({'message': 'Hello from Flask!'}), mimetype='application/json')

@app.route('/api/allscores', methods=['GET'])
def api_all_scores():
    scores = db.get_all_scores()
    if len(scores) == 0:
        #If no scores are found, return code 204 No Content
        return redirect(request.referrer, 204)
    return Response(json.dumps(scores, default=json_serial), mimetype='application/json')

#TODO: Add short term caching to API routes to reduce database load and improve performance under heavy load
@app.route('/api/competitions', methods=['GET'])
def api_competitions():
    """ Get all competitions in the database """
    competitions = db.get_competitions()
    return Response(json.dumps(competitions), mimetype='application/json')

@app.route('/api/matches', methods=['POST'])
def api_matches():
    """ Get all matches in a competition. Expected JSON format: {"competition": "competition_name"} """
    competition = request.get_json().get('competition')
    matches = db.get_matches(competition)
    return Response(json.dumps(matches), mimetype='application/json')

@app.route('/api/classtypes', methods=['GET'])
def api_class_types():
    """ Get all class types in the database """
    classes = db.get_classes()
    return Response(json.dumps(classes), mimetype='application/json')

@app.route('/api/matchscores', methods=['POST'])
def api_match_scores():
    """ Get all scores for a match by match_id. Expected JSON format: {"match": "match_id"} """
    match_id = request.get_json().get('match')
    scores = db.get_match_scores(match_id)
    return Response(json.dumps(scores, default=json_serial), mimetype='application/json')

@app.route('/api/comptotals', methods=['POST'])
def api_comp_totals():
    """ 
    Get all scores for a competition by competition name. 
    Expected JSON format: {"competition": "competition_name"}. 
    Data returned as a dictionary with shooter names as keys and class and total scores as values 
    """
    competition = request.get_json().get('competition')
    results = db.get_comp_totals(competition)
    return Response(json.dumps(results, default=json_serial), mimetype='application/json')

#
# Old flask template routes
#

#Routes for score display and submision
#@app.route('/allscores')
#def all_scores():
#    scores = db.get_all_scores()
#    return render_template('allscores.html', results=scores)

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
    results = db.get_match_scores(match_id)
    return Response(json.dumps(results, default=json_serial), mimetype='application/json')

#Routes for adding scores, matchs and competitions
@app.route('/addscore', methods=['GET'])
@auth.login_required
def add_score_page():
    competitions = db.get_competitions()
    classes = db.get_classes()
    default_match = [{"match_sighters": 2, "match_counters": 10}]
    return render_template('addscore.html', competitions=competitions, classes=classes, match_type=default_match)

@app.route('/addscore', methods=['POST'])
@auth.login_required
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
@auth.login_required
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
                    items[3][i] = '5.001'
                elif score == 'X':
                    items[3][i] = '6.001'
            print(items)
            items.append(competition)
            items.append(match_id)
            items.append(date)
            results.append(items)
    return results

@app.route('/bulkaddscore', methods=['POST'])
@auth.login_required
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
@auth.login_required
def bulk_add_shooter():
    shooters = request.form['csv_text'].strip()
    shooters = string_to_lists(shooters)
    db.bulk_create_shooters(shooters)
    return redirect(request.referrer)

@app.route('/addmatchcomp', methods=['GET'])
@auth.login_required
def add_match_comp_page():
    competitions = db.get_competitions()
    return render_template('addmatchcomp.html', competitions=competitions)

@app.route('/addcomp', methods=['POST'])
@auth.login_required
def add_comp():
    #Handle form submission
    new_competition = request.form['new_competition']
    new_competition_desc = request.form['new_competition_desc']
    new_comp = (new_competition, new_competition_desc)
    db.record_new_competition(new_comp)

    selected_competition = new_competition
    return redirect(request.referrer)

@app.route('/addmatch', methods=['POST'])
@auth.login_required
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
@auth.login_required
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
@auth.login_required
def add_shooter():
    return render_template('addshooter.html')

@app.route('/addshooter', methods=['POST'])
@auth.login_required
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
    email = request.form['email']
    password = request.form['password']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    #TODO: Check existing user before creating user
    new_user = {'email': email, 'password': password, 'first_name': first_name, 'last_name': last_name}
    db.register_user(new_user)
    flash(f'New user with email {email} has been registered')
    return redirect(request.referrer)

#Checks user email and password against users table for http basic auth
@auth.verify_password
def verify_password(email, password):
    print(f'Verifying user {email}')
    user = db.get_user_id(email)
    if user != None:
        if db.verify_user(email, password) == True:
            return email

if __name__ == '__main__':
    app.run(debug=True)
