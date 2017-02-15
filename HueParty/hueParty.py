##############################
#       Hue Party            #
#   Sync lights and music    #
#                            #
#   Created by A. Revaclier  #
#           Feb 2017         #
#                            #
##############################

import os
from HueParty.Hue.hue import Hue
from HueParty.File.md5calculator import md5Calculator
from HueParty.File.luxfile import LuxFile


def check_config_dirs():
    if not os.path.exists("config"):
        os.makedirs("config")
    if not os.path.exists("lux"):
        os.makedirs("lux")

check_config_dirs()

sound_file = "Example.wav"

Hue = Hue("Desktop-Linux")

md5 = md5Calculator()
sound_md5 = md5.get_md5(sound_file)

lux_file = LuxFile(sound_md5, sound_file)
