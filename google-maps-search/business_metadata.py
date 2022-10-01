import requests
import re
from bs4 import BeautifulSoup
from bs4.element import NavigableString

import business_metadata_regex as bmr

# class MapsBusiness(MapsSectionSearch):
class MapsBusiness:
    """collect information on a single business

    Attributes:

        business_name (str)
        business_url (str)
        website (str)
        address (str)
        phone_number (str)
        open_hours (dict): when the business is open by day
        num_reviews (int): number of google reviews, a heuristic for popularity
        traffic_data (dict): how busy the business is by day of week and hour of day
    """

    def __init__(self, driver, business_name, business_url):

        # super().__init__()

        self.days_of_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

        self.driver = driver
        self.business_name = business_name
        self.business_url = business_url

        self.get_business_soup()
        self.get_business_metadata()


    def get_business_metadata(self):

        self.get_business_contact_info()
        self.get_business_num_reviews()
        self.get_business_open_hours()
        self.get_business_traffic_data()


    def get_business_soup(self):

        self.driver.get(self.business_url)
        self.business_soup = BeautifulSoup(self.driver.page_source)

    def get_business_contact_info(self):

        for bs4_tag in self.soup.find_all("div", {"class": "Io6YTe"}):
            self.classify_soup_text(bs4_tag, state=self.state_abr)

    def classify_soup_text(self, bs4_tag, state):
        """text is website, valid address (in state), phone number,
        or none
        """

        text = bs4_tag.get_text().strip()

        if bmr.is_website(text):
            # return ("website", text)
            self.website = text

        elif bmr.is_state_address(text, state=state):
            # return ("address", text)
            self.address = text

        elif bmr.is_phone_number(text):
            # return ("phone number", text)
            self.phone_number = text
        
        else:
            None

    def get_business_num_reviews(self):
        """num google reviews
        """

        self.num_reviews = int(
            self.soup.find_all(
                "button",
                {"class": "DkEaL"}
            )[0]
            .get_text()
            .strip()
            .split(' ')[0]
        )

    def get_business_open_hours(self):
        """ex)
        {
            "Friday": {
                "opens at": "5AM",
                "closes at": "6PM"
            }
            ...
        }
        """

        open_hours_text = (
            self.soup.find_all(
                "div",
                {"class": "t39EBf"}
            )[0]
            ["aria-label"]
        )

        open_hours_text_per_day = [
            text.strip().split(', ')
            for text in open_hours_text.split('.')[0].split(';')
        ]

        self.open_hours = {
            text[0]: {
                "opens at": text[1].split(" to ")[0],
                "closes at": text[1].split(" to ")[1]
            }
            for text in open_hours_text_per_day
        }

    def get_business_traffic_data(self):
        """snag traffic data

        ex. {
            "Monday: {
                "10 AM": 12,
                ...
            },
            ...
        }
        meaning --> this business is 12% busy Mondays at 10 AM
        """

        day_of_week_bs4tag_dict = {
            day_of_week: bs4_tags
            for day_of_week, bs4_tags
            in zip(
                self.days_of_week,
                self.soup.find_all(
                    "div",
                    {"class": "g2BVhd"}
                )
            )
        }

        self.traffic_data = {
            day_of_week: self.get_business_traffic_data_one_day(
                day_of_week_bs4tag_dict[day_of_week]
            )
            for day_of_week in self.days_of_week
        }

    def get_business_traffic_data_one_day(self, bs4_tags):
        """remove bs4_tags that do not have traffic data,
        extract text and put in dictionary

        Parameters:
            bs4_tags (list): list of soup tags associated with traffic data
                of a specific day
        
        Returns:
            traffic_data_dict (dict): ex) {
                "10 AM": 12,
                ...
            }
        """

        # remove empty tags
        bs4_tags = [
            bs4_tag for bs4_tag in bs4_tags
            if type(bs4_tag) != NavigableString
            ]

        # extract text. ex) "0% busy at 4 AM."
        traffic_texts = [
            bs4_tag["aria-label"] 
            for bs4_tag in bs4_tags
            if ("aria-label" in bs4_tag.attrs.keys())
        ]

        traffic_data_dict = {
            text[re.search("at ", text).end():-1]: int(text[:text.index("%")])
            for text in traffic_texts
        }

        return traffic_data_dict
        