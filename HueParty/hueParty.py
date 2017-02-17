##############################
#       Hue Party            #
#   Sync lights and music    #
#                            #
#   Created by A. Revaclier  #
#           Feb 2017         #
#                            #
##############################

import os
from HueParty.File.luxfile import LuxFile
from HueParty.File.md5calculator import md5Calculator
from HueParty.Hue.hue import Hue


def check_config_dirs():
    if not os.path.exists("config"):
        os.makedirs("config")
    if not os.path.exists("lux"):
        os.makedirs("lux")

check_config_dirs()

sound_file = "Music/09 - When Love and Hate Collide.flac"

sampling_rate = 2

hue = Hue("Desktop-Linux")

md5 = md5Calculator()
sound_md5 = md5.get_md5(sound_file)

lux_file = LuxFile(sound_md5, sound_file, sampling_rate)

hue.play_file(lux_file.get_file(), sampling_rate, sound_file)
