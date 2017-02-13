##############################
#       Hue discovery        #
#       and processing       #
#                            #
#   Created by A. Revaclier  #
#           Feb 2017         #
#                            #
##############################

import time, json, urllib.request, xmltodict, requests
from netdisco.discovery import NetworkDiscovery


class Hue:
    def __init__(self, device):
        self.APP_NAME = "HueParty"
        self.device = device
        self.DEVICETYPE = self.APP_NAME + "#" + self.device

        # Try to open the config file
        try:
            config = open('config.json', 'r')
            config.close()

        # If it is not present, create it
        except FileNotFoundError:
            config = open('config.json', 'w+')
            config.close()

        # Connect to the bridge
        config_data = self.connect()

        self.api_key = config_data["api_key"]
        self.ip = config_data["ip"]

    # Checks if devices found on the network are philips hue bridges.
    def check(self, bridge):
        # Request the description file from the bridge
        url = bridge + "description.xml"
        response = urllib.request.urlopen(url)

        # Parse it in JSON
        xml_response = xmltodict.parse(response.read())

        # If the manufacturer is Phillips, then assume it is a hue bridge
        if xml_response["root"]["device"]["manufacturer"] == "Royal Philips Electronics":
            return True
        return False

    # Use various methods to find a philips hue bridge on the network.
    # See https://developers.meethue.com/documentation/hue-bridge-discovery
    # for more information about the way this works
    def discover(self):

        # UPNP discovery

        found_bridges = []
        upnp = NetworkDiscovery()
        upnp.scan()

        for dev in upnp.discover():
            if dev == "philips_hue":
                found_bridges.append(upnp.get_info(dev))

        upnp.stop()

        # If one or more bridges have been found via UPNP
        if len(found_bridges) > 0:

            # If only one bridge was found
            if len(found_bridges) == 1:
                # Save the IP
                bridge = found_bridges[0][0][1]

            # If more than one bridge was found
            else:

                # Ask user to choose the right bridge
                print("More than one bridge has been found:")
                for index in range(len(found_bridges)):
                    print(str(index + 1) + ". IP: " + found_bridges[index][0][1])
                bridge_no = input("Choose a bridge (1-" + str(len(found_bridges)) + ")")

                # Checking for correct value
                while True:
                    if bridge_no.isdigit() and 1 <= int(bridge_no) <= len(found_bridges):
                        bridge = found_bridges[int(bridge_no) - 1][0][1]
                        break
                    else:
                        bridge_no = input("Enter a correct value (1-" + str(len(found_bridges)) + ")")

        # No bridge discovered via UPNP
        else:

            # NUPNP discovery, asks philips website and expects JSON response
            philips_url = "https://www.meethue.com/api/nupnp"
            response = urllib.request.urlopen(philips_url)
            url_data = json.loads(response.read().decode("utf8"))

            # If a device or more was found
            if len(url_data) > 0:
                # If exactly one device was found, save its IP
                if len(url_data) == 1:
                    bridge = "http://" + url_data[0]["internalipaddress"] + "/"

                # If two or more were found, ask user to choose
                else:
                    for index in range(len(url_data)):
                        print((index + 1) + ". ID: " + url_data[index]["id"] + " , IP address: " + url_data[
                            "internalipaddress"])
                        bridge_no = input("Choose a bridge (1-" + len(url_data))

                    # Check for correct value
                    while True:
                        if bridge_no.isdigit() and 1 <= int(bridge_no) <= len(url_data):
                            bridge = "http://" + url_data[int(bridge_no) - 1]["internalipaddress"] + "/"
                            break
                        else:
                            bridge_no = input("Enter a correct value (1-" + len(url_data) + ")")

            # No bridges discovered via UPNP or NUPNP
            # Ask user to enter IP manually
            else:
                ip = input("Enter the IP address of the bridge: (e.g. 192.168.0.2)")
                bridge = ip

        return bridge

    # Create an API key for the app
    def requestAPIKey(self, bridge):
        # API url
        api_url = bridge + "api"
        # JSON data
        data = '{"devicetype":"' + self.DEVICETYPE + '"}'
        # Defines how long the function is going to run (in seconds)
        max_time = 30
        start_time = time.clock()

        api_key = ""

        # Info message for user
        print("Please press the link button on the bridge")

        # This asks a JSON response from the API
        # Stops after 30 seconds or if a key was returned by the bridge.
        # Only indicated as 3 here because of REST requests lag.
        while (time.clock() - start_time) < 3 and not api_key:
            try:
                response = requests.post(api_url, data=data)
                test = response.json()
                api_key = test[0]["success"]["username"]

            # If we get a KeyError, it means the link button was not pressed on the bridge.
            except KeyError:
                pass
        return api_key

    # Connect to a hue bridge
    def connect(self):
        # Open config file
        save_file = open('config.json', 'r+')
        # If non empty, load data
        try:
            config_data = json.load(save_file)
            save_file.close()
            return config_data

        # If empty, perform discovery
        except ValueError:

            config_data = {}

            print("Searching for Hue Bridge...")

            ip = self.discover()

            # If the IP is empty, ask the user for action.
            while True:
                if not ip:
                    rep = input("Something went wrong, want to try again? (Y/N)")
                    if rep == "Y" or rep == "y":
                        ip = self.discover()
                    else:
                        quit()
                else:
                    break

            # If the discovered device is not a hue bridge, ask the user for action.
            while True:
                if not self.check(ip):
                    rep = input("The device you selected seems not to be a hue bridge. Try again? (Y/N)")
                    if rep == "Y" or rep == "y":
                        ip = self.discover()
                    else:
                        quit()
                else:
                    break

            print("Bridge found at " + ip)

            # Requests an API key
            api_key = self.requestAPIKey(ip)

            # As long as the key is not valid, ask the user for action.
            while True:
                if not api_key:
                    rep = input("Something went wrong, please press the link button on the bridge. Retry (Y/N)")
                    if rep == "Y" or rep == "y":
                        api_key = self.requestAPIKey(ip)
                    else:
                        quit()
                else:
                    break

            # Saves the IP address and the API key in a file.
            config_data["api_key"] = api_key
            config_data["ip"] = ip
            json.dump(config_data, save_file)
            save_file.close()

            print("Connection success!")
            return config_data
