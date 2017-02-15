##############################
#       Hue Party            #
#   Sync lights and music    #
#                            #
#   Created by A. Revaclier  #
#           Feb 2017         #
#                            #
##############################

from HueParty.Sound.sound import Sound
from HueParty.Hue.hue import Hue
from HueParty.File.md5calculator import md5Calculator
from HueParty.File.luxfile import LuxFile

#hue = Hue("Desktop-Linux")
#sound = Sound("Example.wav", 20)

md5 = md5Calculator()

sound_md5 = md5.get_md5("Example.wav")
print(sound_md5)

lux_file = LuxFile(sound_md5)

