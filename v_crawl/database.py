from configparser import ConfigParser
import psycopg2


class Database:
    table_name = ""
    conn = None
    cursor = None

    def __init__(self, table_name):
        self.table_name = table_name
        db_settings = {}
        section = "postgresql"
        filename = "database.ini"

        parser = ConfigParser()
        parser.read(filename)

        # Read the settings from the given ini file
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db_settings[param[0]] = param[1]
        else:
            raise Exception("Section {0} not found in the {1} file".format(section, filename))

        print("Connecting to database")
        self.conn = psycopg2.connect(
            host=db_settings['host'],
            port=db_settings['port'],
            database=db_settings['dbname'],
            user=db_settings['user'],
            password=db_settings['password']
        )
        self.cursor = self.conn.cursor()

        return

    def insert_item(self, movie_item):
        # Create the query and add the table to it
        query = "INSERT INTO %s (movie_id, url, title, movie_type, rating, imdb, genres, year, fsk, poster)" \
                "VALUES (" \
                "%%(movie_id)s, " \
                "%%(url)s, " \
                "%%(title)s, " \
                "%%(movie_type)s, " \
                "%%(rating)s, " \
                "%%(imdb)s, " \
                "%%(genres)s, " \
                "%%(year)s, " \
                "%%(fsk)s, " \
                "%%(poster)s" \
                ") ON CONFLICT DO NOTHING RETURNING movie_id;" % self.table_name
        try:
            poster_path = movie_item['poster']

            # No poster found for this movie
            if poster_path is "NULL":
                self.cursor.execute(query, movie_item)
            else:
                # Get the poster and encode it as binary for the DB
                with open(poster_path, "rb") as file:
                    movie_item['poster'] = psycopg2.Binary(file.read())
                    self.cursor.execute(query, movie_item)
        except psycopg2.Error as e:
            print(e.pgerror)
            self.conn.rollback()
            return

        result = self.cursor.fetchone()

        if result is None:
            print("Didn't add item to DB")
            return

        self.conn.commit()
        print("Successfully added new item to DB")
        return

    def __del__(self):
        if self.cursor is not None:
            self.cursor.close()

        if self.conn is not None:
            self.conn.close()
