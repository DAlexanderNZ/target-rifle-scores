//Load first row on page load
document.addEventListener('DOMContentLoaded', function(){
    document.getElementById('date_picker').value = toDateInputValue(new Date())
    add_row()
})

//Get data from flask passed though to js
function match_type_data(data){
    return JSON.parse(data)
}
//Define and render rows and contents for the table
const score_input_table = document.getElementById('score_input')
//increment row_id to allow for unique row ids and existing_rows to existing rows in the table
let row_id = 0
let existing_rows = []
//TODO: Add Flask logic to load type_class's available from database.
//TODO: Add logic to enable X & 6 / disable V for F-Class shooters
function add_row(){
    console.log("create_row")
    row_id++
    existing_rows.push(row_id)
    let new_row = document.createElement('tr')
    new_row.id = "new_row_" + row_id
    let html = '<td id="button_' + row_id + '"><button type="button" onclick="add_row()" id="row_add_button_' + row_id + '">➕</button></td>\
        <td><input type="text" name="name" required></td>\
        <td id="type_class"><select><option default>TR</option><option>FTR</option><option>F-Open</option></select></td>\
        <td id="shots_input_' + row_id + '"></td>\
        <td><span type="float" step="0.01" name="score" id="score_' + row_id + '" required></span></td>'
    new_row.innerHTML = html
    score_input_table.appendChild(new_row)
    render_shots(row_id)
    if (row_id > 1) {
        //Change previous ➕ to ➖
        let last_row = document.getElementById('row_add_button_' + (row_id - 1))
        last_row.innerHTML = "➖"
        last_row.setAttribute('onclick', 'remove_row('+ (row_id - 1) + ')')
        //Add ➖ to new last row.  
        current_row_buttons = document.getElementById('button_' + row_id)
        remove_button = document.createElement('span')
        remove_button.id = 'remove_row_button_' + row_id
        remove_button.innerHTML = '<button type="button" onclick="remove_row(' + row_id +')">➖</button>'
        current_row_buttons.appendChild(remove_button)
        }
        //Remove added ➖ from second to last row
        document.getElementById('remove_row_button_' + (row_id - 1)).remove()
    }

//Allow for selected row to be removed. TODO: Check if user has input in the row and confirm choice.
function remove_row(removal_row_id){
    existing_rows.splice(removal_row_id -1)
    console.log("Remove row " + removal_row_id + "\n Existing rows " + existing_rows)
    if (score_input_table.rows.length > 2) {
        console.log("Remove row " +  removal_row_id + ' new_row_' + removal_row_id)
        document.getElementById('new_row_' + removal_row_id).remove()
        //TODO: Fix this logic to check all rows in table and ➕ to last row if none found
        if (removal_row_id == row_id){
            let last_row = document.getElementById('row_add_button_' + (row_id - 1))
            last_row.innerHTML = "➕"
            last_row.setAttribute('onclick', 'add_row()')
        }
    } else {
       alert('You cannot delete the last row of the table')
    }
}

//Define the options for shot values. TODO: Switch case for 6 & V enabling when changing shooter class type between TR and F-Class
let shots_input = document.getElementById('shots_input_')
function add_shot(new_row_id, i){
    shots_input = document.getElementById('shots_input_' + new_row_id)
    console.log("create_shot row " + new_row_id)
    let select_shot = document.createElement('select')
    select_shot.id = "row_" + new_row_id +"_shot_" + i
    select_shot.onchange = function () {update_score_total(new_row_id)}
    // X & 6 and V are exclusive depending on the shooter being TR or F-Class
    let html = '\
        <option value="6.01" id="X"disabled>X</option>\
        <option value="5.01" id="V">V</option\
        <option value="6" id="6" disabled>6</option>\
        <option value="5" selected>5</option>\
        <option value="4">4</option>\
        <option value="3">3</option>\
        <option value="2">2</option>\
        <option value="1">1</option>\
        <option value="0">0</option>'
    select_shot.innerHTML = html
    shots_input.appendChild(select_shot)
}

function  add_sighter_option(new_row_id, i){
    let sighter_option = document.createElement('select')
    sighter_option.id = "row_" + new_row_id + "_sighter_" + i
    let html = '\
        <option value="counter" id="counter">C</option>\
        <option  value="sighter" id= "sighter">S</option>'
    sighter_option.innerHTML = html
    shots_input.appendChild(sighter_option)
}

//Render the number of shots required to score the match
function render_shots(new_row_id = 1){
    let number_of_shots = match_type[0]["match_counters"]
    console.log("Render shots for row " + new_row_id + " with " + number_of_shots + " shots")
    for (let i = 0; i < number_of_shots; i++) {
        add_shot(new_row_id, i)
        //Add sighters specified in match type details
        if (i < match_type[0]['match_sighters']){
            add_sighter_option(new_row_id, i)
        }
    }
}

function toDateInputValue(dateObject){
    const local = new Date(dateObject);
    local.setMinutes(dateObject.getMinutes() - dateObject.getTimezoneOffset());
    return local.toJSON().slice(0,10);
}

//Update score total on changes to the rows score selects
//TODO: Handle sighters, handle diffrent shoot lengths
function update_score_total(row_id){
    total_score = 0
    for (let i = 0; i < 7; i++){
        let shot_value = document.getElementById('row_' + row_id + '_shot_' + i).value
        total_score = parseFloat(total_score) + parseFloat(shot_value)
    }
    document.getElementById('score_' + row_id).innerHTML = total_score.toFixed(2)
}

function update_sighters(row_id, sighter_id){
    let sighter_value = document.getElementById('row_' + row_id + '_sighter_' + sighter_id).value
    //if 
}