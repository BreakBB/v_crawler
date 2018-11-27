import json
import logging
import random
import re
from pathlib import Path

import time
from decimal import Decimal  # Decimal is required for dynamoDB

import scrapy
from scrapy.exceptions import CloseSpider

from v_crawl.database import Database
from v_crawl.pipelines import JsonLinesExportPipeline


class AmazonDeSpider(scrapy.Spider):
    name = "v_crawler_de"
    spider_timeout = 60
    spider_start_time = 0
    seed_urls = []
    db_conn = None

    movies_crawled = set()
    base_url = 'https://www.amazon.de/gp/video/detail/'

    def __init__(self):
        # Make sure to get the random seeds before anything else happens
        self.seed_urls = self.get_random_seeds()

        # Increase logging level of some annoying loggers
        logging.getLogger("botocore").setLevel(logging.WARNING)
        logging.getLogger("urllib3.util.retry").setLevel(logging.WARNING)
        logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

        super().__init__()
        return

    def start_requests(self):
        self.spider_start_time = time.time()

        # Create a connection to the database
        self.db_conn = Database("amazon_video_de")

        # If this is the first run (so no seed_urls could be read from
        if len(self.seed_urls) == 0:
            # Starting URLs for the spider
            self.seed_urls = [
                self.base_url + 'B00IB1IFL6/',  # Criminal Minds
                self.base_url + 'B00JGV1MY2/',  # Harry Potter 1
                self.base_url + 'B00ET11KUU/',  # The Big Bang Theory
                self.base_url + 'B07HFK1TPS/',  # American Dad
                self.base_url + 'B00I9MWJRS/',  # Die Bourne Identität
                self.base_url + 'B078WZ4LHL/',  # After the Rain
                self.base_url + 'B019ZS6XU8/',  # Die Pinguine aus Madagascar
                self.base_url + 'B01BNU0D5M/',  # Unser Kosmos
            ]

        # Make a Request for each URL in seed_urls
        for url in self.seed_urls:
            yield scrapy.Request(url=url, callback=self.parse)
        return

    def parse(self, response):
        movie_id = response.url[-11:-1]
        url = self.base_url + movie_id + '/'

        meta_selector = response.css('section[class="av-detail-section"]')

        title = self.extract_title(meta_selector)
        rating = self.extract_rating(meta_selector)
        imdb = self.extract_imdb(meta_selector)
        genres = self.extract_genres(meta_selector)
        year = self.extract_year(meta_selector)
        fsk = self.extract_fsk(meta_selector)

        # Create an object for the information
        movie_item = {
            'movie_id': movie_id,
            'url': url,
            'title': title,
            'rating': rating,
            'imdb': imdb,
            'genres': genres,
            'year': year,
            'fsk': fsk
        }

        # Add the found movie/series to the database
        self.db_conn.put_item(movie_item)

        movie_item['rating'] = float(movie_item['rating'])
        movie_item['imdb'] = float(movie_item['imdb'])

        # Return the information (in a generator manner) to add them to the output
        yield movie_item

        # Get the recommendation list of the current site
        recom_selector = response.css('div[class*="a-section"]')

        # For each movie/series in the recommendation list get url and movie_ids of the next movies/series
        for recommendation in recom_selector.css('a[href*="/gp/video/detail/"]'):
            url = recommendation.css('a[href*="/gp/video/detail/"]::attr(href)').extract_first()
            url = str(url)[21:50]
            movie_id = url[17:27]

            # If the movie_id is already in the list then don't add it again and look at the next entry
            if movie_id in self.movies_crawled:
                # self.log("Found duplicated movie_id %s" % movie_id)
                continue

            # Store the movie_id in a set
            self.movies_crawled.add(movie_id)

            # Build the next_page to visit using the found movie_id and yield the request
            next_page = self.base_url + movie_id + '/'
            yield scrapy.Request(next_page, callback=self.parse)

            if self.should_timeout():
                raise CloseSpider("Timeout of %s seconds reached" % self.spider_timeout)

        return

    def extract_genres(self, meta_selector):
        genre_selector = meta_selector.css('div[data-automation-id="meta-info"]')

        genre_list = []
        for genre in genre_selector.css('a[href*="Cp_n_theme_browse-bin"]::text').extract():
            genre_list.append(genre)

        if len(genre_list) == 0:
            genre_list.append("None")

        return genre_list

    def extract_fsk(self, meta_selector):
        fsk_string = meta_selector.css('span[data-automation-id="maturity-rating-badge"]::attr(title)').extract_first()
        fsk = 0

        # Get the actual value out of the string
        if fsk_string:
            fsk_match = re.search(r'\d\d?', fsk_string)
            if fsk_match:
                fsk = int(fsk_match.group(0))

        return fsk

    def extract_rating(self, meta_selector):
        rating = meta_selector.css('span[class*="av-stars"]').re_first(r'\d-?\d?')
        if rating is not None:
            if '-' in rating:
                rating = rating.replace('-', '.')
            rating = Decimal(rating)
        else:
            rating = 0
        return rating

    def extract_year(self, meta_selector):
        year = meta_selector.css('span[data-automation-id="release-year-badge"]::text').extract_first()
        if year is not None:
            year = int(year)
        else:
            year = 0
        return year

    def extract_imdb(self, meta_selector):
        imdb = meta_selector.css('span[data-automation-id="imdb-rating-badge"]::text').extract_first()
        if imdb is not None:
            if ',' in imdb:
                imdb = imdb.replace(',', '.')
            imdb = Decimal(imdb)
        else:
            imdb = 0
            # TODO: Call of imdb module
        return imdb

    def extract_title(self, meta_selector):
        title = meta_selector.css('h1[data-automation-id="title"]::text').extract_first()
        return title

    def should_timeout(self):
        if time.time() - self.spider_start_time > self.spider_timeout:
            return True
        return False

    def get_random_seeds(self):
        item_file = Path(JsonLinesExportPipeline.data_path + self.name + ".jsonl")
        seed_urls = []

        if item_file.is_file():
            with open(item_file, 'r') as data:
                lines = data.read().splitlines()
            if len(lines) != 0:
                for i in range(0, 10):
                    json_line = random.choice(lines)
                    item = json.loads(json_line)
                    seed_urls.append(item['url'])

        return seed_urls
