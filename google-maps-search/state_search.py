# data manipulation imports
import numpy as np, pandas as pd
import re

# geojson imports
import json
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point

# web scraping imports
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from bs4.element import NavigableString

class State:

    ZOOM_FACTOR = 15
    LATLON_DELTA = 0.0307

    def __init__(self, state_name = "Arizona"):

        self.state_name = state_name

        self.read_geojson()
        self.init_webdriver()


    def read_geojson(self):
        """read in polygon coordinates
        """

        state_geojsons = json.load(open("./us-state-boundaries.json"))

        state_geojson = [
            x for x in state_geojsons
            if x["fields"]["name"] == self.state_name
        ][0]

        geojson_data = state_geojson["fields"]
        self.center_lat, self.center_lon = geojson_data["centlat"], geojson_data["centlon"]
        
        # (longitude, latitude)
        self.state_boundary = np.array(
            geojson_data["st_asgeojson"]["coordinates"][0]
        )

        self.state_polygon = Polygon(self.state_boundary)

    def is_point_in_state(self, lon, lat):
        """check if point is within the boundaries of, or touching
            the state polygon

        Parameters:
            lon (float): longitude of point to check
            lat (float): latitude of point to check
        """

        point = Point(lon, lat)

        if (
            self.state_polygon.contains(point)
            | self.state_polygon.touches(point)
            | point.within(self.state_polygon)
        ):
            return True

        else:
            return False

    def init_webdriver(self):
        """initialize headless chrome webdriver
        """

        browser_options = webdriver.ChromeOptions()
        browser_options.add_argument("headless")

        self.driver = webdriver.Chrome(
            executable_path="C:\chromedriver_win32\chromedriver.exe",
            options=browser_options
        )

    def create_maps_url(self, search_term, lat, lon):
        """
        """

        # warning: not tested for more 2+ terms in search_term

        return f"https://www.google.com/maps/search/{search_term}/@{lat},{lon},{self.ZOOM_FACTOR}z"

    def get_soup(self):

        pass


if __name__ == "__main__":

    x = State()
    print(x.state_boundary)