//Load first row on page load
document.addEventListener('DOMContentLoaded', function(){
    document.getElementById('date_picker').value = toDateInputValue(new Date())
    get_competition_matches()
    add_row()
})

//Get data from flask passed though to js
function json_data(data){
    return JSON.parse(data)
}

//Define and render rows and contents for the table
let row_id = 0
let score_input_table = document.getElementById('score_input')
//increment row_id to allow for unique row ids and existing_rows to existing rows in the table
//TODO: Autocompletion suggestions of name from DB after 4 or more chars are entered. To help ensure correct entry and cut down on typo errors.
function add_row(){
    console.log("create_row")
    row_id++
    let new_row = document.createElement('tr')
    new_row.id = "new_row_" + row_id
    let html = '<td title="Add another shooter" id="button_' + row_id + '"><button type="button" onclick="add_row()" id="row_add_button_' + row_id + '">➕</button></td>\
        <td><input type="text" id="name_' + row_id + '" name="name" title="Shooter Name" required></td>\
        <td>' + get_class_types(row_id) + '</td>\
        <td id="shots_input_' + row_id + '"></td>\
        <td><span type="float" step="0.01" id="score_' + row_id + '" required></span><input type="hidden" id="score_' + row_id + '_input"  name="score"></td>'
    new_row.innerHTML = html
    score_input_table.appendChild(new_row)
    render_shots(row_id)
    update_score_total(row_id)
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
    console.log("Remove row " + removal_row_id)
    if (score_input_table.rows.length > 2) {
        console.log("Remove row " +  removal_row_id + ' new_row_' + removal_row_id)
        document.getElementById('new_row_' + removal_row_id).remove()
        //TODO: Fix this logic to check all rows in table and ➕ to last row if none found or if extra
        if (removal_row_id === row_id){
            let last_row = document.getElementById('row_add_button_' + (row_id - 1))
            last_row.innerHTML = "➕"
            last_row.setAttribute('onclick', 'add_row()')
        }     
    } else {
       alert('You cannot delete the last row of the table')
    }
}

let matches
function get_competition_matches(){
    let competition = document.getElementById('competition_select').value
    fetch("/getmatches", {
        method: "POST",
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({competition: competition})
    })
    .then(response => response.json()) // Convert the response to JSON
    .then(data => {
        matches = data // Store the data in matches
        console.log("Gathered matches for ", matches) // Log the matches
        //Create options for match_select
        let match_select = document.getElementById('match_select')
        match_select.options.length = 0 //Clear existing options
        for (let i = 0; i < matches.length; i++){
            let match_option = document.createElement('option')
            match_option.id = matches[i][2] //Distance
            match_option.value = matches[i][0] //match_id
            match_option.textContent = matches[i][1] //match_name
            match_select.append(match_option)
        }
        update_distance() //Update the distance to the selected match       
    })
    .catch(error => console.error('Error:', error)) // Log any errors
}

function update_matches(){
    console.log("Update matches")
    get_competition_matches()
}

function update_match_descriptions(){
    let match_description_id = document.getElementById('match_select').id
    let match_description = document.getElementById('match_description')
    match_description.textContent = matches[0][5]
}

//TODO: Also update shots selects with sighters and counters (matches[i][4], matches[i][3])
function update_distance(){
    let match_distance = document.getElementById('match_select')
    match_distance = match_distance[match_distance.selectedIndex].id //Get id of selected option
    let distance = document.getElementById('distance')
    distance.value = match_distance
    distance.textContent = match_distance
}


//TODO: Add Flask logic to load type_class's available from database.
function get_class_types(row_id){
    class_types = '<select title="Select Shooter Class" id="type_class_' + row_id + '" onchange="update_class_type_select(' + row_id + ')">\
    <option title="Target Rifle Grades" value="TR">TR</option>\
    <option title="FTR Grades"value="FTR">FTR</option>\
    <option title="F-Open Grade" value="FO-O">F-Open</option>\
    </select>'
    grade = get_grades(row_id)
    return class_types + grade
}

