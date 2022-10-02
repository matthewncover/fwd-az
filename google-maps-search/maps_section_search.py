import pandas as pd
from bs4 import BeautifulSoup

from business_metadata import MapsBusiness

class MapsSectionSearch:

    def __init__(self, driver, state_abr, url, df=None):

        self.state_abr = state_abr
        self.driver = driver
        self.url = url

        self.get_soup()
        self.get_business_names_urls()

        if df is not None:
            self.df = df
            self.check_data_for_duplicate()

        self.get_business_data()

    def __repr__(self):

        return f"<class MapsSectionSearch; n={len(self.businesses)}>"

    def __getitem__(self, i):

        return self.businesses[i]

    def get_soup(self):
        """get bs4 html soup

        Parameters:
            url (str): url to pull soup from

        """

        self.driver.get(self.url)
        self.soup = BeautifulSoup(
            self.driver.page_source,
            features = "html.parser"
            )

    def get_business_names_urls(self):

        business_tags = self.soup.find_all(
            "a", {"class": "hfpxzc"}
        )

        self.name_url_tuples = [
            (bs4_tag["aria-label"], bs4_tag["href"])
            for bs4_tag in business_tags
        ]

    def get_business_data(self):
        """
        """

        self.businesses = [
            MapsBusiness(self.driver, self.state_abr, business_name, business_url)
            for (business_name, business_url)
            in self.name_url_tuples
        ]

        # self.businesses = [
        #     business for business in self.businesses
        #     if business.is_valid_state_business_flag
        # ]

    def check_data_for_duplicate(self):

        self.name_url_tuples = [
            (name, url) for (name, url)
            in self.name_url_tuples
            if [name, url] not in self.df[["business_name", "href_url"]].values.tolist()
        ]



