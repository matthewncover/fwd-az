from bs4 import BeautifulSoup

from business_metadata import MapsBusiness

class MapsSectionSearch:

    def __init__(self, driver, state_abr, url):

        self.state_abr = state_abr
        self.driver = driver
        self.url = url

        self.get_soup()
        self.get_businesses()

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
            MapsBusiness(self.driver, self.state_abr, business_name, business_url)
            for (business_name, business_url)
            in business_name_url_tuples
        ]

        self.businesses = [
            business for business in self.businesses
            if business.is_valid_state_business_flag
        ]



