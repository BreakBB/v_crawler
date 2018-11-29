import logging
import random
from time import sleep

import stem
from stem import Signal
from stem.control import Controller
from scrapy.utils.project import get_project_settings


def renew_ip():
    print("Getting new Tor IP")
    with Controller.from_port(port=9151) as controller:
        controller.authenticate()
        try:
            controller.signal(Signal.NEWNYM)
        except stem.ControllerError:
            print("Sending the controller request for a new IP failed")
    sleep(0.5)
    return


tries = 30


class ProxyMiddleware(object):

    def __init__(self):
        super().__init__()
        logging.getLogger("stem").setLevel(logging.WARNING)
        return

    def process_request(self, request, spider):
        global tries
        if tries == 0:
            renew_ip()
            tries = 30
        tries -= 1
        request.meta['proxy'] = 'http://127.0.0.1:8118'
        return


class UserAgentMiddleware(object):
    user_agent_list = []

    def __init__(self):
        super().__init__()

        settings = get_project_settings()
        user_agent_file = settings.get('USER_AGENT_LIST')

        # The USER_AGENT_LIST property is not set
        if not user_agent_file:
            default_agent = settings.get('USER_AGENT')

            if not default_agent:
                self.user_agent_list = ["Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0"]
            else:
                self.user_agent_list = [default_agent]
        else:
            # Get the file and read all lines in it
            with open(user_agent_file, "r") as file:
                self.user_agent_list = [line.strip() for line in file.readlines()]

        return

    def process_request(self, request, spider):
        user_agent = random.choice(self.user_agent_list)
        if user_agent:
            request.headers.setdefault('User-Agent', user_agent)
        return
