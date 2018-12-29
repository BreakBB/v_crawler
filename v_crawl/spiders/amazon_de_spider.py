import re

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
        elif '[OV/Omu]' in title:
            title = title.replace('[OV/Omu]', '')
        elif '[OV]' in title:
            title = title.replace('[OV]', '')
        elif '[OmU]' in title:
            title = title.replace('[OmU]', '')
        elif '[Omu]' in title:
            title = title.replace('[Omu]', '')
        if '(Subbed)' in title:
            title = title.replace('(Subbed)', '')
        if '(inkl. Bonusmaterial)' in title:
            title = title.replace('(inkl. Bonusmaterial)', '')
        if '(4K UHD)' in title:
            title = title.replace('(4K UHD)', '')
        if '(Extended Edition)' in title:
            title = title.replace('(Extended Edition)', '')
        return title

    def extract_genres(self, meta_selector):
        genre_list = super().extract_genres(meta_selector)

        for genre in genre_list:
            if genre == "Adventure":
                genre_list.remove("Adventure")
                genre_list.append("Abenteuer")
            elif genre == "Biography":
                genre_list.remove("Biography")
                genre_list.append("Biografie")
            elif genre == "Crime":
                genre_list.remove("Crime")
                genre_list.append("Krimi")
            elif genre == "Documentary":
                genre_list.remove("Documentary")
                genre_list.append("Dokumentation")
            elif genre == "History":
                genre_list.remove("History")
                genre_list.append("Geschichte")
            elif genre == "Family":
                genre_list.remove("Family")
                genre_list.append("Kinder")
            elif genre == "Music":
                genre_list.remove("Music")
                genre_list.append("Musik")
            elif genre == "Romance":
                genre_list.remove("Romance")
                genre_list.append("Romantik")
            elif genre == "Sci-Fi":
                genre_list.remove("Sci-Fi")
                genre_list.append("Science Fiction")
            elif genre == "War":
                genre_list.remove("War")
                genre_list.append("Militär und Krieg")

        return genre_list

    def extract_maturity_rating(self, meta_selector):
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
