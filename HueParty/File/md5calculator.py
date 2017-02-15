##############################
#     MD5 processing         #
#                            #
#                            #
#   Created by A. Revaclier  #
#           Feb 2017         #
#                            #
##############################
from hashlib import md5


# Placeholder class to provide an efficient method to get md5 checksum.
class md5Calculator:
    # Get a md5 hash of a file
    def get_md5(self, file):
        hash = md5()
        try:
            with open(file, 'rb') as f:
                for chunk in iter(lambda: f.read(128 * hash.block_size), b""):
                    hash.update(chunk)
                return hash.hexdigest()
        except IOError:
            print("Could not read file")
