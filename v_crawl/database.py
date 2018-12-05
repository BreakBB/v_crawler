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
        query_string = "INSERT INTO %s (movie_id, url, title, rating, imdb, genres, year, fsk)" \
                       "VALUES (" \
                       "%%(movie_id)s, %%(url)s, %%(title)s, %%(rating)s, %%(imdb)s, %%(genres)s, %%(year)s, %%(fsk)s" \
                       ") ON CONFLICT DO NOTHING RETURNING movie_id;" % self.table_name
        try:
            self.cursor.execute(query_string, movie_item)
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
