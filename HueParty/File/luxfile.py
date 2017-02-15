import csv
import os
import json
from HueParty.File.md5calculator import md5Calculator


class LuxFile:
    def __init__(self, song_md5, song_file):
        self.song_md5 = song_md5

        # Database name and location
        self.database_folder = "config/"
        self.database_name = "database.db"
        self.database_complete_filename = self.database_folder + self.database_name

        # Lux files location
        self.lux_file_directory = "lux/"
        self.song_file = song_file
        self.lux_md5 = ""

        self.database = open(self.database_complete_filename, "a+")

        self.lux_file = self.get_lux_file()
        self.database.close()

    # Opens a lux file. It might be empty or not
    def get_lux_file(self):
        if self.is_in_db():
            # Check if file exists
            file = self.lux_file_directory + self.lux_md5 + ".lux"
            if os.path.exists(file) and os.path.getsize(file):
                # If it does, load it
                lux_file = open(file).read()
                return json.loads(lux_file)

            # If file doesn't exist, remove it in the database.
            else:
                # Recreate lux file
                lux_file, lux_md5 = self.create_lux_file()

                # Remove previous row from database
                reader = csv.reader(self.database, delimiter=",")
                database = []
                for i in reader:
                    if i[0] != self.song_md5:
                        database.append()
                self.database.close()
                # Rebuild database
                self.database = open(self.database_complete_filename, "w+")
                writer = csv.writer(self.database)
                for row in database:
                    writer.writerow(row)
                self.database.close()

                # Add new file to the database.
                self.database = open(self.database_complete_filename, "a+")
                self.add_to_db(lux_md5)
                return lux_file

        # If the file is not in the database, create it
        else:
            lux_file, lux_md5 = self.create_lux_file()
            self.add_to_db(lux_md5)
            return lux_file

    # Check if a song is in the database
    def is_in_db(self):
        reader = csv.reader(self.database, delimiter=",")
        for row in reader:
            if row[0] == self.song_md5:
                self.lux_md5 = row[1]
                return True
        return False

    # Add a song to the database
    def add_to_db(self, lux_md5):
        writer = csv.writer(self.database, delimiter=",")
        data = [self.song_md5, lux_md5]
        writer.writerow(data)

    # Create lux file from the song using the Sound class
    def create_lux_file(self):
        pass
