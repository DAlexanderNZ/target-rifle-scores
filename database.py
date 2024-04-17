from configparser import ConfigParser
import psycopg

#Database config and loading
def load_config(filename='database.ini', section='postgresql'):
    """ Use configparser to load and parse config ini file """
    parser = ConfigParser()
    parser.read(filename)
    config = {}
    if parser.has_section(section):
        for item in parser.items(section):
            config[item[0]] = item[1]
    else:
        raise Exception(f'Section {section} not found in {filename}')
    return config

#Doesn't work as expected, returns conn as a closed connection
def connect():
    """ Connect to the PostgreSQL database server """
    config = load_config()
    print(config)
    try: 
        conn = psycopg.connect(**config)
        print(f'Connected to {config["database"]} database')
        return conn
    except (Exception, psycopg.DatabaseError) as error:
        print(f'Error : {error}')

def get_competitions(conn, query='SELECT competition FROM competition'):
    """ Get the competitions from the database """
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            competitions = cur.fetchall()
            return(competitions)
    except (Exception, psycopg.DatabaseError) as error:
        print(f'get_competitions: {error}')

def get_matches(conn, competition):
    """ Get the matches for a competition from the database """
    try:
        with conn.cursor() as cur:
            query = """
            SELECT match.match_id, match.match_name, match.match_distance, match.match_counters, match.description
            FROM competition_match
            INNER JOIN match ON competition_match.match_id = match.match_id
            WHERE competition_match.competition = %s
            """
            cur.execute(query, (competition,))
            matches = cur.fetchall()
            if not matches:
                print("No matches found. Check the competition parameter and database state.")
            return matches
    except (Exception, psycopg.DatabaseError) as error:
        print(f"get_matches error: {error}")

def get_classes(conn):
    """ Get the classes from the database """
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT class, name FROM class")
            classes = cur.fetchall()
            return classes
    except (Exception, psycopg.DatabaseError) as error:
        print(f'get_classes: {error}')
        return None
    
def create_tables(conn):
    """ Create tables in the PostgreSQL database """
    commands = (
        """
        CREATE TABLE IF NOT EXISTS club (
            club_name VARCHAR PRIMARY KEY,
            club_country_code CHAR(3) NOT NULL,
            club_location VARCHAR,
            club_description VARCHAR,
            club_website VARCHAR
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS shooter (
            shooter_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            shooter_nra_id INT,
            shooter_first_name VARCHAR,
            shooter_last_name VARCHAR,
            shooter_dob DATE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS shooter_club (
            shooter_id INT NOT NULL,
            club_name VARCHAR NOT NULL,
            date_joined DATE,
            CONSTRAINT shooter_fk FOREIGN KEY (shooter_id) 
                REFERENCES shooter(shooter_id)
                ON DELETE CASCADE,
            CONSTRAINT club_fk FOREIGN KEY (club_name) 
                REFERENCES club(club_name)
                ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS class (
            class VARCHAR PRIMARY KEY,
            score_type CHAR(1),
            name VARCHAR
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS match_type (
            match_distance VARCHAR,
            match_counters SMALLINT,
            match_sighters SMALLINT,
            PRIMARY KEY (match_distance, match_counters)
        )
        """, 
        """
        CREATE TABLE IF NOT EXISTS match (
            match_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            match_name VARCHAR,
            match_distance VARCHAR,
            match_counters SMALLINT,
            description VARCHAR,
            CONSTRAINT match_fk FOREIGN KEY (match_distance, match_counters)
            REFERENCES match_type (match_distance, match_counters)
            ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS competition (
            competition VARCHAR PRIMARY KEY,
            competition_description VARCHAR
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS competition_match (
            competition VARCHAR,
            match_id INT,
            PRIMARY KEY (competition, match_id),
            CONSTRAINT competition_fk FOREIGN KEY (competition)
                REFERENCES competition (competition)
                ON DELETE CASCADE,
            CONSTRAINT match_id_fk FOREIGN KEY (match_id)
                REFERENCES match (match_id)
                ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS score (
            shooter_id INT,
            competition VARCHAR,
            match_id INT,
            shots CHAR(1)[],
            shot_type CHAR(1)[],
            total REAL,
            class VARCHAR,
            date DATE,
            CONSTRAINT shooter_id_fk FOREIGN KEY (shooter_id)
                REFERENCES shooter (shooter_id)
                ON DELETE CASCADE,
            CONSTRAINT competition_match_fk FOREIGN KEY (competition, match_id)
                REFERENCES competition_match (competition, match_id)
                ON DELETE CASCADE,
            CONSTRAINT class_fk FOREIGN KEY (class)
                REFERENCES class (class)
                ON DELETE CASCADE
        )
        """
    )
    try:
        with conn.cursor() as cur:
            print(f'Creating tables in database')
            for command in commands:
                #print(f'Executing {command}')  
                cur.execute(command)
        conn.commit()
    except (Exception, psycopg.DatabaseError) as error:
        print(f'create_tables: {error}')
    