//TODO: When selecting a shooter name, get their current grade in the current comp and set that is the default option if available
function get_grades(row_id){
    let tr_grade = '<select title="Select Shooter Grade" id="tr_grades_' + row_id + '" name="class_type">'
    for (let i = 0; i < classes.length; i++){
        if (classes[i][0].startsWith('TR-')){
            tr_grade = tr_grade.concat('', '<option title="' + classes[i][1] + '" value="' + classes[i][0] + '">' + classes[i][0] + '</option>')
        }   
    }
    tr_grade = tr_grade.concat('', '</select>')
    let ftr_grade = '<select title="Select Shooter Grade" id="ftr_grades_' + row_id + '" style="visibility: hidden">'
    for (let i = 0; i < classes.length; i++){
        if (classes[i][0].startsWith('FTR-')){
            ftr_grade = ftr_grade.concat('', '<option title="' + classes[i][1] + '" value="' + classes[i][0] + '">' + classes[i][0] + '</option>')
        }
    }
    ftr_grade = ftr_grade.concat('', '</select>')
    return tr_grade + ftr_grade

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

//Define the options for shot values. TODO: Switch case for 6 & V enabling when changing shooter class type between TR and F-Class
let shots_input = document.getElementById('shots_input_')
function add_shot(new_row_id, position){
    shots_input = document.getElementById('shots_input_' + new_row_id)
    console.log("create_shot row " + new_row_id)
    let select_shot = document.createElement('select')
    select_shot.id = "row_" + new_row_id +"_shot_" + position
    select_shot.name = "shots"
    select_shot.title = "Select Shot Score"
    select_shot.onchange = function () {update_score_total(new_row_id)}
    // X & 6 and V are exclusive depending on the shooter being TR or F-Class
    let html = '\
        <option value="6.001" id="X_' + new_row_id + position +'"disabled>X</option>\
        <option value="5.001" id="V_' + new_row_id + position +'">V</option>\
        <option value="6" id="6_' + new_row_id + position +'"disabled>6</option>\
        <option value="5" selected>5</option>\
        <option value="4">4</option>\
        <option value="3">3</option>\
        <option value="2">2</option>\
        <option value="1">1</option>\
        <option value="0">0</option>'
    select_shot.innerHTML = html
    shots_input.appendChild(select_shot)
}

//Sighter as checkbox
function add_sighter_option(new_row_id, position){
    let sighter_option = document.createElement('input')
    sighter_option.type = "checkbox"
    sighter_option.id = "row_" + new_row_id + "_sighter_" + position
    sighter_option.name = "shot_type"
    sighter_option.title = "Sighter"
    sighter_option.onchange = function () {update_to_counter(new_row_id, position)}
    shots_input.appendChild(sighter_option)
}

//Start of enforcing rule on sighter converting
function apply_checkbox_state(row_id, position, is_checked){
    let sighter_checkboxs =  document.querySelectorAll('#shots_input_' + row_id + ' input[type="checkbox"]')
    if  (is_checked){
        //Check previous checkboxes
        for (let i = 0; i < position; i++){
            sighter_checkboxs[i].checked = true
        }
    } else  {
        //Uncheck following checkboxes
        for (let i = position; i < sighter_checkboxs.length; i++){
            sighter_checkboxs[i].checked = false
        }
    }
}
//Update score total on changes to the rows score selects or sighters
let unconverted_sighters = 0
function update_score_total(row_id){
    let total_score = 0
    for (let i = 0 + unconverted_sighters; i < (match_type[0]["match_counters"] + unconverted_sighters); i++){
        let shotElement = document.getElementById('row_' + row_id + '_shot_' + i);
        if (shotElement) {
            let shot_value = shotElement.value
            total_score += parseFloat(shot_value)
        } else {
            console.error('Shot element not found for id: row_' + row_id + '_shot_' + i)
        }
    }
    let score_element_display = document.getElementById('score_' + row_id)
    score_element_display.innerHTML = total_score.toFixed(3) //TODO: Remove zeros after the decimal point
    let score_element_input = document.getElementById('score_' + row_id + '_input')
    score_element_input.value = total_score.toFixed(3)
}

//Handles changes to sighter select state
//TODO: Enforce rule that first sigher can only be converted with the second sighter
function update_to_counter(row_id, position){
    let sighter_checkboxs =  document.querySelectorAll('#shots_input_' + row_id + ' input[type="checkbox"]')
    let new_shot_pos = document.getElementById('shots_input_' + row_id).childElementCount - 2
    add_shot(row_id, new_shot_pos)
    unconverted_sighters++
    let sighter_value = document.getElementById('row_' + row_id + '_sighter_' + position)
    sighter_value.onchange = function () {update_to_sighter(row_id, position)}
    
    update_class_type_select(row_id) //Ensure that score selects have correct options enabled
    update_score_total(row_id)
}

function update_to_sighter(row_id, position){
    last_shot_pos = document.getElementById('shots_input_' + row_id).childElementCount - 3
    document.getElementById('row_' + row_id + '_shot_' + last_shot_pos).remove()

    let sighter_value = document.getElementById('row_' + row_id + '_sighter_' + position)
    sighter_value.onchange = function () {update_to_counter(row_id, position)}
    
    unconverted_sighters--
    update_class_type_select(row_id) //Ensure that score selects have correct options enabled
    update_score_total(row_id)
}

//Shooter class type change handling and grade selection
//Checks the selected class, currently only works with NRA fullbore classes. 
//TODO: Generalize function to allow for different class types. E.g ISSF 300m classes
function update_class_type_select(row_id){
    let type_select = document.getElementById('type_class_' + row_id)
    if (type_select.value === 'TR'){
        update_to_tr(row_id)
    } else  {
        update_to_fclass(row_id)
    }
    show_grades(row_id)
}

function update_to_fclass(row_id){
    //console.log("Update to F-Class")
    for (let i = 0; i < document.getElementById('shots_input_' + row_id).childElementCount - 2; i++){
        document.getElementById('X_' + row_id + i).removeAttribute('disabled', 'disabled')
        document.getElementById('6_' + row_id + i).removeAttribute('disabled', 'disabled')
        document.getElementById('V_' + row_id + i).setAttribute('disabled', 'disabled')
    }
}

//TODO: Change any X or 6 score values back to V, otherwise over total scores can be entered
function update_to_tr(row_id){
    //console.log("Update to TR")
    for (let i = 0; i < document.getElementById('shots_input_' + row_id).childElementCount - 2; i++){
        document.getElementById('X_' + row_id + i).setAttribute('disabled', 'disabled')
        document.getElementById('6_' + row_id + i).setAttribute('disabled', 'disabled')
        document.getElementById('V_' + row_id + i).removeAttribute('disabled', 'disabled')
    }
}

//TODO: Filter shown grades by grades defined on a competition basis. E.g. Often there is no TR-T entry or one class isn't run in the comp
function show_grades(row_id){
    let current_class = document.getElementById('type_class_' + row_id).value
    current_class.name = 'hidden'
    let tr_select = document.getElementById('tr_grades_' + row_id)
    let ftr_select = document.getElementById('ftr_grades_' + row_id)
    if (current_class === 'TR'){
        tr_select.style.visibility = 'visible'
        tr_select.name = 'class_type'
        ftr_select.style.visibility = 'hidden'
        ftr_select.name = 'hidden'
    } else {
        tr_select.style.visibility = 'hidden'
        tr_select.name = 'hidden'
        if (current_class === 'FTR'){
            ftr_select.style.visibility = 'visible'
            ftr_select.name = 'class_type'
        } else{
            ftr_select.style.visibility = 'hidden'
        }
    }
    if (current_class === 'FO-O'){
            current_class.name = 'class_type'
        }
}

function toDateInputValue(dateObject){
    const local = new Date(dateObject)
    local.setMinutes(dateObject.getMinutes() - dateObject.getTimezoneOffset())
    return local.toJSON().slice(0,10)
}
