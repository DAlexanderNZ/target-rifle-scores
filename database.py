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

def connect():
    """ Connect to the PostgreSQL database server """
    config = load_config()
    try: 
        with psycopg.connect('dbname=' + config['database'] + ' user=' + config['user']) as conn:
            print(f'Connected to {config["database"]} database')
            return conn
    except (Exception, psycopg.DatabaseError) as error:
        print(error)

def create_tables():
    """ Create tables in the PostgreSQL database """
    commands = (
        """
        CREATE TABLE club (
            club_name VARCHAR PRIMARY KEY,
            club_country_code CHAR(3) NOT NULL,
            club_location VARCHAR,
            club_description VARCHAR,
            club_website VARCHAR
        )
        """,
        """
        CREATE TABLE shooter (
            shooter_id SERIAL PRIMARY KEY,
            shooter_nra_id INT,
            shooter_first_name VARCHAR,
            shooter_last_name VARCHAR,
            shooter_dob DATE,
        )
        """,
        """
        CREATE TABLE shooter_club (
            shooter_id INT NOT NULL,
            club_name VARCHAR NOT NULL,
            date_joined DATE,
            FOREIGN KEY (shooter_id)
                REFERENCE shooter (shooter_id) 
                ON DELETE CASCADE,
            FOREIGN KEY (club_name)
                REFERENCE club (club_name)
                ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE class (
            class VARCHAR PRIMARY KEY,
            score_type CHAR(1)
        )
        """,
        """
        CREATE TABLE match_type (
            match_type VARCHAR PRIMARY KEY,
            match_sighters SMALLINT,
            match_counters SMALLINT,
            distance VARCHAR
        )
        """, 
        """
        CREATE TABLE match (
            match_id SERIAL PRIMARY KEY,
            match_name VARCHAR,
            match_type VARCHAR,
            match_descripton VARCHAR,
            FOREIGN KEY (match_type)
                REFERENCE match_type (match_type)
                ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE competition (
            competition VARCHAR PRIMARY KEY,
            competition_description VARCHAR,
        )
        """,
        """
        CREATE TABLE competition_match (
            competition VARCHAR,
            match_id INT,
            PRIMARY KEY (competition, match_id)
            FOREIGN KEY (competition)
                REFERENCE competition (competition)
                ON DELETE CASCADE,
            FOREIGN KEY (match_id)
                REFERENCE match (match_id)
                ON DELETE CASCADE,
        )
        """,
        """
        CREATE TABLE score (
            shooter_id INT,
            competition VARCHAR,
            match_id INT,
            shots CHAR(1)[],
            shot_type CHAR(1)[],
            class VARCHAR,
            FOREIGN KEY (shooter_id)
                REFERENCE shooter (shooter_id)
                ON DELETE CASCADE,
            FOREIGN KEY (competition)
                REFERENCE competition_match (competition)
                ON DELETE CASCADE,
            FOREIGN KEY (match_id)
                REFERENCE competition_match (match_id)
                ON DELETE CASCADE,
            FOREIGN KEY (class)
                REFERENCE class (class)
                ON DELETE CASCADE
        )
        """
    )
    try:
        conn = connect()
        with conn.cursor() as cur:
            print(f'Creating tables in {load_config()["database"]}')
            for command in commands:
                printf(f'Executing {command}')  
                cur.execute(command)
        conn.commit()
    except (Exception, psycopg.DatabaseError) as error:
        print(error)

create_tables()