def default_info(conn):
    """ Create the default inforamtion for the database. Based on NRANZ classes and match types """
    classes = (
        { 'class': 'TR-A', 'score_type':  'V', 'name': 'Target Rifle A Grade'},
        { 'class': 'TR-B', 'score_type':  'V', 'name': 'Target Rifle B Grade'},
        { 'class': 'TR-C', 'score_type':  'V', 'name': 'Target Rifle C Grade'},
        { 'class': 'TR-T', 'score_type':  'V', 'name': 'Target Rifle Tyro Grade'},
        { 'class': 'FO-O', 'score_type':  'X', 'name': 'F Open'},
        { 'class': 'FTR-C', 'score_type':  'X', 'name': 'FTR Classic'},
        { 'class': 'FTR-O', 'score_type':  'X', 'name': 'FTR'},
        { 'class': 'FPR-O', 'score_type':  'X', 'name': 'FPR (Precision Rifle)'}
    )
    with  conn.cursor() as cur:
        query = "INSERT INTO class (class, score_type, name) VALUES (%(class)s, %(score_type)s, %(name)s)"
        cur.executemany(query, classes)

    match_types = (
        { 'match_distance': '300y', 'match_counters': 7, 'match_sighters': 2},
        { 'match_distance': '500y', 'match_counters': 7, 'match_sighters': 2},
        { 'match_distance': '600y', 'match_counters': 7, 'match_sighters': 2},
        { 'match_distance': '700y', 'match_counters': 7, 'match_sighters': 2},
        { 'match_distance': '800y', 'match_counters': 7, 'match_sighters': 2},
        { 'match_distance': '900y', 'match_counters': 7, 'match_sighters': 2},
        { 'match_distance': '1000y', 'match_counters': 7, 'match_sighters': 2},
        { 'match_distance': '300y', 'match_counters': 10, 'match_sighters': 2},
        { 'match_distance': '500y', 'match_counters': 10, 'match_sighters': 2},
        { 'match_distance': '600y', 'match_counters': 10, 'match_sighters': 2},
        { 'match_distance': '700y', 'match_counters': 10, 'match_sighters': 2},
        { 'match_distance': '800y', 'match_counters': 10, 'match_sighters': 2},
        { 'match_distance': '900y', 'match_counters': 10, 'match_sighters': 2},
        { 'match_distance': '1000y', 'match_counters': 10, 'match_sighters': 2},
        { 'match_distance': '300y', 'match_counters': 15, 'match_sighters': 2},
        { 'match_distance': '500y', 'match_counters': 15, 'match_sighters': 2},
        { 'match_distance': '600y', 'match_counters': 15, 'match_sighters': 2},
        { 'match_distance': '700y', 'match_counters': 15, 'match_sighters': 2},
        { 'match_distance': '800y', 'match_counters': 15, 'match_sighters': 2},
        { 'match_distance': '900y', 'match_counters': 15, 'match_sighters': 2},
        { 'match_distance': '1000y', 'match_counters': 15, 'match_sighters': 2}
    )
    with conn.cursor() as cur:
        query = "INSERT INTO match_type (match_distance, match_counters, match_sighters) VALUES (%(match_distance)s, %(match_counters)s, %(match_sighters)s)"
        cur.executemany(query, match_types)
    conn.commit()

def create_shooter(shooter,  conn):
    """ 
    Create a new shooter 
    :param shooter: a dictionary of shooter attributes [shooter_nra_id, shooter_first_name, shooter_last_name, shooter_dob]
    :param conn: a connection to the database
    """
    try:
            with conn.cursor() as cur:
                #This query needs updating to best practice 
                cur.execute("INSERT INTO shooter (shooter_nra_id, shooter_first_name, shooter_last_name, shooter_dob"")VALUES (%s, %s, %s, %s);", 
                            (shooter['shooter_nra_id'], shooter['shooter_first_name'], shooter['shooter_last_name'], shooter['shooter_dob']))
    except (Exception, psycopg.DatabaseError) as error:
        print(f'create_shooter: {error}')

def record_score(score, conn):
    """
    Record scores for shooters in a match
    :param score: a dictionary of score attributes [shooter_id, competition, match_id, shots, shot_type, total, class, date]
    :param conn: a connection to the database
    """
    with conn.cursor() as cur:
        query = "INSERT INTO score (shooter_id, competition, match_id, shots, shot_type, total, class, date) VALUES (%(shooter_id)s, %(competition)s, %(match_id)s, %(shots)s, %(shot_type)s, %(total)s %(class)s, %(date)s);"
        cur.execute(query, score)
    conn.commit()


#Database setup
#config = load_config()
#conn = psycopg.connect(**config)
#create_tables(conn)
#default_info(conn)
#conn.close()

