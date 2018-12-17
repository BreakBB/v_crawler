import json
import logging
import random
import re
import os
from pathlib import Path

import time

import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.utils.project import get_project_settings

from v_crawl.database import Database
from v_crawl.network import Network
from v_crawl.pipelines import JsonLinesExportPipeline


class AmazonSpider(scrapy.Spider):
    name = ""  # The name of the spider
    table_name = ""  # The name of the database table
    base_url = ""  # The base_url to crawl

    spider_timeout = 120
    spider_start_time = 0
    seed_urls = []
    movies_crawled = set()
    db_conn = None
    network = None
    user_agent = ""
    imdb_data = None
    image_dir = ""

    def set_user_agent(self, agent):
        self.user_agent = agent

    def __init__(self):
        if self.name == "":
            raise Exception("'name' must not be empty")
        if self.table_name == "":
            raise Exception("'table_name' must not be empty")
        if self.base_url == "":
            raise Exception("'base_url' must not be empty")

        # Create a connection to the database
        self.db_conn = Database(self.table_name)

        settings = get_project_settings()
        self.image_dir = settings.get('IMAGE_DIR')
        if not self.image_dir:
            self.image_dir = './images'

        if not os.path.exists(self.image_dir):
            print("Image directory not found. Creating directory: '" + self.image_dir + "'")
            os.makedirs(self.image_dir)

        # Create a network
        self.network = Network()

        # Make sure to get the random seeds before anything else happens
        self.seed_urls = self.get_random_seeds()

        # Increase logging level of some annoying loggers
        logging.getLogger("botocore").setLevel(logging.WARNING)
        logging.getLogger("urllib3.util.retry").setLevel(logging.WARNING)
        logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
        logging.getLogger("scrapy.core.engine").setLevel(logging.WARNING)

        super().__init__()
        return

    def start_requests(self):
        self.spider_start_time = time.time()

        # If this is the first run (so no seed_urls could be read from
        if len(self.seed_urls) == 0:
            # Starting URLs for the spider
            self.seed_urls = self.load_default_seed_urls()

        # Make a Request for each URL in seed_urls
        for url in self.seed_urls:
            request = scrapy.Request(
                url=url,
                callback=self.parse
            )
            yield request
        return

    def load_default_seed_urls(self):
        raise Exception("No default seed urls defined. Make sure to overload 'load_default_seed_urls' method.")

    def parse(self, response):
        movie_id = response.url[-11:-1]
        url = self.base_url + movie_id + '/'

        # Debug purpose
        # with open('./data/' + movie_id + '.html', "wb") as file:
        #     file.write(response.body)

        # We only want to parse the recommendations since we get a poster from there
        if url not in self.seed_urls:
            # Parse the current website
            detail_selector = response.css('section[class="av-detail-section"]')
            series_selector = response.css('div[id="dv-episode-list"]').extract_first()

            movie_item = self.parse_current_site(detail_selector, series_selector, url, movie_id)
            if movie_item is not None:
                yield movie_item
        else:
            self.seed_urls.remove(url)

        # Get the recommendation list of the current site
        recom_selector = response.css('div[class*="a-section"]')

        # For each movie/series in the recommendation list get url and movie_ids of the next movies/series
        for recommendation in recom_selector.css('a[href*="/gp/video/detail/"]'):
            request = self.parse_recommendations(recommendation)
            if request is not None:
                yield request

        return

    def parse_current_site(self, detail_selector, series_selector, url, movie_id):
        title = self.extract_title(detail_selector)

        if title is None:
            print("title is none. Couldn't extract title from HTML?")
            return None

        # Try to get IMDb data from the imdb-api-server
        self.imdb_data = self.network.get_imdb_data(title)

        # Extract all kind of relevant information
        rating = self.extract_rating(detail_selector)
        imdb = self.extract_imdb_rating(detail_selector)
        genres = self.extract_genres(detail_selector)
        year = self.extract_year(detail_selector)
        fsk = self.extract_fsk(detail_selector)
        movie_type = self.extract_movie_type(detail_selector, series_selector)

        poster_path = self.image_dir + movie_id + '.jpg'
        # The poster might be added earlier from the recommendations and we only want to add new posters
        if not os.path.exists(poster_path) and self.imdb_data is not None:
            poster_path = self.network.get_movie_poster(movie_id, self.imdb_data['poster'], self.image_dir)

        # Create an object for the information
        movie_item = {
            'movie_id': movie_id,
            'url': url,
            'title': title,
            'movie_type': movie_type,
            'rating': rating,
            'imdb': imdb,
            'genres': genres,
            'year': year,
            'fsk': fsk,
            'poster': poster_path
        }

        # Add the found movie/series to the database
        self.db_conn.insert_item(movie_item)

        # Cast Decimal back to float to be serializable for json
        movie_item['rating'] = float(movie_item['rating'])
        movie_item['imdb'] = float(movie_item['imdb'])
        movie_item['poster'] = poster_path

        # Keep the directory clean
        if os.path.exists(poster_path):
            os.remove(poster_path)

        # Return the information (in a generator manner) to add them to the output
        return movie_item

    def parse_recommendations(self, recommendation):
        if self.should_timeout():
            raise CloseSpider("Timeout of %s seconds reached" % self.spider_timeout)

        url = recommendation.css('a[href*="/gp/video/detail/"]::attr(href)').extract_first()

        # Some URLs are relative so the base_url needs to be added
        if str(url).startswith("/"):
            url = self.base_url[:-17] + url

        # Get the URL ending (.de / .com / ...)
        url_ending = str(url).split(".")[2][:3]
        if "/" in url_ending:
            url = str(url)[21:50]
        else:
            url = str(url)[22:50]
        movie_id = url[17:27]

        # If the movie_id is already in the list then don't add it again and look at the next entry
        if movie_id in self.movies_crawled:
            # self.log("Found duplicated movie_id %s" % movie_id)
            return None

        # Store the movie_id in a set
        self.movies_crawled.add(movie_id)

        # Get the recommendation poster
        self.extract_poster(recommendation, movie_id)

        # Build the next_page to visit using the found movie_id and yield the request
        next_page = self.base_url + movie_id + '/'
        return scrapy.Request(next_page, callback=self.parse)

    def extract_genres(self, meta_selector):
        genre_selector = meta_selector.css('div[data-automation-id="meta-info"]')

        genre_list = []
        for genre in genre_selector.css('a[href*="Cp_n_theme_browse-bin"]::text').extract():
            genre_list.append(genre)

        if len(genre_list) == 0:
            if self.imdb_data is not None:
                genre_list = self.imdb_data['genres'].split(',')
            else:
                genre_list.append("None")

        return genre_list

    def extract_fsk(self, meta_selector):
        fsk_string = meta_selector.css('span[data-automation-id="maturity-rating-badge"]::attr(title)').extract_first()

        if fsk_string is None:
            fsk_string = meta_selector.css('span[class*="RegulatoryRatingIcon"]::attr(title)').extract_first()

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
            rating = float(rating)
        else:
            rating = 0
        return rating

    def extract_year(self, meta_selector):
        year = meta_selector.css('span[data-automation-id="release-year-badge"]::text').extract_first()
        if year is not None:
            year = int(year)
        else:
            if self.imdb_data is not None:
                year = self.imdb_data['year']
            else:
                year = 0
        return year

    def extract_imdb_rating(self, meta_selector):
        imdb = meta_selector.css('span[data-automation-id="imdb-rating-badge"]::text').extract_first()
        if imdb is not None:
            if ',' in imdb:
                imdb = imdb.replace(',', '.')
            imdb = float(imdb)
        else:
            if self.imdb_data is not None:
                imdb = self.imdb_data['rating']
            else:
                imdb = 0

        return imdb

    def extract_title(self, meta_selector):
        title = meta_selector.css('h1[data-automation-id="title"]::text').extract_first()

        # Some movies/series have a different css attribute for the title
        if title is None:
            title = meta_selector.css('h1[class*="dv-node-dp-title"]::text').extract_first()

        if title is not None:
            title = self.filter_title(title)

        return title

    def extract_poster(self, meta_selector, movie_id):
        poster_url = meta_selector.css('img[class*="a-dynamic-image"]::attr(src)').extract_first()

        if poster_url is not None:
            self.network.get_movie_poster(movie_id, poster_url, self.image_dir)

    def extract_movie_type(self, detail_selector, series_selector):
        if self.imdb_data is not None:
            return self.imdb_data['type']

        if series_selector is not None:
            return "series"

        movie_runtime = detail_selector.css('span[data-automation-id="runtime-badge"]::text').extract_first()
        if movie_runtime is not None:
            return "movie"

        badge_section = detail_selector.css('div[class="av-badges"]')
        if badge_section is not None:
            badges = badge_section.css('span[class="av-badge-text"]::text').extract()
            for badge in badges:
                if "min" in badge:
                    return "movie"

        # This should never happen
        return ""

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

    def filter_title(self, title):
        return title
