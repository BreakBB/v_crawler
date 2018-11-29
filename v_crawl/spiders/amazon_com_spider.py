from v_crawl.spiders.amazon_spider import AmazonSpider


class AmazonComSpider(AmazonSpider):
    name = "v_crawler_com"
    base_url = 'https://www.amazon.com/gp/video/detail/'
    table_name = "amazon_video_com"

    def load_default_seed_urls(self):
        return [
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
