import sqlite3
from sqlite3 import Error


class Database:

    def __init__(self):
        self.db_file = "./golf_database.sqlite"
        self.connection = self.create_connection(self.db_file)
        self.initialize()

    @staticmethod
    def create_connection(path):
        connection = None
        try:
            connection = sqlite3.connect(path)
            print("Connection to SQLite DB successful")
        except Error as e:
            print(f"The error '{e}' occurred")

        return connection

    @staticmethod
    def execute_query(self, connection, query):
        cursor = connection.cursor()
        try:
            cursor.execute(query)
            connection.commit()
            print("Query executed successfully")
            return True
        except Error as e:
            print(f"The error '{e}' occurred")
            return False

    def initialize(self):
        create_golfers_table = """
        CREATE TABLE IF NOT EXISTS golfers(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL DEFAULT 'John Doe'
        );
        """
        self.execute_query(self.connection, create_golfers_table)

        create_shots_table = """
        CREATE TABLE IF NOT EXISTS shots(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          golfer_id INTEGER NOT NULL,
          club TEXT NOT NULL DEFAULT 'Driver'
          speed REAL NOT NULL DEFAULT 0.0,
          v_launch_angle REAL NOT NULL DEFAULT 0.0,
          h_launch_angle REAL NOT NULL DEFAULT 0.0,
          carry_distance REAL NOT NULL DEFAULT 0.0,
          total_distance REAL NOT NULL DEFAULT 0.0,
          FOREIGN KEY(golfer_id) REFERENCES golfers(id)
        );
        """
        self.execute_query(self.connection, create_shots_table)

    def add_golfer(self, name):
        cursor = self.connection.cursor()

        add_query = """
            INSERT INTO
                golfers (name)
            VALUES
                (?);
            """

        cursor.execute(add_query, (name,))
        self.connection.commit()

    def add_shot(self, shot_data):
        cursor = self.connection.cursor()
        values = (shot_data["golfer_id"], shot_data["club"], shot_data["speed"], shot_data["v_launch_angle"],
                  shot_data["h_launch_angle"], shot_data["carry_distance"], shot_data["total_distance"])

        add_query = """
        INSERT INTO
            golfers (golfer_id, club, speed, v_launch_angle, h_launch_angle, 
            carry_distance, total_distance)
        VALUES
            (?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(add_query, values)
