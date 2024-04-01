from flask import Flask, render_template, request
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

@app.route('/')
def index():
    return render_template('index.html', results=scores, zip=zip)

@app.route('/addscore', methods=['GET', 'POST'])
def add_score():
    if request.method == 'POST':
        #Handle form submission
        name = request.form['name'].title()
        match_sighters = request.form['match_sighters']
        match_counters = request.form['match_counters']
        shots = request.form['shots']
        #shot_type = request.form['shot_type']
        score = request.form['score']
        distance = request.form['distance']
        date = request.form['date']

        #Validate form data


        #Store data
        print(f'{name} {match_sighters} {match_counters} {shots} {score} {distance} {date}')

    return render_template('addscore.html')

if __name__ == '__main__':
    app.run(debug=True)