from database import database

#Database class with default values. To be run on setting up app or container
class database_setup(database):
    #Call setup functions when the setup class is defined.
    def __init__(self):
        self.create_tables()
        self.default_info()

    #
    #   First time database setup functions
    #

    def create_tables(self):
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
                match_distance VARCHAR(5),
                match_counters SMALLINT,
                match_sighters SMALLINT,
                PRIMARY KEY (match_distance, match_counters)
            )
            """, 
            """
            CREATE TABLE IF NOT EXISTS match (
                match_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                match_name VARCHAR,
                match_distance VARCHAR(5),
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
                shots VARCHAR(5)[],
                shot_type BOOLEAN[],
                total REAL,
                class VARCHAR,
                date DATE,
                row_created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
            with self.conn.cursor() as cur:
                print('Creating tables in database')
                for command in commands:
                    cur.execute(command)
            self.conn.commit()
        except (Exception, psycopg.DatabaseError) as error:
            print(f'create_tables: {error}')

    def default_info(self):
        """ Create the default inforamtion for the database. Based on NRANZ classes and match types """
        classes = (
            { 'class': 'TR-A', 'score_type':  'V', 'name': 'Target Rifle A Grade'},
            { 'class': 'TR-B', 'score_type':  'V', 'name': 'Target Rifle B Grade'},
            { 'class': 'TR-C', 'score_type':  'V', 'name': 'Target Rifle C Grade'},
            { 'class': 'TR-T', 'score_type':  'V', 'name': 'Target Rifle Tyro Grade'},
            { 'class': 'F-Open', 'score_type':  'X', 'name': 'F Open'},
            { 'class': 'FTR-O', 'score_type':  'X', 'name': 'FTR'},
            { 'class': 'FTR-C', 'score_type':  'X', 'name': 'FTR Classic'},
            { 'class': 'FPR-O', 'score_type':  'X', 'name': 'FPR (Precision Rifle)'}
        )
        with  self.conn.cursor() as cur:
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
        with self.conn.cursor() as cur:
            query = "INSERT INTO match_type (match_distance, match_counters, match_sighters) VALUES (%(match_distance)s, %(match_counters)s, %(match_sighters)s)"
            cur.executemany(query, match_types)
        self.conn.commit()

#Run the db setup
db = database_setup()
