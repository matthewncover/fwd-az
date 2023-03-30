import re
from itertools import product
from bs4 import BeautifulSoup
from bs4.element import NavigableString
import inspect
from numpy import arange, nan

import datetime as dt

import business_metadata_regex as bmr

# class MapsBusiness(MapsSectionSearch):
class MapsBusiness:
    """collect information on a single business

    Attributes:

        name (str): business name
        href_url (str): google maps url for the business
        website (str)
        address (str)
        phone_number (str)
        open_hours (dict): when the business is open by day
        num_reviews (int): number of google reviews, a heuristic for popularity
        traffic_data (dict): how busy the business is by day of week and hour of day
    """

    def __init__(self, driver, state_abr, business_name, href_url):

        # super().__init__()

        self.days_of_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        self.day_hours = [''.join(x) for x in product([str(x) for x in arange(1, 13)], [" AM", " PM"])]

        self.state_abr = state_abr
        self.driver = driver
        self.business_name = business_name
        self.href_url = href_url

        self.get_business_soup()
        self.get_business_metadata()


    def __repr__(self):

        return f"class 'MapsBusiness'; name '{self.business_name}'>"


    def get_business_metadata(self):

        self.get_business_contact_info()
        self.get_business_num_reviews()
        self.get_business_open_hours()
        self.get_business_traffic_data()

        self.agg_single_data_attrs()
        self.collapse_multi_data_attrs()

    def agg_single_data_attrs(self):
        """make data attributes dict-accessible

        single_data_attrs is one-to-one string to string/int/float/bool mapping
        """

        self.data_attrs = dict([
            attr for attr in inspect.getmembers(self)
            if (
                (not attr[0].startswith("_")) # remove special, built-in methods
                and (not str(attr[1]).startswith("<")) # remove bound methods
            )
        ])

        self.single_data_attrs = {
            k: v
            for k, v in self.data_attrs.items()
            if type(v) in [str, int, float, bool]
        }

    def collapse_multi_data_attrs(self):
        """expand dict/list/tuple values to be one-to-one
        string to string/int/float/bool
        """

        self.collapse_open_hours()
        self.collapse_traffic_data()

    def collapse_open_hours(self):

        if self.open_hours == ["No open hours data"]:
            open_hours_flattened = {
                f"{day}_{opens_closes}": nan
                for day, opens_closes in product(self.days_of_week, ["opens", "closes"])
            }

        else:
            open_hours_flattened = {
                f"{day}_{opens_closes}": hrs_dict[opens_closes]
                for day, hrs_dict in self.open_hours.items()
                for opens_closes in hrs_dict.keys()
            }

        self.single_data_attrs.update(open_hours_flattened)

    def collapse_traffic_data(self):

        if self.traffic_data == ["No traffic data"]:
            hour_traffic_flattened = {
                f"{day}_{hour}_traffic": nan
                for day, hour in product(self.days_of_week, self.day_hours)
            }

        else:
            hour_traffic_flattened = {
                f"{day}_{hour}_traffic": 0
                if hour not in hour_traffic_dict.keys()
                else hour_traffic_dict[hour]
                for day, hour_traffic_dict in self.traffic_data.items()
                for hour in self.day_hours
            }

        self.single_data_attrs.update(hour_traffic_flattened)

# {
#     f"{day}_{hour}_traffic": 0
#     if hour not in hour_traffic_dict.keys()
#     else hour_traffic_dict[hour]
#     for day, hour_traffic_dict in traffic_data.items()
#     for hour in day_hours
# }


    def get_business_soup(self):

        self.driver.get(self.href_url)
        self.business_soup = BeautifulSoup(
            self.driver.page_source,
            features="html.parser"
            )

    def get_business_contact_info(self):

        self.website = nan
        self.address = nan
        self.state = nan
        self.phone_number = nan

        contact_info_texts = [
            bs4_tag.get_text().strip() for bs4_tag
            in self.business_soup.find_all(
                "div", 
                {"class": "Io6YTe"}
                )
        ]

        for text in contact_info_texts:
            self.classify_soup_text(text, state=self.state_abr)

    def classify_soup_text(self, text, state):
        """text is website, valid address (in state), phone number,
        or none
        """

        if bmr.is_website(text):
            self.website = text

        elif bmr.is_address(text):
            self.address = text
            self.state = bmr.get_state_from_address(text)

        elif bmr.is_phone_number(text):
            self.phone_number = text
        
        else:
            None

    def get_business_num_reviews(self):
        """num google reviews
        """
        try:
            reviews_string = (
                self.business_soup.find_all(
                    "button", {"class": "DkEaL"}
                )[0]
                .get_text()
                .strip()
                .split(' ')[0]
                .replace(',', '')
            )
        except IndexError:
            self.num_reviews = nan
            return

        try:
            self.num_reviews = int(reviews_string)

        except ValueError:
            self.num_reviews = nan

    def get_business_open_hours(self):
        """ex)
        {
            "Friday": {
                "opens_at": "5AM",
                "closes_at": "6PM"
            }
            ...
        }
        """

        open_hours_bs4_tags = self.business_soup.find_all(
            "div", {"class": "t39EBf"}
        )

        # open_hours_text = (
        #     self.business_soup.find_all(
        #         "div",
        #         {"class": "t39EBf"}
        #     )[0]
        #     ["aria-label"]
        # )
        def get_open_hrs_text(text, ind):
            
            try:
                if text[1] == "Closed":
                    return "Closed"

                elif text[1].startswith("Open 24"):
                    return "Open 24 Hours"

                else:
                    return text[1].split(" to ")[ind]
            except IndexError:
                return nan

        if open_hours_bs4_tags:

            open_hours_text = open_hours_bs4_tags[0]["aria-label"]

            open_hours_text_per_day = [
                text.strip().split(', ')
                for text in open_hours_text.split('.')[0].split(';')
            ]

            self.open_hours = {
                bmr.find_day_of_week(text[0], self.days_of_week): {
                    "opens": get_open_hrs_text(text, 0),
                    "closes": get_open_hrs_text(text, 1)
                }
                for text in open_hours_text_per_day
            }

        else:
            self.open_hours = ["No open hours data"]

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

        traffic_bs4_tags = self.business_soup.find_all(
            "div", {"class": "g2BVhd"}
            )

        if not traffic_bs4_tags:
            self.traffic_data = ["No traffic data"]

        else:
            day_of_week_bs4tag_dict = {
                day_of_week: bs4_tags
                for day_of_week, bs4_tags
                in zip(
                    self.days_of_week,
                    traffic_bs4_tags
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

        def get_hour(text):

            if text.startswith("Currently"):
                return dt.datetime.today().strftime("%H%p")
            else:
                return text[re.search("at ", text).end():-1]

        def get_traffic_percentage(text):

            try:
                return int(re.search(r"\d{1,3}%", text).group()[:-1])
            except AttributeError:
                return 0

        traffic_data_dict = {
            get_hour(text): get_traffic_percentage(text)
            for text in traffic_texts
        }

        return traffic_data_dict
        