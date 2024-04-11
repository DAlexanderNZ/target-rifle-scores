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
    print(config)
    try: 
        conn = psycopg.connect(**config)
        print(f'Connected to {config["database"]} database')
        return conn
    except (Exception, psycopg.DatabaseError) as error:
        print(f'Error : {error}')

def create_tables():
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
            score_type CHAR(1)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS match_type (
            match_type VARCHAR PRIMARY KEY,
            match_sighters SMALLINT,
            match_counters SMALLINT,
            distance VARCHAR
        )
        """, 
        """
        CREATE TABLE IF NOT EXISTS match (
            match_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
            match_name VARCHAR,
            match_type VARCHAR,
            match_description VARCHAR,
            CONSTRAINT match_type_fk FOREIGN KEY (match_type)
                REFERENCES match_type (match_type)
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
            class VARCHAR,
            FOREIGN KEY (shooter_id)
                REFERENCES shooter (shooter_id)
                ON DELETE CASCADE,
            FOREIGN KEY (competition)
                REFERENCES competition (competition)
                ON DELETE CASCADE,
            FOREIGN KEY (match_id)
                REFERENCES match (match_id)
                ON DELETE CASCADE,
            FOREIGN KEY (class)
                REFERENCES class (class)
                ON DELETE CASCADE
        )
        """
    )
    config = load_config()
    conn = psycopg.connect(**config)
    try:
        #conn = connect()
        with conn.cursor() as cur:
            print(f'Creating tables in database')
            for command in commands:
                print(f'Executing {command}')  
                cur.execute(command)
        #conn.commit()
    except (Exception, psycopg.DatabaseError) as error:
        print(f'create_tables: {error}')

create_tables()