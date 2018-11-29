import json
import requests
from time import sleep

import stem
from stem import Signal
from stem.control import Controller


class Network:
    session = None

    def __init__(self):
        self.session = requests.session()
        return

    def renew_ip(self):
        print("Getting new Tor IP")
        with Controller.from_port(port=9151) as controller:
            controller.authenticate()
            try:
                controller.signal(Signal.NEWNYM)
            except stem.ControllerError:
                print("Sending the controller request for a new IP failed")
        sleep(0.5)
        return

    def get_imdb_rating(self, title):

        if '[dt./OV]' in title:
            title = title.replace('[dt./OV]', '')
        elif '[OV/OmU]' in title:
            title = title.replace('[OV/OmU]', '')
        elif '[OV]' in title:
            title = title.replace('[OV]', '')
        elif '[OmU]' in title:
            title = title.replace('[OmU]', '')
        if '(Subbed)' in title:
            title = title.replace('(Subbed)', '')

        # TODO: Check for umlaut since those movies aren't covered in the IMDB module atm

        response = self.session.post("http://localhost:8555/api/imdb", json={"title": title})

        result = json.loads(response.text)

        if response.status_code == 200:
            return result

        print("Could not get imdb rating: %s" % result['message'])
        return 0
