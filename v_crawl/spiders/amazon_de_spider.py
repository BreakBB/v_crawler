from v_crawl.spiders.amazon_spider import AmazonSpider


class AmazonDeSpider(AmazonSpider):
    name = "v_crawler_de"
    base_url = "https://www.amazon.de/gp/video/detail/"
    table_name = "amazon_video_de"

    series = "Serie"
    movie = "Film"

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

    def filter_title(self, title):
        # TODO: Check for umlaut since those movies aren't covered in the IMDb module atm

        if '[dt./OV]' in title:
            title = title.replace('[dt./OV]', '')
        elif '[OV/OmU]' in title:
            title = title.replace('[OV/OmU]', '')
        elif '[OV]' in title:
            title = title.replace('[OV]', '')
        elif '[OmU]' in title:
            title = title.replace('[OmU]', '')
        if '(Subbed)' in title:
            title = title.replace('(Subbed)', '')
        if '(inkl. Bonusmaterial)' in title:
            title = title.replace('(inkl. Bonusmaterial)', '')
        return title

    def extract_movie_type(self, detail_selector, series_selector):
        if self.imdb_data is not None:
            if self.imdb_data['type'] == "movie":
                return self.movie
            elif self.imdb_data['type'] == "series":
                return self.series

        if series_selector is not None:
            return self.series

        movie_runtime = detail_selector.css('span[data-automation-id="runtime-badge"]::text').extract_first()
        if movie_runtime is not None:
            return self.movie

        badge_section = detail_selector.css('div[class="av-badges"]')
        if badge_section is not None:
            badges = badge_section.css('span[class="av-badge-text"]::text').extract()
            for badge in badges:
                if "Min." in badge:
                    return self.movie

        # This should never happen
        return ""
