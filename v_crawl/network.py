import json
import shutil

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
                while not controller.is_newnym_available():
                    sleep(0.5)
                controller.signal(Signal.NEWNYM)
            except stem.ControllerError:
                print("Sending the controller request for a new IP failed")
        sleep(0.5)
        return

    def get_imdb_data(self, title):
        response = self.session.post("http://localhost:8555/api/imdb", json={"title": title})
        result = json.loads(response.text)

        if response.status_code == 200:
            return result

        print("Could not get imdb data: %s" % result['message'])
        return None

    def get_movie_poster(self, movie_id, poster_url, image_dir):
        file_path = "NULL"

        # No poster for this movie
        if poster_url == "N/A":
            return file_path

        response = self.session.get(poster_url, stream=True)

        if response.status_code == 200:
            file_path = image_dir + movie_id + '.jpg'
            with open(file_path, 'wb') as file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, file)
        return file_path
