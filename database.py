from configparser import ConfigParser
import bcrypt
import psycopg

class database():
    def  __init__(self, config_file='database.ini'):
        """ Initialise the database class with a config file """
        self.config_file = config_file
        self.conn = self.connect()
        self.classes = ['TR-A', 'TR-B', 'TR-C', 'TR-T', 'FTR-O', 'FTR-C', 'FPR-O', 'F-Open']

    #Database config and loading
    @staticmethod
    def load_config(filename, section='postgresql'):
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
    def connect(self):
        """ Connect to the PostgreSQL database server """
        config = self.load_config(self.config_file)
        try: 
            conn = psycopg.connect(**config)
            print(f'Connected to {config["dbname"]} database')
            return conn
        except (Exception, psycopg.DatabaseError) as error:
            print(f'connect failed: {error}')

    #
    #   Score related database functions
    #

    @staticmethod
    def replace_v_x(scores, score_pos):
        """ Replace 5.001 with V and 6.001 with X in the scores list when returning scores to display """
        for score in scores:
            for i, shot in enumerate(score[score_pos]):
                if shot == '5.001':
                    score[score_pos][i] = 'V'
                elif shot == '6.001':
                    score[score_pos][i] = 'X'
        return scores
    
    def get_all_scores(self):
        """ Get all scores from the database """
        try:
            with self.conn.cursor() as cur:
                #Get the score values and related infomation in the format [shooter_name, class, competition, match_name, shots, shot_type, total, date]
                cur.execute("""
                SELECT shooter.shooter_first_name || ' ' || shooter.shooter_last_name as shooter_name, score.class, score.competition, match.match_name, score.shots, score.shot_type, score.total, score.date
                FROM score
                INNER JOIN shooter ON score.shooter_id = shooter.shooter_id
                INNER JOIN match ON  score.match_id = match.match_id;
                """)
                scores = cur.fetchall()
                scores = self.replace_v_x(scores, 4)
                return scores
        except (Exception, psycopg.DatabaseError) as error:
            print(f'get_all_scores: {error}')
            return []  # Return an empty list in case of an error
        
    def get_comp_scores(self, competition):
        """ Get all scores for a competition from the database """
        try:
            with self.conn.cursor() as cur:
                #Get the score values and related infomation in the format [shooter_name, class, match_name, shots, shot_type, total, date]
                query = """
                SELECT shooter.shooter_first_name || ' ' || shooter.shooter_last_name as shooter_name, score.class, match.match_name, score.shots, score.shot_type, score.total, score.date
                FROM score
                INNER JOIN shooter ON score.shooter_id = shooter.shooter_id
                INNER JOIN match ON  score.match_id = match.match_id
                LEFT JOIN class ON score.class = class.class
                WHERE score.competition = %s
                ORDER BY match.match_name, 
                array_position(ARRAY[%s], score.class);
                """
                cur.execute(query, (competition, self.classes))
                scores = cur.fetchall()
                scores = self.replace_v_x(scores, 3)
                return scores
        except (Exception, psycopg.DatabaseError) as error:
            print(f'get_comp_scores: {error}')

    def get_comp_results(self, competition):
        """ Get the results for a competition from the database """
        try:
            with self.conn.cursor() as cur:
                #Get the score total values and related infomation in the format [shooter_name, class, match_name, total, date]
                query = """
                SELECT shooter.shooter_first_name || ' ' || shooter.shooter_last_name as shooter_name, score.class, match.match_name, score.total, score.date
                FROM score
                INNER JOIN shooter ON score.shooter_id = shooter.shooter_id
                INNER JOIN match ON  score.match_id = match.match_id
                LEFT JOIN class ON score.class = class.class
                WHERE score.competition = %s
                ORDER BY match.match_name, 
                array_position(ARRAY[%s], score.class);
                """
                cur.execute(query, (competition, self.classes))
                results = cur.fetchall()
                return results
        except (Exception, psycopg.DatabaseError) as error:
            print(f'get_comp_results: {error}')

    def get_competitions(self, query='SELECT competition FROM competition'):
        """ Get the competitions from the database """
        try:
            with self.conn.cursor() as cur:
                cur.execute(query)
                competitions = cur.fetchall()
                return(competitions)
        except (Exception, psycopg.DatabaseError) as error:
            print(f'get_competitions: {error}')

    def get_matches(self, competition):
        """ Get the matches for a competition from the database """
        try:
            with self.conn.cursor() as cur:
                query = """
                SELECT match.match_id, match.match_name, match.match_distance, match.match_counters, match_type.match_sighters, match.description
                FROM competition_match
                INNER JOIN match ON competition_match.match_id = match.match_id
                INNER JOIN match_type ON (match.match_distance, match.match_counters) = (match_type.match_distance, match_type.match_counters)
                WHERE competition_match.competition = %s
                ORDER BY match.match_distance, match.match_counters
                """
                cur.execute(query, (competition,))
                matches = cur.fetchall()
                if not matches:
                    print("No matches found. Check the competition parameter and database state.")
                return matches
        except (Exception, psycopg.DatabaseError) as error:
            print(f"get_matches error: {error}")

    def get_classes(self):
        """ Get the classes from the database """
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT class, name FROM class")
                classes = cur.fetchall()
                return classes
        except (Exception, psycopg.DatabaseError) as error:
            print(f'get_classes: {error}')
            return None

    def get_name_suggestions(self, name):
        """ Get a list of name suggestions from the shooter table """
        try:
            with self.conn.cursor() as cur:
                query = """
                SELECT shooter_id, shooter_first_name, shooter_last_name 
                FROM shooter
                WHERE shooter_first_name ILIKE %s OR shooter_last_name ILIKE %s
                """
                #Add '%' wildcard characters around the name for partial matching  
                name_pattern = '%' + name + '%'          
                cur.execute(query, (name_pattern, name_pattern))
                suggestions = cur.fetchall()
                if not suggestions:
                    suggestions = [(0, "No user by that name found",  "")]
                return suggestions
        except (Exception, psycopg.DatabaseError) as error:
            print(f'get_name_suggestions: {error}')

    def record_score(self, score):
        """
        Record scores for shooters in a match
        :param score: a dictionary of score attributes [shooter_id, competition, match_id, shots, shot_type, total, class, date]
        """
        with self.conn.cursor() as cur:
            query = "INSERT INTO score (shooter_id, competition, match_id, shots, shot_type, total, class, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
            cur.execute(query, score)
        self.conn.commit()

    def record_new_match(self, match):
        """
        Record a new match in the database
        :param match: a dictionary of match attributes [match_name, match_distance + match_distance_type, match_counters, match_description, competition]
        """
        with self.conn.cursor() as cur:
            query = """
            INSERT INTO match (match_name, match_distance, match_counters, description)  VALUES (%s, %s, %s, %s) RETURNING match_id;
            """
            cur.execute(query, (match[0], match[1], match[2], match[3]))
            match_id = cur.fetchone()[0]
            query = "INSERT INTO competition_match (competition, match_id) VALUES (%s, %s);"
            cur.execute(query, (match[4], match_id))
        self.conn.commit()

    def remove_match(self, match_id):
        """
        Removes match from database if it has no scores
        :param match_id: the match_id of the match to be removed
        """
        try:
            with self.conn.cursor() as cur:
                query = """
                DELETE FROM match 
                WHERE match_id NOT IN (
                    SELECT DISTINCT match_id FROM score
                ) AND match_id = %s;
                """
                cur.execute(query, (match_id,))
                match_removed = cur.rowcount
            self.conn.commit()
            if match_removed == 0:
                return False
            return True
        except (Exception, psycopg.DatabaseError) as error:
            print(f'remove_match: {error}')
            return False

    #
    #   User auth and account related database functions
    #

    def register_user(self, new_user):
        """ Register a new user in the database """
        password_hash = bcrypt.hashpw(new_user['password'].encode('utf-8'), bcrypt.gensalt())
        try:
            with self.conn.cursor() as cur:
                query = "INSERT INTO users (email, password_hash, first_name, last_name) VALUES (%s, %s, %s, %s); RETURNING id;"
                cur.execute(query, (new_user['email'], password_hash, new_user['first_name'], new_user['last_name']))
                user_id = cur.fetchone()[0]
                query = "INSERT INTO user_edit_log (user_id) VALUES (%s);"
                cur.execute(query, (user_id,))
            self.conn.commit()
        except (Exception, psycopg.DatabaseError) as error:
            print(f'register_user: {error}')

    def verify_user(self, user_email, user_password):
        """ Verify a user's password """
        try:
            with self.conn.cursor() as cur:
                query = "SELECT password FROM users WHERE email = %s;"
                cur.execute(query, (user_email,))
                password_hash = cur.fetchone()[0]
                if bcrypt.checkpw(user_password.encode('utf-8'), password_hash):
                    return True
                return False
        except (Exception, psycopg.DatabaseError) as error:
            print(f'verify_user: {error}')
            return False

    def get_user_id(self, user_email):
        """ Get a user from the database. Return None if user doesn't exist """
        try:
            with self.conn.cursor() as cur:
                query = "SELECT id FROM users WHERE email = %s"
                cur.execute(query, (user_email,))
                user_id = cur.fetchone()
                return user_id
        except (Exception, psycopg.DatabaseError) as error:
            print(f'get_user_id: {error}')
            return None
    
    def update_user_password(self, user_email, user_password):
        """ Update a user's password """
        password_hash = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt())
        try:
            with self.conn.cursor() as cur:
                query = "UPDATE users SET password_hash = %s WHERE email = %s;"
                cur.execute(query, (password_hash, user_email))
            self.conn.commit()
        except (Exception, psycopg.DatabaseError) as error:
            print(f'update_user_password: {error}')

    def is_authenticated(self, user_id):
        """ Check if a user is authenticated """
        try:
            with self.conn.cursor() as cur:
                query = "SELECT "
                cur.execute(query)
                authenticated = cur.fetchone()
                if authenticated:
                    return True
                return False
        except (Exception, psycopg.DatabaseError) as error:
            print(f'is_authenticated: {error}')
            return False
        
    #
    #   Shooter and club related functions
    #

    def create_shooter(self, shooter):
        """ 
        Create a new shooter 
        :param shooter: a dictionary of shooter attributes [shooter_nra_id, shooter_first_name, shooter_last_name, shooter_dob]
        """
        try:
                with self.conn.cursor() as cur:
                    #This query needs updating to best practice 
                    cur.execute("INSERT INTO shooter (shooter_nra_id, shooter_first_name, shooter_last_name, shooter_dob"")VALUES (%s, %s, %s, %s);", 
                                (shooter['shooter_nra_id'], shooter['shooter_first_name'], shooter['shooter_last_name'], shooter['shooter_dob']))
        except (Exception, psycopg.DatabaseError) as error:
            print(f'create_shooter: {error}')