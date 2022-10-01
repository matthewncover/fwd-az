# data manipulation imports
import numpy as np, pandas as pd
import re

# geojson imports
import json
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point

# web scraping imports
from selenium import webdriver

# homegrown imports
from maps_section_search import MapsSectionSearch

class StateSearch:

    ZOOM_FACTOR = 15
    LATLON_DELTA = 0.0307

    def __init__(self, state_name = "Arizona"):

        self.state_name = state_name
        self.get_state_abr()

        self.read_geojson()
        # self.init_webdriver() # don't want to init webdriver for every map section
        self.init_lat_lon()

    def get_state_abr(self):

        state_abr_dict = {
            "Arizona": "AZ"
        }

        self.state_abr = state_abr_dict[self.state_name]


    def read_geojson(self):
        """read in polygon coordinates
        """

        state_geojsons = json.load(open("./google-maps-search/us-state-boundaries.json"))

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

        Returns:
            bool
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
        """google maps url

        Parameters:
            search_term (str): single term to search google maps
            lat (float): latitude center of search
            lon (float): longitude center of search

        Returns:
            (str): google maps url
        """

        # warning: not tested for more 2+ terms in search_term
        
        url = f"https://www.google.com/maps/search/{search_term}/@{lat},{lon},{self.ZOOM_FACTOR}z"

        return url

    def init_lat_lon(self):
        """starts grid search at most north-east point
        for AZ, this is the four corners monument
        """

        lat_lon_sum = self.state_boundary[:, 0] + self.state_boundary[:, 1]

        north_east_ind = np.where(
            lat_lon_sum == lat_lon_sum.max()
        )

        self.lon0, self.lat0 = self.state_boundary[north_east_ind][0]

    def search_businesses(self, search_term, lat, lon):

        url = self.create_maps_url(search_term, lat, lon)

        search_results = MapsSectionSearch(self.driver, self.state_abr, url)

        return search_results



if __name__ == "__main__":

    x = StateSearch()
    x.init_webdriver()

    lat = 33.3068621
    lon = -111.8752508

    search_results = x.search_businesses(
        search_term="gym", 
        lat=lat, lon=lon
        )

    print("done")