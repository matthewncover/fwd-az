from bs4 import BeautifulSoup

from business_metadata import MapsBusiness

class MapsSectionSearch:

    def __init__(self, driver, url):

        self.driver = driver
        self.url = url

        self.get_soup()
        self.get_businesses()

    def get_soup(self):
        """get bs4 html soup

        Parameters:
            url (str): url to pull soup from

        """

        self.driver.get(self.url)
        self.soup = BeautifulSoup(self.driver.page_source)

    def get_businesses(self):
        """
        """

        business_name_url_tuples = [
            (x["aria-label"], x["href"])
            for x in self.soup.find_all(
                "a",
                {"class": "hfpxzc"}
            )
        ]

        self.businesses = [
            MapsBusiness(self.driver, business_name, business_url)
            for (business_name, business_url)
            in business_name_url_tuples
        ]



