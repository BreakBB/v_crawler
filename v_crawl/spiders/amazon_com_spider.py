import re
import scrapy
import time
from scrapy.exceptions import CloseSpider


class AmazonComSpider(scrapy.Spider):
    name = "v_crawler_com"
    spider_timeout = 60
    spider_start_time = 0

    movies_crawled = set()
    base_url = 'https://www.amazon.com/gp/video/detail/'

    def start_requests(self):
        self.spider_start_time = time.time()

        # Starting URLs for the spider
        seed_urls = [
            self.base_url + 'B0748PJSBJ/',  # Valerian
            self.base_url + 'B000Q76K1A/',  # The Bourne Identity
            self.base_url + 'B078X1RBH5/',  # After the Rain
            self.base_url + 'B07GFS578F/',  # Destination Wedding
            self.base_url + 'B07FDKRJQC/',  # The Man In the High Castle
            self.base_url + 'B006F437YG/',  # Criminal Minds
            self.base_url + 'B00YBX664Q/',  # Mr. Robot
            self.base_url + 'B0786YMWXR/',  # Wonder
            self.base_url + 'B076TKGFYB/',  # Jigsaw
            self.base_url + 'B000HJ4WLC/',  # SpongeBob SquarePants
            self.base_url + 'B07HLZLJN5/',  # Kung Fu Panda: The Paws of Destiny
            self.base_url + 'B07JD5Q9WQ/',  # Whitney
        ]

        # Make a Request for each URL in seed_urls
        for url in seed_urls:
            yield scrapy.Request(url=url, callback=self.parse)
        return

    def parse(self, response):

        # file = open("data/body.html", "wb")
        # file.write(response.body)
        # file.close()

        movie_id = response.url[-11:-1]
        url = self.base_url + movie_id + '/'

        meta_selector = response.css('section[class="av-detail-section"]')

        title = self.extract_title(meta_selector)
        rating = self.extract_rating(meta_selector)
        imdb = self.extract_imdb(meta_selector)
        genres = self.extract_genres(meta_selector)
        year = self.extract_year(meta_selector)
        fsk = self.extract_fsk(meta_selector)

        # Return the information (in a generator manner) to add them to the output
        yield {
            'id': movie_id,
            'url': url,
            'title': title,
            'rating': rating,
            'imdb': imdb,
            'genres': genres,
            'year': year,
            'fsk': fsk
        }

        # Get the recommendation list of the current site
        recom_selector = response.css('div[class*="a-section"]')

        # For each movie/series in the recommendation list get url and movie_ids of the next movies/series
        for recommendation in recom_selector.css('a[href*="/gp/video/detail/"]'):
            url = recommendation.css('a[href*="/gp/video/detail/"]::attr(href)').extract_first()
            url = str(url)[22:50]
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

        return genre_list

    def extract_fsk(self, meta_selector):
        fsk_string = meta_selector.css('span[data-automation-id="maturity-rating-badge"]::attr(title)').extract_first()
        fsk = ""

        # Get the actual value out of the string
        if fsk_string:
            fsk_match = re.search(r'\d\d?', fsk_string)
            if fsk_match:
                fsk = fsk_match.group(0)

        return fsk

    def extract_rating(self, meta_selector):
        rating = meta_selector.css('span[class*="av-stars"]').re_first(r'\d-?\d?')
        if (rating is not None) and ('-' in rating):
            rating.replace('-', ',')
        return rating

    def extract_year(self, meta_selector):
        year = meta_selector.css('span[data-automation-id="release-year-badge"]::text').extract_first()
        return year

    def extract_imdb(self, meta_selector):
        imdb = meta_selector.css('span[data-automation-id="imdb-rating-badge"]::text').extract_first()
        if imdb is None:
            imdb = ""
            # TODO: Call of imdb module
        return imdb

    def extract_title(self, meta_selector):
        title = meta_selector.css('h1[data-automation-id="title"]::text').extract_first()
        return title

    def should_timeout(self):
        if time.time() - self.spider_start_time > self.spider_timeout:
            return True
        return False
