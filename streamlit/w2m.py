import pandas as pd, re, datetime as dt
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager


class When2MeetReader:

    SEARCH_DAY_TAG = {"style": "display:inline-block;*display:inline;zoom:1;font-size:16px;"}
    SEARCH_CELL_TAGS = {"id": lambda x: x and x.startswith("GroupTime")}

    DAY_ORDER = {'Saturday': 1, 'Sunday': 2, 'Monday': 3, 'Tuesday': 4, 'Wednesday': 5, 'Thursday': 6, 'Friday': 7}

    URL_REGEX = r"https:\/\/www\.when2meet\.com\/\?\d+-\w+"

    def __init__(self, url):
        
        self.url = url
        self.__validate_url()

    def __validate_url(self):

        if re.match(self.URL_REGEX, self.url):
            self.is_valid_url = True
        else:
            self.is_valid_url = False

    def get_dataframe(self):

        self.__init_webdriver()
        self.__init_dataframe()

        self.df["cell_datetime"] = self.df.id.map(self._get_cell_datetime)
        self.df["those_available"], self.df["those_unavailable"] = (
            zip(*self.df
                .id.map(self._whos_available)
            )
        )
        self.df["n_available"] = self.df.those_available.map(len)
        self.df["n_unavailable"] = self.df.those_unavailable.map(len)

        self.df["dt_time_of_day"], self.df["day_of_week"] = (
            zip(*self.df
                .cell_datetime.map(self._split_cell_datetime)
            )
        )

        self.__sort_dataframe()
    
    def __init_webdriver(self):

        browser_options = webdriver.ChromeOptions()
        browser_options.add_argument("headless")

        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=browser_options
            )
        
        self.driver.get(self.url)

    def get_soup(self):
        self.soup = BeautifulSoup(self.driver.page_source, "html.parser")

    def __init_dataframe(self):

        self.get_soup()
        cell_tags = self.soup.find_all("div", self.SEARCH_CELL_TAGS)
        cell_ids = [x.get("id") for x in cell_tags]

        self.df = pd.DataFrame(pd.Series(cell_ids, name="id"))


    def _get_surveyed_days(self):

        self.get_soup()

        day_tags = self.soup.find_all("div", self.SEARCH_DAY_TAG)
        days_of_week = [tag.text for tag in day_tags]
        days_of_week = pd.Series(days_of_week).unique().tolist()

        return days_of_week
    
    def _get_cell_datetime(self, cell_id):

        self.get_soup()

        cell_tag = self.soup.find("div", {"id": cell_id})
        cell_tag_mouseover = cell_tag.get("onmouseover")

        cell_datetime = re.search(r'".*"', cell_tag_mouseover).group().strip('"')

        return cell_datetime
    
    def _move_mouse_to_id(self, cell_id):

        cell = self.driver.find_element("id", cell_id)
        
        actions = ActionChains(self.driver)
        actions.move_to_element(cell).perform()

    def _whos_available(self, cell_id):

        self._move_mouse_to_id(cell_id)
        self.get_soup()

        def get_availability(x):
            return [
                z for z in 
                self.soup.find_all("div", {"id": x})[0].contents 
                if isinstance(z, str) and z.strip()
                ]

        return get_availability("Available"), get_availability("Unavailable")
    
    def _split_cell_datetime(self, cell_datetime):

        split_date_data = cell_datetime.split(" ")

        if len(split_date_data) > 3:
            raise NotImplementedError

        else:
            cell_datetime_dt = dt.datetime.strptime(cell_datetime, "%A %I:%M:%S %p")
            day_of_week = split_date_data[0]

        return cell_datetime_dt, day_of_week
    
    def __sort_dataframe(self):

        self.df["day_order"] = self.df.day_of_week.map(self.DAY_ORDER)

        self.df = self.df.sort_values(
            by=["n_available", "day_order", "dt_time_of_day"],
            ascending=[False, True, True]
        ).reset_index(drop=True)