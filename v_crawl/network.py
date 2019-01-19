import json
import shutil

import requests
from time import sleep

import stem
from scrapy.exceptions import CloseSpider
from stem import Signal
from stem.control import Controller


class Network:
    session = None

    def __init__(self):
        self.session = requests.session()
        return

    def renew_identitiy(self):
        # Connect to the TOR-controller
        with Controller.from_port(port=9151) as controller:
            controller.authenticate()
            try:
                # Wait till the controller is ready for a NEWNYM signal
                while not controller.is_newnym_available():
                    sleep(0.5)
                controller.signal(Signal.NEWNYM)
            except stem.ControllerError:
                print("Sending the controller request for a new IP failed")
        sleep(0.5)
        return

    def get_imdb_data(self, title):
        try:
            response = self.session.post("http://localhost:8555/api/imdb", json={"title": title})
        except requests.exceptions.ConnectionError:
            error_message = "Error while connecting to the imdb server. Make sure it is running."
            print(error_message)
            raise CloseSpider(error_message)

        result = json.loads(response.text)

        if response.status_code == 200:
            return result

        print("Could not get imdb data: %s" % result['message'])
        return None

    def get_movie_poster(self, movie_id, poster_url, image_dir):
        file_path = "NULL"

        # No poster from IMDb for this movie
        if poster_url == "N/A":
            return file_path

        # Get the image from the given URL
        response = self.session.get(poster_url, stream=True)

        if response.status_code == 200:
            file_path = image_dir + movie_id + '.jpg'

            # Decode the image and save it in the given directory
            with open(file_path, 'wb') as file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, file)
        return file_path
