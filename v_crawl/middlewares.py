import logging
import random
from multiprocessing import Value, Lock

from scrapy.utils.project import get_project_settings

from v_crawl.network import Network


class ProxyMiddleware(object):
    network = None
    lock = Lock()
    tries = None
    requests_per_identity = 0

    def __init__(self):
        super().__init__()
        logging.getLogger("stem").setLevel(logging.WARNING)

        settings = get_project_settings()
        request_amount = settings.get('REQUESTS_PER_IDENTITY')

        # The REQUESTS_PER_IDENTITY setting is not set
        if not request_amount:
            request_amount = 30

        self.tries = Value('i', request_amount)
        self.requests_per_identity = request_amount

        self.network = Network()
        return

    def process_request(self, request, spider):
        tries = self.tries
        self.lock.acquire()  # Only one thread should enter renew_ip()
        if tries.value == 0:
            print("Request per identity limit of " +
                  str(self.requests_per_identity) + " reached. Getting new Tor Identity")
            self.network.renew_identitiy()
            tries.value = self.requests_per_identity
        tries.value -= 1
        self.lock.release()
        request.meta['proxy'] = 'http://127.0.0.1:8118'
        return


class UserAgentMiddleware(object):
    user_agent_list = []

    def __init__(self):
        super().__init__()

        settings = get_project_settings()
        user_agent_file = settings.get('USER_AGENT_LIST')

        # The USER_AGENT_LIST setting is not set
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
        user_agent = self.get_random_user_agent()
        if user_agent:
            request.headers.setdefault('User-Agent', user_agent)
        return

    def get_random_user_agent(self):
        return random.choice(self.user_agent_list)
