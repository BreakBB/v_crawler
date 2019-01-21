from v_crawl.spiders.amazon_spider import AmazonSpider


class AmazonComSpider(AmazonSpider):

    name = "v_crawler_com"
    base_url = 'https://www.amazon.com/gp/video/detail/'
    table_name = "amazon_video_com"
    image_dir = "./data/images_com/"

    def load_default_seed_urls(self):
        return [
            self.base_url + 'B0748PJSBJ/',  # Valerian
            self.base_url + 'B005H9B2CE/',  # Thor
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

    def filter_title(self, title):

        if ' (Dubbed)' in title:
            title = title.replace(' (Dubbed)', '')
        elif ' (English Subtitled)' in title:
            title = title.replace(' (English Subtitled)', '')
        elif ' [Español]' in title:
            title = title.replace(' [Español]', '')
        elif ' (EXTENDED)' in title:
            title = title.replace(' (EXTENDED)', '')
        elif ' (Extended Cut)' in title:
            title = title.replace(' (Extended Cut)', '')
        elif ' (In Color)' in title:
            title = title.replace(' (In Color)', '')
        elif ' (Original Japanese Version)' in title:
            title = title.replace(' (Original Japanese Version)', '')
        elif ' (Plus Bonus Content)' in title:
            title = title.replace(' (Plus Bonus Content)', '')
        elif '(Plus Bonus Content)' in title:
            title = title.replace('(Plus Bonus Content)', '')
        elif ' (Plus Bonus Features)' in title:
            title = title.replace(' (Plus Bonus Features)', '')
        elif '(Plus Bonus Features)' in title:
            title = title.replace('(Plus Bonus Features)', '')
        elif ' (Subbed)' in title:
            title = title.replace(' (Subbed)', '')
        elif ' (Theatrical)' in title:
            title = title.replace(' (Theatrical)', '')
        elif ' (Theatrical Version)' in title:
            title = title.replace(' (Theatrical Version)', '')
        elif ' (Uncut edition)' in title:
            title = title.replace(' (Uncut edition)', '')
        elif ' (unrated)' in title:
            title = title.replace(' (unrated)', '')
        elif ' (Unrated)' in title:
            title = title.replace(' (Unrated)', '')
        if ' - English Dub' in title:
            title = title.replace(' - English Dub', '')
        elif ' - Rated' in title:
            title = title.replace(' - Rated', '')
        if ' (4K UHD)' in title:
            title = title.replace(' (4K UHD)', '')
        return title

    def extract_maturity_rating(self, meta_selector):
        matu_string = meta_selector.css('span[data-automation-id="maturity-rating-badge"]::attr(title)').extract_first()

        if matu_string is None:
            matu_string = meta_selector.css('span[class*="RegulatoryRatingIcon"]::attr(title)').extract_first()

        return matu_string

    def extract_genres(self, meta_selector):
        genre_list = super().extract_genres(meta_selector)

        # We want the list to be NULL in the DB
        if genre_list is None or "N/A" in genre_list:
            return None

        return genre_list
