import csv
import os
import json

from HueParty.Sound.audiotranscode import AudioTranscode

from HueParty.File.md5calculator import md5Calculator
from HueParty.Sound.sound import Sound


class LuxFile:
    def __init__(self, song_md5, song_file, sampling_rate):
        self.song_md5 = song_md5

        # Database name and location
        self.database_folder = "config/"
        self.database_name = "database.db"
        self.database_complete_filename = self.database_folder + self.database_name

        # Lux files location
        self.lux_file_directory = "lux/"
        self.song_file = song_file
        self.lux_md5 = ""

        # Lux sampling rate (per second)
        self.sampling_rate = sampling_rate

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
                # Go to top of file
                self.database.seek(0)
                reader = csv.reader(self.database, delimiter=",")
                database = []
                for i in reader:
                    # Avoid blank lines
                    if i:
                        # Remove existing info about the song
                        if i[0] != self.song_md5:
                            database.append(i)
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
        # Go to top of file
        self.database.seek(0)
        reader = csv.reader(self.database, delimiter=",")
        for row in reader:
            # Avoid blank lines
            if row:
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
    # Returns the lux_file json data and the md5 of the lux file
    def create_lux_file(self):

        # Convert to song file to wav
        audio_handler = AudioTranscode()
        audio_handler.transcode(self.song_file, 'tmp.wav')
        # Analyse the song file
        song_class = Sound("tmp.wav", self.sampling_rate)
        song = song_class.get_song()
        os.remove("tmp.wav")

        # Transform the values for frequencies and amplitudes to RGB
        for key in song:
            rgb = self.nm_to_rgb(song[key]["amp"], song[key]["freq"])
            song[key]["rgb"] = song[key].pop("freq")
            song[key]["rgb"] = rgb
            song[key].pop("amp")

        # Create the .lux file
        tmp_file_path = self.lux_file_directory + "tmp"

        # Dump the JSON dictionary inside
        lux_file = open(tmp_file_path, "w+")
        json_dic = json.dumps(song, sort_keys=True)
        json.dump(json_dic, lux_file)
        lux_file.close()

        # Get the file's md5
        md5 = md5Calculator()
        lux_md5 = md5.get_md5(tmp_file_path)

        # Rename the file to "md5".lux
        lux_file_name = self.lux_file_directory + lux_md5 + ".lux"
        os.rename(tmp_file_path, lux_file_name)

        # Return the JSON dictionary and the md5 of the file
        return json_dic, lux_md5

    # Create RGB values from brightness and values of the visible spectrum in nm
    def nm_to_rgb(self, brightness, nm):

        # The algorithm was adapted from Earl F. Glynn's algorithm found on his web page:
        # http://www.efg2.com/Lab/ScienceAndEngineering/Spectra.htm
        gamma = 0.8
        red = 0.0
        green = 0.0
        blue = 0.0
        factor = 0.0

        # Scale values from the light spectrum as values of RGB
        if 380 <= nm < 440:
            red = -(nm - 440) / (490 - 380)
            blue = 1.0
        elif 440 <= nm < 490:
            green = (nm - 440) / (490 - 440)
            blue = 1.0
        elif 490 <= nm < 510:
            green = 1.0
            blue = -(nm - 510) / (510 - 490)
        elif 510 <= nm < 580:
            red = (nm - 510) / (580 - 510)
            green = 1.0
        elif 580 <= nm < 645:
            red = 1.0
            green = -(nm - 645) / (645 - 580)
        elif 645 <= nm < 781:
            red = 1.0

        # Adapt the intensity near the extremes of the spectrum
        if 380 <= nm < 420:
            factor = 0.3 + 0.7 * (nm - 380) / (420 - 380)
        elif 420 <= nm < 701:
            factor = 1.0
        elif 701 <= nm < 781:
            factor = 0.3 + 0.7 * (780 - nm) / (780 - 700)

        # Adapt values (we don't want 0^x = 1 for x != 0)
        rgb = []

        # Red
        if red == 0.0:
            rgb.append(1)
        else:
            value = int(round(brightness * (red * factor)**gamma))
            rgb.append(value)

        # Green
        if green == 0.0:
            rgb.append(1)
        else:
            value = int(round(brightness * (green * factor)**gamma))
            rgb.append(value)

        # Blue
        if blue == 0.0:
            rgb.append(1)
        else:
            value = int(round(brightness * (blue * factor) ** gamma))
            rgb.append(value)

        rgb_dict = {'r': rgb[0], 'g': rgb[1], 'b': rgb[2]}
        return rgb_dict

    def get_file(self):
        return self.lux_file