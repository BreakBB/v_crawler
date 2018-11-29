from v_crawl.spiders.amazon_spider import AmazonSpider


class AmazonDeSpider(AmazonSpider):
    name = "v_crawler_de"
    base_url = "https://www.amazon.de/gp/video/detail/"
    table_name = "amazon_video_de"

    def load_default_seed_urls(self):
        return [
                self.base_url + 'B00IB1IFL6/',  # Criminal Minds
                self.base_url + 'B00JGV1MY2/',  # Harry Potter 1
                self.base_url + 'B00ET11KUU/',  # The Big Bang Theory
                self.base_url + 'B07HFK1TPS/',  # American Dad
                self.base_url + 'B00I9MWJRS/',  # Die Bourne Identität
                self.base_url + 'B078WZ4LHL/',  # After the Rain
                self.base_url + 'B019ZS6XU8/',  # Die Pinguine aus Madagascar
                self.base_url + 'B01BNU0D5M/',  # Unser Kosmos
                self.base_url + 'B00GNWJAD2/',  # Dr. House
                self.base_url + 'B078P41Q4Q/'   # McMafia
            ]
